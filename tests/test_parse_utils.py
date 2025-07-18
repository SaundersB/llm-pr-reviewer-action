import json
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '.github', 'scripts'))
from parse_utils import chunk_diff, parse_review_chunk

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


def test_parse_review_chunk_offsets_lines():
    content = json.dumps([
        {"file": "a.py", "line": 2, "domain": "bug", "comment": "fix"}
    ])
    parsed = parse_review_chunk(content, 5)
    assert parsed[0]["line"] == 6
