import pandas as pd
from features.underwriting_features import build_underwriting_features


def test_dispute_rate_calculation():

    df = pd.DataFrame({
        "merchant_id": ["M1"],
        "transaction_count": [100],
        "dispute_count": [5],
        "monthly_volume": [10000],
        "internal_last_30d_volume": [5000],
        "internal_last_30d_txn_count": [50],
        "internal_avg_ticket_size": [100],
        "geo_risk": ["low"],
        "internal_risk": ["medium"]
    })

    features = build_underwriting_features(df)

    assert features["dispute_rate"].iloc[0] == 0.05
