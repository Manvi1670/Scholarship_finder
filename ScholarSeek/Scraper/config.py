BASE_URL = "https://www.buddy4study.com"

# Each category has its own listing URL pattern. Add more sources here later
# by giving each one its own entry - the rest of the scraper doesn't change.
CATEGORIES = {
    "live": "/scholarships",
    "upcoming": "/upcoming-scholarships",
    "always_open": "/open-scholarships",
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/120.0 Safari/537.36"
}

REQUEST_TIMEOUT = 15          # seconds - give up if the server doesn't respond
RATE_LIMIT_SECONDS = 1.5      # pause between requests - be a polite scraper
MAX_RETRIES = 3               # retry a failed request this many times before giving up
MAX_PAGES_PER_CATEGORY = 10   # safety cap so a bug can't loop forever

OUTPUT_FILE = "scholarships.json"
LOG_FILE = "scrape_log.txt"