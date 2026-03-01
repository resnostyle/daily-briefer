#!/bin/sh
# Default: run all briefs. Pass one script name (or shorthand) to run that script only.
# Examples: docker run ...  |  docker run ... github  |  docker run ... post quote
set -e
cd /app

run_script() {
  script="$1"
  shift
  exec python "$script" "$@"
}

if [ $# -eq 0 ]; then
  exec python scripts/run_all.py
fi

case "$1" in
  daily_briefing|briefing)
    shift
    run_script scripts/daily_briefing.py "$@"
    ;;
  github_digest|github)
    shift
    run_script scripts/github_digest.py "$@"
    ;;
  hackernews_top|hn)
    shift
    run_script scripts/hackernews_top.py "$@"
    ;;
  chatgpt_brief|chatgpt)
    shift
    run_script scripts/chatgpt_brief.py "$@"
    ;;
  informational_post|post)
    shift
    run_script scripts/informational_post.py "$@"
    ;;
  run_all|all)
    shift
    run_script scripts/run_all.py "$@"
    ;;
  *)
    # Allow passing script path directly, e.g. scripts/github_digest.py
    if [ -f "$1" ]; then
      script="$1"
      shift
      run_script "$script" "$@"
    else
      echo "Unknown script: $1. Use: daily_briefing|briefing, github_digest|github, hackernews_top|hn, chatgpt_brief|chatgpt, informational_post|post, run_all|all" >&2
      exit 1
    fi
    ;;
esac
