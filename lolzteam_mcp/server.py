from __future__ import annotations

import json
import logging
from collections import defaultdict
from dataclasses import dataclass
from typing import Any

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp import types

from lolzteam_mcp.client import LolzteamClient
from lolzteam_mcp.config import APISettings, Settings
from lolzteam_mcp.openapi import Operation, build_operations, default_spec_path, load_spec


log = logging.getLogger("lolzteam_mcp")


@dataclass
class APIBinding:
    name: str
    settings: APISettings
    operations: list[Operation]


class TokenStore:
    def __init__(self, market: str | None, forum: str | None):
        self.tokens = {"market": market, "forum": forum}

    def get(self, api: str) -> str | None:
        return self.tokens.get(api)

    def set(self, api: str, token: str) -> None:
        self.tokens[api] = token


def _load_bindings(settings: Settings) -> list[APIBinding]:
    bindings: list[APIBinding] = []
    for api in settings.enabled_apis():
        spec_path = api.spec_path or default_spec_path(api.name)
        spec = load_spec(spec_path)
        ops = build_operations(spec, name_prefix=f"{api.name}_")
        bindings.append(APIBinding(name=api.name, settings=api, operations=ops))
        log.info("loaded %d operations for %s", len(ops), api.name)
    return bindings


def build_server(settings: Settings | None = None) -> Server:
    settings = settings or Settings.load()
    logging.basicConfig(level=settings.log_level, format="%(asctime)s %(levelname)s %(name)s %(message)s")

    bindings = _load_bindings(settings)
    by_name: dict[str, tuple[APIBinding, Operation]] = {}
    for binding in bindings:
        for op in binding.operations:
            by_name[op.tool_name] = (binding, op)

    token_store = TokenStore(
        market=settings.market.token if settings.market.enabled else None,
        forum=settings.forum.token if settings.forum.enabled else None,
    )

    server = Server("lolzteam-mcp")

    @server.list_tools()
    async def _list_tools() -> list[types.Tool]:
        meta = _meta_tools(bindings)
        return meta + [_operation_to_tool(op) for _, op in by_name.values()]

    @server.call_tool()
    async def _call_tool(name: str, arguments: dict[str, Any] | None) -> list[types.TextContent]:
        args = arguments or {}

        if name == "lolzteam_list_endpoints":
            return _text(_list_endpoints_payload(bindings, args))

        if name == "lolzteam_describe_endpoint":
            target = args.get("tool")
            entry = by_name.get(target) if target else None
            if entry is None:
                return _text({"ok": False, "error": f"unknown tool: {target}", "hint": "use lolzteam_list_endpoints to discover"})
            return _text(_describe_op(entry[0], entry[1]))

        if name == "lolzteam_set_token":
            target_api = (args.get("api") or "").strip().lower()
            new_token = (args.get("token") or "").strip()
            if not new_token:
                return _text({"ok": False, "error": "token is empty"})
            targets = ["market", "forum"] if target_api in ("", "all", "both") else [target_api]
            for t in targets:
                if t not in ("market", "forum"):
                    return _text({"ok": False, "error": f"unknown api: {t}", "hint": "use 'market', 'forum' or omit for both"})
                token_store.set(t, new_token)
            return _text({"ok": True, "stored_for": targets})

        entry = by_name.get(name)
        if entry is None:
            return _text({"ok": False, "error": f"unknown tool: {name}"})

        binding, op = entry
        token = token_store.get(binding.name)
        if not token:
            return _text(
                {
                    "ok": False,
                    "error": f"no token for {binding.name}",
                    "hint": _token_hint(binding.name),
                }
            )

        async with LolzteamClient(token=token, base_url=binding.settings.base_url, timeout=settings.timeout) as client:
            result = await client.call(op, args)
        return _text(result)

    return server


async def run_stdio() -> None:
    server = build_server()
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


