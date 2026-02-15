from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import date, timedelta
import pandas as pd
import random
import os

app = FastAPI(title="Internal Merchant Risk API")


# -----------------------------------------------------
# Load merchants reference dataset (exists check)
# -----------------------------------------------------
DATA_PATH = "data/merchants.csv"

if os.path.exists(DATA_PATH):
    MERCHANTS = set(pd.read_csv(DATA_PATH)["merchant_id"])
else:
    MERCHANTS = set()


# -----------------------------------------------------
# Response Schema (matches simulated_api_contract.json)
# -----------------------------------------------------
class TransactionSummary(BaseModel):
    last_30d_volume: float = Field(ge=0)
    last_30d_txn_count: int = Field(ge=0)
    avg_ticket_size: float = Field(ge=0)


class MerchantRiskResponse(BaseModel):
    merchant_id: str
    internal_risk_flag: Literal["low", "medium", "high"]
    transaction_summary: TransactionSummary
    last_review_date: Optional[date] = None


# -----------------------------------------------------
# Risk Logic (simple but deterministic)
# -----------------------------------------------------
def calculate_risk(volume, txn_count, dispute_count):

    if txn_count == 0:
        return "low"

    dispute_ratio = dispute_count / txn_count

    if dispute_ratio > 0.02 or volume > 150000:
        return "high"

    if dispute_ratio > 0.005 or volume > 50000:
        return "medium"

    return "low"


# -----------------------------------------------------
# API Endpoint
# -----------------------------------------------------
@app.get("/merchant/{merchant_id}", response_model=MerchantRiskResponse)
def get_merchant_risk(merchant_id: str):

    # --- existence validation ---
    if merchant_id not in MERCHANTS:
        raise HTTPException(status_code=404, detail="Merchant not found")

    # Simulate internal transaction aggregation
    txn_count = random.randint(50, 4000)
    volume = round(random.uniform(1000, 200000), 2)
    dispute_count = random.randint(0, 20)

    avg_ticket = round(volume / txn_count, 2)

    risk_flag = calculate_risk(volume, txn_count, dispute_count)

    review_date = date.today() - timedelta(days=random.randint(1, 365))

    return {
        "merchant_id": merchant_id,
        "internal_risk_flag": risk_flag,
        "transaction_summary": {
            "last_30d_volume": volume,
            "last_30d_txn_count": txn_count,
            "avg_ticket_size": avg_ticket
        },
        "last_review_date": review_date
    }
