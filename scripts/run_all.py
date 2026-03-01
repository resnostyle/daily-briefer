#!/usr/bin/env python3
"""Run all brief scripts in sequence. Exits with the first non-zero exit code."""
import os
import subprocess
import sys

# Allow importing when run from repo root or Docker (PYTHONPATH=/app)
_script_dir = os.path.dirname(os.path.abspath(__file__))
_repo_root = os.path.dirname(_script_dir)
if _repo_root not in sys.path:
    sys.path.insert(0, _repo_root)

SCRIPTS = [
    "scripts/daily_briefing.py",
    "scripts/github_digest.py",
    "scripts/hackernews_top.py",
    "scripts/chatgpt_brief.py",
]


def main() -> int:
    for script in SCRIPTS:
        path = os.path.join(_repo_root, script)
        if not os.path.isfile(path):
            print(f"Skip (not found): {script}", file=sys.stderr)
            continue
        print(f"Running {script}...", file=sys.stderr)
        result = subprocess.run(
            [sys.executable, path],
            cwd=_repo_root,
        )
        if result.returncode != 0:
            print(f"Failed: {script} (exit {result.returncode})", file=sys.stderr)
            return result.returncode
    return 0


if __name__ == "__main__":
    sys.exit(main())
