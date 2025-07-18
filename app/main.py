from config import load_config
from services.pr_review_service import process_pull_request

if __name__ == "__main__":
    config = load_config()
    process_pull_request(config)
    print("✅ PR review completed successfully.")