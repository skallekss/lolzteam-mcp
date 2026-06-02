from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


_SLUG_RE = re.compile(r"[^a-zA-Z0-9]+")
_MCP_NAME_MAX = 64


@dataclass
class Param:
    name: str
    location: str
    required: bool
    schema: dict[str, Any]
    description: str | None = None


@dataclass
class Operation:
    tool_name: str
    operation_id: str
    method: str
    path: str
    summary: str
    description: str
    tag: str
    params: list[Param] = field(default_factory=list)
    body_schema: dict[str, Any] | None = None
    body_required: bool = False
    body_content_type: str | None = None

    def input_schema(self) -> dict[str, Any]:
        properties: dict[str, Any] = {}
        required: list[str] = []
        for p in self.params:
            schema = dict(p.schema or {"type": "string"})
            if p.description and not schema.get("description"):
                schema["description"] = p.description
            schema["x-in"] = p.location
            properties[p.name] = schema
            if p.required:
                required.append(p.name)
        if self.body_schema is not None:
            properties["body"] = {
                "type": "object",
                "description": f"Request body ({self.body_content_type or 'application/json'})",
                **self.body_schema,
            }
            if self.body_required:
                required.append("body")
        return {
            "type": "object",
            "properties": properties,
            "required": required,
            "additionalProperties": False,
        }


def load_spec(path: str | Path) -> dict[str, Any]:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def build_operations(spec: dict[str, Any], name_prefix: str = "") -> list[Operation]:
    paths = spec.get("paths") or {}
    ops: list[Operation] = []
    used_names: set[str] = set()
    name_budget = _MCP_NAME_MAX - len(name_prefix)

    for path, path_item in paths.items():
        common_params = path_item.get("parameters") or []
        for method in ("get", "post", "put", "delete", "patch"):
            op_def = path_item.get(method)
            if not op_def:
                continue
            op = _build_one(spec, method, path, op_def, common_params, used_names, name_budget)
            if name_prefix:
                op = Operation(
                    tool_name=name_prefix + op.tool_name,
                    operation_id=op.operation_id,
                    method=op.method,
                    path=op.path,
                    summary=op.summary,
                    description=op.description,
                    tag=op.tag,
                    params=op.params,
                    body_schema=op.body_schema,
                    body_required=op.body_required,
                    body_content_type=op.body_content_type,
                )
            ops.append(op)
            used_names.add(op.tool_name.removeprefix(name_prefix))
    return ops


def _build_one(
    spec: dict[str, Any],
    method: str,
    path: str,
    op_def: dict[str, Any],
    common_params: list[dict[str, Any]],
    used_names: set[str],
    name_budget: int = _MCP_NAME_MAX,
) -> Operation:
    op_id = op_def.get("operationId") or f"{method}_{_slug(path)}"
    tool_name = _make_tool_name(op_id, used_names, name_budget)

    raw_params = list(common_params) + list(op_def.get("parameters") or [])
    params: list[Param] = []
    for raw in raw_params:
        resolved = _resolve(spec, raw)
        if not resolved:
            continue
        params.append(
            Param(
                name=resolved.get("name") or "",
                location=resolved.get("in") or "query",
                required=bool(resolved.get("required")),
                schema=_inline_refs(spec, resolved.get("schema") or {}),
                description=resolved.get("description"),
            )
        )

    body_schema = None
    body_required = False
    body_content_type = None
    request_body = op_def.get("requestBody")
    if request_body:
        rb = _resolve(spec, request_body) or request_body
        body_required = bool(rb.get("required"))
        content = rb.get("content") or {}
        for ct in ("application/json", "multipart/form-data", "application/x-www-form-urlencoded"):
            if ct in content:
                body_content_type = ct
                body_schema = _inline_refs(spec, content[ct].get("schema") or {})
                break
        if body_schema is None and content:
            first_ct = next(iter(content))
            body_content_type = first_ct
            body_schema = _inline_refs(spec, content[first_ct].get("schema") or {})

    tag = (op_def.get("tags") or ["api"])[0]
    summary = op_def.get("summary") or op_id
    description = op_def.get("description") or summary

    return Operation(
        tool_name=tool_name,
        operation_id=op_id,
        method=method.upper(),
        path=path,
        summary=summary,
        description=description,
        tag=tag,
        params=[p for p in params if p.name],
        body_schema=body_schema,
        body_required=body_required,
        body_content_type=body_content_type,
    )


def _make_tool_name(op_id: str, used: set[str], limit: int = _MCP_NAME_MAX) -> str:
    base = _slug(op_id).strip("_").lower()
    if not base:
        base = "op"
    base = base[:limit]
    candidate = base
    n = 2
    while candidate in used:
        suffix = f"_{n}"
        candidate = (base[: limit - len(suffix)] + suffix)
        n += 1
    return candidate


def _slug(value: str) -> str:
    return _SLUG_RE.sub("_", value)


def _resolve(spec: dict[str, Any], node: Any) -> dict[str, Any] | None:
    if not isinstance(node, dict):
        return None
    ref = node.get("$ref")
    if ref:
        return _resolve(spec, _follow_ref(spec, ref))
    return node


def _follow_ref(spec: dict[str, Any], ref: str) -> dict[str, Any]:
    if not ref.startswith("#/"):
        return {}
    parts = ref[2:].split("/")
    cur: Any = spec
    for p in parts:
        p = p.replace("~1", "/").replace("~0", "~")
        if not isinstance(cur, dict) or p not in cur:
            return {}
        cur = cur[p]
    return cur if isinstance(cur, dict) else {}


def _inline_refs(spec: dict[str, Any], node: Any, depth: int = 0, seen: tuple[str, ...] = ()) -> Any:
    if depth > 30:
        return {}
    if isinstance(node, list):
        return [_inline_refs(spec, item, depth + 1, seen) for item in node]
    if not isinstance(node, dict):
        return node
    if "$ref" in node:
        ref = node["$ref"]
        if ref in seen:
            return {"type": "object", "description": f"(recursive ref {ref})"}
        target = _follow_ref(spec, ref)
        return _inline_refs(spec, target, depth + 1, seen + (ref,))
    return {k: _inline_refs(spec, v, depth + 1, seen) for k, v in node.items()}


def default_spec_path(name: str = "market") -> Path:
    return Path(__file__).parent / "specs" / f"{name}.json"
