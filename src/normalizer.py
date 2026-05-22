import spacy
import nltk
from nltk.stem import PorterStemmer
from utils.helpers import save_json, load_json, setup_logger
from config import SPACY_MODEL, CLEANED_DIR, NORMALIZED_DIR


logger = setup_logger("normalizer", log_file="logs/normalizer.log")
stemmer = PorterStemmer()


def load_nlp():
    try:
        nlp = spacy.load(SPACY_MODEL)
    except OSError:
        logger.info(f"Downloading spaCy model {SPACY_MODEL}...")
        spacy.cli.download(SPACY_MODEL)
        nlp = spacy.load(SPACY_MODEL)
    
    try:
        nltk.data.find('tokenizers/punkt')
    except LookupError:
        logger.info("Downloading NLTK punkt...")
        nltk.download('punkt')
    
    return nlp


def normalize_text(text, nlp):
    if not text or not text.strip():
        return {
            "raw_tokens": [],
            "lowercase_tokens": [],
            "filtered_tokens_no_stop_no_punc": [],
            "stemmed_tokens": [],
            "lemmatized_tokens": [],
            "text_tokenized": "",
            "text_filtered": "",
            "text_stemmed": "",
            "text_lemmatized": ""
        }
    
    doc = nlp(text)
    
    raw_tokens = [token.text for token in doc]
    lowercase_tokens = [t.lower() for t in raw_tokens]
    
    filtered_tokens = [
        token.text.lower() for token in doc
        if not token.is_stop and not token.is_punct and not token.is_space and len(token.text) > 1
    ]
    
    stemmed_tokens = [stemmer.stem(token) for token in filtered_tokens]
    lemmatized_tokens = [token.lemma_.lower() for token in doc
                        if not token.is_stop and not token.is_punct and not token.is_space and len(token.text) > 1]
    
    return {
        "raw_tokens": raw_tokens,
        "lowercase_tokens": lowercase_tokens,
        "filtered_tokens_no_stop_no_punc": filtered_tokens,
        "stemmed_tokens": stemmed_tokens,
        "lemmatized_tokens": lemmatized_tokens,
        "text_tokenized": " ".join(raw_tokens),
        "text_filtered": " ".join(filtered_tokens),
        "text_stemmed": " ".join(stemmed_tokens),
        "text_lemmatized": " ".join(lemmatized_tokens),
        "normalized_text": " ".join(lemmatized_tokens)
    }


def run_normalizer():
    nlp = load_nlp()
    posts = load_json(f"{CLEANED_DIR}/posts.json")
    comments = load_json(f"{CLEANED_DIR}/comments.json")
    logger.info(f"Loading cleaned data：{len(posts)} posts, {len(comments)} comments")

    for i, post in enumerate(posts):
        norm_result = normalize_text(post["raw_text"], nlp)
        post.update(norm_result)
        if (i + 1) % 100 == 0:
            logger.info(f"Standardized {i+1}/{len(posts)} posts")

    for i, comment in enumerate(comments):
        norm_result = normalize_text(comment["raw_text"], nlp)
        comment.update(norm_result)
        if (i + 1) % 100 == 0:
            logger.info(f"{i+1}/{len(comments)} comments standardized")

    save_json(posts, f"{NORMALIZED_DIR}/posts.json")
    save_json(comments, f"{NORMALIZED_DIR}/comments.json")
    
    import pandas as pd
    df_posts = pd.DataFrame(posts)
    df_comments = pd.DataFrame(comments)
    df_posts.to_csv(f"{NORMALIZED_DIR}/posts.csv", index=False, encoding='utf-8-sig')
    df_comments.to_csv(f"{NORMALIZED_DIR}/comments.csv", index=False, encoding='utf-8-sig')
    
    logger.info("standardized done, result has been saved")
    return posts, comments


if __name__ == "__main__":
    run_normalizer()
