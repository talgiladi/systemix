from __future__ import annotations

import sys
from pathlib import Path

# Support direct execution via `python3 main.py` from `src/mcp_host`.
if __package__ in {None, ""}:
    package_dir = Path(__file__).resolve().parent
    src_root = package_dir.parent
    package_dir_str = str(package_dir)
    sys.path = [entry for entry in sys.path if entry != package_dir_str]
    sys.path.insert(0, str(src_root))

import uvicorn

from mcp_host.app import create_app
from mcp_host.config import load_settings


def main() -> None:
    settings = load_settings()
    app = create_app(settings)
    uvicorn.run(
        app,
        host=settings.server.host,
        port=settings.server.port,
        log_config=None,
        access_log=settings.logging.access_log,
    )


if __name__ == "__main__":
    main()
