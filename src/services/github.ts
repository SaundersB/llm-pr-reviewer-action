import { Config } from '../config';

export async function fetchPrDiff(config: Config): Promise<{pr: any; diff: string; commitSha: string}> {
  const diffUrl = config.event.pull_request.diff_url;
  const commitSha = config.event.pull_request.head.sha;
  const resp = await fetch(diffUrl, {
    headers: { Authorization: `Bearer ${config.token}` },
  });
  const diff = await resp.text();
  return { pr: config.event.pull_request, diff, commitSha };
}

export async function fetchChangedFiles(repo: string, token: string, prNumber: number): Promise<any[]> {
  const url = `https://api.github.com/repos/${repo}/pulls/${prNumber}/files`;
  const resp = await fetch(url, { headers: { Authorization: `Bearer ${token}` } });
  if (!resp.ok) {
    throw new Error(`GitHub API error: ${resp.status} - ${await resp.text()}`);
  }
  return await resp.json();
}

export async function postReview(comments: any[], commitSha: string, prNumber: number, config: Config) {
  if (config.dryRun) {
    console.log('DRY_RUN:', comments);
    return;
  }
  const url = `https://api.github.com/repos/${config.repo}/pulls/${prNumber}/reviews`;
  const payload = {
    commit_id: commitSha,
    event: 'COMMENT',
    body: 'AI-powered review.',
    comments,
  };
  const resp = await fetch(url, {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${config.token}`,
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(payload),
  });
  if (!resp.ok) {
    console.error('Failed to post review', resp.status, await resp.text());
  }
}
