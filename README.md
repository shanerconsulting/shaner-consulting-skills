# Shaner Consulting — AI Skill Files

These are Claude Code skill files I built for my AI consulting practice. They encode a framework I call **[Process + Context](https://medium.com/@davidmshaner/where-does-the-sidewalk-end-c3c2260a41bd)** — the idea that every successful AI implementation lives at the intersection of a clear process (the recipe steps) and complete context (the ingredients).

I'm sharing them because a few people asked to try them. They're evolving as I go.

## What's here

**Consulting methodology** — how to work with clients:

| File | What it does |
|------|-------------|
| `shaner-consulting.md` | The main framework. A 6-step lifecycle that takes an AI implementation from "what are we even building" through system design, implementation, and post-implementation review. |
| `process-mapping.md` | A pre-work skill that helps extract and structure a process before any code enters the picture. Feeds into the main framework at Step 3. |
| `first-run.md` | Post-implementation validation. Walks through a built system step by step with real data, gates output at every phase, and classifies failures as process problems or context problems. |

**Operational workflow** — how to start and end your own working sessions:

| File | What it does |
|------|-------------|
| `bootup.md` | Morning centering ritual. Phases: read a mindset statement, check wins and impact metrics, verify the vision-to-priorities chain is connected. Produces a daily session log. |
| `deploy.md` | End-of-session wrap-up. Commits, pushes, notifies your team, scans internal docs for staleness, checks client folders, and saves session context to memory. |

Both categories use the same patterns: phased execution, hard gates, AskUserQuestion with re-ground/simplify/recommend/options, and session logging.

## How to use them

These are [Claude Code](https://docs.anthropic.com/en/docs/claude-code) skill files. Drop them in `.claude/skills/` in any project and invoke them with `/shaner-consulting`, `/process-mapping`, `/first-run`, `/bootup`, or `/deploy`.

The consulting skills (`shaner-consulting`, `process-mapping`, `first-run`) work best in sequence: map the process, build the system, validate it. But each one stands alone.

The operational skills (`bootup`, `deploy`) contain `[bracketed-placeholders]` you'll need to customize — Slack channel IDs, teammate user IDs, GitHub accounts, etc. Each file has setup instructions explaining what to configure.

## Setup for operational skills

`bootup.md` and `deploy.md` reference Slack channels, team members, and MCP tools that you'll need to configure for your environment.

### Finding your Slack IDs

- **Channel ID:** Open Slack, right-click the channel name, select "View channel details", scroll to the bottom — the Channel ID starts with `C`
- **User ID:** Click on a user's profile in Slack, click the "..." menu, select "Copy member ID" — starts with `U`

### Configuring Slack MCP

These skills send messages via a Slack MCP server. Check your `.claude/settings.json` for your Slack MCP server name. The tool will be named like `mcp__[your-server-name]__slack_post_message`.

If you don't have a Slack MCP server configured, see the [Claude Code MCP docs](https://docs.anthropic.com/en/docs/claude-code/mcp).

### GitHub account switching

Only relevant if you use multiple `gh` accounts. See `gh auth switch --help`. If you only use one account, remove the account-switching comments from `deploy.md`.

## Last updated

| File | Last updated | Summary |
|------|-------------|---------|
| `shaner-consulting.md` | 2026-04-07 | Principle 8 (four-bucket skill directories), Plan Self-Review Checklist, Skill Directory Audit |
| `process-mapping.md` | 2026-03-30 | Initial release |
| `first-run.md` | 2026-04-07 | Observable data shape tracing (n8n-style node inspector) |
| `bootup.md` | 2026-03-31 | Daily finance pipeline in background processes |
| `deploy.md` | 2026-03-31 | Initial release |

## Changelog

**2026-04-07**
- `shaner-consulting.md` — Added Principle 8: four-bucket directory structure for skill files (SKILL.md = process, context/ = ingredients, data/ = outputs, prompts/ = LLM payloads). Added Plan Self-Review Checklist as a hard gate before presenting plans. Added Skill Directory Audit to Phase 1.5 for detecting monolith skill files with inline context.
- `first-run.md` — Added observable data shape tracing: each process step now logs its actual output shape (fields, types, counts) so you can see exactly what flows between steps — inspired by n8n's node inspector.

**2026-03-31**
- `shaner-consulting.md` — Added gstack-compatible learnings and telemetry observability (session tracking, prior learnings search, post-session learning capture).
- `bootup.md` — Added daily finance pipeline to background process checks.
- `bootup.md`, `deploy.md` — Initial release of operational workflow skills (anonymized from production versions).

**2026-03-30**
- Initial release: `shaner-consulting.md`, `process-mapping.md`, `first-run.md`.

## Status

Active and evolving. I'm sharing these with a small group to get feedback and see how they hold up outside my own workflows. If something's unclear or doesn't work, I want to know.
