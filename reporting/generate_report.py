import os
import requests
import pandas as pd


OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3"


# ------------------------------------------------------
# Build underwriting prompt
# ------------------------------------------------------
def build_prompt(metrics: dict, merged_df: pd.DataFrame) -> str:

    top_risky = (
        merged_df.sort_values("risk_probability", ascending=False)
        .head(5)[["merchant_id", "monthly_volume", "risk_probability", "country"]]
    )

    risky_lines = "\n".join(
        [
            f"- {row.merchant_id} | volume={row.monthly_volume} | risk={row.risk_probability:.2f} | country={row.country}"
            for _, row in top_risky.iterrows()
        ]
    )

    return f"""
You are an automated underwriting risk engine.

Generate a short internal risk assessment paragraph (120-180 words).

Rules:
- Do NOT write an email
- Do NOT include greetings or signatures
- Do NOT use bullet points or numbered lists
- Do NOT mention yourself
- Do NOT invent causes not present in the data

Portfolio statistics:
Total merchants: {metrics['total_merchants']}
High risk merchants: {metrics['high_risk_merchants']} ({metrics['high_risk_ratio']*100:.1f}%)
High risk exposure: {metrics['high_risk_volume']}
Expected disputes: {metrics['expected_disputes']}
Average risk score: {metrics['avg_risk_probability']}

Top risky merchants:
{risky_lines}

The output must:
- classify portfolio risk (low/moderate/elevated)
- describe dominant risk drivers ONLY using dispute_rate, volume, and internal risk indicators
- give operational decision:
  approve / monitor / manual review required

Do NOT infer geographic causes unless explicitly provided.
Do NOT recommend approving high risk merchants automatically.
Write in objective risk system tone.
"""


# ------------------------------------------------------
# Call local LLM
# ------------------------------------------------------
def call_local_llm(prompt: str) -> str:

    print("Prompt sent to local LLM:")
    response = requests.post(
        OLLAMA_URL,
        json={
            "model": MODEL_NAME,
            "prompt": prompt,
            "stream": False
        }
    )
    print("Response received from local LLM")

    if response.status_code != 200:
        raise RuntimeError("Local LLM call failed. Is Ollama running?")

    return response.json()["response"]


# ------------------------------------------------------
# Generate report
# ------------------------------------------------------
def generate_underwriting_report(metrics, merged_df, output_path="output/underwriting_report.txt"):

    print('Building prompt...')
    prompt = build_prompt(metrics, merged_df)
    print('Completed building prompt')

    print('Calling local LLM...')
    report_text = call_local_llm(prompt)
    print('Received response from local LLM')

    print('Saving report to file...')
    os.makedirs("output", exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(report_text)
    print(f"Report saved to {output_path}")

    print("\n=== UNDERWRITING REPORT GENERATED ===\n")
    print(report_text)

    return report_text
