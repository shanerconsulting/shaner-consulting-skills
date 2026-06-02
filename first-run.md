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

### CRITICAL: Memory Is NOT a Fix Destination

Every bug, design gap, or behavioral miss found during first-run validation MUST be fixed in a reviewable, durable location: code, a skill file (`SKILL.md`), a process file, a config, a prompt template, or the README. **Never use auto-memory (`~/.claude/projects/.../memory/`) as a substitute for fixing the underlying system.**

Memory is for cross-session user preferences ("David prefers casual tone with a client"). It is NOT for system bugs ("the inbox skill didn't fetch Drive links inline" or "email content got hidden in collapsed bash output"). Memory entries aren't reviewed when skills are improved, don't propagate to other agents or fresh sessions, and can silently vanish — so a bug "fixed" in memory recurs.

Global CLAUDE.md guidance that says "save corrections to memory" DOES NOT apply during first-run. Inside this skill, the rule is: **if the system did the wrong thing, fix the system's files.** See Phase 3.2 for the full destination taxonomy and test.

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

### Also Read `improvement/assertions.md` (if present)

If `improvement/assertions.md` exists, **it is the contract at the behavior level** — more specific than the README. Read it end-to-end. Each sentence is a behavior the system must maintain. Every gate check in Phase 2 will cite the specific sentence being tested.

If `improvement/assertions.md` does NOT exist, that is expected for pre-update systems. Phase 1 will produce it. Note this in the status line: `ASSERTIONS: missing — will populate in Phase 1`.

The full schema and voice rules for `improvement/assertions.md` are defined in the sibling file `improvement-bucket.md` at the root of the `/shaner-consulting` skill directory. Read it if you're unfamiliar.

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

### 1.0 Populate or Refresh `improvement/assertions.md` (if needed)

**If `improvement/assertions.md` was missing in Phase 0**, write it now before anything else. For each process, produce 2–5 plain-language sentences describing what the process must do to be correct.

Voice rules from `improvement-bucket.md` — summarized:
- Write like an SOP for a new employee. No function names, API verbs, state transitions, Latin abbreviations, or arrow-syntax.
- One sentence = one behavior. If you wrote "and" between two independent behaviors, split it.
- Describe **what** the system does, not **how**.

Example good sentence: *"Once the system is working again, the incident is closed and the user gets a DM at the next check letting them know."*

Example bad sentence (same meaning, jargon-loaded, REJECT): *"On healthy transition, incident closes and recovery DM fires within one self-test cycle."*

Save the file. Use **AskUserQuestion** to confirm with the user: "Here's the behavior contract I drafted for this system. Does each sentence describe something you'd actually want the system to do? Anything missing, wrong, or jargon-y?"

**If `improvement/assertions.md` was present in Phase 0**, re-read it and flag anything that looks stale, jargon-loaded, or inconsistent with the README. Propose edits; don't silently modify.

### 1.1 Per-Step Test Plan

For each process step (in execution order), define:

### 1. What It Does
Plain English description from the README and the code. Not what the function is called — what it accomplishes.

### 2. Expected Output
What should come out of this step? Be concrete: "A list of 3-5 invoices with amount, due date, and status" — not "invoice data."

### 2.5 Which Assertions Apply
List the specific sentences from `improvement/assertions.md` that this step is responsible for satisfying. Every assertion must map to at least one step; every step that has assertions must cite them.

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
- **Expected input shape:** [what data/records come in, expected fields, expected counts]
- **Expected output shape:** [what data/records come out, expected fields, expected counts]
- **Sources consulted:** [what systems, files, APIs this step reads from]
- **Expected handoff intelligence to Step 2:** [what understanding must be passed]
- **How to verify:** [what to check]
- **Status:** PENDING

### Step 2: [Process Title]
- **What it does:** [plain English]
- **Expected input shape:** [what data/records come in — should match Step 1 output shape]
- **Expected output shape:** [what data/records come out, expected fields, expected counts]
- **Sources consulted:** [what systems, files, APIs this step reads from]
- **Expected handoff intelligence to Step 3:** [what understanding must be passed]
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

