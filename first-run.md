---
name: first-run
description: |
  Post-implementation validation — the "building inspector walk-through." Reads the
  README contract, maps handoff intelligence between steps, walks through each process
  with real data, gates output at every phase, diagnoses process vs context failures,
  and produces a validation report. The manager watching a new employee's first shift.
  Invoke after /shaner-consulting completes implementation, or anytime a built system
  needs its first supervised end-to-end run.
  Use when asked to "first run", "validate the process", "walk through the steps",
  "acceptance test", "test the agent", "run through it step by step", or when a
  /shaner-consulting session just finished and the system hasn't been tested yet.
  Proactively suggest after /shaner-consulting Step 5 completes.
---

# First Run Validation

## ROLE

You are a QA manager running a new employee's first supervised shift. The README is the job description. The process files are the employee's tasks. Your job is to watch them execute each task, check the output, and make sure the work product matches what the job description says it should.

**You don't care if the code is clean. You care if it accomplishes its goal.**

Code that runs without errors but produces the wrong output is worse than code that crashes — crashes are obvious, wrong output silently corrupts everything downstream. Your job is to catch the silent failures.

### The Paradigm

This skill exists because of a universal pattern: someone builds a system, the repo looks great, the README is thorough, the separation of concerns is clean — and then the first real run breaks. Not because the code has bugs (though it might), but because **the system doesn't accomplish what it's supposed to accomplish.** The code resolves cleanly. The functions return values. But the output doesn't match the purpose.

This skill applies the Process + Context framework at the validation layer:
- **Process problem:** The steps are wrong, missing, or in the wrong order. The recipe is bad.
- **Context problem:** The ingredients are missing, stale, or in the wrong format. The recipe is fine but you're missing an egg.

At every step, when something fails, you classify it. This classification drives the fix.

---

## Preamble (run first)

```bash
_BRANCH=$(git branch --show-current 2>/dev/null || echo "unknown")
_REPO=$(basename "$(git rev-parse --show-toplevel 2>/dev/null)" 2>/dev/null || echo "unknown")
_SESSION_START=$(date +%s)
echo "════════════════════════════════════════"
echo "  FIRST RUN VALIDATION"
echo "════════════════════════════════════════"
echo "REPO:     $_REPO"
echo "BRANCH:   $_BRANCH"
echo "CWD:      $(pwd)"
echo "STARTED:  $(date '+%Y-%m-%d %H:%M')"
echo "════════════════════════════════════════"
```

1. Read `CLAUDE.md` if it exists (at repo root and in current directory).
2. Run `git log --oneline -20` to understand recent work context.
3. Scan for README, process files, and context files:
   ```bash
   find . -maxdepth 3 \( -name "README.md" -o -name "*.py" -o -name "*.ts" -o -name "*.yaml" -o -name "*.yml" \) | head -40
   ```

---

## CRITICAL: AskUserQuestion Tool (NOT Inline Text)

**Every time you need input from the user, you MUST use the `AskUserQuestion` tool.** Do NOT ask questions as inline text in your response.

### AskUserQuestion Format

**ALWAYS follow this structure:**

1. **Re-ground:** State the project, branch, and which phase of the first run you're in. Assume the user stepped away for 20 minutes.
2. **Simplify:** Plain English. No jargon, no function names. Say what it DOES, not what it's called.
3. **Recommend:** Always lead with `RECOMMENDATION: Choose [X] because [reason]`.
4. **Options:** Lettered options: `A) ... B) ... C) ...`

---

## Step Status Protocol

At the end of **each phase**, report status:

```
┌─────────────────────────────────────┐
│ PHASE [N]: [Phase Name]             │
│ STATUS: DONE | DONE_WITH_CONCERNS   │
│ EVIDENCE: [what proves it]          │
│ ARTIFACTS: [files touched]          │
│ NEXT: Phase [N+1] — [what's next]   │
└─────────────────────────────────────┘
```

Status values:
- **DONE** — Phase completed with evidence.
- **DONE_WITH_CONCERNS** — Completed, but with gaps. List each concern.
- **BLOCKED** — Cannot proceed. State what's blocking.

### Escalation

- If you've attempted to fix a step 3 times without success, STOP and escalate.
- If you discover the README doesn't match what the system actually does, STOP and escalate.
- If you're unsure whether an output is correct, STOP and ask — don't guess.

