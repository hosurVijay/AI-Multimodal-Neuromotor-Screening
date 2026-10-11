
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
)

# --------------------------------------------------
# 1. PROJECT PATHS
# --------------------------------------------------

PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

from preprocessing.voice_feature_extraction import FEATURE_NAMES

DATASET_PATH = (
    PROJECT_ROOT / "dataset" / "voice_wav_features.csv"
)

MODEL_DIR = PROJECT_ROOT / "models"
MODEL_PATH = MODEL_DIR / "logistic_regression_voice_baseline.joblib"
METRICS_PATH = MODEL_DIR / "logistic_regression_voice_metrics.json"

RANDOM_STATE = 42
TEST_SIZE = 0.20


# --------------------------------------------------
# 2. LOAD AND VALIDATE DATA
# --------------------------------------------------

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
        raise ValueError(
            f"Missing feature columns: {missing_features}"
        )

    # Keep only the expected features and target.
    df = df[FEATURE_NAMES + ["status"]].copy()

    # Convert features to numeric values.
    for feature in FEATURE_NAMES:
        df[feature] = pd.to_numeric(
            df[feature], errors="coerce"
        )

    # Support numeric labels and common text labels.
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

        normalized = (
            df["status"].astype(str).str.strip().str.lower()
        )

        df["status"] = normalized.map(label_map)

    df["status"] = pd.to_numeric(
        df["status"], errors="coerce"
    )

    # Do not silently train on invalid labels or missing values.
    if df["status"].isna().any():
        raise ValueError(
            "Invalid or missing labels found in 'status'."
        )

    if not df["status"].isin([0, 1]).all():
        raise ValueError(
            "Labels must be 0 (Healthy) or 1 (Parkinson's)."
        )

    if df[FEATURE_NAMES].isna().any().any():
        raise ValueError(
            "Missing feature values found. "
            "Inspect the feature extraction output."
        )

    if not np.isfinite(
        df[FEATURE_NAMES].to_numpy(dtype=float)
    ).all():
        raise ValueError(
            "Infinite or non-finite feature values found."
        )

    df["status"] = df["status"].astype(int)

    if df["status"].nunique() != 2:
        raise ValueError(
            "Training requires samples from both classes."
        )

    print("\nDataset loaded successfully.")
    print(f"Number of recordings: {len(df)}")
    print("\nClass distribution:")
    print(
        df["status"]
        .map({0: "Healthy", 1: "Parkinson's"})
        .value_counts()
    )

    return df


# --------------------------------------------------
# 3. TRAIN AND EVALUATE
# --------------------------------------------------

def train_model():
    df = load_dataset()

    X = df[FEATURE_NAMES]
    y = df["status"]

    # Hold out test data before any model fitting.
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=TEST_SIZE,
        random_state=RANDOM_STATE,
        stratify=y,
    )

    print("\nTrain recordings:", len(X_train))
    print("Test recordings:", len(X_test))

    # Scaling is inside the pipeline, so each CV fold
    # learns its scaler using only that fold's training data.
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

    # Tune regularization using training data only.
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

    # GridSearchCV refits the best pipeline on all training data.
    best_model = search.best_estimator_

    print("\nBest parameters:", search.best_params_)
    print(
        "Best cross-validation balanced accuracy:",
        round(search.best_score_, 4),
    )

    # --------------------------------------------------
    # 4. EVALUATE ON HELD-OUT TEST SET
    # --------------------------------------------------

    y_pred = best_model.predict(X_test)
    y_prob = best_model.predict_proba(X_test)[:, 1]

    accuracy = accuracy_score(y_test, y_pred)
    balanced_acc = balanced_accuracy_score(y_test, y_pred)

    print("\n========== TEST RESULTS ==========")
    print(f"Accuracy:          {accuracy:.4f}")
    print(f"Balanced accuracy: {balanced_acc:.4f}")

    print("\nConfusion matrix:")
    print(
        confusion_matrix(
            y_test, y_pred, labels=[0, 1]
        )
    )

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

    # --------------------------------------------------
    # 5. SAVE MODEL AND METRICS
    # --------------------------------------------------

    MODEL_DIR.mkdir(parents=True, exist_ok=True)

    if MODEL_PATH.exists():
        raise FileExistsError(
            f"\nModel already exists: {MODEL_PATH}\n"
            "Rename or move the existing file before saving "
            "a replacement. No model was overwritten."
        )

    # Save the entire pipeline, including StandardScaler.
    joblib.dump(best_model, MODEL_PATH)

    metrics = {
        "model": "LogisticRegression",
        "feature_names": FEATURE_NAMES,
        "label_mapping": {
            "0": "Healthy",
            "1": "Parkinson's",
        },
        "dataset_size": int(len(df)),
        "train_size": int(len(X_train)),
        "test_size": int(len(X_test)),
        "best_parameters": search.best_params_,
        "cv_balanced_accuracy": float(search.best_score_),
        "test_accuracy": float(accuracy),
        "test_balanced_accuracy": float(balanced_acc),
        "test_roc_auc": (
            float(auc) if auc is not None else None
        ),
        "random_state": RANDOM_STATE,
        "test_size_fraction": TEST_SIZE,
        "warning": (
            "Experimental voice-screening baseline; "
            "not clinically validated."
        ),
    }

    with open(METRICS_PATH, "w", encoding="utf-8") as f:
        json.dump(metrics, f, indent=4)

    print("\n========== SAVED ==========")
    print(f"Model:   {MODEL_PATH}")
    print(f"Metrics: {METRICS_PATH}")
    print("\nModel training completed successfully.")


# --------------------------------------------------
# 6. ENTRY POINT
# --------------------------------------------------

if __name__ == "__main__":
    train_model()
