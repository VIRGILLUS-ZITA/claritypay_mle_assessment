import argparse
import os

from features.build_features_pipeline import run_pipeline
from model.train_risk_model import train_model, load_model, predict_risk
from model.portfolio_risk import generate_portfolio_risk
from reporting.generate_report import generate_underwriting_report

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent))


def main():

    parser = argparse.ArgumentParser(description="Merchant Underwriting Pipeline")

    # ------------------------------
    # execution mode
    # ------------------------------
    parser.add_argument("--train", action="store_true", help="Train the model")
    parser.add_argument("--predict", action="store_true", help="Run prediction using trained model")

    # ------------------------------
    # paths
    # ------------------------------
    parser.add_argument(
        "--input",
        type=str,
        default="data/merchants.csv",
        help="Path to merchant CSV"
    )

    parser.add_argument(
        "--output",
        type=str,
        default="output",
        help="Directory to write outputs"
    )

    args = parser.parse_args()

    if not args.train and not args.predict:
        parser.error("Specify at least one mode: --train or --predict")

    input_path = args.input
    output_dir = args.output

    os.makedirs(output_dir, exist_ok=True)

    # --------------------------------------------------
    # BUILD DATASET STEP
    # --------------------------------------------------
    print("\n=== Building dataset ===")
    final_df, features_df = run_pipeline(input_path, output_dir)

    features_path = os.path.join(output_dir, "underwriting_features.csv")
    predictions_path = os.path.join(output_dir, "merchant_predictions.csv")

    # ------------------------------------------------------
    # MODEL STEP
    # ------------------------------------------------------
    print("\n=== MODEL STEP ===")

    if args.train:
        print("Training model...")
        train_model(features_path)   # only trains & saves model

        print("Loading freshly trained model...")
        model = load_model()

    elif args.predict:
        print("Loading existing model...")
        model = load_model()

    else:
        print("No --train or --predict flag provided. Exiting.")
        return


    # ------------------------------------------------------
    # PREDICTION STEP (COMMON PATH)
    # ------------------------------------------------------
    print("\n=== PREDICTION STEP ===")

    scored_df = predict_risk(model, features_df)

    predictions_path = os.path.join(output_dir, "merchant_predictions.csv")
    scored_df.to_csv(predictions_path, index=False)
    print(f"Predictions saved {predictions_path}")


    # ------------------------------------------------------
    # PORTFOLIO RISK STEP
    # ------------------------------------------------------
    print("\n=== PORTFOLIO RISK ANALYSIS ===")

    metrics, merged_df = generate_portfolio_risk(final_df, scored_df)

    merged_path = os.path.join(output_dir, "portfolio_view.csv")
    merged_df.to_csv(merged_path, index=False)
    print(f"Portfolio dataset saved {merged_path}")

    # ------------------------------------------------------
    # LLM UNDERWRITING REPORT
    # ------------------------------------------------------
    print("\n=== GENERATING UNDERWRITING REPORT ===")

    report_path = os.path.join(output_dir, "underwriting_report.txt")
    generate_underwriting_report(metrics, merged_df, report_path)

    print(f"Underwriting report saved → {report_path}")


if __name__ == "__main__":
    main()


# How to use now
# Train default
# python run_pipeline.py --train

# Predict default
# python run_pipeline.py --predict

# Custom dataset
# python run_pipeline.py --predict --input data/test.csv

# Custom output folder
# python run_pipeline.py --predict --output results/

# Everything
# python run_pipeline.py --train --input data/dev.csv --output artifacts/