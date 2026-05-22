from collections import Counter
from utils.helpers import save_json, load_json, save_csv, setup_logger
from config import THREAT_KEYWORDS, NORMALIZED_DIR, PREPROCESSED_DIR, MIN_TOPIC_SIZE
import pandas as pd


logger = setup_logger("topic_extractor", log_file="logs/topic_extractor.log")


def extract_topics_by_keywords(text):
    if not text:
        return "Other", 0.0
    text_lower = text.lower()
    best_label = "Other"
    best_score = 0.0
    for label, keywords in THREAT_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in text_lower)
        if score > best_score:
            best_score = score
            best_label = label
    confidence = min(best_score / 3.0, 1.0)
    return best_label, confidence


def try_bertopic(texts, min_topic_size=10):
    try:
        from bertopic import BERTopic
        from sentence_transformers import SentenceTransformer
        from umap import UMAP
        from hdbscan import HDBSCAN

        logger.info("using BERTopic for topic modeling...")
        embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
        umap_model = UMAP(n_neighbors=15, n_components=5, min_dist=0.0, random_state=42)
        hdbscan_model = HDBSCAN(min_cluster_size=min_topic_size, prediction_data=True)
        topic_model = BERTopic(
            embedding_model=embedding_model,
            umap_model=umap_model,
            hdbscan_model=hdbscan_model,
            verbose=True,
        )
        topics, probs = topic_model.fit_transform(texts)
        topic_info = topic_model.get_topic_info()
        return topics, probs, topic_info
    except Exception as e:
        logger.warning(f"BERTopic failed running，Downgrade to keyword match: {e}")
        return None


def run_topic_extractor():
    posts = load_json(f"{NORMALIZED_DIR}/posts.json")
    comments = load_json(f"{NORMALIZED_DIR}/comments.json")
    all_items = posts + comments
    texts = [item.get("normalized_text", "") for item in all_items]

    logger.info(f" {len(texts)} texts to be extracted")

    logger.info(f"Topic Extraction Using Keyword Matching（data {len(texts)} ）")
    bertopic_result = None

    if bertopic_result:
        topics, probs, topic_info = bertopic_result
        for i, item in enumerate(all_items):
            item["topic_label"] = str(topics[i])
            item["topic_probability"] = float(probs[i]) if probs and i < len(probs) else 0.0
    else:
        for item in all_items:
            label, confidence = extract_topics_by_keywords(item.get("normalized_text", ""))
            item["topic_label"] = label
            item["topic_probability"] = confidence

    topic_counts = Counter(item["topic_label"] for item in all_items)
    logger.info(f"Topic Distribution: {dict(topic_counts)}")

    df_posts = pd.DataFrame(posts)
    df_comments = pd.DataFrame(comments)
    save_json(posts, f"{PREPROCESSED_DIR}/posts.json")
    save_json(comments, f"{PREPROCESSED_DIR}/comments.json")
    save_csv(df_posts, f"{PREPROCESSED_DIR}/posts.csv")
    save_csv(df_comments, f"{PREPROCESSED_DIR}/comments.csv")
    logger.info("Theme extraction complete")
    return all_items


if __name__ == "__main__":
    run_topic_extractor()