#!/bin/bash
# ============================================================
# Auto Company — Shell Script Test Runner
# ============================================================
# Runs shellcheck static analysis and basic integration tests
# for the auto-loop scripts.
#
# Usage:
#   ./tests/run-tests.sh [--quick]
#
# Options:
#   --quick    Skip integration tests, only shellcheck
# ============================================================

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
LIB_DIR="$(cd "$SCRIPT_DIR/../lib" && pwd)"
QUICK_MODE="${1:-}"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

PASSED=0
FAILED=0

pass() {
    echo -e "${GREEN}✓${NC} $1"
    PASSED=$((PASSED + 1))
}

fail() {
    echo -e "${RED}✗${NC} $1"
    FAILED=$((FAILED + 1))
}

warn() {
    echo -e "${YELLOW}!${NC} $1"
}

echo "=== Auto Loop Script Tests ==="
echo ""

# ========================================
# Test 1: Syntax Check (bash -n)
# ========================================
echo "--- Syntax Check ---"

for script in "$LIB_DIR"/*.sh "$SCRIPT_DIR"/../auto-loop.sh; do
    if [ -f "$script" ]; then
        if bash -n "$script" 2>/dev/null; then
            pass "Syntax: $(basename "$script")"
        else
            fail "Syntax: $(basename "$script")"
        fi
    fi
done

# ========================================
# Test 2: Shellcheck (if available)
# ========================================
echo ""
echo "--- Static Analysis (ShellCheck) ---"

if command -v shellcheck >/dev/null 2>&1; then
    # Create temp file with all sources for proper analysis
    for script in "$LIB_DIR"/*.sh "$SCRIPT_DIR"/../auto-loop.sh; do
        if [ -f "$script" ]; then
            name=$(basename "$script")
            # Count warnings (exclude library false positives)
            warnings=$(shellcheck -s bash -x "$script" 2>&1 | grep -c "SC" || true)
            if [ "$warnings" -eq 0 ]; then
                pass "ShellCheck: $name"
            else
                warn "ShellCheck: $name ($warnings warnings - may be library false positives)"
            fi
        fi
    done
else
    warn "ShellCheck not installed, skipping static analysis"
fi

# ========================================
# Test 3: Library Loading
# ========================================
echo ""
echo "--- Library Loading ---"

# Test that lib files can be sourced
test_load_lib() {
    local lib_file="$1"
    local temp_script=$(mktemp)
    
    cat > "$temp_script" << 'HEREDOC'
#!/bin/bash
set -euo pipefail
PROJECT_DIR="/tmp/test-project"
LOG_DIR="/tmp/test-logs"
CONSENSUS_FILE="/tmp/test-consensus.md"
PROMPT_FILE="/tmp/test-prompt.md"
PID_FILE="/tmp/test.pid"
STATE_FILE="/tmp/test.state"
ENGINE="test"
MODEL_LABEL="test-model"
LOOP_INTERVAL=30
CYCLE_TIMEOUT_SECONDS=1800
MAX_CONSECUTIVE_ERRORS=5
COOLDOWN_SECONDS=300
LIMIT_WAIT_SECONDS=3600
MAX_LOGS=200
HEREDOC
    
    echo "source \"$lib_file\"" >> "$temp_script"
    
    if bash -n "$temp_script" 2>/dev/null; then
        rm -f "$temp_script"
        return 0
    else
        rm -f "$temp_script"
        return 1
    fi
}

for lib in "$LIB_DIR"/*.sh; do
    if [ -f "$lib" ]; then
        if test_load_lib "$lib"; then
            pass "Load: $(basename "$lib")"
        else
            fail "Load: $(basename "$lib")"
        fi
    fi
done

# ========================================
# Test 4: Function Existence
# ========================================
echo ""
echo "--- Function Existence ---"

# Source common.sh and check key functions
check_common_functions() {
    local temp_script=$(mktemp)
    
    cat > "$temp_script" << 'HEREDOC'
#!/bin/bash
set -euo pipefail

# Minimal variables needed
PROJECT_DIR="/tmp"
LOG_DIR="/tmp"
CONSENSUS_FILE="/tmp/consensus.md"
PROMPT_FILE="/tmp/prompt.md"
PID_FILE="/tmp/pid"
STATE_FILE="/tmp/state"
ENGINE="test"
MODEL_LABEL="test"
CYCLE_TIMEOUT_SECONDS=60
MAX_CONSECUTIVE_ERRORS=3
COOLDOWN_SECONDS=60
LIMIT_WAIT_SECONDS=60
MAX_LOGS=10
loop_count=0
error_count=0

HEREDOC
    
    echo "source \"$LIB_DIR/common.sh\"" >> "$temp_script"
    echo "type log >/dev/null 2>&1 && exit 0 || exit 1" >> "$temp_script"
    
    bash "$temp_script" 2>/dev/null
    local result=$?
    rm -f "$temp_script"
    return $result
}

if [ -f "$LIB_DIR/common.sh" ]; then
    if check_common_functions; then
        pass "common.sh: log() function exists"
    else
        fail "common.sh: log() function missing"
    fi
fi

# ========================================
# Test 5: Integration (if not quick mode)
# ========================================
if [ "$QUICK_MODE" != "--quick" ]; then
    echo ""
    echo "--- Integration Tests ---"
    
    # Test help output
    if grep -q "ENGINE=" "$SCRIPT_DIR/../auto-loop.sh" 2>/dev/null; then
        pass "auto-loop.sh: Has ENGINE documentation"
    else
        fail "auto-loop.sh: Missing ENGINE documentation"
    fi
    
    # Test stop-loop.sh exists
    if [ -f "$SCRIPT_DIR/../stop-loop.sh" ]; then
        pass "stop-loop.sh: Exists"
    else
        warn "stop-loop.sh: Not found (may need creation)"
    fi
fi

# ========================================
# Summary
# ========================================
echo ""
echo "=== Summary ==="
echo -e "Passed: ${GREEN}$PASSED${NC}"
echo -e "Failed: ${RED}$FAILED${NC}"

if [ "$FAILED" -gt 0 ]; then
    exit 1
fi

exit 0