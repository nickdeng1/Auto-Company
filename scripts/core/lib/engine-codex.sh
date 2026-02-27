#!/bin/bash
# ============================================================
# Auto Company — Codex Engine Adapter
# ============================================================
# Provides Codex-specific functions for the unified auto-loop.
# Source this file after lib/common.sh
# ============================================================

ENGINE="codex"

# === Binary Resolution ===

resolve_codex_bin() {
    if [ -n "$CODEX_BIN" ]; then
        if [ -x "$CODEX_BIN" ]; then
            echo "$CODEX_BIN"
            return 0
        fi
        if command -v "$CODEX_BIN" >/dev/null 2>&1; then
            command -v "$CODEX_BIN"
            return 0
        fi
    fi

    # Prefer WSL-local Codex installed via nvm.
    local nvm_candidate=""
    for candidate in "$HOME"/.nvm/versions/node/*/bin/codex; do
        if [ -x "$candidate" ]; then
            nvm_candidate="$candidate"
        fi
    done
    if [ -n "$nvm_candidate" ]; then
        echo "$nvm_candidate"
        return 0
    fi

    # Fallback: ask an interactive bash shell (loads user profile).
    local interactive_candidate
    interactive_candidate=$(bash -ic 'command -v codex' 2>/dev/null | tail -n1 | tr -d '\r' || true)
    if [ -n "$interactive_candidate" ] && [ -x "$interactive_candidate" ]; then
        echo "$interactive_candidate"
        return 0
    fi

    # Last fallback: current shell PATH.
    if command -v codex >/dev/null 2>&1; then
        command -v codex
        return 0
    fi

    return 1
}

# === Engine Initialization ===

engine_init() {
    if ! RESOLVED_ENGINE_BIN="$(resolve_codex_bin)"; then
        echo "Error: Codex CLI not found. Install Codex and verify with 'codex --version'."
        exit 1
    fi

    # Warn if using Windows-mounted path
    case "$RESOLVED_ENGINE_BIN" in
        /mnt/c/*)
            log "Warning: Codex binary resolves to Windows-mounted path. Prefer WSL-local install for stability."
            ;;
    esac
}

# === Cycle Execution ===

run_engine_cycle() {
    local prompt="$1"
    local output_file timeout_flag message_file

    output_file=$(mktemp)
    timeout_flag=$(mktemp)
    message_file=$(mktemp)

    set +e
    (
        cd "${PROJECT_DIR}" || exit 1
        local codex_cmd=("$RESOLVED_ENGINE_BIN" "exec" "-c" "sandbox_mode=\"${CODEX_SANDBOX_MODE}\"" "-o" "$message_file")
        if [ -n "$MODEL" ]; then
            codex_cmd+=("-m" "$MODEL")
        fi
        codex_cmd+=("$prompt")
        "${codex_cmd[@]}"
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
    RESULT_MESSAGE=$(cat "$message_file" 2>/dev/null || true)
    rm -f "$output_file" "$message_file"

    if [ -s "$timeout_flag" ]; then
        CYCLE_TIMED_OUT=1
        EXIT_CODE=124
    else
        CYCLE_TIMED_OUT=0
    fi
    rm -f "$timeout_flag"
}

# === Metadata Extraction ===

extract_cycle_metadata() {
    CYCLE_COST="N/A"
    CYCLE_SUBTYPE="unknown"
    CYCLE_TYPE="codex_exec"

    RESULT_TEXT=$(echo "$RESULT_MESSAGE" | head -c 2000 || true)
    if [ -z "$RESULT_TEXT" ]; then
        RESULT_TEXT=$(echo "$OUTPUT" | head -c 2000 || true)
    fi

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
    log "Sandbox: ${CODEX_SANDBOX_MODE}"
}