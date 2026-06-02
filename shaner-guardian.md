---
name: shaner-guardian
description: |
  Lightweight paradigm guardian for repos built with /shaner-consulting.
  Audits incremental changes (bug fixes, new features, new process steps) against
  the four-bucket model, README contract, and process-code alignment.
  Two modes: pre-change (audit a plan) and post-change (review diff + fix).
  Use when making any change to a /shaner-consulting-built system.
  Invoke with /shaner-guardian. Proactively suggest when an agent is about to
  modify a repo that has the four-bucket structure.
---

# Shaner Guardian

Lightweight paradigm enforcer for systems built with `/shaner-consulting`.

---

## Preamble

```bash
_BRANCH=$(git branch --show-current 2>/dev/null || echo "unknown")
_REPO=$(basename "$(git rev-parse --show-toplevel 2>/dev/null)" 2>/dev/null || echo "unknown")
echo "════════════════════════════════════════"
echo "  SHANER GUARDIAN — Paradigm Check"
echo "════════════════════════════════════════"
echo "REPO:     $_REPO"
echo "BRANCH:   $_BRANCH"
echo "CWD:      $(pwd)"
echo "STARTED:  $(date '+%Y-%m-%d %H:%M')"
echo "════════════════════════════════════════"
```

Read CLAUDE.md and README.md in the current directory (and repo root if different).

---

## Phase 0: Origin Check

**HARD GATE.** Before doing anything, verify this system was built with /shaner-consulting.

