#!/bin/bash
# ============================================================
# Auto Company — Common Library
# ============================================================
# Shared functions for all auto-loop scripts.
# Source this file: source lib/common.sh
# 
# Logging Format:
#   - Human-readable: logs/auto-loop-${ENGINE}.log
#   - Structured JSON: logs/auto-loop-${ENGINE}.jsonl
# ============================================================

# === Global Variables (set by main script) ===
# PROJECT_DIR, LOG_DIR, CONSENSUS_FILE, PROMPT_FILE, PID_FILE, STATE_FILE
# ENGINE, MODEL, MODEL_LABEL, MAX_LOGS, CYCLE_TIMEOUT_SECONDS, etc.

# === JSON Logging Helper ===
# Outputs a JSON line to the structured log file
log_json() {
    local event="$1"
    local data="${2:-{}}"
    local timestamp
    timestamp=$(date -u '+%Y-%m-%dT%H:%M:%SZ')
    
    # Build JSON object with required fields
    local json_line
    json_line=$(printf '{"ts":"%s","engine":"%s","event":"%s","pid":%s,%s}' \
        "$timestamp" "${ENGINE}" "$event" "$$" "$data")
    
    echo "$json_line" >> "${LOG_DIR}/auto-loop-${ENGINE}.jsonl"
}

# === Logging Functions ===

log() {
    local msg="$1"
    local timestamp
    timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    local human_msg="[$timestamp] $msg"
    
    # Human-readable log
    echo "$human_msg" >> "${LOG_DIR}/auto-loop-${ENGINE}.log"
    
    # Structured JSON log
    local escaped_msg
    escaped_msg=$(echo "$msg" | sed 's/"/\\"/g')
    log_json "log" "\"msg\":\"$escaped_msg\""
    
    # Console output (only if interactive)
    if [ -t 1 ]; then
        echo "$human_msg"
    fi
}

log_cycle() {
    local cycle_num=$1
    local status=$2
    local msg=$3
    local timestamp
    timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    local human_msg="[$timestamp] Cycle #$cycle_num [$status] $msg"
    
    # Human-readable log
    echo "$human_msg" >> "${LOG_DIR}/auto-loop-${ENGINE}.log"
    
    # Structured JSON log
    local escaped_msg
    escaped_msg=$(echo "$msg" | sed 's/"/\\"/g')
    log_json "cycle" "\"cycle\":$cycle_num,\"status\":\"$status\",\"msg\":\"$escaped_msg\""
    
    # Console output (only if interactive)
    if [ -t 1 ]; then
        echo "$human_msg"
    fi
}

# === Utility Functions ===

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

# === State Management ===

check_stop_requested() {
    if [ -f "${PROJECT_DIR}/.auto-loop-stop" ]; then
        rm -f "${PROJECT_DIR}/.auto-loop-stop"
        return 0
    fi
    return 1
}

save_state() {
    local status=$1
    cat > "${STATE_FILE}" << EOF
LOOP_COUNT=${loop_count}
ERROR_COUNT=${error_count}
LAST_RUN=$(date '+%Y-%m-%d %H:%M:%S')
STATUS=${status}
MODEL=${MODEL_LABEL}
ENGINE=${ENGINE}
EOF
}

cleanup() {
    log "=== Auto Loop Shutting Down (PID $$) ==="
    rm -f "${PID_FILE}"
    save_state "stopped"
    exit 0
}

# === Log Rotation ===

rotate_logs() {
    # Keep only the latest N cycle logs
    local count
    count=$(find "${LOG_DIR}" -name "cycle-${ENGINE}-*.log" -type f 2>/dev/null | wc -l | tr -d ' ')
    if [ "$count" -gt "${MAX_LOGS}" ]; then
        local to_delete=$((count - MAX_LOGS))
        find "${LOG_DIR}" -name "cycle-${ENGINE}-*.log" -type f | sort | head -n "$to_delete" | xargs rm -f 2>/dev/null || true
        log "Log rotation: removed $to_delete old cycle logs"
    fi

    # Rotate main log if over 10MB
    local log_size
    log_size=$(get_file_size_bytes "${LOG_DIR}/auto-loop-${ENGINE}.log")
    if [ "$log_size" -gt 10485760 ]; then
        mv "${LOG_DIR}/auto-loop-${ENGINE}.log" "${LOG_DIR}/auto-loop-${ENGINE}.log.old"
        log "Main log rotated (was ${log_size} bytes)"
    fi

    # Rotate JSON log if over 10MB
    local json_log_size
    json_log_size=$(get_file_size_bytes "${LOG_DIR}/auto-loop-${ENGINE}.jsonl")
    if [ "$json_log_size" -gt 10485760 ]; then
        mv "${LOG_DIR}/auto-loop-${ENGINE}.jsonl" "${LOG_DIR}/auto-loop-${ENGINE}.jsonl.old"
        log "JSON log rotated (was ${json_log_size} bytes)"
    fi
}

