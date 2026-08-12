import base64
import sys
from pathlib import Path

import pytest
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import render  # noqa: E402


def write_canvas(tmp_path, spec):
    p = tmp_path / "canvas.yaml"
    p.write_text(yaml.safe_dump(spec, sort_keys=False), encoding="utf-8")
    return p


MINIMAL = {
    "pipeline": "demo",
    "title": "Demo",
    "stages": [
        {"id": "a", "title": "Stage A"},
        {"id": "b", "title": "Stage B"},
    ],
}


class TestLoadCanvas:
    def test_minimal_spec_loads(self, tmp_path):
        spec = render.load_canvas(write_canvas(tmp_path, MINIMAL))
        assert spec["pipeline"] == "demo"
        assert [s["id"] for s in spec["stages"]] == ["a", "b"]

    def test_missing_spec_file_raises(self, tmp_path):
        with pytest.raises(render.CanvasError, match="not found"):
            render.load_canvas(tmp_path / "nope.yaml")

    @pytest.mark.parametrize("key", ["pipeline", "title", "stages"])
    def test_missing_required_key_raises(self, tmp_path, key):
        spec = {k: v for k, v in MINIMAL.items() if k != key}
        with pytest.raises(render.CanvasError, match=key):
            render.load_canvas(write_canvas(tmp_path, spec))

    def test_duplicate_stage_id_raises(self, tmp_path):
        spec = dict(MINIMAL, stages=[{"id": "a", "title": "A"}, {"id": "a", "title": "A2"}])
        with pytest.raises(render.CanvasError, match="duplicate stage id"):
            render.load_canvas(write_canvas(tmp_path, spec))

    def test_unknown_attachment_type_raises(self, tmp_path):
        spec = dict(MINIMAL)
        spec["stages"] = [{"id": "a", "title": "A",
                          "attachments": [{"type": "wat", "file": "x.md"}]}]
        with pytest.raises(render.CanvasError, match="unknown type 'wat'"):
            render.load_canvas(write_canvas(tmp_path, spec))

    def test_file_type_requires_file_key(self, tmp_path):
        spec = dict(MINIMAL)
        spec["stages"] = [{"id": "a", "title": "A", "attachments": [{"type": "prompt"}]}]
        with pytest.raises(render.CanvasError, match="requires 'file'"):
            render.load_canvas(write_canvas(tmp_path, spec))

    def test_note_requires_text(self, tmp_path):
        spec = dict(MINIMAL)
        spec["stages"] = [{"id": "a", "title": "A", "attachments": [{"type": "note"}]}]
        with pytest.raises(render.CanvasError, match="requires 'text'"):
            render.load_canvas(write_canvas(tmp_path, spec))

    def test_bad_medium_raises(self, tmp_path):
        spec = dict(MINIMAL)
        spec["stages"] = [{"id": "a", "title": "A",
                          "attachments": [{"type": "prompt", "file": "p.md", "medium": "FAX"}]}]
        with pytest.raises(render.CanvasError, match="medium"):
            render.load_canvas(write_canvas(tmp_path, spec))

    def test_lane_unknown_stage_raises(self, tmp_path):
        spec = dict(MINIMAL, lanes=[{"id": "l1", "label": "L1", "stages": ["a", "zz"]}])
        with pytest.raises(render.CanvasError, match="unknown stage id 'zz'"):
            render.load_canvas(write_canvas(tmp_path, spec))

    def test_lane_missing_key_raises(self, tmp_path):
        spec = dict(MINIMAL, lanes=[{"id": "l1", "stages": ["a"]}])
        with pytest.raises(render.CanvasError, match="label"):
            render.load_canvas(write_canvas(tmp_path, spec))

    @pytest.mark.parametrize("bad_id", ['a"b', "a b", "a<b", ""])
    def test_non_slug_stage_id_raises(self, tmp_path, bad_id):
        spec = dict(MINIMAL, stages=[{"id": bad_id, "title": "A"}])
        with pytest.raises(render.CanvasError, match="must match"):
            render.load_canvas(write_canvas(tmp_path, spec))

    def test_non_slug_lane_id_raises(self, tmp_path):
        spec = dict(MINIMAL, lanes=[{"id": 'l"1', "label": "L", "stages": ["a"]}])
        with pytest.raises(render.CanvasError, match="must match"):
            render.load_canvas(write_canvas(tmp_path, spec))

    def test_non_mapping_attachment_raises(self, tmp_path):
        spec = dict(MINIMAL)
        spec["stages"] = [{"id": "a", "title": "A", "attachments": ["oops"]}]
        with pytest.raises(render.CanvasError, match="must be a mapping"):
            render.load_canvas(write_canvas(tmp_path, spec))

    def test_scalar_lane_stages_raises(self, tmp_path):
        spec = dict(MINIMAL, lanes=[{"id": "l1", "label": "L", "stages": "ab"}])
        with pytest.raises(render.CanvasError, match="must be a list"):
            render.load_canvas(write_canvas(tmp_path, spec))

    def test_scalar_variables_raises(self, tmp_path):
        spec = dict(MINIMAL)
        spec["stages"] = [{"id": "a", "title": "A",
                          "attachments": [{"type": "prompt", "file": "p.md",
                                           "variables": "corpus"}]}]
        with pytest.raises(render.CanvasError, match="'variables' must be a mapping"):
            render.load_canvas(write_canvas(tmp_path, spec))

    def test_source_unknown_input_raises(self, tmp_path):
        spec = dict(MINIMAL, sources=[{"id": "s1", "title": "S1"}])
        spec["stages"] = [{"id": "a", "title": "A", "inputs": ["nope"]},
                          {"id": "b", "title": "B", "inputs": ["s1"]}]
        with pytest.raises(render.CanvasError, match="unknown source id 'nope'"):
            render.load_canvas(write_canvas(tmp_path, spec))

    def test_duplicate_source_id_raises(self, tmp_path):
        spec = dict(MINIMAL,
                    sources=[{"id": "s1", "title": "S1"},
                             {"id": "s1", "title": "S1 again"}],
                    stages=[{"id": "a", "title": "A", "inputs": ["s1"]}])
        with pytest.raises(render.CanvasError, match="duplicate source id"):
            render.load_canvas(write_canvas(tmp_path, spec))

    def test_unconsumed_source_raises(self, tmp_path):
        spec = dict(MINIMAL, sources=[{"id": "s1", "title": "S1"}])
        with pytest.raises(render.CanvasError, match="consumed by no stage"):
            render.load_canvas(write_canvas(tmp_path, spec))

    def test_source_missing_title_raises(self, tmp_path):
        spec = dict(MINIMAL, sources=[{"id": "s1"}],
                    stages=[{"id": "a", "title": "A", "inputs": ["s1"]}])
        with pytest.raises(render.CanvasError, match="title"):
            render.load_canvas(write_canvas(tmp_path, spec))

    def test_trace_unknown_stage_raises(self, tmp_path):
        spec = dict(MINIMAL, traces=[{"id": "t1", "label": "T1",
                                      "steps": [{"stage": "zz", "file": "x.json"}]}])
        with pytest.raises(render.CanvasError, match="unknown stage id 'zz'"):
            render.load_canvas(write_canvas(tmp_path, spec))

    def test_trace_missing_keys_raise(self, tmp_path):
        spec = dict(MINIMAL, traces=[{"id": "t1", "steps": []}])
        with pytest.raises(render.CanvasError, match="label"):
            render.load_canvas(write_canvas(tmp_path, spec))

    def test_trace_empty_steps_raises(self, tmp_path):
        spec = dict(MINIMAL, traces=[{"id": "t1", "label": "T1", "steps": []}])
        with pytest.raises(render.CanvasError, match="at least one step"):
            render.load_canvas(write_canvas(tmp_path, spec))

    def test_trace_source_step_ok(self, tmp_path):
        spec = dict(MINIMAL,
                    sources=[{"id": "hub", "title": "HubSpot"}],
                    stages=[{"id": "a", "title": "A", "inputs": ["hub"]}],
                    traces=[{"id": "t1", "label": "T1",
                             "steps": [{"source": "hub", "file": "x.json"}]}])
        render.load_canvas(write_canvas(tmp_path, spec))  # no raise

    def test_trace_unknown_source_raises(self, tmp_path):
        spec = dict(MINIMAL, traces=[{"id": "t1", "label": "T1",
                                      "steps": [{"source": "nope", "file": "x.json"}]}])
        with pytest.raises(render.CanvasError, match="unknown source id 'nope'"):
            render.load_canvas(write_canvas(tmp_path, spec))

    def test_trace_step_stage_and_source_raises(self, tmp_path):
        spec = dict(MINIMAL,
                    sources=[{"id": "hub", "title": "H"}],
                    stages=[{"id": "a", "title": "A", "inputs": ["hub"]}],
                    traces=[{"id": "t1", "label": "T1",
                             "steps": [{"stage": "a", "source": "hub", "file": "x"}]}])
        with pytest.raises(render.CanvasError, match="exactly one"):
            render.load_canvas(write_canvas(tmp_path, spec))

    def test_duplicate_trace_id_raises(self, tmp_path):
        t = {"id": "t1", "label": "T1", "steps": [{"stage": "a", "file": "x.json"}]}
        spec = dict(MINIMAL, traces=[t, dict(t)])
        with pytest.raises(render.CanvasError, match="duplicate trace id"):
            render.load_canvas(write_canvas(tmp_path, spec))

    def test_code_bad_display_raises(self, tmp_path):
        spec = dict(MINIMAL)
        spec["stages"] = [{"id": "a", "title": "A",
                          "attachments": [{"type": "code", "file": "x.py",
                                           "display": "tiny"}]}]
        with pytest.raises(render.CanvasError, match="display"):
            render.load_canvas(write_canvas(tmp_path, spec))


