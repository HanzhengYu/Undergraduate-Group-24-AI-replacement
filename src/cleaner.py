import re
import html
from utils.helpers import save_json, load_json, setup_logger
from config import RAW_DIR, CLEANED_DIR


logger = setup_logger("cleaner", log_file="logs/cleaner.log")


def clean_text(text):
    if not isinstance(text, str):
        return ""
    text = html.unescape(text)
    text = re.sub(r"http\S+|www\.\S+", "", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    text = re.sub(r"\*\*|__|~~|`", "", text)
    text = re.sub(r"&amp;|&lt;|&gt;|&quot;|&#x?[0-9a-fA-F]+;", "", text)
    text = re.sub(r"\s+", " ", text).strip()
    text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", "", text)
    return text


def is_deleted(text):
    return text in ("[deleted]", "[removed]", "")


def clean_posts(posts):
    cleaned = []
    for post in posts:
        if is_deleted(post.get("title", "")) and is_deleted(post.get("selftext", "")):
            continue
        post["title_clean"] = clean_text(post.get("title", ""))
        post["selftext_clean"] = clean_text(post.get("selftext", ""))
        post["raw_text"] = f"{post['title_clean']} {post['selftext_clean']}".strip()
        cleaned.append(post)
    return cleaned


def clean_comments(comments):
    cleaned = []
    seen_ids = set()
    for comment in comments:
        if comment["id"] in seen_ids:
            continue
        seen_ids.add(comment["id"])
        if is_deleted(comment.get("body", "")):
            continue
        comment["body_clean"] = clean_text(comment.get("body", ""))
        comment["raw_text"] = comment["body_clean"]
        cleaned.append(comment)
    return cleaned


def run_cleaner():
    posts = load_json(f"{RAW_DIR}/posts.json")
    comments = load_json(f"{RAW_DIR}/comments.json")
    logger.info(f"Original {len(posts)} posts, {len(comments)} comments")

    cleaned_posts = clean_posts(posts)
    cleaned_comments = clean_comments(comments)
    logger.info(f"{len(cleaned_posts)} posts after cleaning, {len(cleaned_comments)} comments")

    save_json(cleaned_posts, f"{CLEANED_DIR}/posts.json")
    save_json(cleaned_comments, f"{CLEANED_DIR}/comments.json")
    return cleaned_posts, cleaned_comments


if __name__ == "__main__":
    run_cleaner()