# === Consensus Management ===

backup_consensus() {
    if [ -f "${CONSENSUS_FILE}" ]; then
        cp "${CONSENSUS_FILE}" "${CONSENSUS_FILE}.bak"
    fi
}

restore_consensus() {
    if [ -f "${CONSENSUS_FILE}.bak" ]; then
        cp "${CONSENSUS_FILE}.bak" "${CONSENSUS_FILE}"
        log "Consensus restored from backup after failed cycle"
    fi
}

validate_consensus() {
    if [ ! -s "${CONSENSUS_FILE}" ]; then
        return 1
    fi
    if ! grep -q "^# Auto Company Consensus" "${CONSENSUS_FILE}"; then
        return 1
    fi
    if ! grep -q "^## Next Action" "${CONSENSUS_FILE}"; then
        return 1
    fi
    if ! grep -q "^## Company State" "${CONSENSUS_FILE}"; then
        return 1
    fi
    return 0
}

consensus_changed_since_backup() {
    if [ ! -f "${CONSENSUS_FILE}" ]; then
        return 1
    fi

    if [ ! -f "${CONSENSUS_FILE}.bak" ]; then
        return 0
    fi

    if cmp -s "${CONSENSUS_FILE}" "${CONSENSUS_FILE}.bak"; then
        return 1
    fi

    return 0
}

# Git commit consensus after successful cycle
# Creates a timestamped commit for audit trail
git_commit_consensus() {
    local cycle_num=$1
    local commit_msg="chore(consensus): update after cycle #${cycle_num}"

    # Check if we're in a git repo
    if ! git -C "${PROJECT_DIR}" rev-parse --git-dir >/dev/null 2>&1; then
        log "Warning: Not a git repo, skipping consensus commit"
        return 1
    fi

    # Check if consensus file has changes
    if ! git -C "${PROJECT_DIR}" diff --quiet "${CONSENSUS_FILE}" 2>/dev/null; then
        # Has staged or unstaged changes
        git -C "${PROJECT_DIR}" add "${CONSENSUS_FILE}"
        git -C "${PROJECT_DIR}" commit -m "$commit_msg" --no-verify 2>/dev/null || true
        log "Consensus committed: $commit_msg"
        return 0
    elif ! git -C "${PROJECT_DIR}" diff --cached --quiet "${CONSENSUS_FILE}" 2>/dev/null; then
        # Has staged changes
        git -C "${PROJECT_DIR}" commit -m "$commit_msg" --no-verify 2>/dev/null || true
        log "Consensus committed: $commit_msg"
        return 0
    fi

    return 0
}

# === Error Detection ===

check_usage_limit() {
    local output="$1"
    if echo "$output" | grep -qi "usage limit\|rate limit\|too many requests\|resource_exhausted\|overloaded\|quota\|429\|billing\|insufficient"; then
        return 0
    fi
    return 1
}

# === Prompt Building ===

