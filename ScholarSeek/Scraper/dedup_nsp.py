import json
import difflib
from dotenv import load_dotenv
import os
from pymongo import MongoClient

load_dotenv()
uri = os.getenv("MONGO_URI")
db_name = os.getenv("DB_NAME", "scholarship_finder")

SIMILARITY_THRESHOLD = 0.75  # tuned to catch near-identical names, not unrelated ones


import re

STOPWORDS = {"the", "for", "of", "and", "a", "an", "scheme", "scholarship", "nsp", "based", "merit"}


def normalize(name: str) -> set:
    """Returns a set of meaningful words, stripped of punctuation/parentheses/stopwords."""
    if not name:
        return set()
    text = re.sub(r"\([^)]*\)", " ", name.lower())  # drop parenthetical padding entirely
    words = re.findall(r"[a-z0-9]+", text)
    # Crude singularization (girls -> girl) - not linguistically perfect, but
    # catches the common case that was causing real duplicates to be missed.
    words = [w[:-1] if w.endswith("s") and len(w) > 4 else w for w in words]
    return {w for w in words if w not in STOPWORDS and len(w) > 2}


def word_overlap_similarity(a: set, b: set) -> float:
    """Jaccard similarity - handles reordered/padded titles far better than character matching."""
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def main():
    with open("nsp_scholarships.json", "r", encoding="utf-8") as f:
        nsp_records = json.load(f)
    print(f"Loaded {len(nsp_records)} NSP records")

    client = MongoClient(uri, serverSelectionTimeoutMS=8000)
    db = client[db_name]
    collection = db["scholarships"]

    # Only compare against existing buddy4study entries, not NSP entries from
    # a previous run of this same script - avoids comparing NSP against itself.
    existing = list(collection.find({"source": {"$ne": "nsp"}}, {"name": 1}))
    existing_names = [(doc.get("name", ""), normalize(doc.get("name", ""))) for doc in existing]
    print(f"Comparing against {len(existing_names)} existing entries")

    unique_records = []
    duplicates = []

    for record in nsp_records:
        norm_name = normalize(record["name"])
        best_match = None
        best_ratio = 0

        for existing_original, existing_normalized in existing_names:
            ratio = word_overlap_similarity(norm_name, existing_normalized)
            if ratio > best_ratio:
                best_ratio = ratio
                best_match = existing_original

        if best_ratio >= SIMILARITY_THRESHOLD:
            duplicates.append({"name": record["name"], "matched": best_match, "similarity": round(best_ratio, 2)})
        else:
            unique_records.append(record)

    with open("nsp_scholarships_deduped.json", "w", encoding="utf-8") as f:
        json.dump(unique_records, f, indent=2, default=str)

    print(f"\nUnique (new) NSP records: {len(unique_records)}")
    print(f"Likely duplicates found: {len(duplicates)}")
    if duplicates:
        print("\nDuplicates flagged (review these - not deleted, just excluded from output):")
        for d in duplicates:
            print(f"  '{d['name'][:60]}' ~= existing '{d['matched'][:60]}' (similarity {d['similarity']})")


if __name__ == "__main__":
    main()