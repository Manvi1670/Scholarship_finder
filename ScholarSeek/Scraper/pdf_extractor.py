import re
import requests
import pdfplumber
import io

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}


def download_pdf_text(url: str):
    """
    Downloads a PDF and extracts its text. Returns None (not an error) if
    the PDF has no extractable text - this is common for scanned government
    documents, and it's a real, expected outcome, not a bug to fix.
    """
    try:
        response = requests.get(url, headers=HEADERS, timeout=20)
        response.raise_for_status()
    except requests.exceptions.RequestException:
        return None

    try:
        with pdfplumber.open(io.BytesIO(response.content)) as pdf:
            text_parts = [page.extract_text() or "" for page in pdf.pages]
            full_text = "\n".join(text_parts).strip()
            return full_text if full_text else None
    except Exception:
        # Corrupt/unreadable PDF - same graceful "we just don't have this one" outcome
        return None


def extract_eligibility_section(pdf_text: str):
    """
    Finds the eligibility section within the PDF text. Government PDFs
    commonly use a numbered heading like '2.0 ELIGIBILITY...' - we grab
    text between that heading and the next numbered section.
    """
    if not pdf_text:
        return None

    # Look for a line that's clearly an "eligibility" heading (numbered or not)
    match = re.search(
        r"(?:\d\.\d\s*)?ELIGIBILITY[^\n]*\n(.*?)(?=\n\s*\d\.\d\s+[A-Z]{3,}|\Z)",
        pdf_text,
        re.IGNORECASE | re.DOTALL,
    )
    if not match:
        return None

    section = match.group(1).strip()
    # Cap length - some sections run for pages; a summary-length excerpt is
    # more useful for matching/display than the entire raw block.
    return section[:1500]


def extract_amount_section(pdf_text: str):
    """Same pattern as eligibility, but for the 'AMOUNT OF SCHOLARSHIP' heading."""
    if not pdf_text:
        return None
    match = re.search(
        r"(?:\d\.\d\s*)?AMOUNT OF SCHOLARSHIP[^\n]*\n(.*?)(?=\n\s*\d\.\d\s+[A-Z]{3,}|\Z)",
        pdf_text,
        re.IGNORECASE | re.DOTALL,
    )
    if not match:
        return None
    return match.group(1).strip()[:800]


if __name__ == "__main__":
    # Test against the two real URLs we already confirmed behave differently
    test_urls = [
        "https://scholarships.gov.in/public/schemeGuidelines/warb/PMSS_Guidelines_1197_3001-2023-24.pdf",  # known: no text
        "https://scholarships.gov.in/public/schemeGuidelines/AICTE/AICTE_3039_G.pdf",  # known: has real text
    ]

    for url in test_urls:
        print(f"--- {url} ---")
        text = download_pdf_text(url)
        if text is None:
            print("No extractable text (likely scanned - this is expected, not an error)")
        else:
            print(f"Got {len(text)} characters of text")
            eligibility = extract_eligibility_section(text)
            print("Eligibility section found:", bool(eligibility))
            if eligibility:
                print(eligibility[:400], "...")
        print()