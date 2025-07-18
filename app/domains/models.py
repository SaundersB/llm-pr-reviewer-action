from dataclasses import dataclass
from typing import List

@dataclass
class DiffChunk:
    text: str
    start_line: int

@dataclass
class ReviewComment:
    file: str
    line: int
    domain: str
    comment: str
