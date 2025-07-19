"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.chunkDiff = chunkDiff;
exports.mapLinePositions = mapLinePositions;
exports.matchLineToPosition = matchLineToPosition;
function chunkDiff(diff, countTokens, maxTokens, baseTokens) {
    const lines = diff.split(/\r?\n/);
    const chunks = [];
    let buffer = '';
    let startLine = 0;
    lines.forEach((line, i) => {
        if (countTokens(buffer + line) + baseTokens > maxTokens) {
            chunks.push({ text: buffer, start: startLine });
            buffer = line + '\n';
            startLine = i + 1;
        }
        else {
            buffer += line + '\n';
        }
    });
    if (buffer) {
        chunks.push({ text: buffer, start: startLine });
    }
    return chunks;
}
function mapLinePositions(diffText) {
    const mapping = new Map();
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
function matchLineToPosition(map, file, line) {
    return map.get(`${file}:${line}`);
}
