#!/usr/bin/env python3
"""Deterministic renderer: canvas.yaml -> self-contained pipeline-canvas HTML.

Part of the pipeline-canvas skill. Contract: canvas-yaml.md in this directory.
"""
import argparse
import base64
import html
import json
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:  # PyYAML is the single allowed third-party dep
    sys.exit("pipeline-canvas: PyYAML required (pip3 install pyyaml)")

ROLE_OF = {"schema": "SCHEMA", "prompt": "PROMPT", "code": "PROMPT",
           "run_example": "OUTPUT", "asset": "OUTPUT", "note": "CONTEXT"}
CODE_DISPLAY = {"full", "pointer"}
ROLE_RANK = {"SCHEMA": 0, "PROMPT": 1, "OUTPUT": 2, "CONTEXT": 3}
MEDIA = {"FILE", "CODE", "CHAT", "SCREEN"}
IMAGE_MIME = {".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
              ".gif": "image/gif", ".svg": "image/svg+xml", ".webp": "image/webp"}
CODE_EXT = {".json", ".yaml", ".yml", ".ts", ".js", ".py", ".sql", ".sh", ".toml"}


ID_RE = re.compile(r"^[A-Za-z0-9_-]+$")  # ids reach querySelector strings in the template


class CanvasError(Exception):
    """Any spec/content problem that must stop the render."""


def _fail(msg):
    raise CanvasError(msg)


def load_canvas(path: Path) -> dict:
    if not path.is_file():
        _fail(f"canvas spec not found: {path}")
    try:
        spec = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as e:
        _fail(f"canvas.yaml is not valid YAML: {e}")
    if not isinstance(spec, dict):
        _fail("canvas.yaml: top level must be a mapping")
    for key in ("pipeline", "title", "stages"):
        if key not in spec:
            _fail(f"canvas.yaml: missing required key '{key}'")
    stages = spec["stages"]
    if not isinstance(stages, list) or not stages:
        _fail("canvas.yaml: 'stages' must be a non-empty list")
    seen = set()
    for i, st in enumerate(stages):
        if not isinstance(st, dict):
            _fail(f"stages[{i}]: must be a mapping")
        for key in ("id", "title"):
            if key not in st:
                _fail(f"stages[{i}]: missing '{key}'")
        if not isinstance(st["id"], str) or not ID_RE.match(st["id"]):
            _fail(f"stages[{i}]: id {st['id']!r} must match [A-Za-z0-9_-]+")
        if st["id"] in seen:
            _fail(f"duplicate stage id '{st['id']}'")
        seen.add(st["id"])
        atts = st.get("attachments") or []
        if not isinstance(atts, list):
            _fail(f"stage '{st['id']}': 'attachments' must be a list")
        for j, att in enumerate(atts):
            if not isinstance(att, dict):
                _fail(f"stage '{st['id']}' attachments[{j}]: must be a mapping")
            t = att.get("type")
            if t not in ROLE_OF:
                _fail(f"stage '{st['id']}' attachments[{j}]: unknown type '{t}' "
                      f"(expected one of {sorted(ROLE_OF)})")
            if t == "note":
                if "text" not in att:
                    _fail(f"stage '{st['id']}' attachments[{j}]: note requires 'text'")
            elif "file" not in att:
                _fail(f"stage '{st['id']}' attachments[{j}]: type '{t}' requires 'file'")
            v = att.get("variables")
            if v is not None and not isinstance(v, dict):
                _fail(f"stage '{st['id']}' attachments[{j}]: 'variables' must be a mapping")
            d = att.get("display")
            if d is not None and d not in CODE_DISPLAY:
                _fail(f"stage '{st['id']}' attachments[{j}]: display '{d}' "
                      f"not in {sorted(CODE_DISPLAY)}")
            m = att.get("medium")
            if m is not None and m not in MEDIA:
                _fail(f"stage '{st['id']}' attachments[{j}]: medium '{m}' "
                      f"not in {sorted(MEDIA)}")
    sources = spec.get("sources") or []
    if not isinstance(sources, list):
        _fail("canvas.yaml: 'sources' must be a list")
    src_ids = set()
    for k, src in enumerate(sources):
        if not isinstance(src, dict):
            _fail(f"sources[{k}]: must be a mapping")
        for key in ("id", "title"):
            if key not in src:
                _fail(f"sources[{k}]: missing '{key}'")
        if not isinstance(src["id"], str) or not ID_RE.match(src["id"]):
            _fail(f"sources[{k}]: id {src['id']!r} must match [A-Za-z0-9_-]+")
        if src["id"] in src_ids:
            _fail(f"duplicate source id '{src['id']}'")
        src_ids.add(src["id"])
        m = src.get("medium")
        if m is not None and m not in MEDIA:
            _fail(f"sources[{k}]: medium '{m}' not in {sorted(MEDIA)}")
    consumed = set()
    for st in stages:
        inputs = st.get("inputs") or []
        if not isinstance(inputs, list):
            _fail(f"stage '{st['id']}': 'inputs' must be a list")
        for sid in inputs:
            if sid not in src_ids:
                _fail(f"stage '{st['id']}': unknown source id '{sid}'")
            consumed.add(sid)
    for sid in sorted(src_ids - consumed):
        _fail(f"source '{sid}' is consumed by no stage — drop it or wire an 'inputs'")
    traces = spec.get("traces") or []
    if not isinstance(traces, list):
        _fail("canvas.yaml: 'traces' must be a list")
    trace_ids = set()
    for k, tr in enumerate(traces):
        if not isinstance(tr, dict):
            _fail(f"traces[{k}]: must be a mapping")
        for key in ("id", "label", "steps"):
            if key not in tr:
                _fail(f"traces[{k}]: missing '{key}'")
        if not isinstance(tr["id"], str) or not ID_RE.match(tr["id"]):
            _fail(f"traces[{k}]: id {tr['id']!r} must match [A-Za-z0-9_-]+")
        if tr["id"] in trace_ids:
            _fail(f"duplicate trace id '{tr['id']}'")
        trace_ids.add(tr["id"])
        if not isinstance(tr["steps"], list) or not tr["steps"]:
            _fail(f"trace '{tr['id']}': needs at least one step")
        for m_, step in enumerate(tr["steps"]):
            if not isinstance(step, dict):
                _fail(f"trace '{tr['id']}' steps[{m_}]: must be a mapping")
            if "file" not in step:
                _fail(f"trace '{tr['id']}' steps[{m_}]: missing 'file'")
            has_stage, has_source = "stage" in step, "source" in step
            if has_stage == has_source:
                _fail(f"trace '{tr['id']}' steps[{m_}]: exactly one of "
                      f"'stage' or 'source' required")
            if has_stage and step["stage"] not in seen:
                _fail(f"trace '{tr['id']}': unknown stage id '{step['stage']}'")
            if has_source and step["source"] not in src_ids:
                _fail(f"trace '{tr['id']}': unknown source id '{step['source']}'")
    lanes = spec.get("lanes") or []
    if not isinstance(lanes, list):
        _fail("canvas.yaml: 'lanes' must be a list")
    for k, lane in enumerate(lanes):
        if not isinstance(lane, dict):
            _fail(f"lanes[{k}]: must be a mapping")
        for key in ("id", "label", "stages"):
            if key not in lane:
                _fail(f"lanes[{k}]: missing '{key}'")
        if not isinstance(lane["id"], str) or not ID_RE.match(lane["id"]):
            _fail(f"lanes[{k}]: id {lane['id']!r} must match [A-Za-z0-9_-]+")
        if not isinstance(lane["stages"], list):
            _fail(f"lane '{lane['id']}': 'stages' must be a list")
        for sid in lane["stages"]:
            if sid not in seen:
                _fail(f"lane '{lane['id']}': unknown stage id '{sid}'")
    return spec


