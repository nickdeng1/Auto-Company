#!/bin/bash
# ============================================================
# Auto Company — 24/7 Autonomous Loop (OpenCode Engine)
# ============================================================
# Keeps OpenCode running continuously to drive the AI team.
# Uses fresh sessions with consensus.md as the relay baton.
#
# Usage:
#   ./auto-loop-opencode.sh              # Run in foreground
#
# Stop:
#   ./stop-loop.sh                       # Graceful stop
#   kill $(cat .auto-loop.pid)           # Force stop
#
# Config (env vars):
#   MODEL=...                            # Optional model override (e.g., anthropic/claude-sonnet-4)
#   LOOP_INTERVAL=30                     # Seconds between cycles (default: 30)
#   CYCLE_TIMEOUT_SECONDS=1800           # Max seconds per cycle before force-kill
#   MAX_CONSECUTIVE_ERRORS=5             # Circuit breaker threshold
#   COOLDOWN_SECONDS=300                 # Cooldown after circuit break
#   LIMIT_WAIT_SECONDS=3600              # Wait on usage limit
#   MAX_LOGS=200                         # Max cycle logs to keep
# ============================================================

set -euo pipefail

# === Resolve project root (always relative to this script) ===
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/../.." && pwd)"

LOG_DIR="$PROJECT_DIR/logs"
CONSENSUS_FILE="$PROJECT_DIR/memories/consensus.md"
PROMPT_FILE="$PROJECT_DIR/PROMPT.md"
PID_FILE="$PROJECT_DIR/.auto-loop-opencode.pid"
STATE_FILE="$PROJECT_DIR/.auto-loop-opencode-state"

# Loop settings (all overridable via env vars)
MODEL="${MODEL:-}"
MODEL_LABEL="${MODEL:-config-default}"
LOOP_INTERVAL="${LOOP_INTERVAL:-30}"
CYCLE_TIMEOUT_SECONDS="${CYCLE_TIMEOUT_SECONDS:-1800}"
MAX_CONSECUTIVE_ERRORS="${MAX_CONSECUTIVE_ERRORS:-5}"
COOLDOWN_SECONDS="${COOLDOWN_SECONDS:-300}"
LIMIT_WAIT_SECONDS="${LIMIT_WAIT_SECONDS:-3600}"
MAX_LOGS="${MAX_LOGS:-200}"

# === Functions ===

log() {
    local timestamp
    timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    local msg="[$timestamp] $1"
    echo "$msg" >> "$LOG_DIR/auto-loop-opencode.log"
    if [ -t 1 ]; then
        echo "$msg"
    fi
}

log_cycle() {
    local cycle_num=$1
    local status=$2
    local msg=$3
    local timestamp
    timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    echo "[$timestamp] Cycle #$cycle_num [$status] $msg" >> "$LOG_DIR/auto-loop.log"
    if [ -t 1 ]; then
        echo "[$timestamp] Cycle #$cycle_num [$status] $msg"
    fi
}

check_usage_limit() {
    local output="$1"
    if echo "$output" | grep -qi "usage limit\|rate limit\|too many requests\|resource_exhausted\|overloaded\|quota\|429\|billing\|insufficient credits"; then
        return 0
    fi
    return 1
}

check_stop_requested() {
    if [ -f "$PROJECT_DIR/.auto-loop-stop" ]; then
        rm -f "$PROJECT_DIR/.auto-loop-stop"
        return 0
    fi
    return 1
}

save_state() {
    cat > "$STATE_FILE" << EOF
LOOP_COUNT=$loop_count
ERROR_COUNT=$error_count
LAST_RUN=$(date '+%Y-%m-%d %H:%M:%S')
STATUS=$1
MODEL=$MODEL_LABEL
ENGINE=opencode
EOF
}

cleanup() {
    log "=== Auto Loop Shutting Down (PID $$) ==="
    rm -f "$PID_FILE"
    save_state "stopped"
    exit 0
}

get_file_size_bytes() {
    local target_file="$1"
    if [ ! -f "$target_file" ]; then
        echo 0
        return
    fi

    if stat -c%s "$target_file" >/dev/null 2>&1; then
        stat -c%s "$target_file"
        return
    fi

    if stat -f%z "$target_file" >/dev/null 2>&1; then
        stat -f%z "$target_file"
        return
    fi

    wc -c < "$target_file" | tr -d ' '
}

