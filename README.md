# LLM PR Reviewer GitHub Action

This GitHub Action uses a Large Language Model (like OpenAI's GPT-4) to automatically review pull requests and add code comments.

## Features

- PR diff analysis
- Inline comment suggestions
- LLM-agnostic (OpenAI by default)
- Handles large diffs by chunking them to fit the model context

## Usage

```yaml
- uses: SaundersB/llm-pr-reviewer-action@v1
  with:
    openai_api_key: ${{ secrets.OPENAI_API_KEY }}
```

### Custom Prompt (Optional)

By default, this action uses a deeply technical reviewer prompt designed for secure, scalable software platforms. It incorporates security, performance, and architecture principles from experts such as Robert Martin, Kent Beck, and NIST along with OWASP practices.

You may override it with your own prompt like so:

```yaml
- uses: SaundersB/llm-pr-reviewer-action@v1
  with:
    openai_api_key: ${{ secrets.OPENAI_API_KEY }}
    custom_prompt: |
      You are a junior frontend developer focused on accessibility...
      {{diff}}
```

### Additional Options

You can customize the model and response size or run in dry-run mode via environment variables:

| Variable | Description | Default |
| -------- | ----------- | ------- |
| `OPENAI_MODEL` | Model name used for reviews | `gpt-4` |
| `RESPONSE_TOKENS` | Max tokens returned from the model | `1024` |
| `DRY_RUN` | If `true`, print the review payload instead of posting | `false` |

## Running Locally with `act`

You can execute the workflow locally using [nektos/act](https://github.com/nektos/act). A sample pull request event payload is provided in `.github/pull_request.json`.

```bash
# Install act if you don't already have it
# https://github.com/nektos/act#installation

# Run the review job locally
act -j review -e .github/pull_request.json
```

This will execute the `llm-review.yml` workflow using the payload and print results to your console.
