import pandas as pd


HIGH_RISK_REGIONS = {"Africa", "South America"}
MEDIUM_RISK_REGIONS = {"Asia"}


def classify_volume(volume):
    if volume >= 100000:
        return "high"
    elif volume >= 10000:
        return "medium"
    return "low"


def classify_geo_risk(region):
    if region in HIGH_RISK_REGIONS:
        return "high"
    if region in MEDIUM_RISK_REGIONS:
        return "medium"
    return "low"


def build_underwriting_features(enriched_df: pd.DataFrame) -> pd.DataFrame:

    df = enriched_df.copy()

    # --- behavioral risk ---
    df["dispute_rate"] = df["dispute_count"] / df["transaction_count"].replace(0, 1)

    df["behavior_risk"] = pd.cut(
        df["dispute_rate"],
        bins=[-1, 0.005, 0.02, 1],
        labels=["low", "medium", "high"]
    )

    # --- volume tier ---
    df["volume_tier"] = df["monthly_volume"].apply(classify_volume)

    # --- geo risk ---
    if "region" in df.columns:
        df["geo_risk"] = df["region"].apply(classify_geo_risk)
    else:
        # allow precomputed geo_risk OR default
        df["geo_risk"] = df.get("geo_risk", "unknown")

    # --- internal risk already exists ---
    df["internal_risk"] = df["internal_risk_flag"]

    # --- heuristic combined signal ---
    df["overall_risk_hint"] = (
        df["behavior_risk"].astype(str) + "_" +
        df["geo_risk"].astype(str) + "_" +
        df["internal_risk"].astype(str)
    )

    return df[[
        "merchant_id",
        "country",
        "region",

        # merchant activity
        "monthly_volume",
        "transaction_count",
        "dispute_count",
        "dispute_rate",

        # internal behavior (IMPORTANT)
        "internal_last_30d_volume",
        "internal_last_30d_txn_count",
        "internal_avg_ticket_size",

        # interpreted risk signals
        "volume_tier",
        "geo_risk",
        "behavior_risk",
        "internal_risk",

        # combined hint
        "overall_risk_hint"
    ]]

