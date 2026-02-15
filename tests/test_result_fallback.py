from reporting.generate_report import rule_based_report


def test_rule_based_report():

    metrics = {
        "total_merchants": 10,
        "high_risk_merchants": 5,
        "high_risk_ratio": 0.5,
        "high_risk_volume": 10000,
        "expected_disputes": 20,
        "avg_risk_probability": 0.4
    }

    text = rule_based_report(metrics)

    assert "elevated" in text.lower()
