import requests
from time import sleep

BASE_URL = "http://127.0.0.1:8000"
TIMEOUT = 3
RETRIES = 3


def get_internal_risk(merchant_id: str):
    """
    Fetch merchant internal risk data from simulated internal API
    Returns JSON dict or None if failed
    """

    url = f"{BASE_URL}/merchant/{merchant_id}"

    for attempt in range(RETRIES):
        try:
            response = requests.get(url, timeout=TIMEOUT)

            if response.status_code == 404:
                return None

            response.raise_for_status()
            return response.json()

        except requests.RequestException:
            if attempt < RETRIES - 1:
                sleep(1)  # retry delay
            else:
                return None
