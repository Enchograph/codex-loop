#!/usr/bin/env bash

set -euo pipefail

trap 'echo "Script failed at line $LINENO." >&2' ERR

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_FILE="$SCRIPT_DIR/codex_supervised_loop.json"
CONFIG_JSON=""
CURRENT_CHILD_PID=""
STOP_REQUESTED=0

request_stop() {
  STOP_REQUESTED=1
  echo
  echo "Stop requested. Terminating current round..."
  if [[ -n "$CURRENT_CHILD_PID" ]]; then
    kill -INT "$CURRENT_CHILD_PID" 2>/dev/null || true
    sleep 1
    kill -TERM "$CURRENT_CHILD_PID" 2>/dev/null || true
  fi
}

trap request_stop INT TERM

require_cmd() {
  if ! command -v "$1" >/dev/null 2>&1; then
    echo "Required command not found: $1" >&2
    exit 1
  fi
}

json_get_raw() {
  local key="$1"
  jq -r "$key" <<<"$CONFIG_JSON"
}

json_get_string() {
  local key="$1"
  jq -er "$key | strings" <<<"$CONFIG_JSON"
}

json_get_bool() {
  local key="$1"
  jq -r "$key | if type == \"boolean\" then . else error(\"expected boolean\") end" <<<"$CONFIG_JSON"
}

json_get_number() {
  local key="$1"
  jq -er "$key | if type == \"number\" then . else error(\"expected number\") end" <<<"$CONFIG_JSON"
}

usage() {
  cat <<'EOF'
This script reads all settings from:
  codex_supervised_loop.json

Behavior:
  - Runs "codex exec" with the configured prompt
  - Waits for the process to exit before considering the round complete
  - Stops after each round and waits for manual confirmation
  - Applies only a total wall-clock limit for the whole loop
  - `log_dir` is optional and defaults to `workdir/.codex/log`
  - Total timeout is configured in minutes
EOF
}

if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then
  usage
  exit 0
fi

if [[ ! -f "$CONFIG_FILE" ]]; then
  echo "Config file not found: $CONFIG_FILE" >&2
  exit 1
fi

require_cmd jq
require_cmd timeout
CONFIG_JSON="$(<"$CONFIG_FILE")"

CODEX_BIN="$(json_get_string '.codex_bin')"
WORKDIR="$(json_get_string '.workdir')"
PROMPT="$(json_get_string '.prompt')"
TOTAL_TIMEOUT_MINUTES="$(json_get_number 'if has("total_timeout_minutes") then .total_timeout_minutes else (.total_timeout_seconds / 60) end')"
LOG_DIR_RAW="$(json_get_raw 'if has("log_dir") then .log_dir else null end')"
SKIP_GIT_REPO_CHECK="$(json_get_bool '.skip_git_repo_check')"
SANDBOX_MODE="$(json_get_string '.sandbox_mode')"
APPROVAL_POLICY="$(json_get_string '.approval_policy')"
SEARCH_ENABLED="$(json_get_bool '.search_enabled')"
PROFILE_RAW="$(json_get_raw '.profile')"
MODEL_RAW="$(json_get_raw '.model')"

if ! command -v "$CODEX_BIN" >/dev/null 2>&1; then
  echo "Codex binary not found: $CODEX_BIN" >&2
  exit 1
fi

if [[ ! -d "$WORKDIR" ]]; then
  echo "Workdir not found: $WORKDIR" >&2
  exit 1
fi

if [[ "$LOG_DIR_RAW" == "null" || -z "$LOG_DIR_RAW" ]]; then
  LOG_DIR="$WORKDIR/.codex/log"
else
  LOG_DIR="$(json_get_string '.log_dir')"
fi

TOTAL_TIMEOUT_SECONDS="$((TOTAL_TIMEOUT_MINUTES * 60))"

mkdir -p "$LOG_DIR"

mapfile -t EXTRA_ARGS < <(jq -r '.extra_args[]? | strings' <<<"$CONFIG_JSON")

CODEX_ARGS=()
if [[ "$SKIP_GIT_REPO_CHECK" == "true" ]]; then
  CODEX_ARGS+=(--skip-git-repo-check)
