from dotenv import load_dotenv
import os
import json
from pymongo import MongoClient, UpdateOne
from pymongo.errors import ServerSelectionTimeoutError

load_dotenv()
uri = os.getenv("MONGO_URI")
db_name = os.getenv("DB_NAME", "scholarship_finder")
INPUT_FILE = "nsp_scholarships_deduped.json"


def main():
    if not uri:
        print("MONGO_URI not found - check your .env file")
        return

    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        records = json.load(f)
    print(f"Loaded {len(records)} deduped NSP records from {INPUT_FILE}")

    try:
        client = MongoClient(uri, serverSelectionTimeoutMS=8000)
        client.admin.command("ping")
    except ServerSelectionTimeoutError as e:
        print("Could not reach MongoDB:", e)
        return

    db = client[db_name]
    collection = db["scholarships"]

    # Same unique index as before - sourceUrl is unique per record here too
    # (each NSP scheme's specificationsUrl), so this stays safe to rerun later.
    collection.create_index("sourceUrl", unique=True)

    operations = [
        UpdateOne({"sourceUrl": r["sourceUrl"]}, {"$set": r}, upsert=True)
        for r in records
        if r.get("sourceUrl")
    ]

    if not operations:
        print("No valid records to import")
        return

    result = collection.bulk_write(operations)

    print(f"\nInserted (new):     {result.upserted_count}")
    print(f"Updated (existing):  {result.modified_count}")
    print(f"Total documents in collection now: {collection.count_documents({})}")
    print(f"Total NSP-sourced documents: {collection.count_documents({'source': 'nsp'})}")


if __name__ == "__main__":
    main()