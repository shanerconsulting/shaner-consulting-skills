# /bootup — Daily Boot Up

Morning centering ritual for Offline. Three sections: Mindset, Wins & Progress, Connect the Dots.

**Invocation:** `/bootup`
**Duration:** 5-10 minutes
**Scope:** `.claude/skills/bootup/` (read/write) and `projects/offline/internal/company-os/vto/` (read, may write to weekly_alignment.md)

## Setup

This skill expects a directory structure with context files you provide. Before first use:

1. Create the directory structure shown below
2. Write your personal mindset statement in `context/mindset.md` (see template at the bottom of this file)
3. List your external data sources in `context/sources.md` (see template at the bottom of this file)
4. The `data/sessions/` directory will be populated automatically as you run bootups

## Directory Structure

```
.claude/skills/bootup/
├── SKILL.md                      # Process (this file — the recipe)
├── context/
│   ├── mindset.md                # Your personal mindset statement
│   └── sources.md                # All external sources: URLs, Slack, commands, file paths
├── data/
│   └── sessions/                 # Daily session logs (YYYY-MM-DD.md) — produced by each bootup
└── improvement/
    └── ideas.md                  # Future improvement ideas
```

**Litmus test:** SKILL.md IS the process. `context/` has ingredients the process CONSUMES. `data/sessions/` has output the process PRODUCES. `improvement/` has ideas for the future.

---

## Phase 0: Boot

```bash
REPO_ROOT=$(git rev-parse --show-toplevel 2>/dev/null)
SKILL_DIR="$REPO_ROOT/.claude/skills/bootup"
VTO_DIR="$REPO_ROOT/projects/offline/internal/company-os/vto"
INBOX_DIR="$REPO_ROOT/projects/offline/internal/non-product-product/inbox_agent"
SESSION_DATE=$(date '+%Y-%m-%d')
SESSION_FILE="$SKILL_DIR/data/sessions/$SESSION_DATE.md"

echo "════════════════════════════════════════"
echo "  DAILY BOOT UP — Offline"
echo "════════════════════════════════════════"
echo "DATE:     $(date '+%A, %B %d, %Y')"
echo "STARTED:  $(date '+%H:%M')"
echo "════════════════════════════════════════"
echo ""

# Verify context files
for f in "$SKILL_DIR/context/mindset.md" "$VTO_DIR/weekly_alignment.md" "$SKILL_DIR/context/sources.md"; do
  if [ -f "$f" ]; then
    echo "  ✅ $(basename $f)"
  else
    echo "  ❌ MISSING: $f"
  fi
done

echo ""
```

**After printing the header**, immediately fire off the inbox agent processes in the background using Bash with `run_in_background: true`:

1. `cd $INBOX_DIR && python3 processes/01_lifecycle/run.py all`
2. `cd $INBOX_DIR && python3 processes/02_waiting_on_me/run.py`

Print:
```
INBOX:    🚀 Lifecycle processing launched (background)
INBOX:    🚀 Waiting-on-me scan launched (background)
```

**Start building the session log.** Initialize `data/sessions/YYYY-MM-DD.md` with:

```markdown
# Boot Up — YYYY-MM-DD

## Phases Completed
<!-- Updated as each phase completes -->
```

Proceed immediately to Phase 1.

### Phase 0 Exit Criteria
- [x] Header printed with today's date
- [x] Context files verified
- [x] Inbox agent processes launched in background
- [x] Session log file initialized

---

## Phase 1: Mindset

Read `context/mindset.md` and display its full contents to the user.

After displaying, print:

```
────────────────────────────────────
Take a moment. Let this land.
────────────────────────────────────
```

No AskUserQuestion here. The mindset section is read-only — meant to be absorbed, not discussed. Proceed directly to Phase 2.

Append to session log: `- [x] Mindset: read`

```
┌─────────────────────────────────────┐
│ PHASE 1: MINDSET                    │
│ STATUS: DONE                        │
└─────────────────────────────────────┘
```

**HARD GATE:** Phase 1 always completes. No conditions. Proceed to Phase 2.

---

## Phase 2: Wins & Progress

Print:

```
════════════════════════════════════════
  WINS & PROGRESS
════════════════════════════════════════

Open your impact metrics:
→ https://davidmshaner.com/impact

Check #companywins in Slack for recent wins.
```

Use **AskUserQuestion** with this structure:

1. **Re-ground:** "Daily Boot Up, Phase 2: Wins & Progress. You're looking at live Offline impact metrics and recent company wins."
2. **Simplify:** "Take a look at the metrics and wins. Anything jump out?"
3. **Recommend:** "RECOMMENDATION: Choose A if nothing notable — the mindset statement already covered the 'evidence' angle. This phase is a quick pulse check, not a deep dive."
4. **Options:**
   - A) "All good, move on"
   - B) "Something stood out" — let the user share, acknowledge it, then proceed

Append to session log:
- If A: `- [x] Wins: checked (nothing notable)`
- If B: `- [x] Wins: checked — [user's note]`

```
┌─────────────────────────────────────┐
│ PHASE 2: WINS & PROGRESS            │
│ STATUS: DONE                        │
└─────────────────────────────────────┘
```

**HARD GATE:** User has confirmed they checked. Proceed to Phase 3.

---

## Phase 3: Connect the Dots

Read `projects/offline/internal/company-os/vto/weekly_alignment.md` and display its full contents.

