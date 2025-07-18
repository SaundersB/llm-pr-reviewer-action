from config import load_config
from services.pr_review_service import process_pull_request

if __name__ == "__main__":
    config = load_config()
    process_pull_request(config)
    print("✅ PR review completed successfully.")
    if config["dry_run"]:
        print("This was a dry run. No comments were posted to the PR.")
    else:
        print("Comments posted to the PR successfully.")
    print("You can view the review on GitHub.")
    print("Thank you for using the LLM PR Reviewer Action!")