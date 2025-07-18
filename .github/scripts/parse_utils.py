import json
from typing import Callable, List, Tuple, Dict


def chunk_diff(
    diff_text: str,
    count_tokens: Callable[[str], int],
    max_prompt_tokens: int,
    base_tokens: int,
) -> List[Tuple[str, int]]:
    """Split a diff into token-safe chunks while tracking starting line numbers."""
    lines = diff_text.splitlines(keepends=True)
    chunks: List[Tuple[str, int]] = []
    current: List[str] = []
    tokens = base_tokens
    current_start = 1
    for i, line in enumerate(lines, 1):
        lt = count_tokens(line)
        if tokens + lt > max_prompt_tokens and current:
            chunks.append(("".join(current), current_start))
            current = [line]
            current_start = i
            tokens = base_tokens + lt
        else:
            current.append(line)
            tokens += lt
    if current:
        chunks.append(("".join(current), current_start))
    return chunks


def parse_review_chunk(content: str, chunk_start: int) -> List[Dict]:
    """Parse LLM JSON output adjusting line numbers based on chunk start.

    Raises ``ValueError`` if the parsed data is not in the expected format.
    """
    data = json.loads(content)
    if not isinstance(data, list):
        raise ValueError("LLM output must be a JSON list")

    for comment in data:
        if not isinstance(comment, dict):
            raise ValueError("Each review entry must be a JSON object")

        if "line" not in comment or not isinstance(comment["line"], int):
            raise ValueError("Review entry missing integer 'line' field")

        comment["line"] += chunk_start - 1

    return data


def diff_line_positions(diff_text: str) -> Dict[int, Tuple[str, int]]:
    """Map global diff line numbers to per-file patch positions.

    Returns a dictionary mapping the line index in ``diff_text`` (1-based)
    to a tuple ``(file_path, position)`` where ``position`` is the line's
    position within that file's patch as expected by GitHub.

    The ``position`` value used by the GitHub API does **not** include the
    hunk header (``@@``) lines. Positions start from ``1`` for the first
    actual line in a hunk.
    """

    mapping: Dict[int, Tuple[str, int]] = {}
    current_file = None
    position = 0
    in_hunk = False

    for idx, line in enumerate(diff_text.splitlines(), 1):
        if line.startswith("diff --git "):
            current_file = None
            position = 0
            in_hunk = False
            continue
        if line.startswith("+++ b/"):
            current_file = line[6:]
            position = 0
            in_hunk = False
            continue
        if line.startswith("--- "):
            continue
        if line.startswith("@@"):
            in_hunk = True
            continue

        if current_file and in_hunk:
            position += 1
            mapping[idx] = (current_file, position)

    return mapping
