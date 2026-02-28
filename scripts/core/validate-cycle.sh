#!/bin/bash
# ============================================================
# Auto Company — Cycle Validation Check
# ============================================================
# This script validates that each cycle meets the required quality gates.
# Run at the end of each cycle before updating consensus.
#
# Exit codes:
#   0 - All checks passed
#   1 - Validation failed (cycle should not end)
# ============================================================

set -euo pipefail

PROJECT_DIR="${PROJECT_DIR:-$(cd "$(dirname "$0")/../.." && pwd)}"
ACTIVITIES_FILE="$PROJECT_DIR/logs/activities.jsonl"
CONSENSUS_FILE="$PROJECT_DIR/memories/consensus.md"
CYCLE="${CYCLE:-1}"

echo "=== Cycle Validation Check ==="
echo "Cycle: $CYCLE"
echo ""

ERRORS=0

# Check 1: Does activities.jsonl exist?
if [ ! -f "$ACTIVITIES_FILE" ]; then
    echo "❌ FAIL: activities.jsonl not found"
    exit 1
fi

# Check 2: Is there a senior-qa review record for this cycle?
if ! grep "\"cycle\": $CYCLE" "$ACTIVITIES_FILE" 2>/dev/null | grep -q "\"action\": \"review\""; then
    echo "❌ FAIL: No senior-qa review record found for cycle $CYCLE"
    echo "   Action required: Call 'skill: \"senior-qa\"' and record to activities.jsonl"
    ERRORS=$((ERRORS + 1))
else
    echo "✅ PASS: senior-qa review record found"
fi

# Check 3: Does consensus have Validation Status section?
if [ -f "$CONSENSUS_FILE" ]; then
    if grep -q "## Validation Status" "$CONSENSUS_FILE"; then
        # Check if status is PASS
        if grep -A 3 "## Validation Status" "$CONSENSUS_FILE" | grep -q "status: ✅ PASS"; then
            echo "✅ PASS: Consensus has Validation Status: PASS"
        elif grep -A 3 "## Validation Status" "$CONSENSUS_FILE" | grep -q "status: ❌ FAIL"; then
            echo "❌ FAIL: Consensus has Validation Status: FAIL"
            echo "   Action required: Fix validation issues and retry"
            ERRORS=$((ERRORS + 1))
        else
            echo "⚠️  WARNING: Consensus has Validation Status but status unclear"
        fi
    else
        echo "⚠️  WARNING: Consensus missing Validation Status section"
        echo "   Action required: Add Validation Status to consensus"
    fi
fi

# Check 3: Check for new project directories with code but no test-checklist.md
for PROJECT in "$PROJECT_DIR"/projects/*/; do
    if [ -d "$PROJECT" ]; then
        PROJECT_NAME=$(basename "$PROJECT")
        
        # Skip archived projects
        if [[ "$PROJECT_NAME" == "archived" ]]; then
            continue
        fi
        
        # Check if there's code (HTML/JS or Python files)
        HAS_CODE=0
        if ls "$PROJECT"*.html 2>/dev/null | head -1 | grep -q .; then
            HAS_CODE=1
        fi
        if ls "$PROJECT"*.py 2>/dev/null | head -1 | grep -q .; then
            HAS_CODE=1
        fi
        if ls "$PROJECT"/app/*.py 2>/dev/null | head -1 | grep -q .; then
            HAS_CODE=1
        fi
        
        if [ "$HAS_CODE" -eq 1 ]; then
            # Check for test evidence
            HAS_TEST=0
            if [ -f "$PROJECT/test-checklist.md" ]; then
                HAS_TEST=1
            fi
            if ls "$PROJECT"/tests/*.py 2>/dev/null | head -1 | grep -q .; then
                HAS_TEST=1
            fi
            
            if [ "$HAS_TEST" -eq 0 ]; then
                echo "⚠️  WARNING: $PROJECT_NAME has code but no test evidence"
                echo "   Expected: $PROJECT/test-checklist.md or $PROJECT/tests/"
                ERRORS=$((ERRORS + 1))
            else
                echo "✅ PASS: $PROJECT_NAME has test evidence"
            fi
        fi
    fi
done

# Summary
echo ""
echo "=== Validation Summary ==="
if [ "$ERRORS" -gt 0 ]; then
    echo "❌ FAILED: $ERRORS error(s) found"
    echo ""
    echo "Cycle CANNOT end. Required actions:"
    echo "1. Call 'skill: \"senior-qa\"' to review code"
    echo "2. Create test-checklist.md for frontend projects"
    echo "3. Run tests for backend projects"
    echo "4. Record review action to activities.jsonl"
    echo "5. Update consensus Validation Status to PASS"
    
    # Auto-update consensus with FAIL status
    if [ -f "$CONSENSUS_FILE" ]; then
        # Remove existing Validation Status section if exists
        if grep -q "## Validation Status" "$CONSENSUS_FILE"; then
            # Use a portable approach to remove the section
            sed -i.bak '/## Validation Status/,/^## [A-Z]/{ /^## Validation Status/d; /^## [A-Z]/!d; }' "$CONSENSUS_FILE" 2>/dev/null || true
            rm -f "${CONSENSUS_FILE}.bak"
        fi
        
        # Add FAIL status after Agent Activities This Cycle section
        if grep -q "## Agent Activities This Cycle" "$CONSENSUS_FILE"; then
            # Insert after the activities table (find the next ## header)
            sed -i.bak '/^|.*|.*|$/a\
\
## Validation Status\
- senior-qa: ❌ NOT CALLED\
- test-evidence: ❌ MISSING\
- status: ❌ FAIL\
\
**⚠️ 此周期验证失败，下个周期必须重试当前任务。**\
' "$CONSENSUS_FILE" 2>/dev/null || true
            rm -f "${CONSENSUS_FILE}.bak"
        fi
    fi
    
    exit 1
else
    echo "✅ PASSED: All validation checks passed"
    
    # Auto-update consensus with PASS status
    if [ -f "$CONSENSUS_FILE" ]; then
        # Remove existing Validation Status section if exists
        if grep -q "## Validation Status" "$CONSENSUS_FILE"; then
            sed -i.bak '/## Validation Status/,/^## [A-Z]/{ /^## Validation Status/d; /^## [A-Z]/!d; }' "$CONSENSUS_FILE" 2>/dev/null || true
            rm -f "${CONSENSUS_FILE}.bak"
        fi
        
        # Add PASS status after Agent Activities This Cycle section
        if grep -q "## Agent Activities This Cycle" "$CONSENSUS_FILE"; then
            sed -i.bak '/^|.*|.*|$/a\
\
## Validation Status\
- senior-qa: ✅ CALLED\
- test-evidence: ✅ CREATED\
- status: ✅ PASS\
' "$CONSENSUS_FILE" 2>/dev/null || true
            rm -f "${CONSENSUS_FILE}.bak"
        fi
    fi
    
    exit 0
fi