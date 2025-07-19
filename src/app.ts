declare const process: any;
import { loadConfig } from './config';
import { processPullRequest } from './services/pr_review';

async function main() {
  const config = loadConfig();
  await processPullRequest(config);
  console.log('✅ PR review completed successfully.');
  if (config.dryRun) {
    console.log('This was a dry run. No comments were posted.');
  } else {
    console.log('Comments posted to the PR successfully.');
  }
}

main().catch(err => {
  console.error('Error:', err);
  process.exit(1);
});
