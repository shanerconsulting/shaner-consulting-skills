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

Launch **three agents in a single message** (parallel execution). Pass each agent:
- The diff (post-change) or plan text (pre-change)
- The current README.md content
- The current folder structure (`find . -type f | head -60`)

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

Check whether the README and CLAUDE.md are still accurate after the change.

1. **Process table:** Does every process in the README still have a corresponding file? Does every process file appear in the table? If a process was added/modified/removed, is the table updated?
2. **File/folder map:** Does the README's file map match the actual directory structure? Any new files missing from the map?
3. **Run commands:** Do the commands in "How to run it" still work with the changes?
4. **Dependencies:** If new APIs, config, or external systems were added, are they in the README's dependencies section?
5. **CLAUDE.md:** Does it still accurately describe the project state?

Report as a checklist:
- [ ] Process table matches process files
- [ ] File/folder map matches directory
- [ ] Run commands still valid
- [ ] Dependencies section current
- [ ] CLAUDE.md accurate

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