fi
case "$APPROVAL_POLICY" in
  never)
    if [[ "$SANDBOX_MODE" == "danger-full-access" ]]; then
      CODEX_ARGS+=(--dangerously-bypass-approvals-and-sandbox)
    else
      CODEX_ARGS+=(--sandbox "$SANDBOX_MODE")
    fi
    ;;
  on-request|untrusted)
    CODEX_ARGS+=(--sandbox "$SANDBOX_MODE")
    ;;
  *)
    echo "Unsupported approval_policy for this codex version: $APPROVAL_POLICY" >&2
    exit 1
    ;;
esac
CODEX_ARGS+=(--cd "$WORKDIR")
if [[ "$SEARCH_ENABLED" == "true" ]]; then
  CODEX_ARGS+=(--enable web_search)
fi
if [[ "$PROFILE_RAW" != "null" ]]; then
  CODEX_ARGS+=(--profile "$(json_get_string '.profile')")
fi
if [[ "$MODEL_RAW" != "null" ]]; then
  CODEX_ARGS+=(--model "$(json_get_string '.model')")
fi
if [[ ${#EXTRA_ARGS[@]} -gt 0 ]]; then
  CODEX_ARGS+=("${EXTRA_ARGS[@]}")
fi

START_TS="$(date +%s)"
DEADLINE_TS="$((START_TS + TOTAL_TIMEOUT_SECONDS))"
ROUND=1

echo "Config file: $CONFIG_FILE"
echo "Codex binary: $CODEX_BIN"
echo "Workdir: $WORKDIR"
echo "Total timeout: ${TOTAL_TIMEOUT_MINUTES} minute(s)"
echo "Log dir: $LOG_DIR"
echo

while true; do
  if (( STOP_REQUESTED != 0 )); then
    echo "Stopped."
    exit 130
  fi

  NOW_TS="$(date +%s)"
  REMAINING_TOTAL="$((DEADLINE_TS - NOW_TS))"
  if (( REMAINING_TOTAL <= 0 )); then
    echo "Total timeout reached. Exiting."
    exit 0
  fi

  RUN_ID="$(date +%Y%m%d-%H%M%S)"
  ROUND_LOG_DIR="$LOG_DIR/round-${ROUND}-${RUN_ID}"
  mkdir -p "$ROUND_LOG_DIR"
  STDOUT_LOG="$ROUND_LOG_DIR/stdout.log"
  STDERR_LOG="$ROUND_LOG_DIR/stderr.log"
  FINAL_MSG_LOG="$ROUND_LOG_DIR/final-message.txt"

  echo "=== Round $ROUND ==="
  echo "Remaining total budget: $(((REMAINING_TOTAL + 59) / 60)) minute(s)"
  echo "Logs: $ROUND_LOG_DIR"

  set +e
  timeout --foreground "${REMAINING_TOTAL}s" \
    "$CODEX_BIN" exec \
    "${CODEX_ARGS[@]}" \
    -o "$FINAL_MSG_LOG" \
    "$PROMPT" \
    > >(tee "$STDOUT_LOG") \
    2> >(tee "$STDERR_LOG" >&2) &
  CURRENT_CHILD_PID=$!
  wait "$CURRENT_CHILD_PID"
  EXIT_CODE=$?
  CURRENT_CHILD_PID=""
  set -e

  case "$EXIT_CODE" in
    130)
      echo "Round $ROUND interrupted."
      ;;
    0)
      echo "Round $ROUND finished successfully."
      ;;
    124)
      echo "Total timeout reached during round $ROUND."
      ;;
    *)
      echo "Round $ROUND exited with code $EXIT_CODE."
      ;;
  esac

  if (( STOP_REQUESTED != 0 )); then
    echo "Stopped."
    exit 130
  fi

  if [[ -s "$FINAL_MSG_LOG" ]]; then
    echo
    echo "--- Final message ---"
    cat "$FINAL_MSG_LOG"
    echo
  fi

  NOW_TS="$(date +%s)"
  REMAINING_TOTAL="$((DEADLINE_TS - NOW_TS))"
  if (( REMAINING_TOTAL <= 0 )); then
    echo "Total timeout reached. Exiting."
    exit 0
  fi

  ROUND="$((ROUND + 1))"
  echo
done
