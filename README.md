# Shaner Consulting — AI Skill Files

These are Claude Code skill files I built for my AI consulting practice. They encode a framework I call **[Process + Context](https://medium.com/@davidmshaner/where-does-the-sidewalk-end-c3c2260a41bd)** — the idea that every successful AI implementation lives at the intersection of a clear process (the recipe steps) and complete context (the ingredients).

I'm sharing them because a few people asked to try them. They're evolving as I go.

## What's here

| File | What it does |
|------|-------------|
| `shaner-consulting.md` | The main framework. A 6-step lifecycle that takes an AI implementation from "what are we even building" through system design, implementation, and post-implementation review. |
| `process-mapping.md` | A pre-work skill that helps extract and structure a process before any code enters the picture. Feeds into the main framework at Step 3. |
| `first-run.md` | Post-implementation validation. Walks through a built system step by step with real data, gates output at every phase, and classifies failures as process problems or context problems. |

## How to use them

These are [Claude Code](https://docs.anthropic.com/en/docs/claude-code) skill files. Drop them in `.claude/skills/` in any project and invoke them with `/shaner-consulting`, `/process-mapping`, or `/first-run`.

They work best in sequence: map the process, build the system, validate it. But each one stands alone.

## Status

Active and evolving. I'm sharing these with a small group to get feedback and see how they hold up outside my own workflows. If something's unclear or doesn't work, I want to know.