build_full_prompt() {
    local cycle_num=$1
    local prompt consensus

    prompt=$(cat "${PROMPT_FILE}")
    consensus=$(cat "${CONSENSUS_FILE}" 2>/dev/null || echo "No consensus file found. This is the very first cycle.")

    cat << EOF
${prompt}

---

## Runtime Guardrails (must follow)

1. Early in the cycle, create or update \`memories/consensus.md\` with the required section skeleton.
2. If work scope is large, persist partial decisions to \`memories/consensus.md\` before deep dives.
3. Prefer shipping one completed milestone over broad parallel exploration.

---

## Current Consensus (pre-loaded, do NOT re-read this file)

${consensus}

---

This is Cycle #${cycle_num}. Act decisively.
EOF
}

# === Process Management ===

run_cycle_with_timeout() {
    local cycle_cmd=("$@")  # Command array to execute
    local output_file timeout_flag

    output_file=$(mktemp)
    timeout_flag=$(mktemp)

    set +e
    (
        cd "${PROJECT_DIR}" || exit 1
        "${cycle_cmd[@]}"
    ) > "$output_file" 2>&1 &
    local child_pid=$!

    (
        sleep "${CYCLE_TIMEOUT_SECONDS}"
        if kill -0 "$child_pid" 2>/dev/null; then
            echo "1" > "$timeout_flag"
            kill -TERM "$child_pid" 2>/dev/null || true
            sleep 5
            kill -KILL "$child_pid" 2>/dev/null || true
        fi
    ) &
    local watchdog_pid=$!

    wait "$child_pid"
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

# === Cycle Result Processing ===

process_cycle_result() {
    local cycle_num=$1
    local cycle_log=$2
    local result_text="${3:-}"

    # Save full output to cycle log
    echo "$OUTPUT" > "$cycle_log"

    # Determine failure reason
    CYCLE_FAILED_REASON=""
    CYCLE_SOFT_TIMEOUT=0

    if [ "$CYCLE_TIMED_OUT" -eq 1 ]; then
        if validate_consensus && consensus_changed_since_backup; then
            CYCLE_SOFT_TIMEOUT=1
        else
            CYCLE_FAILED_REASON="Timed out after ${CYCLE_TIMEOUT_SECONDS}s"
        fi
    elif [ "$EXIT_CODE" -ne 0 ]; then
        CYCLE_FAILED_REASON="Exit code $EXIT_CODE"
    elif ! validate_consensus; then
        CYCLE_FAILED_REASON="consensus.md validation failed after cycle"
    fi

    # Handle result
    if [ "$CYCLE_SOFT_TIMEOUT" -eq 1 ]; then
        log_cycle "$cycle_num" "OK" "Timed out after ${CYCLE_TIMEOUT_SECONDS}s but consensus was updated; keeping progress (subtype: ${CYCLE_SUBTYPE:-unknown})"
        if [ -n "$result_text" ]; then
            log_cycle "$cycle_num" "SUMMARY" "$(echo "$result_text" | head -c 300)"
        fi
        error_count=0
        return 0
    elif [ -z "$CYCLE_FAILED_REASON" ]; then
        log_cycle "$cycle_num" "OK" "Completed (subtype: ${CYCLE_SUBTYPE:-unknown})"
        if [ -n "$result_text" ]; then
            log_cycle "$cycle_num" "SUMMARY" "$(echo "$result_text" | head -c 300)"
        fi
        error_count=0
        return 0
    else
        error_count=$((error_count + 1))
        log_cycle "$cycle_num" "FAIL" "$CYCLE_FAILED_REASON (subtype: ${CYCLE_SUBTYPE:-unknown}, errors: $error_count/$MAX_CONSECUTIVE_ERRORS)"

        # Restore consensus on hard failure
        restore_consensus

        # Check for usage limit
        if check_usage_limit "$OUTPUT"; then
            log_cycle "$cycle_num" "LIMIT" "API usage limit detected. Waiting ${LIMIT_WAIT_SECONDS}s..."
            save_state "waiting_limit"
            sleep "${LIMIT_WAIT_SECONDS}"
            error_count=0
            return 1
        fi

        # Circuit breaker
        if [ "$error_count" -ge "${MAX_CONSECUTIVE_ERRORS}" ]; then
            log_cycle "$cycle_num" "BREAKER" "Circuit breaker tripped! Cooling down ${COOLDOWN_SECONDS}s..."
            save_state "circuit_break"
            sleep "${COOLDOWN_SECONDS}"
            error_count=0
            log "Circuit breaker reset. Resuming..."
        fi

        return 1
    fi
}

# === Setup Functions ===

setup_project() {
    mkdir -p "${LOG_DIR}" "${PROJECT_DIR}/memories"
    rm -f "${PROJECT_DIR}/.auto-loop-stop"
}

check_existing_instance() {
    if [ -f "${PID_FILE}" ]; then
        local existing_pid
        existing_pid=$(cat "${PID_FILE}")
        if kill -0 "$existing_pid" 2>/dev/null; then
            echo "Auto loop already running (PID $existing_pid). Stop it first with stop-loop.sh"
            exit 1
        fi
    fi
}

write_pid_file() {
    echo $$ > "${PID_FILE}"
}

setup_traps() {
    trap cleanup SIGTERM SIGINT SIGHUP
}

init_counters() {
    loop_count=0
    error_count=0
}

# === Startup Logging ===

log_startup_info() {
    local bin_path=$1
    local bin_version=$2

    log "=== Auto Company Loop Started (PID $$) ==="
    log "Project: ${PROJECT_DIR}"
    log "Engine: ${ENGINE} | Model: ${MODEL_LABEL}"
    log "${ENGINE} bin: ${bin_path}"
    if [ -n "$bin_version" ]; then
        log "${ENGINE} version: ${bin_version}"
    fi
    log "Interval: ${LOOP_INTERVAL}s | Timeout: ${CYCLE_TIMEOUT_SECONDS}s | Breaker: ${MAX_CONSECUTIVE_ERRORS} errors"

    # Log skills/agents count if available
    if [ -d "${PROJECT_DIR}/.claude/skills" ]; then
        local skill_count
        skill_count=$(find "${PROJECT_DIR}/.claude/skills" -name "SKILL.md" 2>/dev/null | wc -l | tr -d ' ')
        [ "$skill_count" -gt 0 ] && log "Skills available: $skill_count"
    fi
    if [ -d "${PROJECT_DIR}/.claude/agents" ]; then
        local agent_count
        agent_count=$(find "${PROJECT_DIR}/.claude/agents" -name "*.md" 2>/dev/null | wc -l | tr -d ' ')
        [ "$agent_count" -gt 0 ] && log "Agents available: $agent_count"
    fi
}