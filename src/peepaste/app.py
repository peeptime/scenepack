from __future__ import annotations

import sys
from pathlib import Path

from peepaste.cli import main as cli_main
from peepaste.ui.tray import run_tray


def main() -> int:
    if len(sys.argv) > 1:
        return cli_main(sys.argv[1:])
    return run_tray(Path(""))


if __name__ == "__main__":
    raise SystemExit(main())

