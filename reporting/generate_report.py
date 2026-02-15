import os
import requests
import pandas as pd
import shutil
import subprocess
import time


# ======================================================
# CONFIG
# ======================================================
OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_HEALTH = "http://localhost:11434/api/tags"
MODEL_NAME = "llama3"


# ======================================================
# PROVIDER DETECTION
# ======================================================
def has_openai_key():
    return os.getenv("OPENAI_API_KEY") not in (None, "")


def has_openai_package():
    try:
        import openai  # noqa
        return True
    except ImportError:
        return False



def has_ollama_installed():
    return shutil.which("ollama") is not None


def ensure_ollama_running():
    """Start Ollama automatically if installed but not running"""
    try:
        requests.get(OLLAMA_HEALTH, timeout=2)
        print("Local LLM already running")
        return True
    except:
        print("Local LLM not running -> attempting auto start")

    try:
        subprocess.Popen(
            ["ollama", "serve"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except Exception:
        return False

    # wait for startup
    for _ in range(10):
        try:
            requests.get(OLLAMA_HEALTH, timeout=2)
            print("Local LLM started")
            return True
        except:
            time.sleep(1)

    return False


# ======================================================
# PROMPT BUILDER
# ======================================================
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
You are a payments underwriting risk analyst generating an internal risk note.

Write a concise analytical assessment (130-170 words).

STRICT REQUIREMENTS:
- Not an email
- No greetings or signatures
- No bullet points
- Must reference specific merchants as evidence
- Must justify the decision using the data provided
- No speculation beyond the dataset

PORTFOLIO DATA
Total merchants: {metrics['total_merchants']}
High risk merchants: {metrics['high_risk_merchants']} ({metrics['high_risk_ratio']*100:.1f}%)
High risk exposure volume: {metrics['high_risk_volume']}
Expected disputes: {metrics['expected_disputes']}
Average risk score: {metrics['avg_risk_probability']}

TOP RISKY MERCHANTS
{risky_lines}

ANALYSIS INSTRUCTIONS
1. Classify overall portfolio risk: low / moderate / elevated
2. Identify dominant risk drivers using ONLY:
   - dispute behavior
   - transaction volume
   - internal risk signals
3. Cite at least two merchants as supporting evidence
4. Provide operational decision:
   approve / monitor / manual review required
5. Justify WHY that decision follows from the evidence

Write in professional underwriting tone.
"""


# ======================================================
# OPENAI CALL
# ======================================================
def call_openai(prompt: str) -> str:
    try:
        from openai import OpenAI
    except ImportError:
        raise RuntimeError("OpenAI package not installed")

    print("Using OpenAI API")
    client = OpenAI()

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2
    )

    return response.choices[0].message.content


# ======================================================
# LOCAL LLM CALL
# ======================================================
def call_local_llm(prompt: str) -> str:
    print("Using local LLM via Ollama")

    response = requests.post(
        OLLAMA_URL,
        json={"model": MODEL_NAME, "prompt": prompt, "stream": False},
        timeout=600
    )

    if response.status_code != 200:
        raise RuntimeError("Local LLM call failed")

    return response.json()["response"]


# ======================================================
# FALLBACK RULE-BASED REPORT
# ======================================================
def rule_based_report(metrics: dict) -> str:

    ratio = metrics["high_risk_ratio"]

    if ratio > 0.4:
        level = "elevated"
        decision = "manual review required"
    elif ratio > 0.2:
        level = "moderate"
        decision = "monitor"
    else:
        level = "low"
        decision = "approve"

    return f"""
Portfolio risk is classified as {level}. The portfolio contains {metrics['high_risk_merchants']} high-risk merchants out of {metrics['total_merchants']} with an exposure volume of {metrics['high_risk_volume']}. The average risk probability across merchants is {metrics['avg_risk_probability']:.3f}. Based on dispute behavior and transaction volume indicators, the recommended operational decision is: {decision}.
""".strip()


# ======================================================
# MAIN REPORT GENERATOR
# ======================================================
def generate_underwriting_report(metrics, merged_df, output_path="output/underwriting_report.txt"):

    print("\n=== GENERATING UNDERWRITING REPORT ===")

    prompt = build_prompt(metrics, merged_df)

    report_text = None

    # 1️⃣ OpenAI
    if has_openai_key() and has_openai_package():
        try:
            report_text = call_openai(prompt)
        except Exception as e:
            print("OpenAI failed:", e)

    # 2️⃣ Local LLM
    if report_text is None and has_ollama_installed():
        if ensure_ollama_running():
            try:
                report_text = call_local_llm(prompt)
            except Exception as e:
                print("Local LLM failed:", e)

    # 3️⃣ Deterministic fallback
    if report_text is None:
        print("No LLM available -> using rule-based report")
        report_text = rule_based_report(metrics)

    os.makedirs("output", exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(report_text)

    print("\n=== UNDERWRITING REPORT GENERATED ===\n")
    print(report_text)

    return report_text
