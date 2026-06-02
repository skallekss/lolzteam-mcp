from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


def _bool(value: str | None, default: bool) -> bool:
    if value is None:
        return default
    return value.strip().lower() in ("1", "true", "yes", "on", "y")


@dataclass(frozen=True)
class APISettings:
    name: str
    base_url: str
    token: str | None
    spec_path: Path | None
    enabled: bool


@dataclass(frozen=True)
class Settings:
    market: APISettings
    forum: APISettings
    timeout: float
    log_level: str

    def enabled_apis(self) -> list[APISettings]:
        return [api for api in (self.market, self.forum) if api.enabled]

    @classmethod
    def load(cls) -> "Settings":
        shared_token = os.getenv("LOLZTEAM_TOKEN") or None

        market_spec = os.getenv("LOLZTEAM_MARKET_SPEC")
        forum_spec = os.getenv("LOLZTEAM_FORUM_SPEC")

        market = APISettings(
            name="market",
            base_url=os.getenv("LOLZTEAM_MARKET_BASE_URL", "https://prod-api.lzt.market").rstrip("/"),
            token=os.getenv("LOLZTEAM_MARKET_TOKEN") or shared_token,
            spec_path=Path(market_spec) if market_spec else None,
            enabled=_bool(os.getenv("LOLZTEAM_ENABLE_MARKET"), True),
        )
        forum = APISettings(
            name="forum",
            base_url=os.getenv("LOLZTEAM_FORUM_BASE_URL", "https://prod-api.lolz.live").rstrip("/"),
            token=os.getenv("LOLZTEAM_FORUM_TOKEN") or shared_token,
            spec_path=Path(forum_spec) if forum_spec else None,
            enabled=_bool(os.getenv("LOLZTEAM_ENABLE_FORUM"), True),
        )
        return cls(
            market=market,
            forum=forum,
            timeout=float(os.getenv("LOLZTEAM_HTTP_TIMEOUT", "30")),
            log_level=os.getenv("LOLZTEAM_LOG_LEVEL", "INFO").upper(),
        )