### 2.3 Snapshot Data Shape

**This is the n8n node inspector for first-run.** After executing the step, capture what went in and what came out — not the full raw data, but the **shape**: field names, record counts, a representative sample record, nulls, gaps, and anything skipped.

**Why this exists:** A step can execute without errors and still silently degrade everything downstream because its input was incomplete or its output had gaps. A phone number that's null, a source that was skipped, a record count of zero where you expected twelve — these don't crash. They propagate. The data shape snapshot catches them at the boundary instead of three steps later.

For each step, capture:

```
═══ STEP [N]: [Title] — DATA SHAPE ═══

INPUT:
  [collection_name]: [N] records
  sample: { [field]: [value], [field]: [value], ... }
  [any relevant config, flags, or sources that were consulted]

OUTPUT:
  [collection_name]: [N] records
  sample: { [field]: [value], [field]: [value], ... }
  [derived counts, categories, or groupings]

SKIPPED / UNAVAILABLE:
  [source/path]: [why it was skipped]

GAPS:
  [field]: [N] records with null/missing values → [downstream consequence]
═══════════════════════════════════════
```

**Rules for the snapshot:**

1. **Sample records must be real.** Use an actual record from the run, not a template. Pick a representative one, not the cleanest one — if most records have gaps, show a record with gaps.
2. **If a step iterates over records** (contacts, prospects, invoices), show the count AND a sample of both a complete record and an incomplete record (if any exist). The contrast makes gaps obvious.
3. **SKIPPED is mandatory.** If the step consulted 5 sources and 1 was unavailable, that's a SKIPPED entry even if the step "succeeded." Skipped sources are invisible blind spots.
4. **GAPS is mandatory.** Count nulls per field. "phone: 10 of 22 records null → iMessage not searchable for these contacts" is the kind of gap that catches the missing-surname problem.
5. **Save to the trace file** (see Phase 4). The snapshot is appended to the trace file after each step so the full trace is available for review after the run.

**Present the snapshot to the user in chat** using AskUserQuestion:

"Here's the data shape for Step [N]. [Highlight any SKIPPED or GAPS entries.] Does this look right? Anything surprising?"

**HARD GATE:** The user must confirm the data shape before proceeding to the gate check. If they spot a gap ("why is phone null for this contact?"), that's a FAIL — enter the Diagnose & Fix cycle.

### 2.4 Show Output

Show the user the **actual output** — not a summary, not your interpretation. The raw output. If it's too long, show the first meaningful chunk and tell the user where to find the rest.

### 2.5 Gate Check

Five questions, all must pass:

1. **Purpose check:** Does this output accomplish what the README says this step should do?
2. **Data shape check:** Are there unexpected nulls, zero counts, skipped sources, or missing fields that would silently degrade downstream steps? Cross-reference the GAPS and SKIPPED entries from the data shape snapshot — if any gap would cause a downstream step to produce incomplete results without erroring, this check FAILS.
3. **Assertion check:** For every assertion sentence cited in Phase 1 step 2.5 (which sentences apply to this step), does the actual output satisfy the sentence? Quote the specific sentence. If the sentence describes something the log claims but reality contradicts (or vice versa), this check FAILS — that's the silent failure we're here to catch.
4. **Handoff intelligence check:** Is the understanding present that the next step needs? Not just the data — the *why*.
5. **Next-step readiness check:** If you handed this output to Step N+1 right now, would Step N+1 have everything it needs to succeed?

### 2.6 Outcome

**PASS:** Print a status receipt and continue to 2.7.

```
┌─────────────────────────────────────┐
│ STEP [N]: [Title]                   │
│ STATUS: PASS                        │
│ EVIDENCE: [what the output showed]  │
│ DATA SHAPE: [confirmed by user]     │
│ ASSERTIONS: [which ones this step   │
│   satisfied, by quoted sentence]    │
│ HANDOFF: [intelligence confirmed]   │
│ NEXT: Step [N+1] — [title]          │
└─────────────────────────────────────┘
```

**FAIL:** Enter the Diagnose & Fix cycle (Phase 3) for this step. Do NOT move to the next step.

