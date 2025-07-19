"use strict";
Object.defineProperty(exports, "__esModule", { value: true });
exports.getReviewComments = getReviewComments;
const token_1 = require("../utils/token");
const parse_1 = require("../utils/parse");
const diff_1 = require("../utils/diff");
async function getReviewComments(diff, config) {
    const promptTemplate = config.customPrompt || defaultPrompt;
    const basePrompt = promptTemplate.replace('{{diff}}', '');
    const baseTokens = (0, token_1.countTokens)(basePrompt);
    const maxPromptTokens = 8192 - config.responseTokens;
    const chunks = (0, diff_1.chunkDiff)(diff, token_1.countTokens, maxPromptTokens, baseTokens);
    const results = [];
    for (const chunk of chunks) {
        const prompt = promptTemplate.replace('{{diff}}', chunk.text);
        if (config.dryRun) {
            console.log('\n--- Prompt ---\n');
            console.log(prompt.slice(0, 1000));
            console.log('\n--- End Prompt ---\n');
            continue;
        }
        try {
            const body = {
                model: config.model,
                messages: [{ role: 'user', content: prompt }],
                max_tokens: config.responseTokens,
            };
            const resp = await fetch('https://api.openai.com/v1/chat/completions', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    Authorization: `Bearer ${config.apiKey}`,
                },
                body: JSON.stringify(body),
            });
            const json = await resp.json();
            const content = json.choices[0].message.content;
            results.push(...(0, parse_1.parseReviewChunk)(content, chunk.start));
        }
        catch (err) {
            console.error('OpenAI error', err);
        }
    }
    return results;
}
const defaultPrompt = `You are a senior software engineer reviewing a GitHub pull request diff.
Return a JSON array where each item contains file, line, domain, and comment.
Here is the diff:
{{diff}}`;
