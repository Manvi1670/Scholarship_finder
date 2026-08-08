"""
Fixes the 'deadline: null despite a valid deadlineRaw' gap without
re-scraping anything - just re-runs the (already fixed) date parser over
what's already stored in MongoDB and updates the deadline field in place.

Run this once: python backfill_deadlines.py
"""
from dotenv import load_dotenv
import os
from datetime import datetime
from pymongo import MongoClient, UpdateOne

load_dotenv()
uri = os.getenv("MONGO_URI")
db_name = os.getenv("DB_NAME", "scholarship_finder")


def parse_deadline(deadline_text):
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
    return None


def main():
    if not uri:
        print("MONGO_URI not found - check your .env file")
        return

    client = MongoClient(uri, serverSelectionTimeoutMS=8000)
    db = client[db_name]
    collection = db["scholarships"]

    docs = list(collection.find({}, {"_id": 1, "deadlineRaw": 1, "deadline": 1}))
    print(f"Checking {len(docs)} documents...")

    operations = []
    for doc in docs:
        parsed = parse_deadline(doc.get("deadlineRaw"))
        # Only update documents where the newly parsed value actually differs
        # from what's stored - avoids touching documents that were already correct.
        current = doc.get("deadline")
        if parsed and not current:
            operations.append(UpdateOne({"_id": doc["_id"]}, {"$set": {"deadline": parsed}}))

    if not operations:
        print("Nothing to update - all deadlines already correctly parsed.")
        return

    result = collection.bulk_write(operations)
    print(f"Backfilled {result.modified_count} documents with a real deadline date.")


if __name__ == "__main__":
    main()