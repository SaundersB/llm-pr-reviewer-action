import os
import sys
import json
import requests
import openai
from openai import OpenAI, APIError
import tiktoken

openai.api_key = os.getenv("OPENAI_API_KEY")
MODEL = os.getenv("OPENAI_MODEL", "gpt-4.1")
RESPONSE_TOKENS = int(os.getenv("RESPONSE_TOKENS", "1024"))
DRY_RUN = os.getenv("DRY_RUN", "false").lower() == "true"

repo = os.environ['GITHUB_REPOSITORY']
with open(os.environ['GITHUB_EVENT_PATH']) as f:
    pr_event = json.load(f)

pr_number = str(pr_event["number"])
token = os.getenv("GITHUB_TOKEN")
headers = {"Authorization": f"Bearer {token}"}
pr_url = f"https://api.github.com/repos/{repo}/pulls/{pr_number}"

print(f"Fetching PR #{pr_number} from {repo}...")

try:
    pr_resp = requests.get(pr_url, headers=headers)
    pr_resp.raise_for_status()
    pr_data = pr_resp.json()
except requests.RequestException as e:
    print("❌ Failed to fetch PR data:", e)
    sys.exit(1)

if "pull_request" not in pr_event:
    print("❌ This workflow must be triggered by a 'pull_request' event.")
    sys.exit(1)

diff_url = pr_event.get("pull_request", {}).get("diff_url")
commit_sha = pr_event.get("pull_request", {}).get("head", {}).get("sha")

if not diff_url:
    print("❌ Could not determine diff URL from PR data")
    sys.exit(1)

try:
    diff_resp = requests.get(diff_url, headers=headers)
    diff_resp.raise_for_status()
    diff = diff_resp.text
except requests.RequestException as e:
    print("❌ Failed to fetch diff:", e)
    sys.exit(1)

commit_sha = pr_data["head"]["sha"]

custom_prompt = os.getenv("CUSTOM_PROMPT")
if custom_prompt:
    prompt_template = custom_prompt
else:
    with open("prompts/default_gpt_prompts.txt") as f:
        prompt_template = f.read()

encoding = tiktoken.get_encoding("cl100k_base")

def count_tokens(text: str) -> int:
    return len(encoding.encode(text))

BASE_PROMPT = prompt_template.replace("{{diff}}", "")
BASE_TOKENS = count_tokens(BASE_PROMPT)
MAX_MODEL_TOKENS = 8192
MAX_PROMPT_TOKENS = MAX_MODEL_TOKENS - RESPONSE_TOKENS

def chunk_diff(diff_text: str) -> list[str]:
    lines = diff_text.splitlines(keepends=True)
    chunks: list[str] = []
    current: list[str] = []
    tokens = BASE_TOKENS
    for line in lines:
        lt = count_tokens(line)
        if tokens + lt > MAX_PROMPT_TOKENS and current:
            chunks.append("".join(current))
            current = [line]
            tokens = BASE_TOKENS + lt
        else:
            current.append(line)
            tokens += lt
    if current:
        chunks.append("".join(current))
    return chunks

diff_chunks = chunk_diff(diff)
parsed = []

for chunk in diff_chunks:
    prompt = prompt_template.replace("{{diff}}", chunk)
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=RESPONSE_TOKENS
        )
        content = response.choices[0].message.content
    except APIError as e:
        print("❌ OpenAI API error:", e)
        sys.exit(1)

    try:
        parsed.extend(json.loads(content))
    except json.JSONDecodeError as e:
        print("❌ Failed to parse chunk JSON:", e)
        print("LLM Output:\n", content)

print("Review from OpenAI:\n", json.dumps(parsed, indent=2))

files_url = f"https://api.github.com/repos/{repo}/pulls/{pr_number}/files"
try:
    files_resp = requests.get(files_url, headers=headers)
    files_resp.raise_for_status()
    files_changed = files_resp.json()
except requests.RequestException as e:
    print("❌ Failed to fetch changed files:", e)
    sys.exit(1)

valid_paths = {f["filename"] for f in files_changed}

comments = []
for entry in parsed:
    if entry["file"] not in valid_paths:
        print(f"⚠️ Skipping unknown file: {entry['file']}")
        continue
    comments.append({
        "path": entry["file"],
        "line": entry["line"],
        "side": "RIGHT",
        "body": f"[{entry['domain'].capitalize()}] {entry['comment']}"
    })

if not comments:
    print("No valid comments to post.")
    sys.exit(0)

review_payload = {
    "commit_id": commit_sha,
    "event": "COMMENT",
    "body": "AI-powered code review by LLM.",
    "comments": comments
}

post_url = f"https://api.github.com/repos/{repo}/pulls/{pr_number}/reviews"

if DRY_RUN:
    print("DRY_RUN enabled. Review payload:\n", json.dumps(review_payload, indent=2))
    sys.exit(0)

post_response = requests.post(post_url, headers=headers, json=review_payload)
if post_response.status_code >= 400:
    print("❌ Failed to post review:", post_response.status_code)
    print(post_response.text)
    sys.exit(1)

print("✅ Review posted:", post_response.status_code)
print(post_response.json())