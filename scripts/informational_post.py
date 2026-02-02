#!/usr/bin/env python3
"""Build and send one informational post to Telegram.

Can be invoked with an optional type (e.g. quote, tip) via env POST_TYPE or argv.
"""
import os
import random
import sys

# Allow importing src when run from repo root or from Docker (PYTHONPATH=/app)
_script_dir = os.path.dirname(os.path.abspath(__file__))
_repo_root = os.path.dirname(_script_dir)
if _repo_root not in sys.path:
    sys.path.insert(0, _repo_root)

from src.telegram import send_message

# Placeholder content; can be moved to config or DB later
QUOTES = [
    "The only way to do great work is to love what you do. — Steve Jobs",
    "Stay hungry, stay foolish. — Steve Jobs",
    "It does not matter how slowly you go as long as you do not stop. — Confucius",
]

TIPS = [
    "Tip: Take a 5-minute walk after each focus block to stay sharp.",
    "Tip: Write down the one thing that must get done today before opening email.",
    "Tip: Batch similar tasks to reduce context switching.",
]


def get_post_type() -> str:
    """Post type from POST_TYPE env or first argv; default 'quote'."""
    t = os.environ.get("POST_TYPE") or (sys.argv[1] if len(sys.argv) > 1 else "quote")
    return t.strip().lower()


def build_post(post_type: str) -> str:
    """Build one post message by type."""
    if post_type == "tip":
        return random.choice(TIPS)
    if post_type == "quote":
        return random.choice(QUOTES)
    # Unknown type: fallback to quote
    return random.choice(QUOTES)


def main() -> int:
    post_type = get_post_type()
    text = build_post(post_type)
    if send_message(text, parse_mode=None):
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
