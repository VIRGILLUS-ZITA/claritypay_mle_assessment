import pandas as pd
import pytest
from ingestion.schema_validator import validate_schema_columns


def test_valid_schema():
    df = pd.DataFrame({
        "merchant_id": ["M001"],
        "name": ["Test"],
        "country": ["UK"],
        "registration_number": ["123"],
        "monthly_volume": [1000],
        "dispute_count": [1],
        "transaction_count": [10]
    })

    # should not raise
    validate_schema_columns(df)


def test_missing_column():
    df = pd.DataFrame({
        "merchant_id": ["M001"],
        "name": ["Test"]
    })

    with pytest.raises(ValueError):
        validate_schema_columns(df)
