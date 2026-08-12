# canvas.yaml — the pipeline-canvas contract

One `canvas.yaml` per pipeline, living next to the pipeline it describes (convention:
`<pipeline-dir>/canvas/canvas.yaml`, generated `pipeline-canvas.html` beside it). It
declares STRUCTURE and points at FILES — it never contains prompt or schema text. The
renderer reads every referenced file at render time and inlines it verbatim; that's why
re-running the renderer is the sync mechanism.

## Worked example (the committed fixture, `fixtures/demo-pipeline/canvas/canvas.yaml`)

```yaml
pipeline: demo-pipeline
title: Demo Summarization Pipeline
source_root: ..
stages:
  - id: corpus
    title: Corpus
    description: The raw material the pipeline consumes.
    attachments:
      - type: asset
        file: assets/flow.svg
        label: flow diagram
      - type: note
        label: HOUSE RULE
        text: Intake order beats recency when assembling the corpus.
  - id: summarize
    title: Summarize
    description: One summary per chapter, schema-validated.
    attachments:
      - type: schema
        file: schemas/summary.json
        example: runs/summary-filled.json
      - type: prompt
        file: prompts/summarize.md
        medium: CHAT
        variables:
          corpus: {text: "steve-blank-four-steps"}
  - id: publish
    title: Publish
    description: Validated summaries land in the review doc.
    attachments:
      - type: run_example
        file: runs/2026-08-11_demo-run.md
        medium: FILE
lanes:
  - id: hotfix
    label: HOTFIX
    stages: [corpus, publish]
```

## Top level

| Key | Required | Meaning |
|---|---|---|
| `pipeline` | yes | slug; shows in the header banner |
| `title` | yes | human title; header banner + browser tab |
| `source_root` | no | directory all `file:` refs resolve against, relative to canvas.yaml's directory (default: canvas.yaml's directory). Keeps refs short when the canvas lives in a `canvas/` subfolder |
| `sources` | no | external fan-in nodes; see below |
| `stages` | yes | ordered list, renders left-to-right |
| `lanes` | no | swim lanes; see below |
| `traces` | no | one entity's run, end to end; see below |

## Sources (fan-in)

External systems feeding the pipeline — supports
multi-source fan-in at different stages. Each source: `id` (slug), `title`, optional
`description`, optional `medium`. A stage declares what it consumes with `inputs:
[source_ids]`. Sources render as a band of tan dashed cards above the columns, each
positioned over its consuming stage(s), with dashed edges dropping into the stage
header. Fan-in at ANY stage is legal (e.g. verification sources enter at stage 4).
A declared source no stage consumes is a hard error — drop it or wire an `inputs`.

```yaml
sources:
  - id: crm_events
    title: CRM Events Feed
    description: 700 events / 400d
    medium: FILE
stages:
  - id: ingest
    title: Ingest
    inputs: [crm_events]
```

## Stages

Each stage: `id` (unique), `title`, optional `description`, optional `attachments` list.
A stage renders as one column; its attachments render as boxes in a FIXED role order —
SCHEMA → PROMPT → OUTPUT → CONTEXT. The order is not configurable; that predictability
is the point (readers can always find the prompt in the same place).

## Attachment types

| Type | Keys | Renders as |
|---|---|---|
| `schema` | `file`, optional `example` | SCHEMA slot. With `example`, a SCHEMA / FILLED EXAMPLE toggle |
| `prompt` | `file`, optional `variables` | PROMPT slot, always the FULL verbatim file. With `variables`, a BARE / INJECTED toggle |
| `code` | `file`, optional `display`, optional `example` | PROMPT slot (the producer — for stages whose transform is code, not a prompt file). `display: full` (default) inlines the file mono; `display: pointer` shows just path + line count (the file must still exist — sync guarantee). `example` adds a CODE / EXAMPLE toggle, e.g. a captured assembled prompt or sample output |
| `run_example` | `file` | OUTPUT slot — a finished run (md / json / image) |
| `asset` | `file` | OUTPUT slot — supporting image or file |
| `note` | `text`, optional `label` | CONTEXT slot, sinks to the bottom. The ONLY literal-content type — the escape valve for context that lives in no file. Everything else must point at a real file |

All types accept optional `label` (box title; defaults to the file basename) and
optional `medium`: `FILE` / `CODE` / `CHAT` / `SCREEN` (where this thing lives in the
as-run world).

**Prompt variables:** placeholders in the prompt file are `{{name}}`. Each entry in
`variables` is either a file path string (content read and substituted) or
`{text: "..."}` for a literal. A variable whose placeholder is missing from the prompt
is a hard error — it means the yaml has drifted from the prompt file.

**Images** (`.png .jpg .jpeg .gif .svg .webp`) inline as data URIs; `.json`/code
extensions render mono; everything else renders in the legible prose stack.

## Lanes

`id`, `label`, ordered `stages` list (may skip stages). Edges derive mechanically from
each lane's stage order — never drawn by hand, so there is no second source of truth to
drift. A MAIN lane covering all stages exists implicitly. Toggling a lane in the
rendered canvas dims everything else, accents the lane's edges, and auto-fits to it.

## Traces (the n8n-run view)

A trace follows ONE entity all the way through the pipeline — the equivalent of
opening a single n8n execution and reading each node's actual data.

```yaml
traces:
  - id: acme
    label: "TRACE: ACME"
    steps:
      - {stage: ingest, file: canvas/traces/acme/1-entity-row.json, label: resolved entity row}
      - {stage: infer,  file: canvas/traces/acme/3-assembled-prompt.txt}
```

- `id` (slug), `label`, and a non-empty ordered `steps` list; each step names a `file`
  (optional `label`, defaults to the basename) plus EXACTLY ONE of `stage` or `source`.
  A `source` step is the origin record — the raw payload the entity arrived as (e.g.
  the raw CRM event it arrived as) — and renders inside that source's card in the
  band. A stage may carry several steps; steps keep their declared order in the column.
- With a trace active, only sources the entity actually came through (those with trace
  steps) stay lit — a source that merely feeds an on-path stage still dims.
- Renders as a dashed accent button beside the lane bar. Toggled on, it behaves like a
  lane (everything off-path dims, edges accent along the traced stages) and numbered
  accent boxes (01, 02, …) materialize at the top of each traced column holding that
  entity's actual data at that stage. Lane and trace are mutually exclusive.
- Trace files are captured REAL data, refreshed by a committed capture script in the
  pipeline's repo (pattern: a `canvas/examples/_capture.py` that writes
  `canvas/traces/<entity>/`) — never hand-written, so traces sit inside the sync story.

## Sync rules

- The generated HTML is a **build artifact — never hand-edit it.** Pipeline changed →
  re-run the renderer (update canvas.yaml first if the structure changed).
- A missing or moved referenced file is a **hard error** (exit 2), never a stale box.
- `--check` re-renders and diffs against the committed HTML; exit 1 = stale. Wrap-up
  skills / CI can call it mechanically.
- Fixture regold procedure after intentional template/renderer changes: see the
  docstring in `tests/test_golden.py`.
