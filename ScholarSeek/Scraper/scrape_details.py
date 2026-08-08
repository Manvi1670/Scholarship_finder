"""
Stage 2: for each detail-page URL collected in Stage 1, fetch it with plain
requests (detail pages are static, no Selenium needed - faster) and pull out
the structured fields using extractors.py.
"""
import time
import logging
import requests
from bs4 import BeautifulSoup

from config import HEADERS, REQUEST_TIMEOUT, MAX_RETRIES, RATE_LIMIT_SECONDS
from extractors import classify_award, extract_min_cpi, parse_deadline, extract_contact


def fetch_with_retries(url: str):
    """Try a request up to MAX_RETRIES times before giving up on this URL."""
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            logging.warning(f"Attempt {attempt}/{MAX_RETRIES} failed for {url}: {e}")
            time.sleep(2 * attempt)  # back off a bit longer each retry
    logging.error(f"Giving up on {url} after {MAX_RETRIES} attempts")
    return None


def get_field_by_label(soup, label):
    """
    Eligibility/Region/Award/Deadline have NO class names on this site -
    they're a plain <h6>Label</h6> followed by a plain <p>value</p> sibling.
    So we match by the label text itself, then grab the next <p>.
    """
    h6 = soup.find("h6", string=lambda s: s and s.strip() == label)
    if not h6:
        return None
    value_el = h6.find_next_sibling("p")
    return value_el.get_text(strip=True) if value_el else None


def scrape_detail_page(url: str):
    response = fetch_with_retries(url)
    if response is None:
        return None  # caller decides how to handle a total failure

    soup = BeautifulSoup(response.text, "html.parser")

    h1 = soup.find("h1")
    name = h1.get_text(strip=True) if h1 else None

    eligibility = get_field_by_label(soup, "Eligibility")
    region = get_field_by_label(soup, "Region")
    award_text = get_field_by_label(soup, "Award")
    deadline_text = get_field_by_label(soup, "Deadline")

    # The detailed "About the Program" section (with fuller eligibility
    # criteria, benefits, etc.) lives in a <div id="about">, matching the
    # nav link href="#about" we found earlier.
    about_div = soup.find(id="about")
    description = about_div.get_text(" ", strip=True) if about_div else None

    # Contact block lives in <div id="contactdetails"> - same pattern.
    contact_div = soup.find(id="contactdetails")
    contact_text = contact_div.get_text(" ", strip=True) if contact_div else None
    email, phone = extract_contact(contact_text)

    # No dedicated apply-link class either - find any link whose visible
    # text mentions "apply".
    apply_link = None
    for a in soup.find_all("a"):
        if "apply" in a.get_text(strip=True).lower():
            apply_link = a.get("href")
            break

    # Combine the short eligibility line with the fuller description when
    # looking for a CPI/percentage requirement - the detailed criteria
    # usually live in the "about" section, not the short summary field.
    cpi_search_text = " ".join(filter(None, [eligibility, description]))

    return {
        "name": name,
        "sourceUrl": url,
        "region": region,
        "eligibilityRaw": eligibility,
        "minCPI": extract_min_cpi(cpi_search_text),
        "awardRaw": award_text,
        "awardCategory": classify_award(award_text),
        "deadlineRaw": deadline_text,
        "deadline": parse_deadline(deadline_text),
        "description": description,
        "applyLink": apply_link,
        "contactEmail": email,
        "contactPhone": phone,
    }


def scrape_all_details(urls, existing_records=None, output_file=None, save_every=15) -> list:
    """
    existing_records: records already saved from a previous run - URLs already
        in here are skipped instead of re-scraped, so a restart doesn't waste
        time redoing work.
    output_file/save_every: if given, write progress to disk every N new
        records, instead of only once at the very end. This is the fix for
        losing everything on a crash/interrupt/long stall.
    """
    results = list(existing_records) if existing_records else []
    already_done = {r["sourceUrl"] for r in results}
    remaining = [u for u in urls if u not in already_done]

    logging.info(f"{len(already_done)} already scraped, {len(remaining)} remaining")

    for i, url in enumerate(remaining, start=1):
        logging.info(f"[{i}/{len(remaining)}] scraping {url}")
        record = scrape_detail_page(url)
        if record:
            results.append(record)

        if output_file and i % save_every == 0:
            save_records(results, output_file)
            logging.info(f"Progress saved: {len(results)} total records so far")

        time.sleep(RATE_LIMIT_SECONDS)  # polite pause between every detail page

    if output_file:
        save_records(results, output_file)  # final save

    return results


def save_records(records, output_file):
    """Write current records to disk now, in the same shape main.py expects."""
    import json
    from datetime import datetime as _dt

    to_save = []
    for r in records:
        r = dict(r)
        r.setdefault("scrapedAt", _dt.utcnow().isoformat())
        if r.get("deadline") and hasattr(r["deadline"], "isoformat"):
            r["deadline"] = r["deadline"].isoformat()
        to_save.append(r)

    with open(output_file, "w") as f:
        json.dump(to_save, f, indent=2, default=str)


def load_existing(output_file):
    """Load a previous partial run's output, if the file exists, so we can resume."""
    import json
    import os
    if not output_file or not os.path.exists(output_file):
        return []
    try:
        with open(output_file, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, ValueError):
        logging.warning(f"{output_file} exists but isn't valid JSON - starting fresh")
        return []