### 2.7 Seed Adversarial Fixtures (PASS only)

Behavior is freshest in mind right now. Before moving to Step N+1, seed adversarial fixtures for the assertions this step satisfied.

For each assertion sentence cited above, ask: **"How could this sentence be true in the log but false in reality?"** That's a fixture.

Generate 2–3 fixtures per assertion. Save each to `improvement/adversarial/fixtures/` using the naming convention `[process_num]_[short_name].json` (or `.yaml`). Format per `improvement-bucket.md`:

```json
{
  "fixture_name": "03_slack_returns_ok_false",
  "assertion_ref": "Process 03: 'An alert only counts as sent once Slack confirms...'",
  "input": { ... minimal input to drive the process ... },
  "mock_responses": { ... if the process calls externals ... },
  "expected_behavior": "Plain-language sentence.",
  "expected_behavior_negation": "Plain-language sentence describing the silent failure."
}
```

**Do NOT execute the fixtures now.** The goal of first-run is to validate the happy path with real data. Fixture execution belongs to a later QA cycle or automated runner. Your job here is just to capture them while the step is fresh.

**HARD GATE:** Every assertion cited in this step's gate check MUST have at least one fixture written before you move to Step N+1.

### Phase 2 Exit Criteria
- [ ] Every step has been executed with real data
- [ ] Every step has a data shape snapshot saved to the trace file and confirmed by user
- [ ] Every step has passed its gate check (purpose + data shape + handoff intelligence + next-step readiness)
- [ ] Status receipts printed for every step

**HARD GATE:** Every step must pass before this phase is complete. If a step cannot be fixed after 3 attempts, escalate to the user.

---

## PHASE 2.5: DETERMINISM AUDIT

After all Phase 2 steps pass, step back and audit *how* the system ran, not just whether it produced the right output.

### The Principle

**Deterministic work must live on disk.** If the model re-derived the same logic at runtime — wrote it fresh, ran it, threw it away — the skill has a hole. The output was right this time, but the cost was burned context, forgotten flags, and inconsistency between runs. Next week the model will rewrite the same script slightly differently, hit a different edge case, and maybe get it wrong.

The test: does the answer depend on the *bounds* of the input (dates, IDs, counts) or on its *content* (free text, novel shapes, judgment calls)?
- Bounds-only → belongs in a committed script
- Content-sensitive → belongs in the LLM

### How to Audit

Open the session JSONL for the just-completed run (under `~/.claude/projects/[encoded-path]/*.jsonl`) and read the tool-call stream with the principle in mind. Look for places where the LLM did deterministic work at runtime that could have lived on disk.

Some manifestations to watch for — these are illustrative, not exhaustive:

- Scripts written to `/tmp/` (or any ephemeral path) during execution. Especially if versioned (`foo.py`, `foo_v2.py`, `foo_v3.py`) — that's the LLM iterating a solution from scratch instead of improving a committed one.
- The same MCP tool called twice in one step with different arguments — usually means "forgot a flag the first time, retried." The right flag should be hardcoded.
- Multiple `ToolSearch` calls spread across the run that could have been batched at Step 0 — the skill knows which schemas it needs upfront.
- Runtime-written scripts that embed large string literals copied from prior tool outputs (hardcoded event data, inlined JSON, pasted record lists) — glue that doesn't compose.
- Logic described in prose in a `.md` context file that the LLM re-implements in Python on every run — the prose is a spec, but the spec is never executed, so the implementation drifts.

Beyond these, use judgment. The principle is the test, not the list. If something in the trace feels like it was *re-derived* rather than *recalled*, flag it. If a future run with the same window would require the LLM to figure out the same thing again, flag it.

### For Each Defect Found

Write a one-block finding:

```
DEFECT: [short name]
EVIDENCE: [JSONL line numbers or tool call IDs — enough for a reader to re-verify]
DETERMINISM ARGUMENT: [why this is bounds-only, not content-sensitive]
FIX: [the specific extraction — name the script, where it goes, what it takes as args, what it returns]
```

### Why This Matters for Validation

