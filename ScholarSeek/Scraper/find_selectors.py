from bs4 import BeautifulSoup

with open("sample_detail_page.html", "r", encoding="utf-8") as f:
    soup = BeautifulSoup(f.read(), "html.parser")


def show_field(label_text):
    """
    Find the element containing this exact label (e.g. 'Eligibility'),
    then print it and its next sibling - the label and the actual value
    are usually right next to each other in the markup.
    """
    label_el = soup.find(string=lambda s: s and s.strip() == label_text)
    if not label_el:
        print(f"'{label_text}': not found verbatim - may need a partial match instead")
        return

    container = label_el.find_parent()
    print(f"--- {label_text} ---")
    print("Label element:", container)
    sibling = container.find_next_sibling()
    print("Next sibling (likely the value):", sibling)
    print()


for field in ["Eligibility", "Region", "Award", "Deadline", "Contact Details"]:
    show_field(field)

print("--- H1 (title) ---")
print(soup.find("h1"))
print()

print("--- Links containing 'apply' in href or text ---")
for a in soup.find_all("a"):
    text = a.get_text(strip=True).lower()
    href = (a.get("href") or "").lower()
    if "apply" in text or "apply" in href:
        print(a)

print()
print("--- Element with id='contactdetails' ---")
contact_el = soup.find(id="contactdetails")
print(contact_el)

print()
print("--- Heading containing 'About' (description section) ---")
about_heading = soup.find(string=lambda s: s and "About" in s and len(s.strip()) < 40)
if about_heading:
    container = about_heading.find_parent()
    print("Heading element:", container)
    print("Next sibling:", container.find_next_sibling())
else:
    print("Not found - paste more of the page structure if this happens")