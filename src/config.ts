declare const process: any;
declare function require(module: string): any;
const { existsSync, readFileSync } = require('fs');

export interface Config {
  repo: string;
  token: string;
  apiKey: string;
  model: string;
  responseTokens: number;
  dryRun: boolean;
  customPrompt?: string;
  event: any;
}

export function loadConfig(): Config {
  const eventPath = process.env.GITHUB_EVENT_PATH;
  let prEvent: any;
  if (eventPath && existsSync(eventPath)) {
    const content = readFileSync(eventPath, 'utf8');
    prEvent = JSON.parse(content);
  } else {
    const localPath = '.github/pull_request.json';
    const content = readFileSync(localPath, 'utf8');
    prEvent = JSON.parse(content);
  }

  return {
    repo: process.env.GITHUB_REPOSITORY || 'SaundersB/llm-pr-reviewer-action',
    token: process.env.GITHUB_TOKEN || 'test-token',
    apiKey: process.env.OPENAI_API_KEY || 'test-key',
    model: process.env.OPENAI_MODEL || 'gpt-4.1',
    responseTokens: parseInt(process.env.RESPONSE_TOKENS || '1024', 10),
    dryRun: process.env.DRY_RUN === 'true',
    customPrompt: process.env.CUSTOM_PROMPT,
    event: prEvent,
  };
}