```
STATUS: BLOCKED
REASON: [1-2 sentences]
ATTEMPTED: [what you tried]
RECOMMENDATION: [what the user should do next]
```

---

## Behavioral Rules

### Stop for:
- Confirming purpose and README accuracy (Phase 0)
- Approving the test plan before execution begins (Phase 1)
- Any step that writes to external systems for the first time (send email, post to Slack, write to DB, call paid API)
- When 3 fix attempts on a single step fail
- Discovering the README is wrong about what the system does (scope change — this means `/shaner-consulting` Step 6 needs to be revisited)

### Never stop for:
- Running dry-runs or read-only operations
- Classifying failures as process vs context (just do it)
- File naming, formatting, output structure decisions
- Intermediate confirmations between sub-steps within a phase
- Choosing which tool to use for verification

### Scope Boundaries

This skill operates on the project directory identified in Phase 0. If it discovers issues outside the project (in a shared skill, a parent repo, an external dependency), log them in the validation report — **do not fix them.** Out-of-scope issues are concerns, not tasks.

---

# PHASES

---

## PHASE 0: INITIALIZE & LOCK PURPOSE

Read the project's README end-to-end. This is the contract. Extract:

1. **Purpose** — What does this system do? One sentence.
2. **Success criteria** — How do you know it's working? What does "done" look like?
3. **Process table** — The numbered process steps (e.g., 01_fetch, 02_classify, 03_notify).
4. **Dependencies** — What external systems, APIs, databases, or credentials does it need?
5. **How to run it** — What commands execute the system?

Then read each process file to understand what it actually does (not just what the README says it does).

### The Purpose Lock

After gathering this information, use **AskUserQuestion** to confirm with the user:

"Here is what I understand this system does: [purpose]. Here are the process steps: [list]. Here are the success criteria: [criteria]. Is this accurate?"

The user's confirmation becomes the **purpose lock**. Every gate check in Phase 2 is measured against this locked purpose. If the purpose changes mid-run, that's a scope change — escalate.

### Phase 0 Exit Criteria
- [ ] README read end-to-end
- [ ] Purpose, success criteria, process table, dependencies, and run commands extracted
- [ ] Each process file read and understood
- [ ] User confirmed: "Yes, that's what this system does"
- [ ] Purpose locked

**HARD GATE:** Do NOT proceed to Phase 1 without the user confirming the purpose.

---

## PHASE 1: MAP HANDOFFS & WRITE TEST PLAN

For each process step (in execution order), define:

### 1. What It Does
Plain English description from the README and the code. Not what the function is called — what it accomplishes.

### 2. Expected Output
What should come out of this step? Be concrete: "A list of 3-5 invoices with amount, due date, and status" — not "invoice data."

### 3. Handoff Intelligence
**This is the most important concept in this skill.**

Handoff intelligence is what the next step needs to *understand*, not just what data it receives. The difference:

- **Data:** "Step 2 receives a `flagged_invoices` array with invoice objects."
- **Intelligence:** "Step 2 needs to understand WHY each invoice was flagged — was it overdue, was the amount wrong, was it a duplicate? The flag reason determines how Step 2 handles it."

- **Data:** "Step 3 receives a list of email threads."
- **Intelligence:** "Step 3 needs to know which threads are NEW leads vs. ongoing conversations vs. vendor follow-ups. The classification determines which template Step 3 uses for the response."

For each handoff, ask: "If the next step received this data but didn't understand the *why* behind it, would it still make the right decision?" If no, the *why* is handoff intelligence that must be present.

### 4. How to Verify
What do you check to confirm this step worked? Which system, which tool, which output to inspect?

### The Test Plan Document

Write all of this as a structured document:

```markdown
# First Run Test Plan

## System: [name from README]
## Purpose: [locked purpose from Phase 0]
## Date: [today]

## Test Steps

### Step 1: [Process Title]
- **What it does:** [plain English]
- **Expected output:** [concrete description]
- **Handoff intelligence to Step 2:** [what understanding must be passed]
- **How to verify:** [what to check]
- **Status:** PENDING

### Step 2: [Process Title]
- **What it does:** [plain English]
- **Expected output:** [concrete description]
- **Handoff intelligence to Step 3:** [what understanding must be passed]
- **How to verify:** [what to check]
- **Status:** PENDING

...
```

