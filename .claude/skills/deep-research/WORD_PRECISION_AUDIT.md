# Word Precision Audit: Deep Research Skill

**Date:** 2025-11-04
**Purpose:** Systematic review of every word in SKILL.md for precision, intention, and clarity

---

## Audit Methodology

**Criteria for precision:**
1. **No hedge words** ("reasonably", "generally", "basically", "essentially")
2. **No weak verbs** ("can", "may", "might", "should" → use "must", "will", "do")
3. **No vague adjectives** ("good", "nice", "reasonable" → use specific criteria)
4. **No passive voice** where active is stronger
5. **No colloquialisms** in formal directives
6. **No double negatives** ("no need to" → "proceed without")
7. **No redundancy** (say once, clearly)
8. **No ambiguous pronouns** without clear referents

---

## Issues Found (14 total)

### HIGH PRIORITY (8 issues)

#### Issue #1: "reasonable assumptions" (Lines 54, 58)
**Current:**
```markdown
Proceed with reasonable assumptions.
Make reasonable assumptions based on query context.
```

**Problem:** "reasonable" is subjective, vague, creates uncertainty about what's acceptable

**Fix:**
```markdown
Infer assumptions from query context.
Derive assumptions from query signals.
```

**Intention carried:** "reasonable" → permission-seeking, cautious | "infer/derive" → direct action, confident

---

#### Issue #2: "genuinely incomprehensible" (Line 61)
**Current:**
```markdown
Query is genuinely incomprehensible
```

**Problem:** "genuinely" is hedge word, weakens the criterion

**Fix:**
```markdown
Query is incomprehensible
```

**Intention carried:** "genuinely" → doubting, qualifying | removed → clear, definitive

---

#### Issue #3: "User can redirect if needed" (Line 64)
**Current:**
```markdown
PROCEED with standard mode. User can redirect if needed.
```

**Problem:** "can" is weak permission, "if needed" is uncertain, both undermine autonomy

**Fix:**
```markdown
PROCEED with standard mode. User will redirect if incorrect.
```

**Intention carried:** "can...if needed" → uncertain, permission-seeking | "will...if incorrect" → confident, definitive

---

#### Issue #4: "NO need to wait" - double negative (Line 85)
**Current:**
```markdown
NO need to wait for approval - proceed directly to execution
```

**Problem:** Double negative ("NO need") is weaker than direct command, "proceed directly to execution" is wordy

**Fix:**
```markdown
Proceed without waiting for approval
```

**Intention carried:** "NO need to" → permissive, passive | "Proceed without" → imperative, active

---

#### Issue #5: Contraction "Don't" (Line 113)
**Current:**
```markdown
Don't inline everything - use references
```

**Problem:** Contraction in formal directive, less authoritative

**Fix:**
```markdown
Do not inline everything - reference external files
```

**Intention carried:** "Don't" → casual | "Do not" → formal, authoritative

---

#### Issue #6: "ask to proceed" - weak request (Line 229)
**Current:**
```markdown
<5 sources after exhaustive search → Report limitation, ask to proceed
```

**Problem:** "ask to proceed" is weak, implies uncertainty about whether to continue

**Fix:**
```markdown
<5 sources after exhaustive search → Report limitation, request direction
```

**Intention carried:** "ask to proceed" → tentative | "request direction" → professional, clear need

---

#### Issue #7: "When uncertain" contradicts autonomy (Line 262)
**Current:**
```markdown
**When uncertain:** Be thorough, not fast. Quality > speed.
```

**Problem:** "When uncertain" directly contradicts autonomy principle (line 54 says operate independently), creates confusion about when to be uncertain

**Fix:**
```markdown
**Priority:** Thoroughness over speed. Quality > speed.
```

**Intention carried:** "When uncertain" → hesitation, doubt | "Priority" → clear directive, no uncertainty

---

#### Issue #8: "acceptable" is passive (Line 280)
**Current:**
```markdown
Extended reasoning acceptable (5-45 min)
```

**Problem:** "acceptable" is passive, permission-seeking, weak

**Fix:**
```markdown
Time investment: 5-45 minutes
```

**Intention carried:** "acceptable" → asking permission | "investment" → stating fact

