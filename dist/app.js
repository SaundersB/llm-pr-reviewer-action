"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
const config_1 = require("./config");
const pr_review_1 = require("./services/pr_review");
async function main() {
    const config = (0, config_1.loadConfig)();
    await (0, pr_review_1.processPullRequest)(config);
    console.log('✅ PR review completed successfully.');
    if (config.dryRun) {
        console.log('This was a dry run. No comments were posted.');
    }
    else {
        console.log('Comments posted to the PR successfully.');
    }
}
main().catch(err => {
    console.error('Error:', err);
    process.exit(1);
});
