import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.helpers import setup_logger, ensure_dirs
from config import RAW_DIR, CLEANED_DIR, NORMALIZED_DIR, PREPROCESSED_DIR


logger = setup_logger("pipeline", log_file="logs/pipeline.log")


def run_pipeline(steps=None):
    all_steps = ["scrape", "clean", "normalize", "topics", "sentiment"]
    if steps:
        all_steps = [s for s in all_steps if s in steps]

    ensure_dirs([RAW_DIR, CLEANED_DIR, NORMALIZED_DIR, PREPROCESSED_DIR])

    for step in all_steps:
        logger.info(f"===== start step {step} =====")
        if step == "scrape":
            from src.scraper import run_scraper
            run_scraper()
        elif step == "clean":
            from src.cleaner import run_cleaner
            run_cleaner()
        elif step == "normalize":
            from src.normalizer import run_normalizer
            run_normalizer()
        elif step == "topics":
            from src.topic_extractor import run_topic_extractor
            run_topic_extractor()
        elif step == "sentiment":
            from src.sentiment import run_sentiment
            run_sentiment()
        logger.info(f"===== step {step} done =====\n")

    logger.info("all steps done")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Reddit AI Anxiety Data Preprocessing Pipeline")
    parser.add_argument(
        "--steps", nargs="+",
        choices=["scrape", "clean", "normalize", "topics", "sentiment"],
        help="Specify the steps to run（default run all）"
    )
    args = parser.parse_args()
    run_pipeline(steps=args.steps)