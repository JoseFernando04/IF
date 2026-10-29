from pathlib import Path

from ifcontent.copy.file_engine import FileEngine
from ifcontent.copy.lint import lint_carousel, lint_reel, repair_reel
from ifcontent.core.models import ReelCopy
from ifcontent.video.timeline import _chunks, build_timeline

EXAMPLES = Path(__file__).resolve().parents[1] / "examples" / "copy"
SETTINGS = {"scene_padding_s": 0.45, "min_scene_s": 2.2, "min_seconds": 15}


def test_examples_pass_lint():
    assert lint_reel(FileEngine(EXAMPLES / "reel-estante-inteligente.yaml").reel("soluciones", "")) == []
    assert lint_carousel(FileEngine(EXAMPLES / "carrusel-senales-inventario.yaml").carousel("tips", "")) == []


def test_lint_detects_tuteo_and_structure():
    copy = ReelCopy.model_validate({
        "title": "t", "hook": "h", "caption": "Escríbenos hoy", "hashtags": [],
        "scenes": [{"layout": "statement", "on_screen": "Hola mundo", "narration": "Si necesitas ayuda"}] * 3,
    })
    issues = " ".join(lint_reel(copy))
    assert "hook" in issues and "cta" in issues and "necesitas" in issues and "escríbenos" in issues
    repaired = repair_reel(copy)
    assert repaired.scenes[0].layout == "hook" and repaired.scenes[-1].layout == "cta"


def test_chunks_are_short():
    chunks = _chunks("Recibís una alerta antes de quedarte sin producto, sabés quién tiene cada activo.")
    assert all(len(c.split()) <= 5 for c in chunks)
    assert " ".join(chunks).startswith("Recibís una alerta")


def test_timeline_without_tts_respects_minimum():
    copy = FileEngine(EXAMPLES / "reel-estante-inteligente.yaml").reel("soluciones", "")
    tl = build_timeline(copy, None, SETTINGS)
    assert tl.duration >= 15
    assert tl.scenes[0].start == 0 and abs(tl.scenes[-1].end - tl.duration) < 0.01
    assert all(a.end <= b.start + 1e-6 for a, b in zip(tl.scenes, tl.scenes[1:]))
