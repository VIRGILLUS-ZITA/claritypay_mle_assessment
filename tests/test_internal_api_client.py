import requests
from unittest.mock import patch
from ingestion.internal_service_client import get_internal_risk


@patch("ingestion.internal_service_client.requests.get")
def test_internal_api_success(mock_get):

    mock_get.return_value.status_code = 200
    mock_get.return_value.json.return_value = {
        "merchant_id": "M001",
        "internal_risk_flag": "low",
        "transaction_summary": {
            "last_30d_volume": 1000,
            "last_30d_txn_count": 50,
            "avg_ticket_size": 20
        }
    }

    result = get_internal_risk("M001")
    assert result["internal_risk_flag"] == "low"