def _read_text(path: Path) -> str:
    if not path.is_file():
        _fail(f"referenced file not found: {path}")
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        _fail(f"referenced file is not UTF-8 text: {path}")
    except OSError as e:
        _fail(f"referenced file unreadable: {path} ({e})")


def _read_bytes(path: Path) -> bytes:
    if not path.is_file():
        _fail(f"referenced file not found: {path}")
    try:
        return path.read_bytes()
    except OSError as e:
        _fail(f"referenced file unreadable: {path} ({e})")


def _content_html(path: Path) -> str:
    """One file -> safe HTML block. Images inline as data URIs; code gets mono;
    everything else gets the legible prose treatment."""
    ext = path.suffix.lower()
    if ext in IMAGE_MIME:
        data = base64.b64encode(_read_bytes(path)).decode("ascii")
        return f'<img class="content-img" src="data:{IMAGE_MIME[ext]};base64,{data}">'
    cls = "content-code" if ext in CODE_EXT else "content-prose"
    return f'<pre class="{cls}">{html.escape(_read_text(path))}</pre>'


def _inject(prompt_text: str, variables: dict, root: Path) -> str:
    # Resolve first, substitute in ONE pass over the original text — placeholders
    # inside injected content must never themselves be substituted.
    resolved = {}
    for name, val in variables.items():
        placeholder = "{{" + name + "}}"
        if placeholder not in prompt_text:
            _fail(f"prompt has no placeholder {placeholder}")
        if isinstance(val, dict) and "text" in val:
            resolved[name] = str(val["text"])
        else:
            resolved[name] = _read_text(root / str(val))
    return re.sub(r"\{\{([^{}]+)\}\}",
                  lambda m: resolved.get(m.group(1), m.group(0)), prompt_text)


