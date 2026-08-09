from bs4 import BeautifulSoup

with open("nsp_sample_page.html", "r", encoding="utf-8") as f:
    html = f.read()
    soup = BeautifulSoup(html, "html.parser")

# Check several possible fragments, since the real wording/spacing might
# differ from what we expected.
candidates = ["Scheme Open", "Open from", "Specifications", "AICTE", "Application Open till"]
for text in candidates:
    count = html.count(text)
    print(f"'{text}' appears {count} times in the raw HTML")

print()
print("=== All <a> tags whose text is exactly 'Specifications' (we know this appears on the real page) ===")
spec_links = soup.find_all("a", string="Specifications")
print(f"Found {len(spec_links)} matching links")
if spec_links:
    first = spec_links[0]
    print("First one:", first)
    print()
    print("--- Its parent chain (3 levels up) ---")
    el = first
    for level in range(3):
        el = el.find_parent()
        if el is None:
            break
        print(f"Level {level}: tag={el.name} class={el.get('class')}")
        print(str(el)[:400])
        print()