def make_pipeline(tmp_path):
    """A tiny on-disk pipeline: prompt with a variable, schema + example, run, note."""
    (tmp_path / "prompts").mkdir()
    (tmp_path / "schemas").mkdir()
    (tmp_path / "runs").mkdir()
    (tmp_path / "prompts" / "p.md").write_text(
        "Summarize {{corpus}} carefully.\n<script>not code</script>", encoding="utf-8")
    (tmp_path / "prompts" / "corpus.md").write_text("THE CORPUS BODY", encoding="utf-8")
    (tmp_path / "schemas" / "s.json").write_text('{"a": 1}', encoding="utf-8")
    (tmp_path / "runs" / "filled.json").write_text('{"a": 99}', encoding="utf-8")
    (tmp_path / "runs" / "out.md").write_text("run output", encoding="utf-8")
    # 1x1 px gif is enough for a data-URI test
    (tmp_path / "runs" / "pic.gif").write_bytes(
        base64.b64decode("R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7"))
    spec = {
        "pipeline": "demo", "title": "Demo",
        "stages": [{
            "id": "a", "title": "Stage A", "description": "does things",
            "attachments": [
                {"type": "note", "text": "sink me", "label": "HOUSE RULE"},
                {"type": "run_example", "file": "runs/out.md"},
                {"type": "prompt", "file": "prompts/p.md",
                 "variables": {"corpus": "prompts/corpus.md"}, "medium": "CHAT"},
                {"type": "schema", "file": "schemas/s.json", "example": "runs/filled.json"},
                {"type": "asset", "file": "runs/pic.gif"},
            ],
        }],
        "lanes": [{"id": "fast", "label": "FAST", "stages": ["a"]}],
    }
    return spec