def _views_for(att: dict, root: Path) -> list:
    t = att["type"]
    if t == "note":
        body = f'<pre class="content-prose">{html.escape(str(att["text"]))}</pre>'
        return [{"id": "note", "label": "NOTE", "html": body}]
    path = root / att["file"]
    if t == "schema":
        views = [{"id": "schema", "label": "SCHEMA", "html": _content_html(path)}]
        if att.get("example"):
            views.append({"id": "filled", "label": "FILLED EXAMPLE",
                          "html": _content_html(root / att["example"])})
        return views
    if t == "prompt":
        views = [{"id": "bare", "label": "BARE", "html": _content_html(path)}]
        if att.get("variables"):
            injected = _inject(_read_text(path), att["variables"], root)
            views.append({"id": "injected", "label": "INJECTED",
                          "html": f'<pre class="content-prose">{html.escape(injected)}</pre>'})
        return views
    if t == "code":
        text = _read_text(path)  # pointer mode still validates the file exists
        if att.get("display") == "pointer":
            n = len(text.splitlines())
            body = (f'<div class="content-pointer">{html.escape(str(att["file"]))}'
                    f' &middot; {n} lines</div>')
        else:
            body = f'<pre class="content-code">{html.escape(text)}</pre>'
        views = [{"id": "code", "label": "CODE", "html": body}]
        if att.get("example"):
            views.append({"id": "example", "label": "EXAMPLE",
                          "html": _content_html(root / att["example"])})
        return views
    # run_example / asset
    return [{"id": "content", "label": "CONTENT", "html": _content_html(path)}]


def _box_label(att: dict) -> str:
    if att.get("label"):
        return str(att["label"])
    if att["type"] == "note":
        return "NOTE"
    return Path(att["file"]).name


def build_data(spec: dict, root: Path) -> dict:
    stages = []
    for st in spec["stages"]:
        boxes = []
        for att in st.get("attachments") or []:
            boxes.append({
                "role": ROLE_OF[att["type"]],
                "type": att["type"],
                "label": _box_label(att),
                "medium": att.get("medium"),
                "views": _views_for(att, root),
            })
        boxes.sort(key=lambda b: ROLE_RANK[b["role"]])  # sort() is stable
        stages.append({"id": st["id"], "title": st["title"],
                       "description": st.get("description", ""),
                       "inputs": list(st.get("inputs") or []), "boxes": boxes})
    sources = [{"id": s["id"], "title": s["title"],
                "description": s.get("description", ""), "medium": s.get("medium")}
               for s in spec.get("sources") or []]
    traces = []
    for tr in spec.get("traces") or []:
        steps = [{"stage": step.get("stage"), "source": step.get("source"),
                  "label": str(step.get("label") or Path(step["file"]).name),
                  "html": _content_html(root / step["file"])}
                 for step in tr["steps"]]
        traces.append({"id": tr["id"], "label": tr["label"], "steps": steps})
    lanes = [{"id": "main", "label": "MAIN", "stages": [s["id"] for s in stages]}]
    for lane in spec.get("lanes") or []:
        lanes.append({"id": lane["id"], "label": lane["label"],
                      "stages": list(lane["stages"])})
    return {"pipeline": spec["pipeline"], "title": spec["title"],
            "sources": sources, "stages": stages, "traces": traces, "lanes": lanes}


def render_html(data: dict, template_path: Path) -> str:
    tpl = _read_text(template_path)
    marker = "/*__DATA__*/null"
    if marker not in tpl:
        _fail(f"template missing data marker: {template_path}")
    # < inside JSON string values is semantically identical to '<' and closes
    # every script-breakout class at once (</script>, <!--<script> double-escape state).
    payload = json.dumps(data, ensure_ascii=False).replace("<", "\\u003c")
    return tpl.replace(marker, payload)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        prog="pipeline-canvas",
        description="Render a canvas.yaml pipeline spec to a self-contained HTML canvas.")
    ap.add_argument("spec", type=Path, help="path to canvas.yaml")
    ap.add_argument("-o", "--out", type=Path,
                    help="output HTML path (default: pipeline-canvas.html beside the spec)")
    ap.add_argument("--check", action="store_true",
                    help="exit 1 if the committed output is stale instead of writing")
    ap.add_argument("--template", type=Path,
                    default=Path(__file__).resolve().parent / "template.html")
    args = ap.parse_args(argv)
    try:
        spec = load_canvas(args.spec)
        root = (args.spec.resolve().parent / spec.get("source_root", ".")).resolve()
        html_out = render_html(build_data(spec, root), args.template)
    except CanvasError as e:
        print(f"pipeline-canvas: {e}", file=sys.stderr)
        return 2
    out = args.out or args.spec.resolve().parent / "pipeline-canvas.html"
    if args.check:
        if not out.is_file():
            print(f"--check: {out} does not exist — run the renderer", file=sys.stderr)
            return 1
        if out.read_text(encoding="utf-8") != html_out:
            print(f"--check: {out} is stale — re-run the renderer", file=sys.stderr)
            return 1
        print("--check: canvas up to date")
        return 0
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html_out, encoding="utf-8")
    print(f"wrote {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
