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

## Status

Active and evolving. I'm sharing these with a small group to get feedback and see how they hold up outside my own workflows. If something's unclear or doesn't work, I want to know.
