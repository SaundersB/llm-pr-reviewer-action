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

import parse from 'parse-diff';

export function mapLinePositions(diffText: string): Map<string, number> {
  const mapping = new Map<string, number>();
  const files = parse(diffText);
  for (const file of files) {
    let diffLine = 0;
    for (const chunk of file.chunks) {
      for (const change of chunk.changes) {
        diffLine += 1;
        if (change.type === 'add' || change.type === 'normal') {
          mapping.set(`${file.to}:${diffLine}`, diffLine);
        }
      }
    }
  }
  return mapping;
}

export function matchLineToPosition(map: Map<string, number>, file: string, line: number): number | undefined {
  return map.get(`${file}:${line}`);
}
