#!/usr/bin/env python3

from __future__ import annotations

import subprocess
import sys
import os
from pathlib import Path


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    script = repo_root / "scripts" / "session_capture.py"
    stdin_data = "" if sys.stdin.isatty() else sys.stdin.read()
    result = subprocess.run(
        [sys.executable, str(script), "capture", "--event", "PreCompact"],
        cwd=repo_root,
        input=stdin_data,
        text=True,
        capture_output=True,
        env={**os.environ, "CLAUDE_INVOKED_BY": "commandclaw-hook"},
    )
    if result.stdout:
        sys.stdout.write(result.stdout)
    if result.stderr:
        sys.stderr.write(result.stderr)
    return result.returncode


if __name__ == "__main__":
    raise SystemExit(main())
