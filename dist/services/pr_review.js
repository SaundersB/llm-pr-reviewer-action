"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.processPullRequest = processPullRequest;
const github_1 = require("./github");
const openai_1 = require("./openai");
const diff_1 = require("../utils/diff");
async function processPullRequest(config) {
    const { pr, diff, commitSha } = await (0, github_1.fetchPrDiff)(config);
    const lineMap = (0, diff_1.mapLinePositions)(diff);
    const parsedComments = await (0, openai_1.getReviewComments)(diff, config);
    const changedFiles = await (0, github_1.fetchChangedFiles)(config.repo, config.token, pr.number);
    const validFiles = new Set(changedFiles.map(f => f.filename));
    const comments = [];
    for (const entry of parsedComments) {
        if (!validFiles.has(entry.file)) {
            continue;
        }
        const position = (0, diff_1.matchLineToPosition)(lineMap, entry.file, entry.line);
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
        await (0, github_1.postReview)(comments, commitSha, pr.number, config);
    }
}
