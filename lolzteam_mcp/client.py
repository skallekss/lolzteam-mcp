from __future__ import annotations

import json
from typing import Any

import httpx

from lolzteam_mcp.openapi import Operation


class LolzteamClient:
    def __init__(self, token: str | None, base_url: str = "https://prod-api.lzt.market", timeout: float = 30.0, http: httpx.AsyncClient | None = None):
        self.base_url = base_url.rstrip("/")
        self.token = token
        self.timeout = timeout
        self._http = http
        self._owns_client = http is None

    async def __aenter__(self) -> "LolzteamClient":
        if self._http is None:
            self._http = httpx.AsyncClient(timeout=self.timeout)
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        if self._owns_client and self._http is not None:
            await self._http.aclose()
            self._http = None

    async def call(self, op: Operation, arguments: dict[str, Any]) -> dict[str, Any]:
        if self._http is None:
            self._http = httpx.AsyncClient(timeout=self.timeout)
            self._owns_client = True

        path = op.path
        query: dict[str, Any] = {}
        headers: dict[str, str] = {"Accept": "application/json"}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"

        body_value = arguments.get("body")

        for p in op.params:
            if p.name not in arguments:
                continue
            value = arguments[p.name]
            if value is None:
                continue
            if p.location == "path":
                path = path.replace("{" + p.name + "}", _stringify(value))
            elif p.location == "query":
                query[p.name] = _to_query(value)
            elif p.location == "header":
                headers[p.name] = _stringify(value)

        url = f"{self.base_url}{path}"

        json_body: Any = None
        data_body: Any = None
        files: Any = None
        if op.body_schema is not None and body_value is not None:
            ct = op.body_content_type or "application/json"
            if ct == "application/x-www-form-urlencoded":
                data_body = body_value
            elif ct == "multipart/form-data":
                files = body_value if isinstance(body_value, dict) else {"file": body_value}
            else:
                json_body = body_value

        response = await self._http.request(
            op.method,
            url,
            params=query or None,
            headers=headers,
            json=json_body,
            data=data_body,
            files=files,
        )

        return _format_response(response)


def _stringify(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)


def _to_query(value: Any) -> Any:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, (list, tuple)):
        return [_stringify(v) for v in value]
    return value


def _format_response(response: httpx.Response) -> dict[str, Any]:
    out: dict[str, Any] = {
        "status": response.status_code,
        "url": str(response.url),
    }
    try:
        out["json"] = response.json()
    except ValueError:
        text = response.text
        out["text"] = text if len(text) <= 8000 else text[:8000] + "...(truncated)"
    if response.status_code >= 400:
        out["ok"] = False
        out["error"] = _extract_error(out)
    else:
        out["ok"] = True
    return out


def _extract_error(payload: dict[str, Any]) -> str:
    body = payload.get("json") or {}
    if isinstance(body, dict):
        for key in ("errors", "error", "error_description", "message"):
            value = body.get(key)
            if value:
                return value if isinstance(value, str) else json.dumps(value, ensure_ascii=False)
    return f"HTTP {payload.get('status')}"
