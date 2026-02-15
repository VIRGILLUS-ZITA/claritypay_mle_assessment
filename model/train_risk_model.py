import os
import joblib
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from sklearn.model_selection import train_test_split, learning_curve
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    classification_report,
    roc_auc_score,
    confusion_matrix
)


MODEL_PATH = "model/risk_model.pkl"


# ------------------------------------------------------
# Target definition
# ------------------------------------------------------
def prepare_target(df: pd.DataFrame):
    df = df.copy()

    # define high risk as top 20% dispute rate
    threshold = df["dispute_rate"].quantile(0.80)

    df["target_high_risk"] = (df["dispute_rate"] >= threshold).astype(int)

    print(f"High risk threshold (dispute_rate): {threshold:.5f}")
    print("Class distribution:")
    print(df["target_high_risk"].value_counts(normalize=True))

    return df



# ------------------------------------------------------
# Feature importance
# ------------------------------------------------------
def print_feature_importance(model, categorical_features, numeric_features):

    clf = model.named_steps["clf"]
    preprocessor = model.named_steps["preprocess"]

    # categorical names
    cat_encoder = preprocessor.named_transformers_["cat"]
    cat_names = cat_encoder.get_feature_names_out(categorical_features)

    # numeric names (unchanged)
    num_names = numeric_features

    # combine in correct order
    all_feature_names = list(cat_names) + list(num_names)

    importance = clf.coef_[0]

    print("\n=== Feature Importance (clean) ===")

    sorted_feats = sorted(
        zip(all_feature_names, importance),
        key=lambda x: abs(x[1]),
        reverse=True
    )

    for name, val in sorted_feats:
        print(f"{name:30s} {val:.3f}")



# ------------------------------------------------------
# Learning curve
# ------------------------------------------------------
def plot_learning_curve(model, X, y):

    print("\nGenerating learning curve...")

    train_sizes, train_scores, val_scores, *_  = learning_curve(
        model,
        X,
        y,
        cv=3,
        scoring="roc_auc",
        train_sizes=np.linspace(0.2, 1.0, 5),
        n_jobs=None
    )

    plt.figure()
    plt.plot(train_sizes, train_scores.mean(axis=1), label="Train AUC")
    plt.plot(train_sizes, val_scores.mean(axis=1), label="Validation AUC")
    plt.xlabel("Training Samples")
    plt.ylabel("ROC-AUC")
    plt.title("Learning Curve")
    plt.legend()

    os.makedirs("output", exist_ok=True)
    plt.savefig("output/learning_curve.png")
    plt.close()

    print("Learning curve saved output/learning_curve.png")


# ------------------------------------------------------
# Main training function
# ------------------------------------------------------
def train_model(features_path: str):

    print("\nLoading feature dataset...")
    df = pd.read_csv(features_path)

    df = prepare_target(df)

    y = df["target_high_risk"]

    categorical_features = [
        "geo_risk",
        "internal_risk"
    ]

    numeric_features = [
        "dispute_rate",
        "monthly_volume",
        "internal_last_30d_volume",
        "internal_last_30d_txn_count",
        "internal_avg_ticket_size"
    ]

    X = df[categorical_features + numeric_features]


    # preprocessing
    preprocessor = ColumnTransformer(
        transformers=[
            ("cat", OneHotEncoder(handle_unknown="ignore"), categorical_features),
            ("num", StandardScaler(), numeric_features),
        ]
    )


    # simple interpretable model
    model = Pipeline(
        steps=[
            ("preprocess", preprocessor),
            ("clf", LogisticRegression(max_iter=1000, class_weight="balanced"))
        ]
    )

    # --------------------------------------------------
    # Train / test split
    # --------------------------------------------------
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, random_state=42, stratify=y
    )

    print("Training model...")
    model.fit(X_train, y_train)

    preds = model.predict(X_test)
    probs = model.predict_proba(X_test)[:, 1]

    # --------------------------------------------------
    # Evaluation
    # --------------------------------------------------
    print("\n=== Classification Report ===")
    print(classification_report(y_test, preds))

    print("\n=== ROC AUC ===")
    print(roc_auc_score(y_test, probs))

    print("\n=== Confusion Matrix ===")
    print(confusion_matrix(y_test, preds))

    # --------------------------------------------------
    # Interpretability
    # --------------------------------------------------
    print_feature_importance(model, categorical_features, numeric_features)

    # --------------------------------------------------
    # Learning curve
    # --------------------------------------------------
    plot_learning_curve(model, X, y)

    # --------------------------------------------------
    # Save model
    # --------------------------------------------------
    os.makedirs("models", exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    print(f"\nModel saved {MODEL_PATH}")

# ------------------------------------------------------
# Load trained model (inference mode)
# ------------------------------------------------------
def load_model(model_path: str = MODEL_PATH):

    if not os.path.exists(model_path):
        raise FileNotFoundError(
            f"Model not found at {model_path}. Run training first using --train"
        )

    print(f"Loading trained model from {model_path}")
    return joblib.load(model_path)

# ------------------------------------------------------
# Predict risk using trained model
# ------------------------------------------------------
def predict_risk(model, features_df: pd.DataFrame):

    categorical_features = [
        "geo_risk",
        "internal_risk"
    ]

    numeric_features = [
        "dispute_rate",
        "monthly_volume",
        "internal_last_30d_volume",
        "internal_last_30d_txn_count",
        "internal_avg_ticket_size"
    ]

    X = features_df[categorical_features + numeric_features]

    scored_df = features_df.copy()

    scored_df["risk_probability"] = model.predict_proba(X)[:, 1]

    # Note:
    # The threshold is intentionally lowered to prioritise recall and minimise undetected high-risk merchants. 
    # The model is used as a triage tool for manual underwriting rather than an automatic rejection system.
    THRESHOLD = 0.30
    scored_df["predicted_high_risk"] = (scored_df["risk_probability"] >= THRESHOLD).astype(int)

    return scored_df