class TestBuildData:
    def test_roles_sorted_schema_prompt_output_context(self, tmp_path):
        data = render.build_data(make_pipeline(tmp_path), tmp_path)
        roles = [b["role"] for b in data["stages"][0]["boxes"]]
        assert roles == ["SCHEMA", "PROMPT", "OUTPUT", "OUTPUT", "CONTEXT"]

    def test_prompt_verbatim_and_escaped(self, tmp_path):
        data = render.build_data(make_pipeline(tmp_path), tmp_path)
        prompt = next(b for b in data["stages"][0]["boxes"] if b["role"] == "PROMPT")
        bare = next(v for v in prompt["views"] if v["id"] == "bare")
        assert "Summarize {{corpus}} carefully." in bare["html"]
        assert "&lt;script&gt;" in bare["html"] and "<script>" not in bare["html"]

    def test_prompt_injected_view(self, tmp_path):
        data = render.build_data(make_pipeline(tmp_path), tmp_path)
        prompt = next(b for b in data["stages"][0]["boxes"] if b["role"] == "PROMPT")
        injected = next(v for v in prompt["views"] if v["id"] == "injected")
        assert "THE CORPUS BODY" in injected["html"]
        assert "{{corpus}}" not in injected["html"]

    def test_injected_literal_variable(self, tmp_path):
        spec = make_pipeline(tmp_path)
        spec["stages"][0]["attachments"][2]["variables"] = {"corpus": {"text": "LITERAL"}}
        data = render.build_data(spec, tmp_path)
        prompt = next(b for b in data["stages"][0]["boxes"] if b["role"] == "PROMPT")
        injected = next(v for v in prompt["views"] if v["id"] == "injected")
        assert "LITERAL" in injected["html"]

    def test_missing_placeholder_raises(self, tmp_path):
        spec = make_pipeline(tmp_path)
        spec["stages"][0]["attachments"][2]["variables"] = {"nope": "prompts/corpus.md"}
        with pytest.raises(render.CanvasError, match="no placeholder"):
            render.build_data(spec, tmp_path)

    def test_schema_filled_toggle(self, tmp_path):
        data = render.build_data(make_pipeline(tmp_path), tmp_path)
        schema = next(b for b in data["stages"][0]["boxes"] if b["role"] == "SCHEMA")
        assert [v["id"] for v in schema["views"]] == ["schema", "filled"]
        assert "99" in schema["views"][1]["html"]

    def test_image_becomes_data_uri(self, tmp_path):
        data = render.build_data(make_pipeline(tmp_path), tmp_path)
        img = [b for b in data["stages"][0]["boxes"] if b["type"] == "asset"][0]
        assert 'src="data:image/gif;base64,' in img["views"][0]["html"]

    def test_missing_file_hard_error(self, tmp_path):
        spec = make_pipeline(tmp_path)
        spec["stages"][0]["attachments"][1]["file"] = "runs/GONE.md"
        with pytest.raises(render.CanvasError, match="GONE.md"):
            render.build_data(spec, tmp_path)

    def test_non_utf8_file_hard_error(self, tmp_path):
        spec = make_pipeline(tmp_path)
        (tmp_path / "runs" / "binary.md").write_bytes(b"\xff\xfe\x00binary")
        spec["stages"][0]["attachments"][1]["file"] = "runs/binary.md"
        with pytest.raises(render.CanvasError, match="not UTF-8"):
            render.build_data(spec, tmp_path)

    def test_code_full_renders_mono_in_producer_slot(self, tmp_path):
        spec = make_pipeline(tmp_path)
        (tmp_path / "resolve.py").write_text("def resolve():\n    return 1\n", encoding="utf-8")
        spec["stages"][0]["attachments"].append({"type": "code", "file": "resolve.py"})
        data = render.build_data(spec, tmp_path)
        code = next(b for b in data["stages"][0]["boxes"] if b["type"] == "code")
        assert code["role"] == "PROMPT"
        assert "def resolve():" in code["views"][0]["html"]
        assert 'class="content-code"' in code["views"][0]["html"]

    def test_code_pointer_shows_path_not_content(self, tmp_path):
        spec = make_pipeline(tmp_path)
        (tmp_path / "resolve.py").write_text("def resolve():\n    return 1\n", encoding="utf-8")
        spec["stages"][0]["attachments"].append(
            {"type": "code", "file": "resolve.py", "display": "pointer"})
        data = render.build_data(spec, tmp_path)
        code = next(b for b in data["stages"][0]["boxes"] if b["type"] == "code")
        html_ = code["views"][0]["html"]
        assert "resolve.py" in html_ and "2 lines" in html_
        assert "def resolve():" not in html_

    def test_code_pointer_still_requires_file_to_exist(self, tmp_path):
        spec = make_pipeline(tmp_path)
        spec["stages"][0]["attachments"].append(
            {"type": "code", "file": "GONE.py", "display": "pointer"})
        with pytest.raises(render.CanvasError, match="GONE.py"):
            render.build_data(spec, tmp_path)

    def test_code_example_toggle(self, tmp_path):
        spec = make_pipeline(tmp_path)
        (tmp_path / "resolve.py").write_text("def resolve(): ...\n", encoding="utf-8")
        (tmp_path / "captured.md").write_text("THE ASSEMBLED PROMPT", encoding="utf-8")
        spec["stages"][0]["attachments"].append(
            {"type": "code", "file": "resolve.py", "display": "pointer",
             "example": "captured.md"})
        data = render.build_data(spec, tmp_path)
        code = next(b for b in data["stages"][0]["boxes"] if b["type"] == "code")
        assert [v["id"] for v in code["views"]] == ["code", "example"]
        assert "THE ASSEMBLED PROMPT" in code["views"][1]["html"]

    def test_sources_and_inputs_in_data(self, tmp_path):
        spec = make_pipeline(tmp_path)
        spec["sources"] = [{"id": "hub", "title": "HubSpot", "medium": "FILE",
                            "description": "697 events"}]
        spec["stages"][0]["inputs"] = ["hub"]
        data = render.build_data(spec, tmp_path)
        assert data["sources"] == [{"id": "hub", "title": "HubSpot",
                                    "description": "697 events", "medium": "FILE"}]
        assert data["stages"][0]["inputs"] == ["hub"]

    def test_no_sources_key_yields_empty(self, tmp_path):
        data = render.build_data(make_pipeline(tmp_path), tmp_path)
        assert data["sources"] == []
        assert data["stages"][0]["inputs"] == []
        assert data["traces"] == []

    def test_trace_content_resolved(self, tmp_path):
        spec = make_pipeline(tmp_path)
        (tmp_path / "trace-step.json").write_text('{"venue": "Acme"}', encoding="utf-8")
        spec["traces"] = [{"id": "t1", "label": "TRACE: T1",
                           "steps": [{"stage": "a", "file": "trace-step.json",
                                      "label": "resolved row"}]}]
        data = render.build_data(spec, tmp_path)
        trace = data["traces"][0]
        assert trace["id"] == "t1" and trace["label"] == "TRACE: T1"
        step = trace["steps"][0]
        assert step["stage"] == "a" and step["label"] == "resolved row"
        assert "Acme" in step["html"]

    def test_trace_missing_file_hard_error(self, tmp_path):
        spec = make_pipeline(tmp_path)
        spec["traces"] = [{"id": "t1", "label": "T1",
                           "steps": [{"stage": "a", "file": "GONE.json"}]}]
        with pytest.raises(render.CanvasError, match="GONE.json"):
            render.build_data(spec, tmp_path)

    def test_trace_step_label_defaults_to_basename(self, tmp_path):
        spec = make_pipeline(tmp_path)
        (tmp_path / "step.json").write_text("{}", encoding="utf-8")
        spec["traces"] = [{"id": "t1", "label": "T1",
                           "steps": [{"stage": "a", "file": "step.json"}]}]
        data = render.build_data(spec, tmp_path)
        assert data["traces"][0]["steps"][0]["label"] == "step.json"

    def test_injected_content_placeholders_not_resubstituted(self, tmp_path):
        # Var A's file content containing {{b}} must stay literal — the INJECTED
        # view shows what the real pipeline would run.
        spec = make_pipeline(tmp_path)
        (tmp_path / "prompts" / "p.md").write_text("A={{a}} B={{b}}", encoding="utf-8")
        (tmp_path / "prompts" / "a.md").write_text("has {{b}} inside", encoding="utf-8")
        spec["stages"][0]["attachments"][2]["variables"] = {
            "a": "prompts/a.md", "b": {"text": "BEE"}}
        data = render.build_data(spec, tmp_path)
        prompt = next(b for b in data["stages"][0]["boxes"] if b["role"] == "PROMPT")
        injected = next(v for v in prompt["views"] if v["id"] == "injected")
        assert "has {{b}} inside" in injected["html"]
        assert "B=BEE" in injected["html"]

    def test_main_lane_implicit_and_first(self, tmp_path):
        data = render.build_data(make_pipeline(tmp_path), tmp_path)
        assert data["lanes"][0] == {"id": "main", "label": "MAIN", "stages": ["a"]}
        assert data["lanes"][1]["id"] == "fast"

    def test_note_label_and_medium_default(self, tmp_path):
        data = render.build_data(make_pipeline(tmp_path), tmp_path)
        note = next(b for b in data["stages"][0]["boxes"] if b["role"] == "CONTEXT")
        assert note["label"] == "HOUSE RULE"
        assert note["medium"] is None