**Staleness check:** Look at the "This Week's Focus" section. If it's empty (just has HTML comment placeholders) or hasn't been updated, flag it:

```
⚠️  "This Week's Focus" is empty. What are the 1-3 things that matter most this week?
```

**Inbox agent results:** If the background processes have completed by now, summarize:
- Lifecycle: how many threads processed, how many drafts created
- Waiting-on-me: how many threads need attention, top 3 subjects

If not finished yet, note: "Inbox agent still running — results will appear when done."

Use **AskUserQuestion** with this structure:

1. **Re-ground:** "Daily Boot Up, Phase 3: Connect the Dots. The chain from 'Why We Exist' down to today's priorities."
2. **Simplify:** "Does the vision-to-today chain feel connected? Is anything stale, missing, or off?"
3. **Recommend:** "RECOMMENDATION: Choose C if 'This Week's Focus' is empty — that's the most common gap and the fastest win."
4. **Options:**
   - A) "Chain is good" — proceed to completion
   - B) "Something is off" — user describes what. Offer to update weekly_alignment.md.
   - C) "Update This Week's Focus" — user provides priorities. Write them into the file.

Append to session log:
- If A: `- [x] Chain: connected`
- If B: `- [x] Chain: updated — [what changed]`
- If C: `- [x] Chain: This Week's Focus updated — [priorities]`

```
┌─────────────────────────────────────┐
│ PHASE 3: CONNECT THE DOTS           │
│ STATUS: DONE                        │
└─────────────────────────────────────┘
```

**HARD GATE:** User has confirmed the chain. Proceed to Completion.

---

## Completion

Finalize the session log in `data/sessions/YYYY-MM-DD.md`. The complete file should look like:

```markdown
# Boot Up — YYYY-MM-DD

## Phases Completed
- [x] Mindset: read
- [x] Wins: checked — [note or "nothing notable"]
- [x] Chain: [connected | updated — details]

## Inbox Agent Results
- Lifecycle: [X threads processed, Y drafts created]
- Waiting on me: [X threads need attention]
  - [top subjects if any]

## Notes
[Any observations from the user during the session]
```

Print:

```
════════════════════════════════════════
  DAILY BOOT UP — COMPLETE
════════════════════════════════════════
PHASES:     Mindset ✓ · Wins ✓ · Chain ✓
INBOX:      [lifecycle summary] · [waiting-on-me summary]
SESSION:    data/sessions/YYYY-MM-DD.md
════════════════════════════════════════

You know who you are. You know what matters. Go.
```

---

## Stop For / Never Stop For

**Stop for:**
- Stale "This Week's Focus" section
- User wants to edit weekly_alignment.md
- User wants to talk about something they saw in wins/metrics
- Inbox agent results that surface urgent threads

**Never stop for:**
- Whether to display the mindset (always display it)
- Which Slack channel (always #companywins)
- Formatting or display choices
- Whether to run inbox agent (always run it)

---

## Editing the Mindset Statement

The mindset statement lives at `context/mindset.md`. You can edit it directly or ask the skill to update it. The statement should evolve as your identity and focus evolve — it's not static.

## Process Layers

- **L1: Personal** — faith, family, health, career, personal growth. The mindset statement lives here.
- **L2: Company OS** — the strategic layer connecting all business units. Each domain gets its own chain; they ladder up to a unified allocation view.
- **L3: Daily Boot Up (Offline)** — this implementation. The chain from the company mission down to weekly priorities.

## Extending to Other Domains

This skill is built for Offline first. To add other domains:
1. Add domain-specific chain files to `context/` (e.g., `other-domain-chain.md`)
2. Add phases to the skill for each domain
3. Update `context/sources.md` with new external sources
4. Build the L2 unified view — a document that connects all domain chains to your overall allocation strategy
5. Keep the mindset section domain-agnostic (it already lives at L1)

---

## Context File Templates

### `context/mindset.md`

```markdown
# Mindset

<!--
Write your personal mindset statement here. This gets displayed at the start
of every bootup — it's meant to center you before the day begins.

What to include:
- What you're focused on this year / season
- The patterns you're trying to break or build
- Evidence that you're on the right track
- A reminder of who you are when you're at your best

This is personal. It's for you. Update it whenever it stops landing.
-->
```

### `context/sources.md`

```markdown
# Boot Up — External Context Sources

Everything the bootup process consumes beyond the mindset statement.

## Local Files

| Source | Path | Consumed By |
|--------|------|-------------|
| Vision → Today chain | `projects/offline/internal/company-os/vto/weekly_alignment.md` | Phase 3: Connect the Dots |
| <!-- Add other strategic docs here --> | | |

## External URLs

| Source | URL | Consumed By |
|--------|-----|-------------|
| Impact Metrics (live) | https://davidmshaner.com/impact | Phase 2: Wins & Progress |
| <!-- Add other dashboards, docs, etc. --> | | |

## Slack Channels

| Channel | Workspace | Consumed By |
|---------|-----------|-------------|
| #companywins | Offline | Phase 2: Wins & Progress |

## Background Commands (fired during Phase 0)

| Command | Working Dir | Purpose |
|---------|-------------|---------|
| `python3 processes/01_lifecycle/run.py all` | `projects/offline/internal/non-product-product/inbox_agent` | Process lifecycle emails |
| `python3 processes/02_waiting_on_me/run.py` | `projects/offline/internal/non-product-product/inbox_agent` | Surface threads waiting for your response |
```
