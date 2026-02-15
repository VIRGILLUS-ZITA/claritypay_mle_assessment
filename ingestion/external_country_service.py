import requests
from urllib.parse import quote
from time import sleep

BASE_URL = "https://restcountries.com/v3.1/name"
TIMEOUT = 5
RETRIES = 3

# in-memory cache
_country_cache = {}


def get_country_details(country_name: str):
    """
    Fetch region & subregion from REST Countries API
    Uses caching to prevent repeated API calls
    Returns dict or None
    """

    if not isinstance(country_name, str) or not country_name.strip():
        return None

    country_name = country_name.strip()

    # ---- cache check ----
    if country_name in _country_cache:
        return _country_cache[country_name]

    url = f"{BASE_URL}/{quote(country_name)}"

    for attempt in range(RETRIES):
        try:
            response = requests.get(url, timeout=TIMEOUT)

            if response.status_code == 404:
                _country_cache[country_name] = None
                return None

            response.raise_for_status()

            data = response.json()[0]

            result = {
                "country_name": data.get("name", {}).get("common"),
                "region": data.get("region"),
                "subregion": data.get("subregion")
            }

            _country_cache[country_name] = result
            return result

        except requests.RequestException:
            if attempt < RETRIES - 1:
                sleep(1)
            else:
                _country_cache[country_name] = None
                return None
