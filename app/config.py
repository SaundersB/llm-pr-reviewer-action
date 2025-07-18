import os, json

def load_config():
    event_path = os.getenv("GITHUB_EVENT_PATH")
    if event_path and os.path.exists(event_path):
        try:
            with open(event_path) as f:
                pr_event = json.load(f)
        except Exception as e:
            raise ValueError(f"Invalid event payload: {e}")
    else:
        # Local fallback using real metadata from PR #9
        pr_event = {
            "action": "opened",
            "number": 9,
            "pull_request": {
                "url": "https://api.github.com/repos/SaundersB/llm-pr-reviewer-action/pulls/9",
                "id": 2010491300,
                "node_id": "PR_kwDOKzqb1c5yQZ4R",
                "html_url": "https://github.com/SaundersB/llm-pr-reviewer-action/pull/9",
                "diff_url": "https://github.com/SaundersB/llm-pr-reviewer-action/pull/9.diff",
                "patch_url": "https://github.com/SaundersB/llm-pr-reviewer-action/pull/9.patch",
                "issue_url": "https://api.github.com/repos/SaundersB/llm-pr-reviewer-action/issues/9",
                "number": 9,
                "state": "open",
                "locked": False,
                "title": "Add explicit model validation",
                "user": {
                    "login": "SaundersB",
                    "id": 123456,
                    "html_url": "https://github.com/SaundersB"
                },
                "body": "Add supported model validation and doc",
                "head": {
                    "label": "SaundersB:codex/define-enum-for-supported-models",
                    "ref": "codex/define-enum-for-supported-models",
                    "sha": "b8ccc0089143ce29b8a28aa49cdd57528aa9392e",
                    "repo": {
                        "full_name": "SaundersB/llm-pr-reviewer-action"
                    }
                },
                "base": {
                    "label": "SaundersB:main",
                    "ref": "main",
                    "sha": "abcdef0123456789abcdef0123456789abcdef01",
                    "repo": {
                        "full_name": "SaundersB/llm-pr-reviewer-action"
                    }
                }
            },
            "repository": {
                "id": 123456789,
                "full_name": "SaundersB/llm-pr-reviewer-action",
                "html_url": "https://github.com/SaundersB/llm-pr-reviewer-action"
            },
            "sender": {
                "login": "SaundersB",
                "id": 123456,
                "html_url": "https://github.com/SaundersB"
            }
        }

    return {
        "repo": os.getenv("GITHUB_REPOSITORY", "SaundersB/llm-pr-reviewer-action"),
        "token": os.getenv("GITHUB_TOKEN", "test-token"),
        "api_key": os.getenv("OPENAI_API_KEY", "test-key"),
        "model": os.getenv("OPENAI_MODEL", "gpt-4.1"),
        "response_tokens": int(os.getenv("RESPONSE_TOKENS", "1024")),
        "dry_run": os.getenv("DRY_RUN", "true") == "true",
        "custom_prompt": os.getenv("CUSTOM_PROMPT"),
        "event": pr_event
    }