---

### MEDIUM PRIORITY (6 issues)

#### Issue #9: "Good autonomous assumptions" - vague judgment (Line 66)
**Current:**
```markdown
**Good autonomous assumptions:**
```

**Problem:** "Good" is vague value judgment without criteria

**Fix:**
```markdown
**Default assumptions:**
```

**Intention carried:** "Good" → subjective approval-seeking | "Default" → objective, standard procedure

---

#### Issue #10: "Standard+" unclear notation (Lines 96, 101)
**Current:**
```markdown
**Standard+ adds:**
**Deep+ adds:**
```

**Problem:** "+" notation is programming jargon, unclear if it means "and above" or "additional to"

**Fix:**
```markdown
**Standard/Deep/UltraDeep execute:**
**Deep/UltraDeep execute:**
```

**Intention carried:** "+" → ambiguous scope | explicit listing → clear scope

---

#### Issue #11: "(optional)" weakens directive (Line 174)
**Current:**
```markdown
4. Next steps (optional)
```

**Problem:** "(optional)" signals uncertainty, weakens the delivery item

**Fix:**
```markdown
4. Next steps (if relevant)
```
OR remove entirely since it's in "Deliver to user" section

**Intention carried:** "(optional)" → uncertain, dismissible | "(if relevant)" → conditional, purposeful | removed → expected

---

#### Issue #12: "Offer:" implies asking permission (Lines 176-179)
**Current:**
```markdown
**Offer:**
- Deep-dive any section
- Follow-up questions
- Alternative formats
```

**Problem:** "Offer" implies asking permission, waiting for response, breaks autonomous flow

**Fix:**
```markdown
**Available on request:**
- Section deep-dives
- Follow-up analysis
- Alternative formats
```
OR remove entirely (user will ask if interested)

**Intention carried:** "Offer" → salesperson, permission-seeking | "Available on request" → service menu, user-initiated | removed → autonomous

---

#### Issue #13: "hit" colloquial (Line 234)
**Current:**
```markdown
Time constraint hit → Package partial results, document gaps
```

**Problem:** "hit" is colloquial, imprecise for technical directive

**Fix:**
```markdown
Time constraint reached → Package partial results, document gaps
```

**Intention carried:** "hit" → casual, imprecise | "reached" → formal, precise

---

#### Issue #14: "explicitly needed" redundant (Line 324)
**Current:**
```markdown
Load these files only when explicitly needed for current phase.
```

**Problem:** "explicitly needed" is redundant - either needed or not, "explicitly" adds no precision

**Fix:**
```markdown
Load files on-demand for current phase only.
```

**Intention carried:** "explicitly needed" → overthinking, redundant | "on-demand" → clear technical term

---

## Impact Analysis

### Before Fixes (Current State)

**Hedge words count:** 4 ("reasonable" ×2, "genuinely", "acceptable")
**Weak modal verbs:** 2 ("can redirect", "may")
**Passive constructions:** 3 ("can", "acceptable", "optional")
**Vague adjectives:** 2 ("good", "reasonable")
**Colloquialisms:** 1 ("hit")
**Redundancies:** 2 ("explicitly needed", "NO need to")

**Total weakness indicators:** 14

### After Fixes (Proposed State)

**Hedge words count:** 0
**Weak modal verbs:** 0
**Passive constructions:** 0
**Vague adjectives:** 0
**Colloquialisms:** 0
**Redundancies:** 0

**Total weakness indicators:** 0

---

## Word Intention Analysis

### Critical Word Replacements

| Current Word | Unintended Intention | Replacement | Intended Intention |
|--------------|---------------------|-------------|-------------------|
| reasonable | subjective, cautious | infer/derive | objective, confident |
| genuinely | doubting, qualifying | [remove] | certain, definitive |
| can | permission-seeking | will | confident expectation |
| if needed | uncertain | if incorrect | conditional, clear |
| NO need to | passive, permissive | Proceed without | active, imperative |
| Don't | casual, conversational | Do not | formal, authoritative |
| ask to | tentative, weak | request | professional, clear |
| When uncertain | hesitant, contradictory | Priority | directive, unambiguous |
| acceptable | permission-seeking | investment | factual, confident |
