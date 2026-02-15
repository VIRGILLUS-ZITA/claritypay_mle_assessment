import requests
from bs4 import BeautifulSoup
import time
from datetime import datetime


URL = "https://claritypay.com"

HEADERS = {
    "User-Agent": "MLE-Assignment-Bot/1.0 (Educational Project; Respectful Scraping)"
}

REQUEST_DELAY_SECONDS = 1


# ------------------------------------------------------
# Logging Helpers
# ------------------------------------------------------
def log(message):
    now = datetime.now().strftime("%H:%M:%S")
    print(f"[{now}] [SCRAPER] {message}")


# ------------------------------------------------------
# Fetch Page
# ------------------------------------------------------
def fetch_page(url: str) -> str:
    log("Fetching claritypay.com homepage")
    time.sleep(REQUEST_DELAY_SECONDS)  # polite rate limiting

    response = requests.get(url, headers=HEADERS, timeout=10)
    response.raise_for_status()

    log("Page fetched successfully")
    return response.text


# ------------------------------------------------------
# Extract Value Propositions
# ------------------------------------------------------
def extract_value_propositions(soup):
    log("Extracting value propositions")

    propositions = []
    keywords = ["pay", "flexible", "transparent", "terms", "checkout"]

    for tag in soup.find_all(["h1", "h2", "h3", "p"]):
        text = tag.get_text(strip=True)

        if len(text) < 120 and any(k in text.lower() for k in keywords):
            propositions.append(text)

    unique_props = list(set(propositions))
    log(f"Found {len(unique_props)} potential value propositions")

    return unique_props


# ------------------------------------------------------
# Extract Public Stats
# ------------------------------------------------------
def extract_public_stats(soup):
    log("Extracting public statistics")

    stats = []

    for text in soup.stripped_strings:
        if any(char.isdigit() for char in text):
            if any(sym in text for sym in ["+", "$"]):
                if len(text) < 100:
                    stats.append(text)

    unique_stats = list(set(stats))
    log(f"Found {len(unique_stats)} potential public stats")

    return unique_stats


# ------------------------------------------------------
# Extract Partner Names
# ------------------------------------------------------
def extract_partners(soup):
    log("Extracting partner names")

    partners = []

    # Often partner names appear in image alt text
    for img in soup.find_all("img"):
        alt = img.get("alt")

        if alt and len(alt) < 50 and "logo" not in alt.lower():
            partners.append(alt.strip())

    unique_partners = list(set(partners))
    log(f"Found {len(unique_partners)} potential partners")

    return unique_partners


# ------------------------------------------------------
# Main Scraper Function
# ------------------------------------------------------
def scrape_claritypay():

    log("Starting scrape process")

    try:
        html = fetch_page(URL)
        soup = BeautifulSoup(html, "lxml")

        data = {
            "value_propositions": extract_value_propositions(soup),
            "partners": extract_partners(soup),
            "public_stats": extract_public_stats(soup)
        }

        log("Scraping completed successfully")
        return data

    except Exception as e:
        log(f"Scraping failed: {e}")
        return {
            "value_propositions": [],
            "partners": [],
            "public_stats": [],
            "error": str(e)
        }
