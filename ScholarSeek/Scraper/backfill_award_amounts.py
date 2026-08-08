"""
Adds a comparable awardAmountINR figure to existing scholarships, computed
from the already-scraped awardRaw text. No re-scraping needed.

Run this once: python backfill_award_amounts.py
"""
from dotenv import load_dotenv
import os
import re
from pymongo import MongoClient, UpdateOne

load_dotenv()
uri = os.getenv("MONGO_URI")
db_name = os.getenv("DB_NAME", "scholarship_finder")

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


def extract_award_amount_inr(award_text):
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
    return round(amount * _CURRENCY_TO_INR.get(currency, 1))


def main():
    if not uri:
        print("MONGO_URI not found - check your .env file")
        return

    client = MongoClient(uri, serverSelectionTimeoutMS=8000)
    db = client[db_name]
    collection = db["scholarships"]

    docs = list(collection.find({}, {"_id": 1, "awardRaw": 1, "awardAmountINR": 1}))
    print(f"Checking {len(docs)} documents...")

    operations = []
    for doc in docs:
        amount = extract_award_amount_inr(doc.get("awardRaw"))
        if amount is not None and doc.get("awardAmountINR") != amount:
            operations.append(UpdateOne({"_id": doc["_id"]}, {"$set": {"awardAmountINR": amount}}))

    if not operations:
        print("Nothing to update.")
        return

    result = collection.bulk_write(operations)
    print(f"Backfilled {result.modified_count} documents with an award amount.")


if __name__ == "__main__":
    main()