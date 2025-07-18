from utils.token_utils import count_tokens
from utils.diff_utils import chunk_diff

def prepare_prompt_chunks(diff, prompt_template, base_tokens, max_prompt_tokens):
    if base_tokens + count_tokens(diff) <= max_prompt_tokens:
        return [(diff, 0)]
    return chunk_diff(diff, count_tokens, max_prompt_tokens, base_tokens)