rotate_logs() {
    local count
    count=$(find "$LOG_DIR" -name "cycle-opencode-*.log" -type f 2>/dev/null | wc -l | tr -d ' ')
    if [ "$count" -gt "$MAX_LOGS" ]; then
        local to_delete=$((count - MAX_LOGS))
        find "$LOG_DIR" -name "cycle-opencode-*.log" -type f | sort | head -n "$to_delete" | xargs rm -f 2>/dev/null || true
        log "Log rotation: removed $to_delete old cycle logs"
    fi

    local log_size
    log_size=$(get_file_size_bytes "$LOG_DIR/auto-loop-opencode.log")
    if [ "$log_size" -gt 10485760 ]; then
        mv "$LOG_DIR/auto-loop-opencode.log" "$LOG_DIR/auto-loop-opencode.log.old"
        log "Main log rotated (was ${log_size} bytes)"
    fi
}

backup_consensus() {
    if [ -f "$CONSENSUS_FILE" ]; then
        cp "$CONSENSUS_FILE" "$CONSENSUS_FILE.bak"
    fi
}

restore_consensus() {
    if [ -f "$CONSENSUS_FILE.bak" ]; then
        cp "$CONSENSUS_FILE.bak" "$CONSENSUS_FILE"
        log "Consensus restored from backup after failed cycle"
    fi
}

validate_consensus() {
    if [ ! -s "$CONSENSUS_FILE" ]; then
        return 1
    fi
    if ! grep -q "^# Auto Company Consensus" "$CONSENSUS_FILE"; then
        return 1
    fi
    if ! grep -q "^## Next Action" "$CONSENSUS_FILE"; then
        return 1
    fi
    if ! grep -q "^## Company State" "$CONSENSUS_FILE"; then
        return 1
    fi
    return 0
}

consensus_changed_since_backup() {
    if [ ! -f "$CONSENSUS_FILE" ]; then
        return 1
    fi

    if [ ! -f "$CONSENSUS_FILE.bak" ]; then
        return 0
    fi

    if cmp -s "$CONSENSUS_FILE" "$CONSENSUS_FILE.bak"; then
        return 1
    fi

    return 0
}

run_opencode_cycle() {
    local prompt="$1"
    local output_file timeout_flag

    output_file=$(mktemp)
    timeout_flag=$(mktemp)

    set +e
    (
        cd "$PROJECT_DIR" || exit 1
        local opencode_cmd=("opencode" "run")
        if [ -n "$MODEL" ]; then
            opencode_cmd+=("-m" "$MODEL")
        fi
        opencode_cmd+=("$prompt")
        "${opencode_cmd[@]}"
    ) > "$output_file" 2>&1 &
    local opencode_pid=$!

    (
        sleep "$CYCLE_TIMEOUT_SECONDS"
        if kill -0 "$opencode_pid" 2>/dev/null; then
            echo "1" > "$timeout_flag"
            kill -TERM "$opencode_pid" 2>/dev/null || true
            sleep 5
            kill -KILL "$opencode_pid" 2>/dev/null || true
        fi
    ) &
    local watchdog_pid=$!

    wait "$opencode_pid"
    EXIT_CODE=$?

    kill "$watchdog_pid" 2>/dev/null || true
    wait "$watchdog_pid" 2>/dev/null || true
    set -e

    OUTPUT=$(cat "$output_file")
    rm -f "$output_file"

    if [ -s "$timeout_flag" ]; then
        CYCLE_TIMED_OUT=1
        EXIT_CODE=124
    else
        CYCLE_TIMED_OUT=0
    fi
    rm -f "$timeout_flag"
}

extract_cycle_metadata() {
    RESULT_TEXT=""
    CYCLE_SUBTYPE="unknown"
    CYCLE_TYPE="opencode_run"

    RESULT_TEXT=$(echo "$OUTPUT" | head -c 2000 || true)

    if [ "$EXIT_CODE" -eq 0 ]; then
        CYCLE_SUBTYPE="success"
    else
        CYCLE_SUBTYPE="error"
    fi
}

# === Setup ===

mkdir -p "$LOG_DIR" "$PROJECT_DIR/memories"

rm -f "$PROJECT_DIR/.auto-loop-stop"

if [ -f "$PID_FILE" ]; then
    existing_pid=$(cat "$PID_FILE")
    if kill -0 "$existing_pid" 2>/dev/null; then
        echo "Auto loop already running (PID $existing_pid). Stop it first with ./stop-loop.sh"
        exit 1
    fi
fi

if ! command -v opencode >/dev/null 2>&1; then
    echo "Error: OpenCode CLI not found. Install with: npm install -g @anthropics/anthropic-quickstarts-opencode-cli"
    exit 1
fi

if [ ! -f "$PROMPT_FILE" ]; then
    echo "Error: PROMPT.md not found at $PROMPT_FILE"
    exit 1
fi

echo $$ > "$PID_FILE"

