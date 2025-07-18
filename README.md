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