Look for ALL of the following signals:
1. A `processes/` folder (or process files with numeric prefixes like `01_`, `02_`)
2. A `context/` folder
3. A `data/` folder
4. A README with a process table (columns: #, Process Title, Trigger, Process Steps, Context Required)
5. A "How to modify" section in the README that references the four-bucket model

**If 3+ signals are present:** This is a SC-built system. Proceed to Phase 1.

**If fewer than 3 signals are present:** STOP. This repo was not built with /shaner-consulting.

```
════════════════════════════════════════
  SHANER GUARDIAN — NOT APPLICABLE
════════════════════════════════════════
This repo does not appear to be built with /shaner-consulting.
Missing signals: [list what's missing]
RECOMMENDATION: Run /shaner-consulting for a full Process + Context overhaul.
════════════════════════════════════════
```

Do NOT proceed. Do NOT try to "fix" a non-SC repo with guardian logic.

For **skill files** (.claude/skills/*/SKILL.md): the four buckets manifest differently. Look for:
- SKILL.md with process steps, gates, and receipts
- A `context/` subfolder (or evidence that reference content is externalized)
- Hard gates between phases
- Status receipts

If the skill was built with SC principles, proceed. If it's a plain prompt file with no structure, recommend /shaner-consulting.

---

## Phase 1: Mode Detection

Determine which mode to run based on the current state.

**Check for uncommitted changes:**
```bash
git diff --stat
git diff --cached --stat
```

**Check for a plan file in context:**
Scan the conversation for any plan the user has shared or that exists in plan mode.

| Condition | Mode |
|-----------|------|
| Uncommitted diff exists (staged or unstaged) | **Post-change** — review the diff, fix violations |
| User shared a plan or is in plan mode | **Pre-change** — audit the plan for paradigm violations |
| User explicitly says "I'm about to..." | **Pre-change** — audit what they describe |
| No diff, no plan | Ask the user what they want to audit |

Tell the user which mode you're running:
```
MODE: [Pre-change audit | Post-change review]
SCOPE: [files/plan being reviewed]
```

---

## Phase 2: Parallel Review

Launch **four agents in a single message** (parallel execution). Pass each agent:
- The diff (post-change) or plan text (pre-change)
- The current README.md content
- The current folder structure (`find . -type f | head -60`)
- The current `improvement/assertions.md` content (if present)

### Agent 1: Bucket Integrity

Review every file touched in the diff/plan against the four-bucket model.

For EACH new or moved file, apply the litmus test:
- Does a process CREATE this? → `data/`
- Does a process CONSUME this? → `context/`
- IS it a process step? → `processes/`
- Is it sent to an LLM? → `prompts/`

Flag:
- Files in the wrong bucket
- New top-level folders outside the four canonical names (`processes/`, `context/`, `data/`, `prompts/`)
- New `helpers/`, `utils/`, `lib/`, `shared/`, `config/`, `agents/`, `sources/` folders (common violations)
- Reference data classified as "data" when it's actually consumed by processes (context)
- For skills: inline context in SKILL.md (style rules, spec tables, prompt templates, examples) that should be in `context/`

Report as a table:
| File | Current Location | Correct Location | Reason |
|------|-----------------|------------------|--------|

### Agent 2: Contract Sync

Check whether the README, CLAUDE.md, AND data files the process writes to are still accurate after the change.

1. **Process table:** Does every process in the README still have a corresponding file? Does every process file appear in the table? If a process was added/modified/removed, is the table updated?
2. **File/folder map:** Does the README's file map match the actual directory structure? Any new files missing from the map?
3. **Run commands:** Do the commands in "How to run it" still work with the changes?
4. **Dependencies:** If new APIs, config, or external systems were added, are they in the README's dependencies section?
5. **CLAUDE.md:** Does it still accurately describe the project state?
6. **Data file shape sync** (CRITICAL — easy to miss): If the edit changes what the process WRITES to a data file (a log, a registry, a state file, etc.), you MUST read the target data file on disk and verify:
   - The current schema (column names, field order, nested structure)
   - Any existing rows/records and their shape
   - Whether the proposed write-format matches the existing schema
   If they don't match, flag as **CRITICAL**. Do NOT trust the scaffold block in the SKILL/process file — that block describes what the file *would* look like if fresh, but the real file on disk may have evolved past it. Classic failure mode: a process edit defines a new table name/schema, and on execution creates a parallel table instead of appending to the existing one, silently orphaning prior data. Always: (a) identify which data files this edit writes to, (b) read them, (c) diff the current schema against the proposed write-format, (d) flag mismatches.

Report as a checklist:
- [ ] Process table matches process files
- [ ] File/folder map matches directory
- [ ] Run commands still valid
- [ ] Dependencies section current
- [ ] CLAUDE.md accurate
- [ ] Target data files read; write-format matches existing schema (or mismatches flagged CRITICAL)

Flag each discrepancy with the specific line/section that needs updating.

### Agent 3: Paradigm Coherence

Check the deeper architectural principles.

1. **Process-code naming:** Do process files still have numeric prefixes that match execution order? If a new step was inserted, was it numbered correctly? Can you say "the problem is in process 3" and have it mean something?
2. **Handoff intelligence:** If Process N's output changed (new fields, removed fields, changed format), does Process N+1 still get what it needs? Check the interface between adjacent processes.
3. **Source of truth:** Did the change introduce local state that duplicates an external system's truth? (e.g., caching invoice status locally instead of reading from Mercury)
4. **Scope creep into other processes:** Did the change to Process N accidentally modify or affect Process M? Each process should be independently modifiable.
5. **For skills:** Are hard gates still intact? Did someone add a step that bypasses a gate? Are AskUserQuestion calls still structured (not inline text)? Is the SKILL.md still process-only (no new inline context)?

Report violations with severity:
- **CRITICAL** — Breaks the paradigm (wrong bucket, broken handoff, gate bypassed)
- **WARNING** — Weakens the paradigm (naming drift, missing README update, scope leak)
- **NOTE** — Minor drift worth knowing about

### Agent 4: Improvement Bucket Integrity

The `improvement/` bucket is how the system learns. Its integrity is paradigm-critical. Read the schema in the `/shaner-consulting` skill's sibling file `improvement-bucket.md` if unfamiliar.

Run these checks:

#### 4.1 Structural

- `improvement/assertions.md` exists
- `improvement/grader.md` exists
- `improvement/adversarial/fixtures/` directory exists
- `improvement/runs.jsonl` exists (may be empty)

Missing any = **CRITICAL**.

#### 4.2 Assertion Voice (Jargon Lint)

For every sentence in `improvement/assertions.md`, apply the jargon ban list from `improvement-bucket.md`. Flag any sentence that contains:

1. Function or API verbs: `emit`, `fire`, `trigger`, `dispatch`, `invoke`, `call`, `return`, `throw`, `raise`
2. State-transition computing terms: `transition`, `healthy → unhealthy`, `flip`, `toggle`, `latch`, `debounce`, `dedupe`, `retry-with-backoff`
3. Raw API / HTTP language: `ok:true`, `200`, `429`, `5xx`, `exit 0`, `null`, `undefined`, backticked field names
4. Latin abbreviations: `i.e.`, `e.g.`, `etc.`, `vs.`, `et al.`
5. Arrow-syntax: `X → Y`, `if X then Y` as shorthand
6. Code-shaped glue: `==`, `!=`, `&&`, `||`, parentheses around conditions
7. Implementation details: specific timeouts, specific retry counts, algorithm names

Each violation = **CRITICAL** with the quoted sentence and a plain-language rewrite.

Also flag: sentences describing **how** instead of **what**. "The monitor retries with exponential backoff, 2/4/8/16 seconds" is HOW — rewrite to "The monitor tries again if it fails the first time."

#### 4.3 Assertion ↔ Fixture Coverage

Every assertion sentence must have at least one fixture in `improvement/adversarial/fixtures/` that references it via `assertion_ref`. Cross-check.

- Assertion with no fixture = **WARNING** (fixture missing)
- Fixture with no matching assertion = **CRITICAL** (orphaned test — the sentence it protects was deleted or never existed)

#### 4.4 Diff ↔ Assertion Coverage

If the diff touches any process code, check: does an assertion sentence cover the behavior being modified?

- Process code changed, no assertion covers it = **WARNING** (untested behavior — write the assertion)
- Process code changed, assertion exists, assertion sentence is now stale relative to the new behavior = **CRITICAL** (the contract lies about what the code does; update the assertion or revert the code)

#### 4.5 Runs Trend Check

Read the last N (default: 10) entries in `improvement/runs.jsonl`. For each assertion, compute the pass rate over those runs.

- Assertion pass rate below 80% over the last 10 runs = **WARNING** (the system is drifting — even if this diff doesn't touch that process)
- Assertion pass rate below 50% over the last 10 runs = **CRITICAL** (the system is actively broken on that behavior)

If `runs.jsonl` has fewer than 3 entries, skip this check (not enough history).

Report as:

| Check | Status | Severity | Finding |
|-------|--------|----------|---------|
| Structural | OK / Missing | — / CRITICAL | [details] |
| Jargon lint | N violations | — / CRITICAL | [quoted sentences + rewrites] |
| Coverage | OK / Gaps | — / WARNING / CRITICAL | [details] |
| Diff ↔ assertion | OK / Gaps | — / WARNING / CRITICAL | [details] |
| Trend | OK / Drifting | — / WARNING / CRITICAL | [per-assertion pass rates] |

---

## Phase 3: Act

### Post-change mode: Fix

Aggregate findings from all three agents. For each finding:

1. **CRITICAL** — Fix immediately. Move files to correct buckets. Update README. Restore gates.
2. **WARNING** — Fix if straightforward. If it requires a design decision, flag it for the user.
3. **NOTE** — Log it but don't change anything.

After fixing, run `git diff --stat` to show what was changed.

### Pre-change mode: Flag

Do NOT modify any files. Instead, produce a **Guardian Report**:

```
════════════════════════════════════════
  GUARDIAN REPORT — Pre-Change Audit
════════════════════════════════════════
PLAN/CHANGE: [summary of what's proposed]

CRITICAL: [count]
[list each with one-line description]

WARNING: [count]
[list each with one-line description]

NOTE: [count]
[list each with one-line description]

RECOMMENDATION: [proceed / revise plan / stop]
════════════════════════════════════════
```

If there are any CRITICAL findings, the recommendation is always "revise plan."

---

## Completion

```
════════════════════════════════════════
  SHANER GUARDIAN — COMPLETE
════════════════════════════════════════
MODE:       [Pre-change | Post-change]
FINDINGS:   [N critical, N warning, N note]
FIXED:      [N items] (post-change only)
FLAGGED:    [N items] (pre-change only)
FILES:      [files modified or flagged]
════════════════════════════════════════
```
