"""
Runs the full refresh: buddy4study scrape + clean + import, then NSP
scrape + dedup + import. One command, meant to be triggered by GitHub
Actions (or Task Scheduler) instead of run manually.

    python refresh_all.py
"""
import subprocess
import sys
import os
import logging

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

# A scheduled refresh needs to re-check EVERY scholarship (deadlines close,
# amounts change) - not just add new ones. Deleting these first forces a
# genuine full re-scrape each run instead of silently skipping everything
# already in the file from a previous run.
FILES_TO_RESET = [
    "scholarships.json",
    "scholarships_clean.json",
    "nsp_scholarships.json",
    "nsp_scholarships_deduped.json",
]

STEPS = [
    ("Scrape buddy4study", [sys.executable, "main.py"]),
    ("Clean buddy4study data", [sys.executable, "clean_data.py"]),
    ("Import buddy4study to MongoDB", [sys.executable, "import_to_mongo.py"]),
    ("Scrape NSP", [sys.executable, "nsp_pipeline.py"]),
    ("Dedup NSP against existing data", [sys.executable, "dedup_nsp.py"]),
    ("Import NSP to MongoDB", [sys.executable, "import_nsp_to_mongo.py"]),
]


def reset_previous_output():
    for filename in FILES_TO_RESET:
        if os.path.exists(filename):
            os.remove(filename)
            logging.info(f"Removed old {filename} - forcing a fresh scrape this run")


def main():
    reset_previous_output()
    for name, command in STEPS:
        logging.info(f"=== {name} ===")
        result = subprocess.run(command)
        if result.returncode != 0:
            logging.error(f"'{name}' failed with exit code {result.returncode} - stopping pipeline")
            sys.exit(1)
    logging.info("=== Full refresh complete ===")


if __name__ == "__main__":
    main()