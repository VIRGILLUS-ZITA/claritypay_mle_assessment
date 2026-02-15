# ClarityPay MLE Assessment — Merchant Risk Pipeline

This project implements a minimal production-style underwriting risk pipeline that ingests multiple heterogeneous data sources, constructs underwriting features, trains a risk model, aggregates portfolio risk, and generates an automated underwriting report using an LLM (with robust fallbacks).

The system is designed to run on a clean machine with zero configuration and gracefully degrades if optional services are unavailable.

## What the pipeline does

End-to-end flow:

1. Ingest data sources
  
  - CSV dataset
  
  - Simulated internal API (local service)
  
  - Public country metadata API
  
  - PDF extraction (async)
  
  - Website scraping

2. Validate and collate data into underwriting view

3. Train or load a risk model

  - Predict high dispute risk

4. Aggregate portfolio risk metrics

5. Generate underwriting report (LLM or fallback)

## Architecture
data sources → ingestion → feature engineering → model → portfolio aggregation → LLM report


## Project structure:

data/
ingestion/
features/
model/
reporting/
common/
output/
models/
run_pipeline.py

## Requirements

Python 3.10+

### Install dependencies:

pip install -r requirements.txt


### Optional (for cloud LLM):

pip install openai

## Running the pipeline
### Basic run (no training, prediction only)
python run_pipeline.py --predict

### Train model + predict
python run_pipeline.py --train --predict

### Custom dataset
python run_pipeline.py --input data/test_merchants.csv --predict

### Custom output folder
python run_pipeline.py --output results/ --predict

## Data Sources Used
### 1. Simulated Internal API (local FastAPI service)

Provides:

  - internal risk tier
  
  - transaction summary

The pipeline automatically starts the API if not running.

No manual setup required.

### 2. Public API — REST Countries

Used to enrich merchants with:

  - region
  
  - subregion
  
  - normalized country

Handles failures and rate limits gracefully.

### 3. CSV Dataset

data/merchants.csv

Validated for:

  - required columns
  
  - invalid rows logged to output/invalid_rows.csv

### 4. PDF Processing (async)

Extracts merchant summary text from:

data/sample_merchant_summary.pdf


Runs in background while API calls execute.

### 5. Website Scraping

Scrapes claritypay.com for:

  - value propositions
  
  - partners
  
  - public statistics

Rate-limited and resilient to layout changes.

## Risk Model

Model: Logistic Regression
Target: High dispute risk (top 20% dispute_rate)

Features include:

  - dispute behavior
  
  - transaction volume
  
  - internal API metrics
  
  - geo risk indicators

The model is saved to:

models/risk_model.pkl

## Portfolio Risk Metrics

Generated automatically after prediction:

  - high-risk merchant count
  
  - exposure volume
  
  - expected disputes
  
  - average risk probability

Saved to:

output/portfolio_view.csv

## Underwriting Report Generation

The pipeline automatically chooses the best available report generator:

Priority order:

  1. OpenAI API

  2. Local LLM (Ollama)

  3. Deterministic rule-based report

### Option A — Use OpenAI

Set API key:

Windows:

setx OPENAI_API_KEY "your_api_key"


Mac/Linux:

export OPENAI_API_KEY="your_api_key"


Then run normally.

### Option B — Use Local LLM (Recommended)

Install Ollama:
https://ollama.com

Pull model:

ollama pull llama3


Run pipeline — it auto-starts the model.

### Option C — No AI installed

The system generates a deterministic underwriting summary.

## Output Files
output/enriched_merchants.csv
output/underwriting_features.csv
output/merchant_predictions.csv
output/portfolio_view.csv
output/underwriting_report.txt
models/risk_model.pkl

## Design Decisions
### Production-style robustness

The system runs even if:

  - API unavailable
  
  - internet unavailable
  
  - no LLM available

### Deterministic fallback

A report is always produced.

### Auto service bootstrap

Internal API and local LLM auto-start if installed.

### Separation of concerns

Ingestion, features, modeling, reporting separated into modules.

## Notes

This project intentionally prioritizes reliability and explainability over heavy model tuning, matching real underwriting workflows.

## Running Unit Tests

The project includes lightweight unit tests covering:

    - schema validation
    
    - API client behavior (mocked)
    
    - feature engineering correctness
    
    - model prediction pipeline
    
    - deterministic report fallback

Install test dependencies:

pip install pytest pytest-mock


Run tests from project root:

pytest -q


Expected output:

5 passed


The tests do not require:

    - starting the internal API
    
    - internet access
    
    - an LLM
    
    - model retraining

All external dependencies are mocked to ensure reproducibility.
