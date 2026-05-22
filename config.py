import os

USER_AGENT = "AI-Anxiety-Research/1.0"


HTTP_PROXY = os.getenv("HTTP_PROXY", "")
HTTPS_PROXY = os.getenv("HTTPS_PROXY", "")

# request timed out
REQUEST_TIMEOUT = 30

REQUEST_DELAY = 1.0

# Target Subforum
SUBREDDITS = [
    "programming",
    "webdev",
    "artificial",
    "MachineLearning",
    "ChatGPTCoding",
    "copilot",
]

# Search keywords
SEARCH_KEYWORDS = [
    "AI replacement",
    "AI anxiety",
    "Copilot",
    "job security",
    "AI replace developer",
    "AI coding tool",
    "ChatGPT programming",
    "AI take over coding",
]

# time range
DAYS_LOOKBACK = 180

# data path
DATA_DIR = "data"
RAW_DIR = os.path.join(DATA_DIR, "raw")
CLEANED_DIR = os.path.join(DATA_DIR, "cleaned")
NORMALIZED_DIR = os.path.join(DATA_DIR, "normalized")
PREPROCESSED_DIR = os.path.join(DATA_DIR, "preprocessed")

# limited
MAX_POSTS_PER_SUBREDDIT = 500
MAX_COMMENTS_PER_POST = 100

# spaCy model
SPACY_MODEL = "en_core_web_sm"

# BERTopic configuration
BERT_MODEL = "all-MiniLM-L6-v2"
MIN_TOPIC_SIZE = 10

# Threat Category Keyword Mapping
THREAT_KEYWORDS = {
    "Job Replacement": ["job", "layoff", "replace", "automate", "fired", "unemployment", "obsolete"],
    "Copyright": ["copyright", "license", "steal", "legal", "lawsuit", "intellectual property", "ip theft"],
    "Ethics": ["bias", "ethical", "fair", "responsible", "moral", "accountability"],
    "Code Quality": ["quality", "bug", "wrong", "incorrect", "error-prone", "technical debt"],
    "Skill Obsolescence": ["learn", "skill", "education", "obsolete", "upskill", "reskill"],
}

# sentiment threshold
SENTIMENT_THRESHOLD = 0.05