from openai import OpenAI, APIError
from utils.parse_utils import parse_review_chunk
from services.prompt_service import prepare_prompt_chunks
from utils.token_utils import count_tokens
from services.default_prompt import default_prompt
import os

def get_review_comments(diff, config):
    client = OpenAI(api_key=config["api_key"])

    if config.get("custom_prompt"):
        prompt_template = config["custom_prompt"]
    else:
        prompt_template = default_prompt

    base_prompt = prompt_template.replace("{{diff}}", "")
    base_tokens = count_tokens(base_prompt)
    max_prompt_tokens = 8192 - config["response_tokens"]

    chunks = prepare_prompt_chunks(diff, prompt_template, base_tokens, max_prompt_tokens)
    results = []

    for chunk_text, start in chunks:
        prompt = prompt_template.replace("{{diff}}", chunk_text)
        try:
            response = client.chat.completions.create(
                model=config["model"],
                messages=[{"role": "user", "content": prompt}],
                max_tokens=config["response_tokens"]
            )
            content = response.choices[0].message.content
            results.extend(parse_review_chunk(content, start))
        except APIError as e:
            print("❌ OpenAI error:", e)
            continue
    return results
