#!/bin/bash
# ============================================================
# Auto Company — Configuration
# ============================================================
# Centralized configuration management for auto-loop scripts.
# All values can be overridden via environment variables.
#
# Source this file: source lib/config.sh
#
# After sourcing, call setup_engine_paths() to set engine-specific paths.
# ============================================================

# === Project Paths (set once at load time) ===
# These are computed when config.sh is sourced
_CONFIG_SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$_CONFIG_SCRIPT_DIR/../../.." && pwd)"
LIB_DIR="$_CONFIG_SCRIPT_DIR"
LOG_DIR="$PROJECT_DIR/logs"
CONSENSUS_FILE="$PROJECT_DIR/memories/consensus.md"
PROMPT_FILE="$PROJECT_DIR/PROMPT.md"

# === Loop Settings ===
LOOP_INTERVAL="${LOOP_INTERVAL:-30}"              # Seconds between cycles
CYCLE_TIMEOUT_SECONDS="${CYCLE_TIMEOUT_SECONDS:-1800}"  # Max seconds per cycle
MAX_CONSECUTIVE_ERRORS="${MAX_CONSECUTIVE_ERRORS:-5}"    # Circuit breaker threshold
COOLDOWN_SECONDS="${COOLDOWN_SECONDS:-300}"       # Cooldown after circuit break
LIMIT_WAIT_SECONDS="${LIMIT_WAIT_SECONDS:-3600}"  # Wait on usage limit
MAX_LOGS="${MAX_LOGS:-200}"                       # Max cycle logs to keep

# === Model Settings ===
MODEL="${MODEL:-}"
MODEL_LABEL="${MODEL:-config-default}"

# === Engine Selection ===
ENGINE="${ENGINE:-qwen}"

# === Engine-specific Binary Overrides ===
CODEX_BIN="${CODEX_BIN:-}"
QWEN_BIN="${QWEN_BIN:-}"
OPENCODE_BIN="${OPENCODE_BIN:-}"

# === Codex-specific Settings ===
CODEX_SANDBOX_MODE="${CODEX_SANDBOX_MODE:-danger-full-access}"

# === Feature Flags ===
export CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS="${CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS:-1}"

# === Functions ===

# Validate engine name
validate_engine() {
    local eng="${1:-$ENGINE}"
    case "$eng" in
        codex|qwen|opencode)
            return 0
            ;;
        *)
            echo "Error: Unknown engine '$eng'. Valid options: codex, qwen, opencode" >&2
            return 1
            ;;
    esac
}

# Setup engine-specific paths (call after ENGINE is confirmed)
# Sets: PID_FILE, STATE_FILE globally
setup_engine_paths() {
    if ! validate_engine "$ENGINE"; then
        return 1
    fi

    PID_FILE="$PROJECT_DIR/.auto-loop-${ENGINE}.pid"
    STATE_FILE="$PROJECT_DIR/.auto-loop-${ENGINE}-state"

    # Export for subshells
    export PID_FILE STATE_FILE PROJECT_DIR LOG_DIR CONSENSUS_FILE PROMPT_FILE ENGINE
}

# Print configuration summary (useful for debugging)
print_config() {
    cat << EOF
Auto Company Configuration
=========================
Project: ${PROJECT_DIR}
Engine: ${ENGINE}
Model: ${MODEL_LABEL}

Paths:
  PID File: ${PID_FILE:-<not set>}
  State File: ${STATE_FILE:-<not set>}
  Log Dir: ${LOG_DIR}
  Consensus: ${CONSENSUS_FILE}

Loop Settings:
  Interval: ${LOOP_INTERVAL}s
  Timeout: ${CYCLE_TIMEOUT_SECONDS}s
  Max Errors: ${MAX_CONSECUTIVE_ERRORS}
  Cooldown: ${COOLDOWN_SECONDS}s
  Limit Wait: ${LIMIT_WAIT_SECONDS}s
  Max Logs: ${MAX_LOGS}
EOF
}