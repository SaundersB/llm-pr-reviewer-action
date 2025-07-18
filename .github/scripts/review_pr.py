import os
import json
import requests
import openai

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
    prompt = custom_prompt.replace("{{diff}}", diff)
else:
    with open("prompts/default_gpt_prompt.txt") as f:
        base_prompt = f.read()
    prompt = f"""{base_prompt}

Please return your review comments as a JSON array, one object per comment. Each object should contain:
- "file": the exact file path
- "line": the line number in the diff (not original file)
- "domain": the concern category (e.g., security, performance)
- "comment": the review comment

Here is the diff you are reviewing:

{diff}
"""

response = openai.ChatCompletion.create(
    model="gpt-4",
    messages=[{"role": "user", "content": prompt}],
    max_tokens=2048
)

review = response['choices'][0]['message']['content']
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
