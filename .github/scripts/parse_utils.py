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
    """Parse LLM JSON output adjusting line numbers based on chunk start."""
    data = json.loads(content)
    for comment in data:
        if isinstance(comment.get("line"), int):
            comment["line"] += chunk_start - 1
    return data
