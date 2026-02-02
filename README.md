# Daily Briefing

Containerized daily scripts that build a daily briefing and informational posts and publish them to Telegram. The host runs the container on a schedule (cron or systemd timer).

## Prerequisites

- Docker (and optionally Docker Compose)
- A Telegram bot token ([@BotFather](https://t.me/BotFather)) and the chat/channel id to send to

## Configuration

Copy the example env file and set your secrets:

```bash
cp .env.example .env
# Edit .env: set TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID
```

## Build

```bash
docker build -t daily-briefing:latest .
```

## Run once

**Daily briefing (default):**

```bash
docker run --rm --env-file .env daily-briefing:latest
```

**Informational post (quote or tip):**

```bash
docker run --rm --env-file .env daily-briefing:latest python scripts/informational_post.py quote
docker run --rm --env-file .env daily-briefing:latest python scripts/informational_post.py tip
```

**GitHub trending digest (top 10 repos):**

```bash
docker run --rm --env-file .env daily-briefing:latest python scripts/github_digest.py
```

**Hacker News top 10:**

```bash
docker run --rm --env-file .env daily-briefing:latest python scripts/hackernews_top.py
```

**ChatGPT brief (YAML-driven prompts):**

Requires `OPENAI_API_KEY` in `.env`. Edit `config/prompts.yaml` to set prompts (e.g. "check CNN for the latest news and summarize with links") and an optional `summarize` prompt. The script runs each prompt via the OpenAI API, optionally runs a summarization step, and sends the result to Telegram.

```bash
docker run --rm --env-file .env daily-briefing:latest python scripts/chatgpt_brief.py
```

To use a different prompts file (e.g. a mounted volume): set `PROMPTS_YAML_PATH` to the path inside the container.

Example `config/prompts.yaml`:

```yaml
model: gpt-4o-mini
prompts:
  - "Check CNN for the latest news and summarize with links."
  - "Check BBC for top tech stories and summarize with links."
summarize: "Combine the above into one brief summary with links. Keep it concise."
```

- `prompts`: list of prompts sent to ChatGPT; each reply is collected.
- `summarize`: optional; if set, one more call is made with this prompt and the collected replies as context; the model's reply is sent to Telegram.
- `model`: optional; default `gpt-4o-mini`.

**With Docker Compose:**

```bash
docker compose run --rm daily-briefing
# Or override command:
docker compose run --rm daily-briefing python scripts/informational_post.py tip
docker compose run --rm daily-briefing python scripts/github_digest.py
docker compose run --rm daily-briefing python scripts/hackernews_top.py
docker compose run --rm daily-briefing python scripts/chatgpt_brief.py
```

## Scheduling with cron

Use an absolute path to your env file and image. Example: run the daily briefing every day at 8:00:

```cron
0 8 * * * docker run --rm --env-file /path/to/daily-briefing/.env daily-briefing:latest
```

To run both briefing and a post in one go, use a wrapper script that runs the container twice (or add a `scripts/run_all.py` that runs both and a single cron line).

## Scheduling with systemd

1. Create a oneshot service (e.g. `/etc/systemd/system/daily-briefing.service`):

```ini
[Unit]
Description=Daily Briefing to Telegram

[Service]
Type=oneshot
ExecStart=/usr/bin/docker run --rm --env-file /path/to/daily-briefing/.env daily-briefing:latest
```

2. Create a timer (e.g. `/etc/systemd/system/daily-briefing.timer`):

```ini
[Unit]
Description=Run Daily Briefing daily at 8:00

[Timer]
OnCalendar=*-*-* 08:00:00
Persistent=true

[Install]
WantedBy=timers.target
```

3. Enable and start the timer:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now daily-briefing.timer
```

## Project layout

- `scripts/daily_briefing.py` — Builds and sends the daily briefing (placeholder content; add RSS/APIs later).
- `scripts/informational_post.py` — Builds and sends one informational post (quote or tip; extend with more types as needed).
- `scripts/github_digest.py` — Fetches GitHub trending (top 10 repos today) and sends digest to Telegram.
- `scripts/hackernews_top.py` — Fetches Hacker News top 10 stories and sends to Telegram.
- `scripts/chatgpt_brief.py` — Runs prompts from YAML via OpenAI (ChatGPT), optionally summarizes, sends result to Telegram.
- `config/prompts.yaml` — YAML config: `prompts` (list of prompts), optional `summarize`, optional `model`. Override path with `PROMPTS_YAML_PATH`.
- `src/telegram.py` — Shared Telegram publisher (Bot API; uses `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID`).
