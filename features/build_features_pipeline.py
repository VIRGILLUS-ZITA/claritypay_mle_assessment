import os
import pandas as pd
import json
from concurrent.futures import ThreadPoolExecutor, as_completed

from ingestion.service_bootstrap import ensure_internal_api_running
from ingestion.internal_service_client import get_internal_risk
from ingestion.external_country_service import get_country_details
from ingestion.pdf_processor import extract_pdf_text
from ingestion.claritypay_scraper import scrape_claritypay
from ingestion.schema_validator import validate_schema_columns, validate_rows
from common.logger_config import setup_logger
from features.underwriting_features import build_underwriting_features


logger = setup_logger()


TOTAL_STEPS = 10


def log_step(step, total, message):
    logger.info(f"[STEP {step}/{total}] {message}")


# ======================================================
# MAIN PIPELINE FUNCTION (CLI CALLS THIS)
# ======================================================
def run_pipeline(input_path: str, output_dir: str):

    OUTPUT_DATASET = os.path.join(output_dir, "enriched_merchants.csv")
    OUTPUT_PDF_TEXT = os.path.join(output_dir, "merchant_summary.txt")
    OUTPUT_INVALID = os.path.join(output_dir, "invalid_rows.csv")
    OUTPUT_SCRAPE = os.path.join(output_dir, "claritypay_site_data.json")

    os.makedirs(output_dir, exist_ok=True)

    # ------------------------------------------------------
    # 1. Load merchant dataset
    # ------------------------------------------------------
    log_step(1, TOTAL_STEPS, "Loading merchant dataset")

    df = pd.read_csv(input_path)

    validate_schema_columns(df)
    valid_df, invalid_df = validate_rows(df)

    logger.info(f"Loaded {len(df)} rows")
    logger.info(f"Valid rows: {len(valid_df)}")

    if len(invalid_df) > 0:
        logger.warning(f"{len(invalid_df)} invalid rows detected")
        invalid_df.to_csv(OUTPUT_INVALID, index=False)
        logger.info(f"Invalid rows saved to {OUTPUT_INVALID}")

    df = valid_df

    # ------------------------------------------------------
    # 2. Ensure internal API is running
    # ------------------------------------------------------
    log_step(2, TOTAL_STEPS, "Ensuring internal API is running")

    ensure_internal_api_running()
    logger.info("Internal API is ready to use")

    # ------------------------------------------------------
    # 3. Start PDF extraction in background
    # ------------------------------------------------------
    log_step(3, TOTAL_STEPS, "Starting background PDF extraction")

    background_executor = ThreadPoolExecutor(max_workers=2)
    pdf_future = background_executor.submit(extract_pdf_text)

    # ------------------------------------------------------
    # 4. Fetch country metadata
    # ------------------------------------------------------
    log_step(4, TOTAL_STEPS, "Fetching country metadata (parallel)")

    def fetch_all_country_metadata(countries, max_workers=5):
        results = {}
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_country = {
                executor.submit(get_country_details, country): country
                for country in countries
            }

            for future in as_completed(future_to_country):
                country = future_to_country[future]
                try:
                    results[country] = future.result()
                    logger.info(f"SUCCESS country={country}")
                except Exception:
                    results[country] = None
                    logger.error(f"FAILED country={country}")

        return results

    unique_countries = df["country"].dropna().unique()
    country_map = fetch_all_country_metadata(unique_countries)
    logger.info(f"Fetched metadata for {len(country_map)} countries")

    # ------------------------------------------------------
    # 5. Fetch internal risk
    # ------------------------------------------------------
    log_step(5, TOTAL_STEPS, "Fetching internal risk data (parallel)")

    def fetch_all_internal_risk(merchant_ids, max_workers=10):
        results = {}
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_mid = {
                executor.submit(get_internal_risk, mid): mid
                for mid in merchant_ids
            }

            for future in as_completed(future_to_mid):
                mid = future_to_mid[future]
                try:
                    results[mid] = future.result()
                    logger.info(f"SUCCESS merchant_id={mid}")
                except Exception:
                    results[mid] = None
                    logger.error(f"FAILED merchant_id={mid}")

        return results

    merchant_ids = df["merchant_id"].unique()
    internal_map = fetch_all_internal_risk(merchant_ids)
    logger.info(f"Fetched internal risk for {len(internal_map)} merchants")

    # ------------------------------------------------------
    # 6. Build enriched dataset
    # ------------------------------------------------------
    log_step(6, TOTAL_STEPS, "Building enriched dataset")

    records = []

    for _, row in df.iterrows():
        merchant_id = row["merchant_id"]
        country = row["country"]

        internal = internal_map.get(merchant_id)
        geo = country_map.get(country)

        if internal is None:
            logger.warning(f"Skipping merchant_id={merchant_id} due to missing internal data")
            continue

        records.append({
            "merchant_id": merchant_id,
            "name": row["name"],
            "country": country,
            "registration_number": row["registration_number"],
            "monthly_volume": row["monthly_volume"],
            "transaction_count": row["transaction_count"],
            "dispute_count": row["dispute_count"],

            "internal_risk_flag": internal["internal_risk_flag"],
            "internal_last_30d_volume": internal["transaction_summary"]["last_30d_volume"],
            "internal_last_30d_txn_count": internal["transaction_summary"]["last_30d_txn_count"],
            "internal_avg_ticket_size": internal["transaction_summary"]["avg_ticket_size"],

            "normalized_country": geo["country_name"] if geo else None,
            "region": geo["region"] if geo else None,
            "subregion": geo["subregion"] if geo else None
        })

    final_df = pd.DataFrame(records)
    logger.info(f"Final dataset size: {len(final_df)}")

    # ------------------------------------------------------
    # 7. Wait for PDF extraction
    # ------------------------------------------------------
    log_step(7, TOTAL_STEPS, "Waiting for PDF processing to complete")

    pdf_text = pdf_future.result()
    logger.info(f"Extracted {len(pdf_text)} characters from PDF")

    # ------------------------------------------------------
    # 8. Scrape website
    # ------------------------------------------------------
    log_step(8, TOTAL_STEPS, "Scraping claritypay.com")
    
    if os.path.exists(OUTPUT_SCRAPE):
        logger.info(f"Loading existing scrape data from {OUTPUT_SCRAPE}")
        with open(OUTPUT_SCRAPE, "r") as f:
            site_data = json.load(f)
    else:
        site_data = None

    if not site_data:
        logger.info("Scraping website data...")
        site_data = scrape_claritypay()

    with open(OUTPUT_SCRAPE, "w") as f:
        json.dump(site_data, f, indent=2)

    logger.info(f"Website data saved {OUTPUT_SCRAPE}")

    # ------------------------------------------------------
    # 9. Save outputs
    # ------------------------------------------------------
    log_step(9, TOTAL_STEPS, "Saving outputs")

    final_df.to_csv(OUTPUT_DATASET, index=False)
    logger.info(f"Dataset saved {OUTPUT_DATASET}")

    with open(OUTPUT_PDF_TEXT, "w", encoding="utf-8") as f:
        f.write(pdf_text)

    logger.info(f"PDF text saved {OUTPUT_PDF_TEXT}")

    # ------------------------------------------------------
    # 10. Build underwriting features
    # ------------------------------------------------------
    log_step(10, TOTAL_STEPS, "Building underwriting feature view")

    features_df = build_underwriting_features(final_df)

    features_path = os.path.join(output_dir, "underwriting_features.csv")
    features_df.to_csv(features_path, index=False)

    logger.info(f"Underwriting feature view saved {features_path}")

    logger.info("Data pipeline complete — returning datasets to caller")

    return final_df, features_df


# ======================================================
# BACKWARD COMPATIBILITY (direct execution)
# ======================================================
if __name__ == "__main__":
    run_pipeline("data/merchants.csv", "output")
    