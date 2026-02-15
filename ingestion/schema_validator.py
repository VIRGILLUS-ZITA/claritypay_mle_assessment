import pandas as pd

REQUIRED_COLUMNS = [
    "merchant_id",
    "name",
    "country",
    "registration_number",
    "monthly_volume",
    "transaction_count",
    "dispute_count"
]


def validate_schema_columns(df: pd.DataFrame):
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")


def validate_rows(df: pd.DataFrame):
    """
    Returns:
        valid_df, invalid_df
    """

    invalid_mask = (
        df["merchant_id"].isna()
        | df["country"].isna()
        | (df["monthly_volume"] < 0)
        | (df["transaction_count"] < 0)
        | (df["dispute_count"] < 0)
        | (df["dispute_count"] > df["transaction_count"])
    )

    invalid_df = df[invalid_mask].copy()
    valid_df = df[~invalid_mask].copy()

    return valid_df, invalid_df
