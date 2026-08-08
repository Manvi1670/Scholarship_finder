"""
Stage 1: use Selenium to walk the (JS-rendered) listing pages and collect
every scholarship detail-page URL. We do NOT extract scholarship fields
here - listing pages only have enough info to build a URL list.
"""
import time
import logging
from urllib.robotparser import RobotFileParser
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup

from config import BASE_URL, CATEGORIES, MAX_PAGES_PER_CATEGORY, RATE_LIMIT_SECONDS

LISTING_ITEM_CLASS = "Listing_categoriesBox__CiGvQ"  # verify this in DevTools - sites change these


def robots_allows(path: str) -> bool:
    rp = RobotFileParser()
    rp.set_url(f"{BASE_URL}/robots.txt")
    rp.read()
    return rp.can_fetch("*", f"{BASE_URL}{path}")


def make_driver():
    options = Options()
    options.add_argument("--headless=new")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    return webdriver.Chrome(options=options)


def collect_links_for_category(driver, category_name: str, path: str) -> set:
    links = set()
    page = 1

    while page <= MAX_PAGES_PER_CATEGORY:
        url = f"{BASE_URL}{path}?page={page}"

        if not robots_allows(path):
            logging.warning(f"robots.txt disallows {path} - skipping category {category_name}")
            break

        logging.info(f"[{category_name}] loading page {page}: {url}")
        driver.get(url)

        try:
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, LISTING_ITEM_CLASS))
            )
        except Exception:
            # No items found on this page within the timeout - assume we've
            # run past the last page and stop, rather than crashing.
            logging.info(f"[{category_name}] no items found on page {page} - stopping category")
            break

        soup = BeautifulSoup(driver.page_source, "html.parser")
        items = soup.find_all("a", class_=LISTING_ITEM_CLASS)

        if not items:
            break

        for item in items:
            href = item.get("href")
            if href and "/scholarship/" in href:
                full_url = href if href.startswith("http") else f"{BASE_URL}{href}"
                links.add(full_url)

        page += 1
        time.sleep(RATE_LIMIT_SECONDS)

    return links


def collect_all_links() -> set:
    driver = make_driver()
    all_links = set()
    try:
        for category_name, path in CATEGORIES.items():
            category_links = collect_links_for_category(driver, category_name, path)
            logging.info(f"[{category_name}] collected {len(category_links)} links")
            all_links |= category_links
    finally:
        driver.quit()
    return all_links