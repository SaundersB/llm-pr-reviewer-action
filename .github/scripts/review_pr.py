import os
import json
import requests
import openai
import tiktoken

openai.api_key = os.getenv("OPENAI_API_KEY")

repo = os.environ['GITHUB_REPOSITORY']
pr_number = os.environ['GITHUB_REF'].split('/')[-1]
token = os.getenv("GITHUB_TOKEN")
headers = {"Authorization": f"Bearer {token}"}
pr_url = f"https://api.github.com/repos/{repo}/pulls/{pr_number}"

pr_data = requests.get(pr_url, headers=headers).json()
diff_url = pr_data['diff_url']
diff = requests.get(diff_url, headers=headers).text
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
RESPONSE_TOKENS = 1024
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

responses = []
for chunk in diff_chunks:
    prompt = prompt_template.replace("{{diff}}", chunk)
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=RESPONSE_TOKENS,
    )
    responses.append(response['choices'][0]['message']['content'])

review = "\n".join(responses)
print("Review from OpenAI:\n", review)

try:
    parsed = json.loads(review)
except json.JSONDecodeError as e:
    print("❌ Failed to parse JSON from model:", e)
    print("LLM Output:\n", review)
    exit(1)

files_url = f"https://api.github.com/repos/{repo}/pulls/{pr_number}/files"
files_changed = requests.get(files_url, headers=headers).json()
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
    exit(0)

review_payload = {
    "commit_id": commit_sha,
    "event": "COMMENT",
    "body": "AI-powered code review by LLM.",
    "comments": comments
}

post_url = f"https://api.github.com/repos/{repo}/pulls/{pr_number}/reviews"
post_response = requests.post(post_url, headers=headers, json=review_payload)

print("✅ Review posted:", post_response.status_code)
print(post_response.json())

