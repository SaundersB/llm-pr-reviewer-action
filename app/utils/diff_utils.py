from unidiff import PatchSet

def chunk_diff(diff, count_tokens, max_tokens, base_tokens):
    lines = diff.splitlines(keepends=True)
    chunks = []
    buffer = ""
    start_line = 0

    for i, line in enumerate(lines):
        if count_tokens(buffer + line) + base_tokens > max_tokens:
            chunks.append((buffer, start_line))
            buffer = line
            start_line = i
        else:
            buffer += line

    if buffer:
        chunks.append((buffer, start_line))
    return chunks


def map_line_positions(diff_text):
    mapping = {}  # (filename, new_line) -> diff position
    patch = PatchSet(diff_text)
    for patched_file in patch:
        filename = patched_file.path
        position = 0
        for hunk in patched_file:
            for line in hunk:
                position += 1
                if line.is_added or line.is_context:
                    mapping[(filename, line.target_line_no)] = position
    return mapping

    
def match_line_to_position(line_map, file, line):
    return line_map.get((file, line))
