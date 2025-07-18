from services.github_service import fetch_pr_diff, fetch_changed_files, post_review
from services.prompt_service import prepare_prompt_chunks
from services.openai_service import get_review_comments
from utils.diff_utils import map_line_positions, match_line_to_position
from domains.models import ReviewComment

def process_pull_request(config):
    pr_data, diff, commit_sha = fetch_pr_diff(config)
    line_map = map_line_positions(diff)
    parsed_comments = get_review_comments(diff, config)
    changed_files = fetch_changed_files(config["repo"], config["token"], pr_data["number"])

    valid_files = {f["filename"] for f in changed_files}
    comments = []

    for entry in parsed_comments:
        print(f"Processing comment for file: {entry.file}")
        if entry.file not in valid_files:
            continue
        position = match_line_to_position(line_map, entry.file, entry.line)
        if position is None:
            continue
        comments.append({
            "path": entry.file,
            "position": position,
            "body": f"[{entry.domain.capitalize()}] {entry.comment}"
        })

    if comments:
        post_review(comments, commit_sha, pr_data["number"], config)
