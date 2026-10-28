
from pathlib import Path
import json
import sys

import joblib
import numpy as np
import pandas as pd

from sklearn.model_selection import train_test_split, GridSearchCV, StratifiedKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    classification_report,
    confusion_matrix,
    roc_auc_score,
    precision_score,
    recall_score,
    f1_score,
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from preprocessing.voice_feature_extraction import FEATURE_NAMES

DATASET_PATH = PROJECT_ROOT / "dataset" / "voice_wav_features.csv"

MODEL_DIR = PROJECT_ROOT / "models"
MODEL_PATH = MODEL_DIR / "logistic_regression_voice_baseline.joblib"

METRICS_DIR = PROJECT_ROOT / "metrics"
METRICS_PATH = METRICS_DIR / "logistic_regression_voice_metrics.json"

RANDOM_STATE = 42
TEST_SIZE = 0.20


def load_dataset():
    if not DATASET_PATH.exists():
        raise FileNotFoundError(
            f"Feature CSV not found: {DATASET_PATH}\n"
            "Run voice_feature_extraction.py first."
        )

    df = pd.read_csv(DATASET_PATH)

    if "status" not in df.columns:
        raise ValueError(
            "CSV must contain a 'status' column "
            "with labels: 0 = Healthy, 1 = Parkinson's."
        )

    missing_features = [
        feature for feature in FEATURE_NAMES
        if feature not in df.columns
    ]

    if missing_features:
        raise ValueError(f"Missing feature columns: {missing_features}")

    df = df[FEATURE_NAMES + ["status"]].copy()

    for feature in FEATURE_NAMES:
        df[feature] = pd.to_numeric(df[feature], errors="coerce")

    if not pd.api.types.is_numeric_dtype(df["status"]):
        label_map = {
            "healthy": 0,
            "hc": 0,
            "control": 0,
            "0": 0,
            "pd": 1,
            "parkinson": 1,
            "parkinsons": 1,
            "parkinson's": 1,
            "1": 1,
        }

        normalized = df["status"].astype(str).str.strip().str.lower()
        df["status"] = normalized.map(label_map)

    df["status"] = pd.to_numeric(df["status"], errors="coerce")

    if df["status"].isna().any():
        raise ValueError("Invalid or missing labels found in 'status'.")

    if not df["status"].isin([0, 1]).all():
        raise ValueError("Labels must be 0 (Healthy) or 1 (Parkinson's).")

    if df[FEATURE_NAMES].isna().any().any():
        raise ValueError(
            "Missing feature values found. Inspect the feature extraction output."
        )

    if not np.isfinite(df[FEATURE_NAMES].to_numpy(dtype=float)).all():
        raise ValueError("Infinite or non-finite feature values found.")

    df["status"] = df["status"].astype(int)

    if df["status"].nunique() != 2:
        raise ValueError("Training requires samples from both classes.")

    print("\nDataset loaded successfully.")
    print(f"Number of recordings: {len(df)}")
    print("\nClass distribution:")
    print(df["status"].map({0: "Healthy", 1: "Parkinson's"}).value_counts())

    return df


def train_model():
    df = load_dataset()

    X = df[FEATURE_NAMES]
    y = df["status"]

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=TEST_SIZE,
        random_state=RANDOM_STATE,
        stratify=y,
    )

    print("\nTrain recordings:", len(X_train))
    print("Test recordings:", len(X_test))

    pipeline = Pipeline([
        ("scaler", StandardScaler()),
        (
            "classifier",
            LogisticRegression(
                max_iter=5000,
                class_weight="balanced",
                random_state=RANDOM_STATE,
            ),
        ),
    ])

    class_counts = y_train.value_counts()
    n_splits = min(5, int(class_counts.min()))

    if n_splits < 2:
        raise ValueError(
            "Not enough examples per class for cross-validation."
        )

    cv = StratifiedKFold(
        n_splits=n_splits,
        shuffle=True,
        random_state=RANDOM_STATE,
    )

    param_grid = {
        "classifier__C": [0.01, 0.1, 1.0, 10.0, 100.0],
    }

    search = GridSearchCV(
        estimator=pipeline,
        param_grid=param_grid,
        scoring="balanced_accuracy",
        cv=cv,
        n_jobs=-1,
        refit=True,
    )

    print("\nTraining Logistic Regression...")
    search.fit(X_train, y_train)

    best_model = search.best_estimator_

    print("\nBest parameters:", search.best_params_)
    print(
        "Best cross-validation balanced accuracy:",
        round(search.best_score_, 4),
    )

    y_pred = best_model.predict(X_test)
    y_prob = best_model.predict_proba(X_test)[:, 1]

    accuracy = accuracy_score(y_test, y_pred)
    balanced_acc = balanced_accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred, zero_division=0)
    recall = recall_score(y_test, y_pred, zero_division=0)
    f1 = f1_score(y_test, y_pred, zero_division=0)

    cm = confusion_matrix(y_test, y_pred, labels=[0, 1])

    print("\n========== TEST RESULTS ==========")
    print(f"Accuracy:          {accuracy:.4f}")
    print(f"Balanced accuracy: {balanced_acc:.4f}")
    print(f"Precision:         {precision:.4f}")
    print(f"Recall:            {recall:.4f}")
    print(f"F1-score:          {f1:.4f}")

    print("\nConfusion matrix:")
    print(cm)

    print("\nClassification report:")
    print(
        classification_report(
            y_test,
            y_pred,
            labels=[0, 1],
            target_names=["Healthy", "Parkinson's"],
            zero_division=0,
        )
    )

    try:
        auc = roc_auc_score(y_test, y_prob)
        print(f"ROC-AUC:           {auc:.4f}")
    except ValueError:
        auc = None
        print("ROC-AUC unavailable for this test split.")

    tn, fp, fn, tp = cm.ravel()

    specificity = float(tn / (tn + fp)) if (tn + fp) else None
    sensitivity = float(tp / (tp + fn)) if (tp + fn) else None

    print(
        f"Specificity:       {specificity:.4f}"
        if specificity is not None
        else "Specificity: unavailable"
    )
    print(
        f"Sensitivity:       {sensitivity:.4f}"
        if sensitivity is not None
        else "Sensitivity: unavailable"
    )

    MODEL_DIR.mkdir(parents=True, exist_ok=True)
    METRICS_DIR.mkdir(parents=True, exist_ok=True)

    if not MODEL_PATH.exists():
        joblib.dump(best_model, MODEL_PATH)
        print(f"\nNew model saved: {MODEL_PATH}")
    else:
        print(f"\nExisting model preserved: {MODEL_PATH}")
        print("The existing model was not overwritten.")

    metrics = {
        "accuracy": float(accuracy),
        "precision": float(precision),
        "recall": float(recall),
        "f1_score": float(f1),
    }

    with open(METRICS_PATH, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=4)

    print(f"\nMetrics saved: {METRICS_PATH}")
    print("\nEvaluation completed successfully.")


if __name__ == "__main__":
    train_model()
