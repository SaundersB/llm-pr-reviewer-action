import { ReviewComment } from '../domains/models';

export function parseReviewChunk(content: string, chunkStart: number): ReviewComment[] {
  let raw: any;
  try {
    raw = JSON.parse(content);
  } catch (err) {
    throw new Error(`Failed to parse LLM output: ${err}\n\nOutput:\n${content}`);
  }
  if (!Array.isArray(raw)) {
    throw new Error('Expected a list of review items');
  }

  const comments: ReviewComment[] = [];
  for (const item of raw) {
    const { file, line, domain, comment } = item ?? {};
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
