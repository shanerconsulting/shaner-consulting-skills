---
name: pipeline-canvas
description: Visualize any data-transformation pipeline as an interactive canvas.
  Use when asked to "visualize this data transformation", "pipeline canvas",
  "put this pipeline on a canvas", or when a project's multi-stage prompt/schema
  pipeline needs a visual map. Claude authors a canvas.yaml (structure + file
  pointers, never pasted content); a deterministic renderer builds the HTML.
  Re-running the renderer is the sync mechanism — never hand-edit the output.
---

# Pipeline Canvas

This directory holds the renderer (`render.py`), the template (`template.html`), and
the canvas.yaml contract (`canvas-yaml.md` — read it before authoring any canvas.yaml).

## Flow

1. **Explore the pipeline directory.** Identify the stages of the transformation and,
   for each stage: its schema file (if any), its prompt file, a representative finished
   run, and any context that lives in no file. This is the only judgment work.
2. **Draft `canvas/canvas.yaml`** next to the pipeline, per canvas-yaml.md. Point at
   files; never paste content. Anything with no file home becomes a `note`.
3. **Ask the configuration questions** (short, all at once): Which swim lanes, and which
   stages does each hit? Which run should be the featured example? Any stage boundaries
   I got wrong?
4. **Render:**
   ```bash
   python3 <path-to-this-skill>/render.py <pipeline>/canvas/canvas.yaml
   ```
   Output lands as `pipeline-canvas.html` beside the yaml. Exit 2 = spec/content error
   (message says which file or key); fix the yaml or the pipeline, don't work around it.
5. **Verify in Chrome before showing the user** (hard gate): open the output via
   chrome-devtools MCP, screenshot to file, READ the screenshot, and exercise the
   interactive states with `evaluate_script` (toggles switch views, lane toggle dims +
   accents + auto-fits, arrow keys zoom, load is fit-to-screen). Never assert a visual
   verdict from memory.
6. **Sync:** when the pipeline changes, update canvas.yaml if structure changed, then
   re-run the renderer. `--check` (exit 1 = stale) is available for wrap-up flows.

## Regression tests

`python3 -m pytest pipeline-canvas/tests/ -v` (60+ tests incl. a golden-file render of `fixtures/demo-pipeline`). Run after any
change to render.py or template.html; regold per `tests/test_golden.py` docstring.
