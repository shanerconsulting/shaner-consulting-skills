"""Golden regression: the fixture pipeline must render byte-identically to the
committed golden file.

To REGOLD after an intentional template/renderer change:
  python3 .claude/skills/pipeline-canvas/render.py \
    .claude/skills/pipeline-canvas/fixtures/demo-pipeline/canvas/canvas.yaml \
    -o .claude/skills/pipeline-canvas/fixtures/golden/pipeline-canvas.html
then open the golden file in a browser, eyeball it, and commit it.
"""
import sys
from pathlib import Path

SKILL = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(SKILL))
import render  # noqa: E402

FIXTURE = SKILL / "fixtures" / "demo-pipeline" / "canvas" / "canvas.yaml"
GOLDEN = SKILL / "fixtures" / "golden" / "pipeline-canvas.html"


def test_fixture_matches_golden(tmp_path):
    out = tmp_path / "out.html"
    assert render.main([str(FIXTURE), "-o", str(out)]) == 0
    assert out.read_text(encoding="utf-8") == GOLDEN.read_text(encoding="utf-8")


def test_golden_passes_check(tmp_path):
    # --check against a fresh copy of the golden proves the drift detector's
    # clean path on real fixture content.
    out = tmp_path / "pipeline-canvas.html"
    out.write_text(GOLDEN.read_text(encoding="utf-8"), encoding="utf-8")
    assert render.main([str(FIXTURE), "-o", str(out), "--check"]) == 0
