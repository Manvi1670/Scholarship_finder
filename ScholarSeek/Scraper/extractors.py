"""
Pure functions that turn messy scraped text into structured data.
Keeping these separate from the scraping code means you can unit-test
them with plain strings, with no network or browser involved at all.
"""
import re
from datetime import datetime


def classify_award(award_text: str) -> str:
    """Categorize an award description into a fixed set of types."""
    if not award_text:
        return "other"

    text = award_text.lower()

    has_currency = bool(re.search(
        r"(inr|rs\.?|₹|\$|£|€|usd|gbp|eur|aud|cad|chf|nzd|sgd|jpy|yen)\s?[\d,]+",
        text,
    ))
    has_waiver = "tuition" in text and ("waiver" in text or "waive" in text)

    if has_currency and has_waiver:
        return "mixed"
    if has_currency:
        return "monetary"
    if has_waiver:
        return "tuition_waiver"
    if any(word in text for word in ["certificate", "internship", "mentorship", "kit"]):
        return "non_monetary"
    return "other"


def extract_min_cpi(eligibility_text: str):
    """
    Pull a minimum CPI/CGPA/percentage requirement out of free text like
    'Minimum 60% marks' or 'CGPA of 6.5 or above required'.
    Returns a float on a 0-10 scale, or None if nothing was found.
    """
    if not eligibility_text:
        return None

    text = eligibility_text.lower()

    # Pattern: "CGPA 6.5", "CPI of 7", "GPA: 8.0"
    cgpa_match = re.search(r"(?:cgpa|cpi|gpa)\D{0,5}(\d+(?:\.\d+)?)", text)
    if cgpa_match:
        return float(cgpa_match.group(1))

    # Only trust a bare percentage as an academic requirement if it's tied
    # to marks/aggregate/score, or preceded by "minimum" - otherwise a
    # percentage is very often an AWARD amount ("90% tuition fee waiver"),
    # not an eligibility bar, and would corrupt the CPI field if matched.
    percent_match = re.search(
        r"(\d{1,3})\s?%\s*(?:marks|aggregate|score|scored)"
        r"|(?:minimum|min\.?)\s*(?:of\s*)?(\d{1,3})\s?%",
        text,
    )
    if percent_match:
        value = percent_match.group(1) or percent_match.group(2)
        return round(float(value) / 10, 1)

    return None


# Rough, fixed conversion rates to INR - good enough to RANK scholarships by
# scale, not for financial accuracy. Only the first amount mentioned in the
# text is used (later parenthetical "approx conversions" are ignored).
_CURRENCY_TO_INR = {
    "inr": 1, "rs": 1, "₹": 1,
    "usd": 83, "$": 83,
    "eur": 90, "€": 90,
    "gbp": 105, "£": 105,
    "aud": 55,
    "cad": 61,
    "chf": 95,
    "nzd": 50,
    "sgd": 62,
}


def extract_award_amount_inr(award_text: str):
    """
    Pull the first currency+number out of award text and convert it to a
    rough INR figure, purely for ranking scholarships by scale. Returns
    None for non-monetary text ("Variable benefits", "Mentorship", etc.)
    """
    if not award_text:
        return None

    text = award_text.lower()
    match = re.search(
        r"(inr|rs\.?|₹|\$|£|€|usd|gbp|eur|aud|cad|chf|nzd|sgd)\s?([\d,]+(?:\.\d+)?)",
        text,
    )
    if not match:
        return None

    currency = match.group(1).replace(".", "")
    amount_str = match.group(2).replace(",", "")
    try:
        amount = float(amount_str)
    except ValueError:
        return None

    rate = _CURRENCY_TO_INR.get(currency, 1)
    return round(amount * rate)


def parse_deadline(deadline_text: str):
    """
    Try a handful of known date formats. Returns a datetime, or None for
    things like 'Always Open' that aren't a real date - never guess.
    """
    if not deadline_text:
        return None

    text = deadline_text.strip()
    if "always open" in text.lower() or "ongoing" in text.lower():
        return None

    known_formats = ["%d %b %Y", "%d %B %Y", "%B %d, %Y", "%d/%m/%Y", "%d-%b-%Y", "%d-%B-%Y"]
    for fmt in known_formats:
        try:
            return datetime.strptime(text, fmt)
        except ValueError:
            continue
    return None  # didn't match any known format - log this, don't crash


def extract_contact(contact_text: str):
    """Pull an email and phone number out of a contact block, if present."""
    email = None
    phone = None
    if contact_text:
        email_match = re.search(r"[\w.+-]+@[\w-]+\.[\w.-]+", contact_text)
        phone_match = re.search(r"(\+?\d[\d\s-]{8,13}\d)", contact_text)
        email = email_match.group(0) if email_match else None
        phone = phone_match.group(0) if phone_match else None
    return email, phone