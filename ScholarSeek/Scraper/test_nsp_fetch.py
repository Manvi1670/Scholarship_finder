import requests
from bs4 import BeautifulSoup

url = "https://scholarships.gov.in/All-Scholarships"
headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}

response = requests.get(url, headers=headers, timeout=15)
html = response.text

with open("nsp_sample_page.html", "w", encoding="utf-8") as f:
    f.write(html)

print("Status code:", response.status_code)
print("HTML length:", len(html), "characters")
print()

# The real test: does actual scheme content show up, or did we get
# redirected to a login/error page instead?
if "Scheme Open from" in html or "AICTE" in html:
    print("FOUND real scheme content -> plain requests works, no session needed.")
else:
    print("Real scheme content NOT found -> likely redirected/blocked.")
    print("First 500 characters of what we actually got:")
    print(html[:500])