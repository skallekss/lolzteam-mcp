from __future__ import annotations

import asyncio
import sys

from lolzteam_mcp.server import run_stdio


def main() -> None:
    try:
        asyncio.run(run_stdio())
    except KeyboardInterrupt:
        sys.exit(0)


if __name__ == "__main__":
    main()
