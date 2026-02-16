def print_and_log_summary(metrics, provider, output_dir, logger):
    # 1. Define the risk level logic
    risk_level = (
        "Low" if metrics["high_risk_ratio"] < 0.2
        else "Moderate" if metrics["high_risk_ratio"] < 0.4
        else "Elevated"
    )

    # 2. Build the summary string as a list of lines
    summary_lines = [
        "",
        "="*52,
        "PIPELINE EXECUTION SUMMARY",
        "="*52,
        f"Dataset processed:        {metrics['total_merchants']} merchants",
        f"High risk merchants:      {metrics['high_risk_merchants']} ({metrics['high_risk_ratio']*100:.1f}%)",
        f"Portfolio risk level:     {risk_level}",
        f"Report provider:          {provider}",
        "",
        "Generated files:",
        f" - {output_dir}/enriched_merchants.csv",
        f" - {output_dir}/underwriting_features.csv",
        f" - {output_dir}/merchant_predictions.csv",
        f" - {output_dir}/portfolio_view.csv",
        f" - {output_dir}/underwriting_report.txt",
        " - models/risk_model.pkl",
        "",
        "Pipeline completed successfully",
        "="*52
    ]

    # 3. Join them into a single block of text
    full_summary = "\n".join(summary_lines)

    # 4. Output to both locations
    print(full_summary)      # Visible in Terminal
    logger.info(full_summary) # Saved in Log File