import difflib

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

def map_line_positions(diff):
    mapping = {}
    current_file = None
    new_line = None
    position = 0

    for line in diff.splitlines():
        position += 1
        if line.startswith('+++ b/'):
            current_file = line[6:]
            new_line = None
        elif line.startswith('@@'):
            parts = line.split(' ')
            new_line = int(parts[2].split(',')[0].replace('+', ''))
        elif line.startswith('+') and current_file:
            mapping[(current_file, new_line)] = position
            new_line += 1
        elif not line.startswith('-') and current_file:
            new_line += 1
    return mapping

def match_line_to_position(line_map, file, line):
    return line_map.get((file, line))
