import json
import os
import sys
import pytest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '.github', 'scripts'))
from parse_utils import chunk_diff, parse_review_chunk, diff_line_positions

def simple_count(line: str) -> int:
    return len(line)


def test_chunk_diff_tracks_line_numbers():
    diff_text = """line1\nline2\nline3\nline4\nline5\n"""
    # max_prompt_tokens=20 to group roughly three lines using simple_count
    chunks = chunk_diff(diff_text, simple_count, 20, 0)
    assert chunks == [
        ("line1\nline2\nline3\n", 1),
        ("line4\nline5\n", 4)
    ]


def test_chunk_diff_handles_empty_diff():
    assert chunk_diff("", simple_count, 20, 0) == []


def test_chunk_diff_respects_base_tokens():
    diff_text = "line1\nline2\n"
    # base_tokens=5 should force a single line per chunk when max_prompt_tokens=6
    chunks = chunk_diff(diff_text, simple_count, 6, 5)
    assert chunks == [
        ("line1\n", 1),
        ("line2\n", 2)
    ]


def test_parse_review_chunk_offsets_lines():
    content = json.dumps([
        {"file": "a.py", "line": 2, "domain": "bug", "comment": "fix"}
    ])
    parsed = parse_review_chunk(content, 5)
    assert parsed[0]["line"] == 6


def test_parse_review_chunk_validates_structure():
    content = json.dumps({"file": "a.py"})
    with pytest.raises(ValueError):
        parse_review_chunk(content, 1)


def test_parse_review_chunk_requires_line_int():
    content = json.dumps([{"file": "a.py", "line": "a", "domain": "bug", "comment": "x"}])
    with pytest.raises(ValueError):
        parse_review_chunk(content, 1)


def test_diff_line_positions_maps_files_and_positions():
    diff = (
        "diff --git a/a.py b/a.py\n"
        "--- a/a.py\n"
        "+++ b/a.py\n"
        "@@\n"
        "+added line\n"
        " line1\n"
        "@@\n"
        " line2\n"
    )
    mapping = diff_line_positions(diff)
    assert mapping[4] == ("a.py", 1)
    assert mapping[5] == ("a.py", 2)
    assert mapping[6] == ("a.py", 3)
