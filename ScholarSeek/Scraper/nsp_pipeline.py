import time
import json
import logging
from datetime import datetime

from nsp_scraper import scrape_nsp_schemes, parse_nsp_deadline, URL, HEADERS
from pdf_extractor import download_pdf_text, extract_eligibility_section, extract_amount_section
from extractors import extract_min_cpi, extract_award_amount_inr, classify_award

import requests

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

RATE_LIMIT_SECONDS = 1.5
OUTPUT_FILE = "nsp_scholarships.json"


def build_record(scheme: dict) -> dict:
    pdf_text = download_pdf_text(scheme["specificationsUrl"])

    eligibility = extract_eligibility_section(pdf_text)
    amount_text = extract_amount_section(pdf_text)

    return {
        "name": scheme["name"],
        "sourceUrl": scheme["specificationsUrl"],  # stable per-scheme URL, used as our dedup key
        "region": "India",
        "eligibilityRaw": eligibility,
        "minCPI": extract_min_cpi(eligibility) if eligibility else None,
        "awardRaw": amount_text,
        "awardAmountINR": extract_award_amount_inr(amount_text) if amount_text else None,
        "awardCategory": classify_award(amount_text) if amount_text else "other",
        "deadlineRaw": scheme["deadlineRaw"],
        "deadline": parse_nsp_deadline(scheme["deadlineRaw"]),
        "description": eligibility,  # NSP has no separate long description - reuse eligibility text
        "applyLink": scheme["faqUrl"],  # NSP applications happen on the portal itself, not an external link
        "contactEmail": None,
        "contactPhone": None,
        "source": "nsp",
        "scrapedAt": datetime.utcnow().isoformat(),
    }


def main():
    logging.info("Fetching NSP listing page...")
    response = requests.get(URL, headers=HEADERS, timeout=20)
    schemes = scrape_nsp_schemes(response.text)
    logging.info(f"Found {len(schemes)} schemes")

    records = []
    for i, scheme in enumerate(schemes, start=1):
        logging.info(f"[{i}/{len(schemes)}] {scheme['name'][:60]}")
        try:
            record = build_record(scheme)
            records.append(record)
        except Exception as e:
            logging.warning(f"Failed on this scheme, skipping: {e}")
        time.sleep(RATE_LIMIT_SECONDS)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2, default=str)

    with_eligibility = sum(1 for r in records if r["eligibilityRaw"])
    with_amount = sum(1 for r in records if r["awardAmountINR"])
    logging.info(f"Saved {len(records)} records to {OUTPUT_FILE}")
    logging.info(f"  {with_eligibility}/{len(records)} have extracted eligibility text")
    logging.info(f"  {with_amount}/{len(records)} have a parsed award amount")


if __name__ == "__main__":
    main()