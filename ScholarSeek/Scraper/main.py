"""
Entry point: run this file to perform a full scrape.
    python3 main.py
"""
import json
import logging
from datetime import datetime

from config import OUTPUT_FILE, LOG_FILE
from scrape_listings import collect_all_links
from scrape_details import scrape_all_details, load_existing, save_records


def setup_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[logging.FileHandler(LOG_FILE), logging.StreamHandler()],
    )


def main():
    setup_logging()
    logging.info("=== Starting scrape ===")

    logging.info("Stage 1: collecting listing links via Selenium...")
    links = collect_all_links()
    logging.info(f"Stage 1 complete: {len(links)} unique detail-page URLs found")

    existing = load_existing(OUTPUT_FILE)
    if existing:
        logging.info(f"Found existing {OUTPUT_FILE} with {len(existing)} records - resuming")

    logging.info("Stage 2: scraping each detail page via requests...")
    # Saves progress to OUTPUT_FILE every 15 records - a crash/interrupt now
    # loses at most ~15 records of work instead of the entire run.
    records = scrape_all_details(links, existing_records=existing, output_file=OUTPUT_FILE, save_every=15)
    logging.info(f"Stage 2 complete: {len(records)} scholarships scraped successfully")

    save_records(records, OUTPUT_FILE)
    logging.info(f"Saved {len(records)} records to {OUTPUT_FILE}")
    logging.info("=== Done ===")


if __name__ == "__main__":
    main()