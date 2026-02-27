#!/bin/bash
# ============================================================
# Auto Company — Qwen Engine Adapter
# ============================================================
# Provides Qwen Code CLI-specific functions for the unified auto-loop.
# Source this file after lib/common.sh
# ============================================================

ENGINE="qwen"

# === Binary Resolution ===

resolve_qwen_bin() {
    if [ -n "$QWEN_BIN" ]; then
        if [ -x "$QWEN_BIN" ]; then
            echo "$QWEN_BIN"
            return 0
        fi
        if command -v "$QWEN_BIN" >/dev/null 2>&1; then
            command -v "$QWEN_BIN"
            return 0
        fi
    fi

    # Check common locations
    local candidates=(
        "$HOME/.npm-global/bin/qwen"
        "/usr/local/bin/qwen"
        "/usr/bin/qwen"
    )

    for candidate in "${candidates[@]}"; do
        if [ -x "$candidate" ]; then
            echo "$candidate"
            return 0
        fi
    done

    # Fallback: check PATH
    if command -v qwen >/dev/null 2>&1; then
        command -v qwen
        return 0
    fi

    return 1
}

# === Engine Initialization ===

engine_init() {
    if ! RESOLVED_ENGINE_BIN="$(resolve_qwen_bin)"; then
        echo "Error: Qwen CLI not found. Install with: npm install -g qwen-code"
        exit 1
    fi
}

# === Cycle Execution ===

run_engine_cycle() {
    local prompt="$1"
    local output_file timeout_flag

    output_file=$(mktemp)
    timeout_flag=$(mktemp)

    set +e
    (
        cd "${PROJECT_DIR}" || exit 1
        local qwen_cmd=("$RESOLVED_ENGINE_BIN" "--yolo")
        if [ -n "$MODEL" ]; then
            qwen_cmd+=("-m" "$MODEL")
        fi
        qwen_cmd+=("$prompt")
        "${qwen_cmd[@]}"
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

    if [ -s "$timeout_flag" ]; then
        CYCLE_TIMED_OUT=1
        EXIT_CODE=124
    else
        CYCLE_TIMED_OUT=0
    fi
    rm -f "$output_file" "$timeout_flag"
}

# === Metadata Extraction ===

extract_cycle_metadata() {
    CYCLE_SUBTYPE="unknown"

    # Extract last portion of output as summary
    RESULT_TEXT=$(echo "$OUTPUT" | tail -100 | head -c 2000 || true)

    if [ "$EXIT_CODE" -eq 0 ]; then
        CYCLE_SUBTYPE="success"
    else
        CYCLE_SUBTYPE="error"
    fi
}

# === Startup Info ===

engine_log_startup() {
    local bin_version
    bin_version=$("$RESOLVED_ENGINE_BIN" --version 2>/dev/null | head -n1 || true)
    log_startup_info "$RESOLVED_ENGINE_BIN" "$bin_version"
    log "Agent Teams: ENABLED (CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1)"
}