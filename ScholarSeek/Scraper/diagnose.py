import requests
from bs4 import BeautifulSoup

url = "https://www.buddy4study.com/scholarship/university-of-birmingham-postgraduate-high-fliers-scholarship-2026"
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

response = requests.get(url, headers=headers, timeout=15)
html = response.text

# Save the raw HTML so you can open and search it yourself too
with open("sample_detail_page.html", "w", encoding="utf-8") as f:
    f.write(html)

print("Status code:", response.status_code)
print("HTML length:", len(html), "characters")
print()

# THE KEY TEST: does the scholarship's actual name text appear anywhere
# in the raw HTML we got back? If yes -> page is static, our selectors are
# just wrong. If no -> page is JS-rendered, we need Selenium here too.
if "Birmingham" in html:
    print("FOUND 'Birmingham' in the raw HTML -> page IS static.")
    print("-> Our selectors are wrong, not the fetching method. Need to find real class names.")
else:
    print("'Birmingham' NOT found in raw HTML -> page is JS-rendered (dynamic).")
    print("-> We need Selenium for detail pages too, same as listing pages.")

print()

# Bonus: print every h1 on the page - the scholarship title is almost always
# in an h1, so this alone often reveals the real class name immediately.
soup = BeautifulSoup(html, "html.parser")
print("All <h1> tags found on this page:")
for h1 in soup.find_all("h1"):
    print(" ", h1)