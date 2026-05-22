import requests
import xml.etree.ElementTree as ET
import re
import time
from datetime import datetime, timedelta

from utils.helpers import save_json, setup_logger, timestamp_to_date
from config import (
    HTTP_PROXY, HTTPS_PROXY, REQUEST_TIMEOUT, REQUEST_DELAY,
    SUBREDDITS, SEARCH_KEYWORDS, DAYS_LOOKBACK,
    RAW_DIR, MAX_POSTS_PER_SUBREDDIT,
)


logger = setup_logger("scraper", log_file="logs/scraper.log")
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
ATOM_NS = {"atom": "http://www.w3.org/2005/Atom"}
BASE_URL = "https://www.reddit.com"

PROXIES = {}
if HTTP_PROXY:
    PROXIES["http"] = HTTP_PROXY
if HTTPS_PROXY:
    PROXIES["https"] = HTTPS_PROXY


def fetch_rss(url):
    resp = requests.get(url, headers=HEADERS, proxies=PROXIES, timeout=REQUEST_TIMEOUT)
    resp.raise_for_status()
    return resp.content


def parse_rss_date(date_str):
    try:
        dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
        return dt.timestamp()
    except Exception:
        return 0


def extract_subreddit_from_link(link):
    match = re.search(r"/r/([^/]+)/", link)
    return match.group(1) if match else "unknown"


def parse_post_from_entry(entry, subreddit=None):
    title = entry.find("atom:title", ATOM_NS)
    title = title.text if title is not None else ""

    author = entry.find("atom:author/atom:name", ATOM_NS)
    author = author.text if author is not None else "[deleted]"

    entry_id = entry.find("atom:id", ATOM_NS)
    entry_id_text = entry_id.text if entry_id is not None else ""
    post_id = entry_id_text.split("_")[-1] if "_" in entry_id_text else entry_id_text

    link = entry.find("atom:link", ATOM_NS)
    link_href = link.attrib.get("href", "") if link is not None else ""

    updated = entry.find("atom:updated", ATOM_NS)
    updated_ts = parse_rss_date(updated.text) if updated is not None and updated.text is not None else 0

    content = entry.find("atom:content", ATOM_NS)
    selftext_html = content.text if content is not None and content.text is not None else ""
    selftext_text = re.sub(r"<[^>]+>", "", selftext_html) if selftext_html else ""

    actual_subreddit = subreddit or extract_subreddit_from_link(link_href)

    return {
        "id": post_id,
        "type": "post",
        "subreddit": actual_subreddit,
        "author": author,
        "created_utc": updated_ts,
        "created_date": timestamp_to_date(updated_ts),
        "score": 0,
        "title": title,
        "selftext": selftext_text,
        "num_comments": 0,
        "url": link_href,
    }


def scrape_subreddit_posts(subreddit_name, limit=MAX_POSTS_PER_SUBREDDIT):
    logger.info(f"scraping r/{subreddit_name} posts...")
    cutoff = datetime.utcnow() - timedelta(days=DAYS_LOOKBACK)
    cutoff_ts = cutoff.timestamp()

    try:
        xml_data = fetch_rss(f"{BASE_URL}/r/{subreddit_name}/.rss")
        root = ET.fromstring(xml_data)
        entries = root.findall("atom:entry", ATOM_NS)
    except Exception as e:
        logger.warning(f"scrap r/{subreddit_name} failed: {e}")
        return []

    posts = []
    for entry in entries:
        post = parse_post_from_entry(entry, subreddit_name)
        if post["created_utc"] >= cutoff_ts:
            posts.append(post)

    logger.info(f"From r/{subreddit_name} scrapped {len(posts)}  posts ( {len(entries)} in total)")
    return posts


def search_keywords_across_reddit(keywords, limit=100):
    logger.info(f"Searching for keywords across subforums...")
    cutoff = datetime.utcnow() - timedelta(days=DAYS_LOOKBACK)
    cutoff_ts = cutoff.timestamp()

    all_posts = []
    seen_ids = set()

    for keyword in keywords:
        logger.info(f"search key words: {keyword}")
        try:
            q = keyword.replace(" ", "+")
            xml_data = fetch_rss(f"{BASE_URL}/r/all/search.rss?q={q}&sort=relevance")
            root = ET.fromstring(xml_data)
            entries = root.findall("atom:entry", ATOM_NS)
        except Exception as e:
            logger.warning(f"search key words '{keyword}' failed: {e}")
            continue

        for entry in entries:
            entry_id = entry.find("atom:id", ATOM_NS)
            entry_id_text = entry_id.text if entry_id is not None else ""
            post_id = entry_id_text.split("_")[-1] if "_" in entry_id_text else entry_id_text

            if post_id in seen_ids:
                continue

            post = parse_post_from_entry(entry)
            if post["created_utc"] < cutoff_ts:
                continue

            seen_ids.add(post_id)
            all_posts.append(post)

        time.sleep(REQUEST_DELAY)

    logger.info(f"search keywords and found {len(all_posts)} posts")
    return all_posts


def run_scraper():
    all_posts = []
    all_comments = []

    for subreddit in SUBREDDITS:
        posts = scrape_subreddit_posts(subreddit)
        all_posts.extend(posts)

    keyword_posts = search_keywords_across_reddit(SEARCH_KEYWORDS)
    seen_post_ids = {p["id"] for p in all_posts}
    for p in keyword_posts:
        if p["id"] not in seen_post_ids:
            seen_post_ids.add(p["id"])
            all_posts.append(p)

    logger.info(f"{len(all_posts)} posts left after deduplication")

    save_json(all_posts, f"{RAW_DIR}/posts.json")
    save_json(all_comments, f"{RAW_DIR}/comments.json")
    logger.info(f"scrapping done！posts: {len(all_posts)}, comments: {len(all_comments)}")
    return all_posts, all_comments


if __name__ == "__main__":
    run_scraper()