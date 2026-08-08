import json

with open("scholarships.json", "r", encoding="utf-8") as f:
    data = json.load(f)

before = len(data)

# Drop exact duplicate URLs (keep first occurrence)
seen = set()
deduped = []
for r in data:
    url = r.get("sourceUrl")
    if url not in seen:
        seen.add(url)
        deduped.append(r)
duplicates_removed = before - len(deduped)

# Drop records with no name - these are unusable for matching/display either way
cleaned = [r for r in deduped if r.get("name")]
nulls_removed = len(deduped) - len(cleaned)

with open("scholarships_clean.json", "w", encoding="utf-8") as f:
    json.dump(cleaned, f, indent=2, default=str)

print(f"Started with:        {before}")
print(f"Duplicates removed:  {duplicates_removed}")
print(f"Null-name removed:   {nulls_removed}")
print(f"Final clean count:   {len(cleaned)}")
print(f"Saved to: scholarships_clean.json")