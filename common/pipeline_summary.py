def print_pipeline_summary(metrics, provider, output_dir):

    print("\n" + "="*52)
    print("PIPELINE EXECUTION SUMMARY")
    print("="*52)

    print(f"\nDataset processed:        {metrics['total_merchants']} merchants")
    print(f"High risk merchants:      {metrics['high_risk_merchants']} ({metrics['high_risk_ratio']*100:.1f}%)")

    risk_level = (
        "Low" if metrics["high_risk_ratio"] < 0.2
        else "Moderate" if metrics["high_risk_ratio"] < 0.4
        else "Elevated"
    )
    print(f"Portfolio risk level:     {risk_level}")
    print(f"Report provider:          {provider}")

    print("\nGenerated files:")
    print(f" - {output_dir}/enriched_merchants.csv")
    print(f" - {output_dir}/underwriting_features.csv")
    print(f" - {output_dir}/merchant_predictions.csv")
    print(f" - {output_dir}/portfolio_view.csv")
    print(f" - {output_dir}/underwriting_report.txt")
    print(f" - models/risk_model.pkl")

    print("\nPipeline completed successfully")
    print("="*52)
