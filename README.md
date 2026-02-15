# ClarityPay MLE Assessment — Merchant Risk Pipeline

This project implements a minimal production-style underwriting risk pipeline that ingests multiple heterogeneous data sources, constructs underwriting features, trains a risk model, aggregates portfolio risk, and generates an automated underwriting report using an LLM (with robust fallbacks).

The system is designed to run on a clean machine with zero configuration and gracefully degrades if optional services are unavailable.

## What the pipeline does

End-to-end flow:

1. Ingest data sources

<<<<<<< HEAD
    CSV dataset

Simulated internal API (local service)

Public country metadata API

PDF extraction (async)

Website scraping

Validate and collate data into underwriting view

Train or load a risk model

Predict high dispute risk

Aggregate portfolio risk metrics

Generate underwriting report (LLM or fallback)

Architecture
data sources → ingestion → feature engineering → model → portfolio aggregation → LLM report


Project structure:
=======
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


### Project structure:
>>>>>>> a34fede96d0c436ddf5d6f48c7e5cef38dcb6d18

data/
ingestion/
features/
model/
reporting/
common/
output/
models/
run_pipeline.py

<<<<<<< HEAD
Requirements
=======
## Requirements
>>>>>>> a34fede96d0c436ddf5d6f48c7e5cef38dcb6d18

Python 3.10+

Install dependencies:

pip install -r requirements.txt


Optional (for cloud LLM):

pip install openai

<<<<<<< HEAD
Running the pipeline
Basic run (no training, prediction only)
python run_pipeline.py --predict

Train model + predict
python run_pipeline.py --train --predict

Custom dataset
python run_pipeline.py --input data/test_merchants.csv --predict

Custom output folder
python run_pipeline.py --output results/ --predict

Data Sources Used
1. Simulated Internal API (local FastAPI service)

Provides:

internal risk tier

transaction summary
=======
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
>>>>>>> a34fede96d0c436ddf5d6f48c7e5cef38dcb6d18

The pipeline automatically starts the API if not running.

No manual setup required.

<<<<<<< HEAD
2. Public API — REST Countries

Used to enrich merchants with:

region

subregion

normalized country

Handles failures and rate limits gracefully.

3. CSV Dataset
=======
### 2. Public API — REST Countries

Used to enrich merchants with:

  - region

  - subregion

  - normalized country

Handles failures and rate limits gracefully.

### 3. CSV Dataset
>>>>>>> a34fede96d0c436ddf5d6f48c7e5cef38dcb6d18

data/merchants.csv

Validated for:

<<<<<<< HEAD
required columns

invalid rows logged to output/invalid_rows.csv

4. PDF Processing (async)
=======
  - required columns

  - invalid rows logged to output/invalid_rows.csv

### 4. PDF Processing (async)
>>>>>>> a34fede96d0c436ddf5d6f48c7e5cef38dcb6d18

Extracts merchant summary text from:

data/sample_merchant_summary.pdf


Runs in background while API calls execute.

<<<<<<< HEAD
5. Website Scraping

Scrapes claritypay.com for:

value propositions

partners

public statistics

Rate-limited and resilient to layout changes.

Risk Model
=======
### 5. Website Scraping

Scrapes claritypay.com for:

  - value propositions

  - partners

  - public statistics

Rate-limited and resilient to layout changes.

## Risk Model
>>>>>>> a34fede96d0c436ddf5d6f48c7e5cef38dcb6d18

Model: Logistic Regression
Target: High dispute risk (top 20% dispute_rate)

Features include:

<<<<<<< HEAD
dispute behavior

transaction volume

internal API metrics

geo risk indicators
=======
  - dispute behavior

  - transaction volume

  - internal API metrics

  - geo risk indicators
>>>>>>> a34fede96d0c436ddf5d6f48c7e5cef38dcb6d18

The model is saved to:

models/risk_model.pkl

<<<<<<< HEAD
Portfolio Risk Metrics

Generated automatically after prediction:

high-risk merchant count

exposure volume

expected disputes

average risk probability
=======
## Portfolio Risk Metrics

Generated automatically after prediction:

  - high-risk merchant count

  - exposure volume

  - expected disputes

  - average risk probability
>>>>>>> a34fede96d0c436ddf5d6f48c7e5cef38dcb6d18

Saved to:

output/portfolio_view.csv

<<<<<<< HEAD
Underwriting Report Generation
=======
## Underwriting Report Generation
>>>>>>> a34fede96d0c436ddf5d6f48c7e5cef38dcb6d18

The pipeline automatically chooses the best available report generator:

Priority order:

<<<<<<< HEAD
OpenAI API

Local LLM (Ollama)

Deterministic rule-based report

Option A — Use OpenAI
=======
1. OpenAI API

2. Local LLM (Ollama)

3. Deterministic rule-based report

### Option A — Use OpenAI
>>>>>>> a34fede96d0c436ddf5d6f48c7e5cef38dcb6d18

Set API key:

Windows:

setx OPENAI_API_KEY "your_api_key"


Mac/Linux:

export OPENAI_API_KEY="your_api_key"


Then run normally.

<<<<<<< HEAD
Option B — Use Local LLM (Recommended)
=======
### Option B — Use Local LLM (Recommended)
>>>>>>> a34fede96d0c436ddf5d6f48c7e5cef38dcb6d18

Install Ollama:
https://ollama.com

Pull model:

ollama pull llama3


Run pipeline — it auto-starts the model.

<<<<<<< HEAD
Option C — No AI installed

The system generates a deterministic underwriting summary.

Output Files
=======
### Option C — No AI installed

The system generates a deterministic underwriting summary.

## Output Files
>>>>>>> a34fede96d0c436ddf5d6f48c7e5cef38dcb6d18
output/enriched_merchants.csv
output/underwriting_features.csv
output/merchant_predictions.csv
output/portfolio_view.csv
output/underwriting_report.txt
models/risk_model.pkl

<<<<<<< HEAD
Design Decisions
=======
## Design Decisions
>>>>>>> a34fede96d0c436ddf5d6f48c7e5cef38dcb6d18
Production-style robustness

The system runs even if:

<<<<<<< HEAD
API unavailable

internet unavailable

no LLM available

Deterministic fallback

A report is always produced.

Auto service bootstrap

Internal API and local LLM auto-start if installed.

Separation of concerns

Ingestion, features, modeling, reporting separated into modules.

Notes
=======
  - API unavailable

  - internet unavailable

  - no LLM available

## Deterministic fallback

A report is always produced.

## Auto service bootstrap

Internal API and local LLM auto-start if installed.

## Separation of concerns

Ingestion, features, modeling, reporting separated into modules.

## Notes
>>>>>>> a34fede96d0c436ddf5d6f48c7e5cef38dcb6d18

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
