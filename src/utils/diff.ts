export function chunkDiff(
  diff: string,
  countTokens: (t: string) => number,
  maxTokens: number,
  baseTokens: number
): Array<{text: string; start: number}> {
  const lines = diff.split(/\r?\n/);
  const chunks: Array<{text: string; start: number}> = [];
  let buffer = '';
  let startLine = 0;

  lines.forEach((line, i) => {
    if (countTokens(buffer + line) + baseTokens > maxTokens) {
      chunks.push({ text: buffer, start: startLine });
      buffer = line + '\n';
      startLine = i + 1;
    } else {
      buffer += line + '\n';
    }
  });
  if (buffer) {
    chunks.push({ text: buffer, start: startLine });
  }
  return chunks;
}

export function mapLinePositions(diffText: string): Map<string, number> {
  const mapping = new Map<string, number>();
  const lines = diffText.split(/\r?\n/);
  let file = '';
  let position = 0;
  for (const line of lines) {
    if (line.startsWith('+++ b/')) {
      file = line.slice(6).trim();
      position = 0;
      continue;
    }
    if (line.startsWith('diff --git')) {
      continue;
    }
    if (line.startsWith('@@')) {
      continue;
    }
    position += 1;
    if (line.startsWith('+') || line.startsWith(' ')) {
      mapping.set(`${file}:${position}`, position);
    }
  }
  return mapping;
}

export function matchLineToPosition(map: Map<string, number>, file: string, line: number): number | undefined {
  return map.get(`${file}:${line}`);
}
