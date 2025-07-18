import json
from domains.models import ReviewComment

def parse_review_chunk(content: str, chunk_start: int) -> list[ReviewComment]:
    try:
        raw_data = json.loads(content)
        if not isinstance(raw_data, list):
            raise ValueError("Expected a list of review items")

        comments = []
        for item in raw_data:
            file = item.get("file")
            line = item.get("line")
            domain = item.get("domain")
            comment = item.get("comment")

            if not all([file, line, domain, comment]):
                continue  # skip malformed entries

            # Lines returned by the LLM are relative to the provided diff chunk.
            # Adjust them back to the absolute diff line numbers using the
            # chunk_start offset.
            absolute_line = int(line) + chunk_start

            comments.append(ReviewComment(
                file=file,
                line=absolute_line,
                domain=domain,
                comment=comment
            ))
        return comments
    except Exception as e:
        raise ValueError(
            f"Failed to parse LLM output: {e}\n\nOutput:\n{content}"
        )
