import json
from pathlib import Path

import pytest

from domain.segmentation import align, reconstruct, segment, segment_by_separators

CASES = json.loads(
    (Path(__file__).parents[2] / "frontend" / "src" / "segmentation_cases.json").read_text(
        encoding="utf-8"
    )
)["cases"]


@pytest.mark.parametrize("case", CASES, ids=lambda case: case["name"])
def test_segmentation_conformance(case):
    parts = segment(case["text"], tuple(case["start"]), tuple(case["end"]))
    segments = [part.segment for part in parts if part.is_segment]
    assert [
        {
            "text": s.text,
            "body": s.body,
            "start_line": s.start_line,
            "end_line": s.end_line,
        }
        for s in segments
    ] == case["segments"]
    assert reconstruct(parts) == case["reconstructed"]


def test_reconstruct_without_edit_matches_original():
    text = "HEAD\n<d>\nA\n</d>\nFOOT"
    assert reconstruct(segment(text, ("^<d>",), ("^</d>",))) == text


def test_align_pairs_by_order_and_marks_unpaired():
    original = segment("<d>\nA\n</d>\n<d>\nB\n</d>", ("^<d>",), ("^</d>",))
    translated = segment("<d>\nA'\n</d>", ("^<d>",), ("^</d>",))
    pairs = align(original, translated)
    assert len(pairs) == 2
    assert pairs[0].original is not None and pairs[0].translated is not None
    assert pairs[1].original is not None and pairs[1].translated is None


def test_segment_by_separators_yields_blocks():
    text = "[h]\nナレーション\n!***!\n<V0000>oi\n!***!\n[h2]\nNome\n!***!\n<V0010>tchau\n!***!"
    parts = segment_by_separators(text, (r"^\[.+\]$", r"^!.*!$"))
    bodies = [part.segment.body for part in parts if part.is_segment]
    assert bodies == ["ナレーション", "<V0000>oi", "Nome", "<V0010>tchau"]
    assert reconstruct(parts) == text
