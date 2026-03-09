#!/bin/bash
# ============================================================
# Auto Company — Claude Engine Adapter
# ============================================================
# Provides Claude CLI-specific functions for the unified auto-loop.
# Source this file after lib/common.sh
#
# Usage:
#   ENGINE=claude ./auto-loop.sh
#
# Claude CLI Options:
#   CLAUDE_BIN          - Override Claude binary path
#   CLAUDE_MODEL        - Model to use (sonnet, opus, haiku)
#   CLAUDE_TOOLS        - Comma-separated allowed tools (or "all")
#   CLAUDE_PERMISSION_MODE - Permission mode (accept-edits, plan, etc.)
# ============================================================

ENGINE="claude"

# === Binary Resolution ===

resolve_claude_bin() {
    if [ -n "$CLAUDE_BIN" ]; then
        if [ -x "$CLAUDE_BIN" ]; then
            echo "$CLAUDE_BIN"
            return 0
        fi
        if command -v "$CLAUDE_BIN" >/dev/null 2>&1; then
            command -v "$CLAUDE_BIN"
            return 0
        fi
    fi

    # Check common installation locations
    local candidates=(
        "$HOME/.claude/bin/claude"
        "$HOME/.npm-global/bin/claude"
        "/usr/local/bin/claude"
        "/usr/bin/claude"
    )

    for candidate in "${candidates[@]}"; do
        if [ -x "$candidate" ]; then
            echo "$candidate"
            return 0
        fi
    done

    # Check nvm installations
    local nvm_candidate=""
    for candidate in "$HOME"/.nvm/versions/node/*/bin/claude; do
        if [ -x "$candidate" ]; then
            nvm_candidate="$candidate"
        fi
    done
    if [ -n "$nvm_candidate" ]; then
        echo "$nvm_candidate"
        return 0
    fi

    # Fallback: check PATH
    if command -v claude >/dev/null 2>&1; then
        command -v claude
        return 0
    fi

    return 1
}

# === Engine Initialization ===

engine_init() {
    if ! RESOLVED_ENGINE_BIN="$(resolve_claude_bin)"; then
        echo "Error: Claude CLI not found. Install Claude Code CLI first."
        echo "  npm install -g @anthropic-ai/claude-code"
        echo "  or visit: https://claude.ai/code"
        exit 1
    fi

    # Use CLAUDE_MODEL if set, otherwise let Claude CLI use its default
    if [ -n "$CLAUDE_MODEL" ]; then
        MODEL_LABEL="$CLAUDE_MODEL"
    else
        MODEL_LABEL="claude-default"
    fi
}

# === Cycle Execution ===

run_engine_cycle() {
    local prompt="$1"
    local output_file timeout_flag prompt_file

    output_file=$(mktemp)
    timeout_flag=$(mktemp)
    prompt_file=$(mktemp)

    # Write prompt to file (Claude CLI accepts file input better for long prompts)
    echo "$prompt" > "$prompt_file"

    set +e
    (
        cd "${PROJECT_DIR}" || exit 1

        # Build Claude CLI command
        # Use -p for print mode (non-interactive)
        # Use --dangerously-skip-permissions for autonomous operation
        local claude_cmd=(
            "$RESOLVED_ENGINE_BIN"
            "-p"
            "$prompt_file"
            "--dangerously-skip-permissions"
        )

        # Add model only if explicitly set
        if [ -n "$CLAUDE_MODEL" ]; then
            claude_cmd+=("--model" "$CLAUDE_MODEL")
        fi

        # Add allowed tools if specified and not "all"
        if [ -n "$CLAUDE_TOOLS" ] && [ "$CLAUDE_TOOLS" != "all" ]; then
            claude_cmd+=("--allowedTools" "$CLAUDE_TOOLS")
        fi

        # Run Claude CLI
        "${claude_cmd[@]}"
    ) > "$output_file" 2>&1 &
    local child_pid=$!

    # Watchdog process for timeout
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
    rm -f "$output_file" "$timeout_flag" "$prompt_file"
}

# === Metadata Extraction ===

extract_cycle_metadata() {
    CYCLE_SUBTYPE="unknown"
    CYCLE_TYPE="claude_exec"

    # Extract last portion of output as summary
    # Claude CLI outputs are typically more structured
    RESULT_TEXT=$(echo "$OUTPUT" | tail -100 | head -c 2000 || true)

    # Try to extract cost/tokens if available in output
    CYCLE_COST="N/A"
    if echo "$OUTPUT" | grep -qi "cost\|tokens\|usage"; then
        # Extract usage info if present
        local usage_info
        usage_info=$(echo "$OUTPUT" | grep -i "cost\|tokens\|usage" | tail -3 | tr '\n' ' ' | head -c 200)
        [ -n "$usage_info" ] && CYCLE_COST="$usage_info"
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
    log "Permission Mode: dangerously-skip-permissions (autonomous)"
    log "Allowed Tools: ${CLAUDE_TOOLS}"

    # Log available skills/agents
    if [ -d "${PROJECT_DIR}/.claude/skills" ]; then
        local skill_count
        skill_count=$(find "${PROJECT_DIR}/.claude/skills" -name "SKILL.md" 2>/dev/null | wc -l | tr -d ' ')
        [ "$skill_count" -gt 0 ] && log "Skills: $skill_count loaded"
    fi
    if [ -d "${PROJECT_DIR}/.claude/agents" ]; then
        local agent_count
        agent_count=$(find "${PROJECT_DIR}/.claude/agents" -name "*.md" 2>/dev/null | wc -l | tr -d ' ')
        [ "$agent_count" -gt 0 ] && log "Agents: $agent_count loaded"
    fi
}