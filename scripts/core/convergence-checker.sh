#!/bin/bash
# Convergence Checker - Validates each cycle produces tangible output
# Run at end of each cycle to enforce "Ship > Plan > Discuss" rule

set -e

CYCLE_LOG="$1"
CONSENSUS_FILE="memories/consensus.md"

echo "=== Convergence Checker ==="
echo "Checking cycle output..."

# Check 1: Was a file created or modified?
FILES_CREATED=$(git diff --name-only HEAD~1 2>/dev/null | wc -l || echo "0")
if [ "$FILES_CREATED" -gt 0 ]; then
    echo "✅ Files created/modified: $FILES_CREATED"
else
    echo "⚠️  No files created/modified this cycle"
fi

# Check 2: Is there a user-visible artifact?
USER_VISIBLE=$(find docs projects -name "*.md" -o -name "*.py" -o -name "*.js" 2>/dev/null | \
    xargs git diff --name-only HEAD~1 2>/dev/null | wc -l || echo "0")
if [ "$USER_VISIBLE" -gt 0 ]; then
    echo "✅ User-visible artifacts: $USER_VISIBLE"
else
    echo "⚠️  No user-visible artifacts created"
fi

# Check 3: Did Next Action change?
if [ -f "$CONSENSUS_FILE" ]; then
    CURRENT_NEXT=$(grep -A1 "## Next Action" "$CONSENSUS_FILE" | tail -1 | head -c 100)
    echo "📋 Current Next Action: $CURRENT_NEXT..."
fi

# Check 4: Was activities.jsonl updated?
ACTIVITIES_COUNT=$(wc -l < logs/activities.jsonl 2>/dev/null || echo "0")
echo "📊 Activities logged: $ACTIVITIES_COUNT"

# Summary
echo ""
echo "=== Cycle Validation ==="
if [ "$FILES_CREATED" -gt 0 ] && [ "$ACTIVITIES_COUNT" -gt 0 ]; then
    echo "✅ CYCLE VALID: Tangible output produced"
    exit 0
else
    echo "❌ CYCLE INVALID: No tangible output - violates 'Ship > Plan > Discuss'"
    exit 1
fi