trap cleanup SIGTERM SIGINT SIGHUP

loop_count=0
error_count=0

log "=== Auto Company Loop Started (PID $$) ==="
log "Project: $PROJECT_DIR"
log "Engine: opencode | Model: $MODEL_LABEL"
opencode_version=$(opencode --version 2>/dev/null | head -n1 || true)
if [ -n "$opencode_version" ]; then
    log "OpenCode version: $opencode_version"
fi
log "Interval: ${LOOP_INTERVAL}s | Timeout: ${CYCLE_TIMEOUT_SECONDS}s | Breaker: ${MAX_CONSECUTIVE_ERRORS} errors"

# === Main Loop ===

while true; do
    if check_stop_requested; then
        log "Stop requested. Shutting down gracefully."
        cleanup
    fi

    loop_count=$((loop_count + 1))
    cycle_log="$LOG_DIR/cycle-opencode-$(printf '%04d' "$loop_count")-$(date '+%Y%m%d-%H%M%S').log"

    log_cycle "$loop_count" "START" "Beginning work cycle"
    save_state "running"

    rotate_logs
    backup_consensus

    PROMPT=$(cat "$PROMPT_FILE")
    CONSENSUS=$(cat "$CONSENSUS_FILE" 2>/dev/null || echo "No consensus file found. This is the very first cycle.")
    FULL_PROMPT="$PROMPT

---

## Runtime Guardrails (must follow)

1. Early in the cycle, create or update \`memories/consensus.md\` with the required section skeleton.
2. If work scope is large, persist partial decisions to \`memories/consensus.md\` before deep dives.
3. Prefer shipping one completed milestone over broad parallel exploration.

---

## Current Consensus (pre-loaded, do NOT re-read this file)

$CONSENSUS

---

This is Cycle #$loop_count. Act decisively."

    run_opencode_cycle "$FULL_PROMPT"

    echo "$OUTPUT" > "$cycle_log"

    extract_cycle_metadata

    cycle_failed_reason=""
    cycle_soft_timeout=0
    if [ "$CYCLE_TIMED_OUT" -eq 1 ]; then
        if validate_consensus && consensus_changed_since_backup; then
            cycle_soft_timeout=1
        else
            cycle_failed_reason="Timed out after ${CYCLE_TIMEOUT_SECONDS}s"
        fi
    elif [ "$EXIT_CODE" -ne 0 ]; then
        cycle_failed_reason="Exit code $EXIT_CODE"
    elif ! validate_consensus; then
        cycle_failed_reason="consensus.md validation failed after cycle"
    fi

    if [ "$cycle_soft_timeout" -eq 1 ]; then
        log_cycle "$loop_count" "OK" "Timed out after ${CYCLE_TIMEOUT_SECONDS}s but consensus was updated; keeping progress (subtype: ${CYCLE_SUBTYPE})"
        if [ -n "$RESULT_TEXT" ]; then
            log_cycle "$loop_count" "SUMMARY" "$(echo "$RESULT_TEXT" | head -c 300)"
        fi
        error_count=0
    elif [ -z "$cycle_failed_reason" ]; then
        log_cycle "$loop_count" "OK" "Completed (subtype: ${CYCLE_SUBTYPE})"
        if [ -n "$RESULT_TEXT" ]; then
            log_cycle "$loop_count" "SUMMARY" "$(echo "$RESULT_TEXT" | head -c 300)"
        fi
        error_count=0
    else
        error_count=$((error_count + 1))
        log_cycle "$loop_count" "FAIL" "$cycle_failed_reason (subtype: ${CYCLE_SUBTYPE}, errors: $error_count/$MAX_CONSECUTIVE_ERRORS)"

        restore_consensus

        if check_usage_limit "$OUTPUT"; then
            log_cycle "$loop_count" "LIMIT" "API usage limit detected. Waiting ${LIMIT_WAIT_SECONDS}s..."
            save_state "waiting_limit"
            sleep "$LIMIT_WAIT_SECONDS"
            error_count=0
            continue
        fi

        if [ "$error_count" -ge "$MAX_CONSECUTIVE_ERRORS" ]; then
            log_cycle "$loop_count" "BREAKER" "Circuit breaker tripped! Cooling down ${COOLDOWN_SECONDS}s..."
            save_state "circuit_break"
            sleep "$COOLDOWN_SECONDS"
            error_count=0
            log "Circuit breaker reset. Resuming..."
        fi
    fi

    save_state "idle"
    log_cycle "$loop_count" "WAIT" "Sleeping ${LOOP_INTERVAL}s before next cycle..."
    sleep "$LOOP_INTERVAL"
done