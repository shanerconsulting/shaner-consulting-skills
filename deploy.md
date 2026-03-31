# Deploy — End-of-Session Wrap-Up

## Trigger
- User says `/deploy`, "deploy", "wrap up", "I'm done"
- End of a working session

## Overview
Standard "I'm done with this chat" command. Commits, pushes, notifies your team, and ensures operational docs stay in sync with the work done this session.

## Steps

### Step 1: Commit & Push

1. Run `git status` and `git diff` (staged + unstaged).
2. Show the user a summary of what changed.
3. Draft a commit message and get approval.
4. Stage specific files (never `git add -A`).
5. Commit.
6. Push to your remote:
   ```bash
   # If you use multiple GitHub accounts, add your account-switching commands here.
   # Example:
   # gh auth switch --user [your-github-user]
   git push origin main
   # gh auth switch --user [your-default-github-user]
   ```

### Step 2: Internal Scan + To-Dos

**Do this BEFORE the Slack message** — to-dos and doc updates from the session may be relevant context for what you tell your team.

#### To-Dos (MANDATORY — never skip)

**Always read your to-do file and actively look for:**
1. **New action items** from this session — things you or your team need to do next. If the session produced work, it almost certainly produced follow-up actions. Think: what's the next step someone has to take?
2. **Completed items** — anything that was on the list that this session's work finished
3. **Invalidated items** — anything that no longer applies given what happened

**Common sources of new to-dos:**
- Emails sent that need a response (follow-up needed)
- Contracts signed (next: scheduling, onboarding, insurance, finance setup)
- Meetings discussed (next: scheduling, prep, follow-ups)
- Decisions made that require implementation
- External dependencies (waiting on someone — track it)

Propose additions/changes and get approval before editing.

#### Other Internal Docs

Scan your internal docs for files that may need updates based on the session's work. Customize this table with your actual internal file paths and update triggers:

| Category | Example Files | Update Triggers |
|----------|--------------|-----------------|
| Processes | `internal/processes/*.md` | Workflow changes, new patterns |
| Finance | `internal/finance/*.yaml` | New contracts, rate changes, client additions/removals |
| Legal | `internal/legal/contracts/**` | Active negotiations, new positions |
| Meetings | `internal/meetings/` | Meeting notes saved with correct naming (`YYYY-MM-DD_description.md`) |

For each file that may need an update:
1. Read the current file.
2. Propose specific edits based on the session's work.
3. **Show the proposed changes and get explicit approval before editing.**
4. Apply approved changes.

If nothing needs updating, say so — don't force updates.

### Step 3: Notify Your Team

1. Draft the message following the Voice & Framing guidelines below.
2. **Include any relevant to-dos or action items for your teammate** that were identified in Step 2.
3. **Show the draft and get explicit approval before sending.**
4. If the user says skip, don't send. If approved, send via your Slack MCP tool (e.g., `[your-slack-mcp-tool]`) with your team channel ID (`[your-channel-id]`). Tag your teammate with `<@[your-teammate-user-id]>` so they get a notification.

#### Voice & Framing

Write this like you're telling your business partner what you just worked on — not a deploy log. Mirror the *narrative arc* of the session.

**Lead with the "why" of the session.** What were you trying to figure out, build, or respond to? Frame it like you'd explain it walking up to their desk.

**Structure:**
1. **What I was working on and where I landed** — 2-3 sentences that tell the story. What triggered the work, what the thinking was, what the output is.
2. **What to look at** — Point your teammate to the specific file(s) or areas worth reviewing, with a one-line note on what they'll find.

**Anti-patterns to avoid:**
- Bullet-point changelogs ("Created X, Updated Y, Added Z")
- Generic headers like "Session update" or "Deploy summary"
- Restating file paths as content (say what's *in* the doc, not that the doc exists)
- Robotic tone — no "the following changes were made" energy
- Pull instructions or basic git commands — your teammate knows how to pull

**Good example:**
> Spent some time working through the Acme contract — their counsel came back with a counteroffer on the insurance clause. Landed on accepting their language with a carve-out for gross negligence, which matches a prior engagement's precedent. Updated the position doc and drafted the response email.
>
> Worth reading: `internal/legal/contracts/negotiation/acme/position.md` — has the updated redlines and reasoning.

**Bad example:**
> Deploy summary — Acme contract negotiation
> - Updated internal/legal/contracts/negotiation/acme/position.md
> - Modified insurance clause language
> - Drafted email response

### Step 4: Sync Public Artifacts

If you maintain public copies of any internal files (e.g., open-source skill files, public documentation), check if they changed this session.

**How to check:**
```bash
# Clone or pull your public repo
git clone https://github.com/[your-org]/[your-public-repo].git /tmp/[your-public-repo] 2>/dev/null || (cd /tmp/[your-public-repo] && git pull)

# Diff each file (canonical internal → public copy)
diff internal/path/to/file.md /tmp/[your-public-repo]/public-name.md
```

**If any files changed:**
1. Copy the updated files to the public repo (applying any anonymization if needed)
2. Commit with a message describing what changed
3. Push

**If nothing changed:** Skip — say "Public artifacts are in sync."

<!-- This step is optional. Remove if you don't maintain public copies of internal files. -->

### Step 5: Client Scan

Based on the session's work, check if any client folders need updates:

- **`clients/active/`** — Did client-specific work happen? Check that deliverables, meeting notes, or product docs are current.
- **`clients/pipeline/`** — Pipeline conversations? Check that prospect folders reflect latest status.
- **`clients/past/`** — Rare, but check if a past client reference came up that needs annotation.

Skip areas that clearly aren't relevant to the session.

### Step 6: Memory Check

Did anything come up this session that should persist to future conversations?
- Non-obvious decisions or context that won't be in the code/docs
- Relationship dynamics, preferences, or patterns worth remembering
- If yes, save to auto memory with the appropriate type

### Step 7: Final Status

Print a clean summary using indented plain-text block format (no markdown tables, no bold, no bullets — just aligned key-value pairs inside an indented block):

```
DEPLOY COMPLETE
  COMMITTED: [commit message(s)]
  PUSHED: [your-org]/[your-repo]
  PUBLIC ARTIFACTS: [synced / in sync / skipped]
  SLACK: [sent to team / skipped]
  INTERNAL SCAN: [X files updated / no updates needed]
  CLIENT SCAN: [X files updated / no updates needed]
  MEMORY: [X items saved / no updates]
```

Use line wrapping with alignment for long values (indent continuation lines to match the value start column).
