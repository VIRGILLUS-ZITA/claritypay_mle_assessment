import pandas as pd


# ------------------------------------------------------
# Merge predictions with merchant data
# ------------------------------------------------------
def merge_predictions(final_df: pd.DataFrame, scored_df: pd.DataFrame) -> pd.DataFrame:

    merged = final_df.merge(
        scored_df[["merchant_id", "risk_probability", "predicted_high_risk"]],
        on="merchant_id",
        how="inner"
    )

    return merged


# ------------------------------------------------------
# Compute portfolio risk metrics
# ------------------------------------------------------
def compute_portfolio_metrics(merged: pd.DataFrame) -> dict:

    total_merchants = len(merged)

    high_risk = merged[merged["predicted_high_risk"] == 1]
    low_risk = merged[merged["predicted_high_risk"] == 0]

    high_risk_merchants = len(high_risk)
    high_risk_ratio = high_risk_merchants / total_merchants if total_merchants else 0

    # exposure based on volume
    high_risk_volume = high_risk["monthly_volume"].sum()

    # expected disputes approximation
    expected_disputes = (merged["risk_probability"] * merged["transaction_count"]).sum()

    avg_risk_probability = merged["risk_probability"].mean()

    metrics = {
        "total_merchants": total_merchants,
        "high_risk_merchants": high_risk_merchants,
        "high_risk_ratio": round(high_risk_ratio, 3),
        "high_risk_volume": round(high_risk_volume, 2),
        "expected_disputes": round(expected_disputes, 2),
        "avg_risk_probability": round(avg_risk_probability, 3)
    }

    return metrics


# ------------------------------------------------------
# Pretty print summary
# ------------------------------------------------------
def print_portfolio_summary(metrics: dict):

    print("\n========== PORTFOLIO RISK SUMMARY ==========")
    print(f"Total merchants: {metrics['total_merchants']}")
    print(f"High-risk merchants: {metrics['high_risk_merchants']} ({metrics['high_risk_ratio']*100:.1f}%)")
    print(f"High-risk exposure volume: {metrics['high_risk_volume']}")
    print(f"Expected disputes (est): {metrics['expected_disputes']}")
    print(f"Average portfolio risk score: {metrics['avg_risk_probability']}")
    print("=============================================\n")


# ------------------------------------------------------
# Full pipeline function
# ------------------------------------------------------
def generate_portfolio_risk(final_df: pd.DataFrame, scored_df: pd.DataFrame):

    merged = merge_predictions(final_df, scored_df)

    metrics = compute_portfolio_metrics(merged)

    print_portfolio_summary(metrics)

    return metrics, merged
