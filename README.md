# Daily Briefing

**Purpose:** This repo runs scheduled scripts that produce daily briefings and informational posts and deliver them to you via Telegram. Everything runs in containers and can be triggered by cron or systemd. You get:

- **Daily briefing** — A configurable morning brief (placeholder sections; plug in weather, headlines, reminders).
- **Informational posts** — Short tips or quotes on a schedule.
- **GitHub trending digest** — Top 10 trending repos (today).
- **Hacker News top 10** — Top stories from HN.
- **ChatGPT brief** — YAML-defined prompts (e.g. “check CNN for latest news and summarize with links”) run through the OpenAI API, optionally summarized, then sent to Telegram.

Edit config (e.g. `config/prompts.yaml`) and run the container on a schedule; no code changes needed for new prompts or brief types.

## Prerequisites

- Docker (and optionally Docker Compose)
- A Telegram bot token ([@BotFather](https://t.me/BotFather)) and the chat/channel id to send to

## Development

- **mise** — Runtime and tasks are defined in `.mise.toml`. With [mise](https://mise.jdx.dev/) installed, run:
  - `mise install` — Install Python, hk, pkl, ruff (and other tools).
  - `mise run build` — Build the Docker image.
  - `mise run run-briefing` — Run the daily briefing (requires `.env`).
  - `mise run run-github` / `mise run run-hn` / `mise run run-chatgpt` — Run each brief type.
  - `mise run install-hooks` — Install git hooks via [hk](https://hk.jdx.dev/) (uses `hk install --mise` so hooks run with `mise x`).
  - `mise run pre-commit` — Run the pre-commit hook manually (`hk run pre-commit`).
- **Pre-commit (hk)** — Git hooks are managed by [hk](https://hk.jdx.dev/); config is in `hk.pkl`. Hooks run ruff (Python lint/format) and a YAML check. See [hk mise integration](https://hk.jdx.dev/mise_integration.html).
- **CI** — A GitHub Action (`.github/workflows/build.yml`) builds the container image on push/PR and pushes the image to GitHub Container Registry (GHCR) on push to the default branch.

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
