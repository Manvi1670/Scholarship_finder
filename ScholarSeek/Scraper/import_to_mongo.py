from dotenv import load_dotenv
import os
import json
from pymongo import MongoClient, UpdateOne
from pymongo.errors import ServerSelectionTimeoutError

load_dotenv()
uri = os.getenv("MONGO_URI")
db_name = os.getenv("DB_NAME", "scholarship_finder")
INPUT_FILE = "scholarships_clean.json"


def main():
    if not uri:
        print("MONGO_URI not found - check your .env file")
        return

    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        records = json.load(f)
    print(f"Loaded {len(records)} records from {INPUT_FILE}")

    try:
        client = MongoClient(uri, serverSelectionTimeoutMS=8000)
        client.admin.command("ping")
    except ServerSelectionTimeoutError as e:
        print("Could not reach MongoDB - check your .env and Atlas Network Access settings")
        print("Details:", e)
        return

    db = client[db_name]
    collection = db["scholarships"]

    # Enforce uniqueness at the database level too, not just in our own
    # code - this makes accidental duplicate inserts impossible even if
    # this script is run in a weird way later.
    collection.create_index("sourceUrl", unique=True)

    # Build one upsert operation per record: match on sourceUrl, replace
    # the rest of the fields, insert if it doesn't exist yet. bulk_write
    # sends these in one batch instead of one round-trip per record.
    operations = [
        UpdateOne({"sourceUrl": r["sourceUrl"]}, {"$set": r}, upsert=True)
        for r in records
        if r.get("sourceUrl")  # skip anything missing our dedup key entirely
    ]

    if not operations:
        print("No valid records to import (all missing sourceUrl)")
        return

    result = collection.bulk_write(operations)

    print()
    print(f"Inserted (new):  {result.upserted_count}")
    print(f"Updated (existing): {result.modified_count}")
    print(f"Total documents in collection now: {collection.count_documents({})}")


if __name__ == "__main__":
    main()