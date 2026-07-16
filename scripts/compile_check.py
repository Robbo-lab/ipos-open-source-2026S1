"""Compile all Python files under the repo (syntax check)."""
from __future__ import annotations

import compileall
import sys
from pathlib import Path

def main() -> int:
    root = Path(__file__).resolve().parents[1]
    ok = compileall.compile_dir(str(root), quiet=1, force=False)
    return 0 if ok else 1

if __name__ == "__main__":
    raise SystemExit(main())
