"""Send messages to Telegram via Bot API."""
import os
import sys

import requests

TELEGRAM_API = "https://api.telegram.org/bot{token}/sendMessage"
MAX_MESSAGE_LENGTH = 4096


def send_message(text: str, parse_mode: str | None = "Markdown") -> bool:
    """Send a single message to the configured Telegram chat.

    Uses TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID from the environment.
    If text exceeds Telegram's limit (4096 chars), it is split into multiple messages.

    Returns True on success, False on failure (and logs to stderr).
    """
    token = os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = os.environ.get("TELEGRAM_CHAT_ID")
    if not token or not chat_id:
        print("TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID must be set", file=sys.stderr)
        return False

    url = TELEGRAM_API.format(token=token)
    payload: dict = {"chat_id": chat_id, "text": text}
    if parse_mode:
        payload["parse_mode"] = parse_mode

    if len(text) <= MAX_MESSAGE_LENGTH:
        return _post(url, payload)

    # Split into chunks
    chunks = [
        text[i : i + MAX_MESSAGE_LENGTH]
        for i in range(0, len(text), MAX_MESSAGE_LENGTH)
    ]
    for chunk in chunks:
        payload["text"] = chunk
        if not _post(url, payload):
            return False
    return True


def _post(url: str, payload: dict) -> bool:
    try:
        r = requests.post(url, json=payload, timeout=30)
        r.raise_for_status()
        return True
    except requests.RequestException as e:
        print(f"Telegram API error: {e}", file=sys.stderr)
        if hasattr(e, "response") and e.response is not None and e.response.text:
            print(e.response.text, file=sys.stderr)
        return False
