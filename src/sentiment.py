from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from utils.helpers import save_json, load_json, save_csv, setup_logger
from config import SENTIMENT_THRESHOLD, PREPROCESSED_DIR
import pandas as pd


logger = setup_logger("sentiment", log_file="logs/sentiment.log")
analyzer = SentimentIntensityAnalyzer()


def analyze_sentiment(text):
    if not text or not text.strip():
        return {
            "sentiment_compound": 0.0,
            "sentiment_label": "neutral",
            "sentiment_pos": 0.0,
            "sentiment_neu": 1.0,
            "sentiment_neg": 0.0,
        }
    scores = analyzer.polarity_scores(text)
    compound = scores["compound"]
    if compound >= SENTIMENT_THRESHOLD:
        label = "positive"
    elif compound <= -SENTIMENT_THRESHOLD:
        label = "negative"
    else:
        label = "neutral"
    return {
        "sentiment_compound": compound,
        "sentiment_label": label,
        "sentiment_pos": scores["pos"],
        "sentiment_neu": scores["neu"],
        "sentiment_neg": scores["neg"],
    }


def run_sentiment():
    posts = load_json(f"{PREPROCESSED_DIR}/posts.json")
    comments = load_json(f"{PREPROCESSED_DIR}/comments.json")
    logger.info(f"Loading data：{len(posts)} posts, {len(comments)} comments")

    for i, post in enumerate(posts):
        text = post.get("normalized_text", "") or post.get("raw_text", "")
        post.update(analyze_sentiment(text))
        if (i + 1) % 100 == 0:
            logger.info(f"{i+1}/{len(posts)} posts emotion analysis done")

    for i, comment in enumerate(comments):
        text = comment.get("normalized_text", "") or comment.get("raw_text", "")
        comment.update(analyze_sentiment(text))
        if (i + 1) % 100 == 0:
            logger.info(f"analyzed emotion of {i+1}/{len(comments)} comments")

    all_items = posts + comments
    df = pd.DataFrame(all_items)
    save_json(all_items, f"{PREPROCESSED_DIR}/preprocessed_data.json")
    save_csv(df, f"{PREPROCESSED_DIR}/preprocessed_data.csv")
    logger.info("emotional analysis done")
    sentiment_dist = df["sentiment_label"].value_counts().to_dict()
    logger.info(f"Emotional Distribution: {sentiment_dist}")
    return all_items


if __name__ == "__main__":
    run_sentiment()