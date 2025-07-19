import { countTokens } from '../utils/token';
import { parseReviewChunk } from '../utils/parse';
import { chunkDiff } from '../utils/diff';
import { ReviewComment } from '../domains/models';
import { Config } from '../config';

export async function getReviewComments(diff: string, config: Config): Promise<ReviewComment[]> {
  const promptTemplate = config.customPrompt || defaultPrompt;
  const basePrompt = promptTemplate.replace('{{diff}}', '');
  const baseTokens = countTokens(basePrompt);
  const maxPromptTokens = 8192 - config.responseTokens;

  const chunks = chunkDiff(diff, countTokens, maxPromptTokens, baseTokens);
  const results: ReviewComment[] = [];

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
      const content = json.choices[0].message.content as string;
      results.push(...parseReviewChunk(content, chunk.start));
    } catch (err) {
      console.error('OpenAI error', err);
    }
  }
  return results;
}

const defaultPrompt = `You are a senior software engineer reviewing a GitHub pull request diff.
Return a JSON array where each item contains file, line, domain, and comment.
Here is the diff:
{{diff}}`;
