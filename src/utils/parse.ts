import { ReviewComment } from '../domains/models';

export function parseReviewChunk(content: string, chunkStart: number): ReviewComment[] {
  const raw = JSON.parse(content);
  if (!Array.isArray(raw)) {
    throw new Error('Expected an array of review items');
  }
  const comments: ReviewComment[] = [];
  for (const item of raw) {
    const { file, line, domain, comment } = item || {};
    if (file && line && domain && comment) {
      comments.push({
        file,
        line: Number(line) + chunkStart,
        domain,
        comment,
      });
    }
  }
  return comments;
}
