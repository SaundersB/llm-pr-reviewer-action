import { fetchPrDiff, fetchChangedFiles, postReview } from './github';
import { getReviewComments } from './openai';
import { mapLinePositions, matchLineToPosition } from '../utils/diff';
import { ReviewComment } from '../domains/models';
import { Config } from '../config';

export async function processPullRequest(config: Config) {
  const { pr, diff, commitSha } = await fetchPrDiff(config);
  const lineMap = mapLinePositions(diff);
  const parsedComments = await getReviewComments(diff, config);
  const changedFiles = await fetchChangedFiles(config.repo, config.token, pr.number);
  const validFiles = new Set(changedFiles.map(f => f.filename));
  const comments: any[] = [];

  for (const entry of parsedComments) {
    if (!validFiles.has(entry.file)) {
      continue;
    }
    const position = matchLineToPosition(lineMap, entry.file, entry.line);
    if (position === undefined) {
      continue;
    }
    comments.push({
      path: entry.file,
      position,
      body: `[${entry.domain.charAt(0).toUpperCase() + entry.domain.slice(1)}] ${entry.comment}`,
    });
  }

  if (comments.length) {
    await postReview(comments, commitSha, pr.number, config);
  }
}
