#!/usr/bin/env python3
"""Run prompts from YAML via OpenAI (ChatGPT), optionally summarize, send result to Telegram."""
import os
import sys

# Allow importing src when run from repo root or from Docker (PYTHONPATH=/app)
_script_dir = os.path.dirname(os.path.abspath(__file__))
_repo_root = os.path.dirname(_script_dir)
if _repo_root not in sys.path:
    sys.path.insert(0, _repo_root)

import yaml
from openai import OpenAI

from src.telegram import send_message

DEFAULT_MODEL = "gpt-4o-mini"
MAX_RESPONSE_CHARS_FOR_SUMMARY = 500


def _get_prompts_path() -> str:
    path = os.environ.get("PROMPTS_YAML_PATH")
    if path:
        return path
    return os.path.join(_repo_root, "config", "prompts.yaml")


def _load_config(path: str) -> dict:
    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    if not data or not isinstance(data, dict):
        raise ValueError("YAML must be a non-empty object")
    prompts = data.get("prompts")
    if not prompts:
        raise ValueError("YAML must have a 'prompts' list with at least one prompt")
    if isinstance(prompts, str):
        prompts = [prompts]
    elif not isinstance(prompts, list):
        raise ValueError("'prompts' must be a list or a string")
    data["prompts"] = [str(p).strip() for p in prompts if p]
    if not data["prompts"]:
        raise ValueError("'prompts' must contain at least one non-empty prompt")
    return data


def _call_openai(client: OpenAI, model: str, user_content: str) -> str:
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": user_content}],
    )
    content = response.choices[0].message.content
    return content.strip() if content else ""


def main() -> int:
    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        print("OPENAI_API_KEY must be set", file=sys.stderr)
        return 1

    config_path = _get_prompts_path()
    if not os.path.isfile(config_path):
        print(f"Prompts config not found: {config_path}", file=sys.stderr)
        if send_message("ChatGPT brief failed: prompts config file not found.", parse_mode=None):
            pass
        return 1

    try:
        config = _load_config(config_path)
    except Exception as e:
        print(f"Invalid prompts config: {e}", file=sys.stderr)
        if send_message(f"ChatGPT brief failed: invalid config ({e}).", parse_mode=None):
            pass
        return 1

    model = config.get("model") or DEFAULT_MODEL
    prompts = config["prompts"]
    summarize_prompt = (config.get("summarize") or "").strip()

    try:
        client = OpenAI(api_key=api_key)
    except Exception as e:
        print(f"OpenAI client error: {e}", file=sys.stderr)
        if send_message("ChatGPT brief failed: could not create OpenAI client.", parse_mode=None):
            pass
        return 1

    responses = []
    for i, prompt in enumerate(prompts):
        try:
            content = _call_openai(client, model, prompt)
            responses.append(content)
        except Exception as e:
            print(f"OpenAI API error (prompt {i + 1}): {e}", file=sys.stderr)
            if send_message(
                f"ChatGPT brief failed: API error on prompt {i + 1}.",
                parse_mode=None,
            ):
                pass
            return 1

    if summarize_prompt:
        # Truncate each response for context to avoid token limits
        truncated = []
        for r in responses:
            if len(r) > MAX_RESPONSE_CHARS_FOR_SUMMARY:
                r = r[: MAX_RESPONSE_CHARS_FOR_SUMMARY - 3] + "..."
            truncated.append(r)
        context = "\n\n---\n\n".join(truncated)
        user_content = f"{summarize_prompt}\n\n---\n\n{context}"
        try:
            final_text = _call_openai(client, model, user_content)
        except Exception as e:
            print(f"OpenAI API error (summarize): {e}", file=sys.stderr)
            if send_message("ChatGPT brief failed: summarize step failed.", parse_mode=None):
                pass
            return 1
    else:
        final_text = "\n\n---\n\n".join(responses)

    if not final_text:
        final_text = "(No content generated.)"

    if send_message(final_text, parse_mode=None):
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
