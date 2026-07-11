#!/usr/bin/env python3
"""Bump the pinned test-framework tag: edit pyproject.toml -> `uv lock` -> show diff.

Usage: uv run scripts/bump-framework.py v0.2.0
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PYPROJECT = REPO_ROOT / "pyproject.toml"


def main() -> None:
    if len(sys.argv) != 2:
        print(f"usage: {sys.argv[0]} <vX.Y.Z>", file=sys.stderr)
        sys.exit(2)
    new_tag = sys.argv[1]

    text = PYPROJECT.read_text()
    updated = re.sub(
        r'(test-framework = \{ git = "[^"]+", tag = ")[^"]+(" \})',
        rf"\g<1>{new_tag}\g<2>",
        text,
        count=1,
    )
    if updated == text:
        raise RuntimeError("test-framework git source not found in pyproject.toml")
    PYPROJECT.write_text(updated)

    subprocess.run(["uv", "lock"], cwd=REPO_ROOT, check=True)
    subprocess.run(["git", "diff", "--", "pyproject.toml", "uv.lock"], cwd=REPO_ROOT, check=True)

    print(f"\nBumped test-framework to {new_tag}. Review the diff above, then commit.")


if __name__ == "__main__":
    main()
