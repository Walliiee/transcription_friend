from pathlib import Path
import importlib.util


_MODULE_PATH = Path(__file__).resolve().parents[1] / "scripts" / "postprocess.py"
_SPEC = importlib.util.spec_from_file_location("postprocess_module", _MODULE_PATH)
assert _SPEC is not None and _SPEC.loader is not None
_POSTPROCESS = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(_POSTPROCESS)

apply_corrections = _POSTPROCESS.apply_corrections
clean_formatting = _POSTPROCESS.clean_formatting
flag_potential_issues = _POSTPROCESS.flag_potential_issues


def test_apply_corrections_tracks_changes() -> None:
    original = "Gemni is good. Gemni helps."
    corrections = {"Gemni": "Gemini"}

    corrected, changes = apply_corrections(original, corrections)

    assert corrected == "Gemini is good. Gemini helps."
    assert any("Gemni" in c and "2 occurrence" in c for c in changes)


def test_flag_potential_issues_is_case_insensitive() -> None:
    text = "We should Deploy this today."
    flags = ["deploy"]

    issues = flag_potential_issues(text, flags)

    assert len(issues) == 1
    assert "deploy" in issues[0].lower()


def test_clean_formatting_normalizes_spacing_and_newlines() -> None:
    dirty = "[00:00:01]Hello  \n\n\nworld , test ."

    cleaned = clean_formatting(dirty)

    assert "[00:00:01] Hello" in cleaned
    assert "\n\n\n" not in cleaned
    assert "world," in cleaned
    assert "test." in cleaned
