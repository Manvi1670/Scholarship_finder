from bs4 import BeautifulSoup

with open("nsp_sample_page.html", "r", encoding="utf-8") as f:
    soup = BeautifulSoup(f.read(), "html.parser")

# Find an element containing "Scheme Open from" - this text appears once
# per scheme, so it's our anchor for locating the repeating container.
anchor = soup.find(string=lambda s: s and "Scheme Open from" in s)

if not anchor:
    print("Could not find 'Scheme Open from' text - structure may differ from what we saw earlier")
else:
    # Walk up a few parent levels and print each one, so we can see which
    # level is the actual repeating "card" for one scheme.
    element = anchor.find_parent()
    for level in range(4):
        print(f"--- Parent level {level} ---")
        print("Tag:", element.name, "| class:", element.get("class"))
        print(str(element)[:300])
        print()
        element = element.find_parent()
        if element is None:
            break

print("=== Heading right before the first 'Scheme Open from' (likely the scheme name) ===")
heading = anchor.find_previous(["h1", "h2", "h3", "h4", "h5", "h6"])
print(heading)