A run can pass every gate in Phase 2 and still leave the skill with tech debt that guarantees the same bugs recur. Phase 2.5 catches that. If the run passes but has determinism defects, the validation verdict is `VALIDATED_WITH_CONCERNS` — the system works, but has a tech-debt list that must be addressed before it can be claimed as clean.

### Phase 2.5 Exit Criteria
- [ ] Session JSONL read with the deterministic-work-on-disk principle in mind
- [ ] Every defect has a finding block with evidence, argument, and specific fix
- [ ] Findings saved to `data/determinism-audit-YYYY-MM-DD.md` (or appended to the trace file)
- [ ] If zero defects, the audit file says so explicitly (don't skip writing it)

**HARD GATE:** Do NOT proceed to Phase 4 until the audit is written. If defects were found, note them in the Phase 4 report and let the user decide whether to extract them now or track them as follow-ups.

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

Fix the root cause. Be specific about what you changed — name the file and line range.

#### Valid fix destinations
- **Code files** (`.py`, `.ts`, `.js`, etc.) — logic bugs, wrong defaults, broken loops, bad error handling
- **Skill files** (`SKILL.md`, `*.md` skill definitions) — missing behaviors, wrong workflow, unhandled edge cases, rendering/UX rules in an agent-driven process
- **Process files** (`processes/*.md`, numbered process docs) — wrong steps, missing steps, wrong order
- **Config/env files** (`.env`, `config.yaml`, registry files) — missing credentials, wrong endpoints, wrong routing
- **README / contract docs** — when the system's behavior contract itself is wrong
- **Prompt templates** — when an LLM call has the wrong instructions or missing context

#### INVALID fix destination: auto-memory

**Do not write the bug into `~/.claude/projects/.../memory/` as a `feedback` or `project` entry instead of fixing the file.** Memory is user-preference glue across sessions. It is not a bug tracker, not a skill patch, and not reviewed when skills are improved — so anything "saved" there will recur.

#### The memory-vs-file test

Ask: **"Did the SYSTEM do the wrong thing, or did the USER express a preference?"**
- SYSTEM did the wrong thing → fix the system's files. Every time. No exceptions inside first-run.
- USER expressed a cross-session preference ("call me Hey man with a client") → memory is appropriate.

If you can restate the issue as "next time the system runs, it should do X instead of Y", the fix belongs in the files that drive that run.

#### Concrete examples of the trap

These are real misfires — each one should have been a file edit, not a memory write:

| Observation during first-run | Wrong (memory) | Right (file) |
|------------------------------|---------------|--------------|
| "/inbox didn't dereference Drive links in emails" | Save feedback: "/inbox must fetch linked Drive files inline" | Edit the inbox-triage `SKILL.md` to add a fetch-and-render step for Drive URLs |
| "Email content got hidden in collapsed bash output" | Save feedback: "render email content in response as plain text" | Edit the skill's output rules to require inline markdown rendering |
| "draft-and-archive picked wrong To-address" | — | Edit `gmail_ops.py` counterparty selection logic (done correctly) |
| "Link-shared Sheets not visible via Drive API" | — | Add Sheets-API fallback in the fetcher (done correctly) |

If you catch yourself drafting a memory entry mid-fix, STOP. Re-classify as a file fix and locate the right destination from the table above.

#### Self-check before leaving 3.2
- [ ] I edited at least one code/skill/process/config/README file.
- [ ] I did NOT write a `feedback_*.md` or `project_*.md` in the memory directory for this fix.
- [ ] If I genuinely believe this is a user-preference item and memory is warranted, I will flag it to the user with AskUserQuestion before writing it, and still fix any system behavior in the files.

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

The report is an **observable trace** — not just a scorecard. Anyone reading it after the fact should be able to reconstruct what data flowed through each step, what was skipped, and where gaps existed. Think of it as the n8n execution log: you can click any node and see inputs/outputs.

```markdown
# First Run Validation Report

## System: [name]
## Purpose: [locked purpose]
## Date: [today]
## Verdict: VALIDATED | VALIDATED_WITH_CONCERNS

## Summary
[2-3 sentences: what happened, how many steps, how many fixes]

## Step Trace

### Step 1: [Title]
- **Status:** PASS | PASS_AFTER_FIX

#### Data Shape
**Input:**
  [collection_name]: [N] records
  sample: { [field]: [value], ... }
  sources consulted: [list]

**Output:**
  [collection_name]: [N] records
  sample: { [field]: [value], ... }

**Skipped:** [source/path — why] (or "none")
**Gaps:** [field — N records null — downstream consequence] (or "none")

#### Verification
- **Purpose check:** [what the output accomplished]
- **Data shape check:** [gaps/skips reviewed — confirmed or flagged]
- **Handoff intelligence:** [what understanding was confirmed for next step]
- **Fixes applied:** [none | description + classification]

### Step 2: [Title]
...

## Fixes Applied

Every row must name the file path that was edited. If the "File(s) edited" column is empty or names a path under `memory/`, the fix is incomplete — go back and fix the system's files.

| # | Step | Fix Description | Type | Root Cause | File(s) edited |
|---|------|----------------|------|------------|----------------|
| 1 | 03 | Updated prompt to include invoice reason | PROCESS | Step wasn't extracting the "why" | `processes/03_classify.md`, `prompts/classify.txt` |
| 2 | 04 | Added SLACK_TOKEN to .env | CONTEXT | Missing credential | `.env.example`, `README.md` |

## Determinism Defects

From the Phase 2.5 audit. Every defect is a promise that the same bug will recur next run unless extracted.

| # | Defect | Evidence | Fix |
|---|--------|----------|-----|
| 1 | [short name] | [JSONL lines / tool-call IDs] | [script path + args + return shape] |

If zero defects, write `None — the run used only committed on-disk logic.`

## Memory Audit

Confirm no bug or design gap from this run was "fixed" by writing to auto-memory instead of the system's files:

- [ ] I did NOT create any new `feedback_*.md` or `project_*.md` in `~/.claude/projects/.../memory/` for issues discovered during this run.
- [ ] If any memory write happened, it is user-preference glue (tone, naming, cross-session habit) — NOT a system bug — and the underlying system behavior is separately fixed in a file above.
- [ ] Every issue surfaced to the user in the completion message can be traced to a file path in the "Fixes Applied" table.

## Data Flow Summary

A condensed view of what flowed through the full pipeline:

| Step | Records In | Records Out | Skipped Sources | Gaps |
|------|-----------|-------------|-----------------|------|
| 1 | [N] [type] | [N] [type] | [list or none] | [field: N null] |
| 2 | [N] [type] | [N] [type] | [list or none] | [field: N null] |
| ... | | | | |

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

### Phase 4.5: Append to runs.jsonl

First-run is itself a real run. Append a scored entry to `improvement/runs.jsonl` using the schema in `improvement-bucket.md`:

```json
{
  "run_id": "[ISO 8601 timestamp]",
  "ts": "[ISO 8601 timestamp]",
  "input_ref": "first-run validation",
  "scores": [
    {"assertion": "[quoted sentence]", "score": "pass|partial|fail|not_applicable|needs_human", "rationale": "[one sentence]"}
  ],
  "overall": "pass|partial|fail|needs_human",
  "follow_up": "[any fixtures opened, any assertions edited, any README changes needed]"
}
```

Score every assertion in `improvement/assertions.md`, even ones not exercised by this run (mark those `not_applicable` with a one-sentence rationale). This establishes the baseline — the first row in the grade history.

### Phase 4 Exit Criteria
- [ ] Validation report written and saved
- [ ] Every step has a data shape snapshot (input, output, skipped, gaps)
- [ ] Every step has a documented result
- [ ] Every fix is classified as PROCESS or CONTEXT
- [ ] Every handoff boundary is verified
- [ ] Data flow summary table is complete
- [ ] Determinism defects from Phase 2.5 are listed in the report (or the explicit "None" note)
- [ ] Concerns and out-of-scope issues documented
- [ ] `improvement/runs.jsonl` has a baseline entry with scores for every assertion
- [ ] `improvement/adversarial/fixtures/` has at least one fixture per assertion (seeded in Phase 2.7)

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
