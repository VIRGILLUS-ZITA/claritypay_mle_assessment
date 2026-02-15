import pandas as pd
from model.train_risk_model import predict_risk


def test_prediction_output(tmp_path):

    df = pd.DataFrame({
        "dispute_rate":[0.01],
        "monthly_volume":[10000],
        "internal_last_30d_volume":[5000],
        "internal_last_30d_txn_count":[50],
        "internal_avg_ticket_size":[100],
        "geo_risk":["low"],
        "internal_risk":["medium"]
    })

    model_path = "models/risk_model.pkl"

    result = predict_risk(df, model_path)

    assert "risk_probability" in result.columns
