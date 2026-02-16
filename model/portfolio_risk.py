from fastapi import logger
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
def print_portfolio_summary(metrics: dict, logger):
    # 1. Build the multi-line string block
    summary_block = (
        "\n========== PORTFOLIO RISK SUMMARY ==========\n"
        f"Total merchants:               {metrics['total_merchants']}\n"
        f"High-risk merchants:           {metrics['high_risk_merchants']} ({metrics['high_risk_ratio']*100:.1f}%)\n"
        f"High-risk exposure volume:     {metrics['high_risk_volume']}\n"
        f"Expected disputes (est):       {metrics['expected_disputes']}\n"
        f"Average portfolio risk score:  {metrics['avg_risk_probability']:.4f}\n"
        "============================================="
    )

    # 2. Print to terminal
    print(summary_block)

    # 3. Log to file as a single entry
    # This ensures the "box" looks perfect in your log file
    logger.info(summary_block)

# ------------------------------------------------------
# Full pipeline function
# ------------------------------------------------------
def generate_portfolio_risk(final_df: pd.DataFrame, scored_df: pd.DataFrame, logger):

    merged = merge_predictions(final_df, scored_df)

    metrics = compute_portfolio_metrics(merged)

    print_portfolio_summary(metrics, logger)

    return metrics, merged
