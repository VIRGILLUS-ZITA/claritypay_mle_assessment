# Human-in-the-Loop Underwriting System – Design Document

## 1. Objective
The purpose of this system is to support risk analysts in evaluating merchant underwriting risk using a machine learning assisted decision workflow. The system does not automate approval decisions. Instead, it provides structured insights, risk scoring, and explanations while keeping the final decision authority with a human analyst.

The design prioritizes:
- Interpretability
- Auditability
- Operational usability
- Continuous model improvement

---

## 2. System Overview

The system is a decision-support platform composed of five layers:

1. Data ingestion & validation
2. Risk scoring (ML model)
3. Explainability & reporting
4. Human decision layer
5. Feedback learning loop

The ML model acts as a prioritization engine, not an autonomous approval mechanism.

---

## 3. High Level Architecture

User uploads merchant dataset → System enriches & scores → Analyst reviews → Analyst decides → Feedback stored → Model retrained periodically

Key principle:
Human judgment overrides model prediction at all times.

---

## 4. Components

### 4.1 Ingestion Layer
Responsible for collecting and validating data before risk evaluation.

---

### 4.2 Feature Engineering Layer
Transforms raw data into underwriting signals.

---

### 4.3 Risk Scoring Layer (Machine Learning)
A logistic regression classifier predicts probability of high dispute risk.

Outputs:
- Risk probability (0–1)
- High risk classification

This score represents risk likelihood, not approval decision.

---

### 4.4 Portfolio Risk Aggregation
Produces risk insights at portfolio level:
- High‑risk merchant ratio
- Exposure volume
- Expected disputes
- Average risk score

Used for monitoring operational exposure.

---

### 4.5 Report Generation Layer
Generates a short underwriting summary

Purpose: Provide human‑readable risk context for analysts.

---

### 4.6 Human Decision Layer (Core Concept)
The analyst reviews the model output and chooses an action.

Possible actions:
- Approve
- Monitor
- Manual review
- Reject

The system never auto‑approves merchants.

---

### 4.7 Feedback Storage
Every decision is stored with context:
- Merchant features
- Model prediction
- Analyst decision
- Timestamp
- Analyst notes

This forms labeled ground truth data.

---

### 4.8 Retraining Loop
At regular intervals (weekly/monthly):
1. Collect analyst decisions
2. Treat them as labels
3. Retrain model
4. Replace deployed model

This allows the model to learn institutional risk policy over time.

---

## 5. Workflow Lifecycle

### Step 1 — Upload
Analyst uploads merchant dataset

### Step 2 — Enrichment
System validates and enriches data

### Step 3 — Prediction
Model assigns risk probabilities

### Step 4 — Review
Analyst reviews risk drivers and report

### Step 5 — Decision
Analyst approves or rejects

### Step 6 — Feedback
Decision stored for future training

### Step 7 — Retraining
Model updated periodically using analyst decisions

---

## 6. Human Involvement Points

| Stage | Human Role |
|------|------|
Upload | Select merchants |
Review | Interpret risk insights |
Decision | Approve or reject |
Override | Correct model mistakes |
Feedback | Provide learning signal |
Monitoring | Observe portfolio trends |

---

## 7. Example API Design (Conceptual)

POST /cases/upload
Upload merchant dataset

GET /cases/{id}/scores
Return model risk scores

POST /cases/{id}/decision
Store analyst decision

GET /portfolio/summary
Return aggregated risk view

---

## 8. Governance & Safety

- No automated approvals
- Every decision traceable
- All predictions explainable
- Analyst override always allowed
- Model continuously calibrated using real outcomes

---

## 9. Key Principle

The system is an AI‑assisted underwriting tool, not an automated underwriting engine. The machine learning model surfaces risk patterns, while the analyst remains the final decision authority.

---

## 10. Benefits

- Faster review prioritization
- Consistent risk evaluation
- Improved explainability
- Continuous policy learning
- Regulatory compliance friendly design

