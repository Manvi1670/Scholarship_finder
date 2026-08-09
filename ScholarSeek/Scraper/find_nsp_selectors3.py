from bs4 import BeautifulSoup

with open("nsp_sample_page.html", "r", encoding="utf-8") as f:
    soup = BeautifulSoup(f.read(), "html.parser")

containers = soup.find_all("div", class_="row mb-4 border-1 border-bottom")
print(f"Found {len(containers)} scheme containers total\n")

if containers:
    first = containers[0]
    print("=== Full text of the first scheme container ===")
    print(first.get_text(" | ", strip=True))
    print()
    print("=== Raw HTML of the status span specifically ===")
    status_span = first.find("span", class_="d-inline-block")
    print(status_span)