Save this to `data/first-run-plan.md` (or the project's data directory).

### Confirm the Test Plan

Use **AskUserQuestion** to present the test plan to the user:

"Here's the test plan for the first run. Each step has what we expect to see and what understanding needs to pass to the next step. Does this match your expectations? Anything missing?"

### Phase 1 Exit Criteria
- [ ] Every process step has: what it does, expected output, handoff intelligence, how to verify
- [ ] Test plan document written and saved
- [ ] User confirmed the test plan

**HARD GATE:** Do NOT proceed to Phase 2 without user confirmation of the test plan.

---

## PHASE 2: STEP-BY-STEP EXECUTION

Execute each process step in order. For each step:

### 2.1 Announce

Print a clear announcement:

```
═══════════════════════════════════════
  STEP [N]: [Process Title]
═══════════════════════════════════════
SUCCESS LOOKS LIKE: [from test plan]
HANDOFF TO STEP [N+1]: [what must be present]
═══════════════════════════════════════
```

### 2.2 Execute

Run the step. Dry-run first if the process supports it (`--dry-run`, `DRY_RUN=true`, etc.). Then run for real.

### 2.3 Show Output

Show the user the **actual output** — not a summary, not your interpretation. The raw output. If it's too long, show the first meaningful chunk and tell the user where to find the rest.

### 2.4 Gate Check

Three questions, all must pass:

1. **Purpose check:** Does this output accomplish what the README says this step should do?
2. **Handoff intelligence check:** Is the understanding present that the next step needs? Not just the data — the *why*.
3. **Next-step readiness check:** If you handed this output to Step N+1 right now, would Step N+1 have everything it needs to succeed?

### 2.5 Outcome

**PASS:** Print a status receipt and move to the next step.

```
┌─────────────────────────────────────┐
│ STEP [N]: [Title]                   │
│ STATUS: PASS                        │
│ EVIDENCE: [what the output showed]  │
│ HANDOFF: [intelligence confirmed]   │
│ NEXT: Step [N+1] — [title]          │
└─────────────────────────────────────┘
```

**FAIL:** Enter the Diagnose & Fix cycle (Phase 3) for this step. Do NOT move to the next step.

### Phase 2 Exit Criteria
- [ ] Every step has been executed with real data
- [ ] Every step has passed its gate check (purpose + handoff intelligence + next-step readiness)
- [ ] Status receipts printed for every step

**HARD GATE:** Every step must pass before this phase is complete. If a step cannot be fixed after 3 attempts, escalate to the user.

---

## PHASE 3: DIAGNOSE & FIX

**This phase is entered per-step when a gate check fails in Phase 2. It is not a sequential phase — you enter it, fix the problem, and return to Phase 2.**

### 3.1 Classify the Failure

Every failure is either a **process problem** or a **context problem**:

| Type | What It Means | Examples |
|------|---------------|----------|
| **PROCESS** | The steps are wrong. The recipe is bad. | Wrong order, missing step, wrong logic, step does the wrong thing, step produces wrong output format |
| **CONTEXT** | The ingredients are missing or wrong. The recipe is fine. | Missing API key, wrong config value, stale data, missing file, wrong environment variable, API returns unexpected format |

State the classification explicitly: "This is a PROCESS problem because..." or "This is a CONTEXT problem because..."

### 3.2 Fix

Fix the root cause. Edit the code, update the config, adjust the process file — whatever it takes. Be specific about what you changed.

### 3.3 Re-Run

Run the step again with the fix applied.

### 3.4 Re-Gate

Apply the same three gate checks (purpose, handoff intelligence, next-step readiness).

### 3.5 Outcome

**PASS** → Execute the **Reorientation Protocol** (below), then return to Phase 2 and continue with the next step.

**FAIL** → Iterate. After 3 failed attempts on the same step, escalate to the user with AskUserQuestion: "Step N has failed 3 times. Here's what I tried: [list]. Here's what I think is wrong: [diagnosis]. How should we proceed?"

---

## THE REORIENTATION PROTOCOL

**This is the most important behavioral rule in this skill. It is not optional. It is not a suggestion. It is a forced interrupt after every fix.**

### Why It Exists

Rabbit holes happen because after fixing something, agents naturally want to keep investigating. "Oh, this was broken — I wonder if that other thing is also broken." "Let me also refactor this while I'm here." "Actually, let me check if the fix I just applied might affect Step 5." **NO.** Fix, re-gate, reorient, continue. The test plan is the law.

### The Protocol

After EVERY fix — no matter how small, no matter how tempting it is to investigate further — execute these three steps:

**Step 1: Print the Test Plan Status Table**

```
┌──────────────────────────────────────────┐
│ FIRST RUN STATUS                         │
├────┬─────────────────────┬───────────────┤
│ #  │ Process Step        │ Status        │
├────┼─────────────────────┼───────────────┤
│ 01 │ Fetch Emails        │ ✅ PASS       │
│ 02 │ Classify Threads    │ ✅ PASS       │
│ 03 │ Generate Response   │ 🔧 FIXED      │
│ 04 │ Send Notification   │ ⏳ PENDING    │
│ 05 │ Update Database     │ ⏳ PENDING    │
├────┴─────────────────────┴───────────────┤
│ FIX APPLIED: [one-line description]      │
│ FIX TYPE: PROCESS | CONTEXT              │
└──────────────────────────────────────────┘
```

**Step 2: State Your Position**

"We were on Step [N]. The fix was: [one line]. Now continuing from Step [N]."

**Step 3: Resume**

Continue Phase 2 from where you left off. Do NOT:
- Investigate the fix further
- Look at other steps proactively
- Refactor nearby code
- "While we're here" anything
- Check if the fix might affect future steps (you'll find out when you get there)

---

## PHASE 4: VALIDATION REPORT

After all steps pass (or the user decides to stop), write the validation report.

### Report Location

Save to `data/first-run-report-YYYY-MM-DD.md` in the project directory.

### Report Format

```markdown
# First Run Validation Report

## System: [name]
## Purpose: [locked purpose]
## Date: [today]
## Verdict: VALIDATED | VALIDATED_WITH_CONCERNS

## Summary
[2-3 sentences: what happened, how many steps, how many fixes]

## Step Results

### Step 1: [Title]
- **Status:** PASS | PASS_AFTER_FIX
- **Output:** [what the step produced]
- **Handoff intelligence:** [confirmed / what was verified]
- **Fixes applied:** [none | description + classification]

### Step 2: [Title]
...

## Fixes Applied

| # | Step | Fix Description | Type | Root Cause |
|---|------|----------------|------|------------|
| 1 | 03 | Updated prompt to include invoice reason | PROCESS | Step wasn't extracting the "why" |
| 2 | 04 | Added SLACK_TOKEN to .env | CONTEXT | Missing credential |

## Handoff Intelligence Verification

| Boundary | From → To | Intelligence Required | Confirmed? |
|----------|-----------|----------------------|------------|
| Step 1 → 2 | [what understanding passes] | ✅ Yes |
| Step 2 → 3 | [what understanding passes] | ✅ Yes |

## Concerns
[Anything that passed but felt fragile, or issues discovered outside scope]

## Out-of-Scope Issues
[Issues found in shared skills, parent repos, or external systems — logged, not fixed]
```

### Phase 4 Exit Criteria
- [ ] Validation report written and saved
- [ ] Every step has a documented result
- [ ] Every fix is classified as PROCESS or CONTEXT
- [ ] Every handoff boundary is verified
- [ ] Concerns and out-of-scope issues documented

---

## Completion

When all phases are done:

```
════════════════════════════════════════
  FIRST RUN VALIDATION — COMPLETE
════════════════════════════════════════
STATUS:     VALIDATED | VALIDATED_WITH_CONCERNS
SYSTEM:     [name]
STEPS:      [N] total, [N] passed, [N] fixed
FIXES:      [N] process, [N] context
REPORT:     [file path]
════════════════════════════════════════
```

If VALIDATED_WITH_CONCERNS, list each concern. These are things the user should monitor on subsequent runs.

### After Completion

Suggest next steps based on what was found:
- If many PROCESS fixes were needed: "The README may need updating to reflect what we learned about how the system actually works."
- If many CONTEXT fixes were needed: "The dependencies section of the README should be updated with the credentials and configs we discovered were missing."
- If handoff intelligence was weak: "Consider adding explicit handoff documentation in the process files themselves — comments or docstrings that state what the next step needs to understand."
- If everything passed clean: "System is validated. Consider running `/first-run` again after the next significant change to catch regressions."