TEMPLATE = Path(__file__).resolve().parents[1] / "template.html"


class TestRenderHtmlAndCli:
    def test_output_is_self_contained_and_verbatim(self, tmp_path):
        spec = make_pipeline(tmp_path)
        data = render.build_data(spec, tmp_path)
        out = render.render_html(data, TEMPLATE)
        assert out.startswith("<!DOCTYPE html>")
        assert "/*__DATA__*/null" not in out
        assert "Summarize {{corpus}} carefully." in out

    def test_payload_cannot_break_script_tag(self, tmp_path):
        # No raw '<' may survive in the payload at all — that closes every
        # script-breakout class (</script>, and the <!--<script> double-escaped
        # parser state that blanks the whole canvas).
        spec = make_pipeline(tmp_path)
        spec["title"] = 'x <!--<script> y'
        data = render.build_data(spec, tmp_path)
        out = render.render_html(data, TEMPLATE)
        payload = out.split("const CANVAS_DATA = ", 1)[1].split(";\n", 1)[0]
        assert "<" not in payload
        assert "\\u003c" in payload

    def test_deterministic(self, tmp_path):
        spec = make_pipeline(tmp_path)
        a = render.render_html(render.build_data(spec, tmp_path), TEMPLATE)
        b = render.render_html(render.build_data(spec, tmp_path), TEMPLATE)
        assert a == b

    def _write_full_pipeline(self, tmp_path):
        spec = make_pipeline(tmp_path)
        p = tmp_path / "canvas.yaml"
        p.write_text(yaml.safe_dump(spec, sort_keys=False), encoding="utf-8")
        return p

    def test_cli_writes_default_output(self, tmp_path, capsys):
        p = self._write_full_pipeline(tmp_path)
        assert render.main([str(p)]) == 0
        assert (tmp_path / "pipeline-canvas.html").is_file()

    def test_cli_check_clean_then_stale(self, tmp_path):
        p = self._write_full_pipeline(tmp_path)
        assert render.main([str(p)]) == 0
        assert render.main([str(p), "--check"]) == 0
        (tmp_path / "runs" / "out.md").write_text("CHANGED", encoding="utf-8")
        assert render.main([str(p), "--check"]) == 1

    def test_cli_check_missing_output(self, tmp_path):
        p = self._write_full_pipeline(tmp_path)
        assert render.main([str(p), "--check"]) == 1

    def test_cli_spec_error_exits_2(self, tmp_path, capsys):
        bad = tmp_path / "canvas.yaml"
        bad.write_text("pipeline: x\n", encoding="utf-8")
        assert render.main([str(bad)]) == 2
        assert "missing required key" in capsys.readouterr().err