def _meta_tools(bindings: list[APIBinding]) -> list[types.Tool]:
    enabled = [b.name for b in bindings]
    return [
        types.Tool(
            name="lolzteam_list_endpoints",
            description=f"Список всех Lolzteam tool'ов, сгруппированных по API ({', '.join(enabled)}) и разделу. Принимает фильтры api и tag.",
            inputSchema={
                "type": "object",
                "properties": {
                    "api": {"type": "string", "description": "Опциональный фильтр: market | forum"},
                    "tag": {"type": "string", "description": "Опциональный фильтр по разделу (case-insensitive substring)"},
                },
                "additionalProperties": False,
            },
        ),
        types.Tool(
            name="lolzteam_describe_endpoint",
            description="Полная схема параметров, путь и описание конкретного метода по имени tool'а.",
            inputSchema={
                "type": "object",
                "properties": {"tool": {"type": "string", "description": "Имя tool'а, например market_category_steam или forum_threads_create"}},
                "required": ["tool"],
                "additionalProperties": False,
            },
        ),
        types.Tool(
            name="lolzteam_set_token",
            description="Установить Bearer-токен в рантайме. Действует до перезапуска процесса. api: 'market', 'forum' или пусто для обоих сразу.",
            inputSchema={
                "type": "object",
                "properties": {
                    "token": {"type": "string", "description": "Lolzteam API токен"},
                    "api": {"type": "string", "description": "market | forum | пусто для обоих"},
                },
                "required": ["token"],
                "additionalProperties": False,
            },
        ),
    ]


def _operation_to_tool(op: Operation) -> types.Tool:
    desc_parts = [f"[{op.method} {op.path}]", op.summary]
    if op.description and op.description != op.summary:
        snippet = op.description.strip().splitlines()[0]
        if snippet and snippet != op.summary:
            desc_parts.append(snippet)
    description = " — ".join(p for p in desc_parts if p)[:1024]
    return types.Tool(name=op.tool_name, description=description, inputSchema=op.input_schema())


def _list_endpoints_payload(bindings: list[APIBinding], args: dict[str, Any]) -> dict[str, Any]:
    api_filter = (args.get("api") or "").strip().lower()
    tag_filter = (args.get("tag") or "").strip().lower()

    by_api: dict[str, dict[str, list[dict[str, Any]]]] = {}
    totals: dict[str, int] = {}
    for b in bindings:
        if api_filter and api_filter != b.name:
            continue
        groups: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for op in b.operations:
            if tag_filter and tag_filter not in op.tag.lower():
                continue
            groups[op.tag].append({"tool": op.tool_name, "method": op.method, "path": op.path, "summary": op.summary})
        if groups:
            by_api[b.name] = dict(groups)
            totals[b.name] = sum(len(v) for v in groups.values())
    return {"ok": True, "totals": totals, "endpoints": by_api}


def _describe_op(binding: APIBinding, op: Operation) -> dict[str, Any]:
    return {
        "ok": True,
        "api": binding.name,
        "base_url": binding.settings.base_url,
        "tool": op.tool_name,
        "operation_id": op.operation_id,
        "method": op.method,
        "path": op.path,
        "tag": op.tag,
        "summary": op.summary,
        "description": op.description,
        "input_schema": op.input_schema(),
        "body_content_type": op.body_content_type,
    }


def _token_hint(api: str) -> str:
    if api == "market":
        return "Установить LOLZTEAM_MARKET_TOKEN или общий LOLZTEAM_TOKEN. Получить: https://zelenka.guru/account/api"
    if api == "forum":
        return "Установить LOLZTEAM_FORUM_TOKEN или общий LOLZTEAM_TOKEN. Получить: https://zelenka.guru/account/api"
    return "Установить токен через переменную окружения или lolzteam_set_token."


def _text(payload: Any) -> list[types.TextContent]:
    if isinstance(payload, str):
        return [types.TextContent(type="text", text=payload)]
    return [types.TextContent(type="text", text=json.dumps(payload, ensure_ascii=False, indent=2))]
