import re
import requests
from bs4 import BeautifulSoup

URL = "https://scholarships.gov.in/All-Scholarships"
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}


def scrape_nsp_schemes(html: str) -> list:
    soup = BeautifulSoup(html, "html.parser")

    # "Specifications" links are the one reliable, unique-per-scheme anchor -
    # the surrounding div classes are just reused Bootstrap utilities, not
    # a real per-scheme wrapper, so we anchor on this instead.
    spec_links = soup.find_all("a", string="Specifications")

    schemes = []
    for link in spec_links:
        # 2 levels up reaches the full scheme block (name + status + links),
        # confirmed against the real saved page structure.
        container = link.find_parent()
        if container:
            container = container.find_parent()
        if container is None:
            continue

        h6 = container.find("h6")
        name = h6.get_text(strip=True) if h6 else None

        # Multiple status spans exist (scheme open, student application open,
        # verification stages...) - we want the one about STUDENT applications,
        # since that's the actual deadline a student cares about.
        status_spans = container.find_all("span", class_="d-inline-block")
        deadline_raw = None
        for span in status_spans:
            text = span.get_text(" ", strip=True)
            if "Student Application" in text:
                deadline_raw = text
                break
        if deadline_raw is None and status_spans:
            # "NOT YET OPENED" schemes only have the first status line
            deadline_raw = status_spans[0].get_text(" ", strip=True)

        # FAQ link sits in the same small wrapper as the Specifications link
        links_wrapper = link.find_parent()
        faq_link_el = links_wrapper.find("a", string="FAQ") if links_wrapper else None

        schemes.append({
            "name": name,
            "deadlineRaw": deadline_raw,
            "specificationsUrl": link.get("href"),
            "faqUrl": faq_link_el.get("href") if faq_link_el else None,
            "region": "India",
            "source": "nsp",
        })

    return schemes


def parse_nsp_deadline(deadline_raw: str):
    """Pull the DD-MM-YYYY date out of text like 'Student Application Open till : 31-10-2026'."""
    if not deadline_raw:
        return None
    match = re.search(r"(\d{2}-\d{2}-\d{4})", deadline_raw)
    if not match:
        return None
    from datetime import datetime
    try:
        return datetime.strptime(match.group(1), "%d-%m-%Y")
    except ValueError:
        return None


if __name__ == "__main__":
    # Run against the already-saved sample page first - no network call needed
    # to verify the extraction logic itself.
    with open("nsp_sample_page.html", "r", encoding="utf-8") as f:
        html = f.read()

    schemes = scrape_nsp_schemes(html)
    print(f"Found {len(schemes)} schemes\n")
    for s in schemes[:5]:
        print(s)
        print("Parsed deadline:", parse_nsp_deadline(s["deadlineRaw"]))
        print()