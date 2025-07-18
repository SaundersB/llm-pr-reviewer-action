import requests

def fetch_pr_diff(config):
    pr_event = config["event"]
    diff_url = pr_event["pull_request"]["diff_url"]
    commit_sha = pr_event["pull_request"]["head"]["sha"]

    headers = {"Authorization": f"Bearer {config['token']}"}
    diff = requests.get(diff_url, headers=headers).text

    return pr_event["pull_request"], diff, commit_sha


def fetch_changed_files(repo, token, pr_number):
    headers = {"Authorization": f"Bearer {token}"}
    url = f"https://api.github.com/repos/{repo}/pulls/{pr_number}/files"
    resp = requests.get(url, headers=headers)

    try:
        resp.raise_for_status()
    except requests.HTTPError as e:
        raise RuntimeError(f"GitHub API error: {resp.status_code} - {resp.text}") from e

    data = resp.json()
    if not isinstance(data, list) or not all(isinstance(f, dict) and "filename" in f for f in data):
        raise ValueError(f"Unexpected response structure from GitHub API: {data}")

    print(f"Fetched {len(data)} changed files for PR #{pr_number} in {repo}")
    return data


def post_review(comments, commit_sha, pr_number, config):
    print(f"Posting {len(comments)} comments to PR #{pr_number}...")
    if config["dry_run"]:
        print("DRY_RUN: ", comments)
        return

    headers = {"Authorization": f"Bearer {config['token']}"}
    review_payload = {
        "commit_id": commit_sha,
        "event": "COMMENT",
        "body": "AI-powered review.",
        "comments": comments
    }

    url = f"https://api.github.com/repos/{config['repo']}/pulls/{pr_number}/reviews"
    resp = requests.post(url, headers=headers, json=review_payload)

    if resp.status_code >= 400:
        print("Failed to post review", resp.status_code, resp.text)
