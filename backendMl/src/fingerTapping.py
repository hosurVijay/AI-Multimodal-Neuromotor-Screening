
from pathlib import Path
import sys
import json
from datetime import datetime, timezone

import numpy as np
import pandas as pd
import joblib

from sklearn.model_selection import train_test_split, StratifiedGroupKFold
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    confusion_matrix,
    classification_report,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
)

root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root))

from preprocessing.fingerTapping_preprocessing import (
    process_file,
    get_person_id,
)

dataset_path = root / "dataset" / "fingerTappingData"
ctrl_path = dataset_path / "CTRL"
pd_path = dataset_path / "PD"

model_dir = root / "models"
model_path = model_dir / "finger_tapping_model.joblib"

metrics_dir = root / "metrics"
metrics_path = metrics_dir / "finger_tapping_model_metrics.json"

RANDOM_STATE = 42
TEST_SIZE = 0.20
N_ESTIMATORS = 200
RECORDING_THRESHOLD = 0.5

ctrl_files = sorted(ctrl_path.glob("*.mat"))
pd_files = sorted(pd_path.glob("*.mat"))

if not ctrl_files:
    raise FileNotFoundError(f"No CTRL .mat files found in {ctrl_path}")

if not pd_files:
    raise FileNotFoundError(f"No PD .mat files found in {pd_path}")

rows = []
recording_info = []

for file in ctrl_files:
    data = process_file(file)

    if not data.empty:
        data["label"] = 0
        rows.append(data)

        recording_info.append({
            "recording_id": file.name,
            "person_id": get_person_id(file),
            "label": 0,
        })

for file in pd_files:
    data = process_file(file)

    if not data.empty:
        data["label"] = 1
        rows.append(data)

        recording_info.append({
            "recording_id": file.name,
            "person_id": get_person_id(file),
            "label": 1,
        })

if not rows:
    raise ValueError("No valid finger-tapping windows were extracted.")

data = pd.concat(rows, ignore_index=True)
recording_info = pd.DataFrame(recording_info)

if recording_info.empty:
    raise ValueError("No valid recording metadata was generated.")

feature_columns = [
    column
    for column in data.columns
    if column not in ["recording_id", "window_id", "label"]
]

if not feature_columns:
    raise ValueError("No finger-tapping feature columns were found.")

data[feature_columns] = data[feature_columns].apply(
    pd.to_numeric,
    errors="coerce",
)

if data[feature_columns].isna().any().any():
    raise ValueError("Missing or non-numeric feature values were found.")

if not np.isfinite(data[feature_columns].to_numpy(dtype=float)).all():
    raise ValueError("Infinite or non-finite feature values were found.")

person_info = (
    recording_info[["person_id", "label"]]
    .drop_duplicates()
)

if person_info["person_id"].duplicated().any():
    raise ValueError(
        "At least one person has conflicting labels. "
        "Check get_person_id() and the dataset labels."
    )

if person_info["person_id"].nunique() < 5:
    raise ValueError(
        "At least five distinct people are needed for "
        "the requested five-fold grouped cross-validation."
    )

train_persons, test_persons = train_test_split(
    person_info["person_id"].values,
    test_size=TEST_SIZE,
    random_state=RANDOM_STATE,
    stratify=person_info["label"],
)

train_recordings = recording_info[
    recording_info["person_id"].isin(train_persons)
]["recording_id"].tolist()

test_recordings = recording_info[
    recording_info["person_id"].isin(test_persons)
]["recording_id"].tolist()

recording_to_person = dict(
    zip(
        recording_info["recording_id"],
        recording_info["person_id"],
    )
)

train_data = data[
    data["recording_id"].isin(train_recordings)
].copy()

test_data = data[
    data["recording_id"].isin(test_recordings)
].copy()

train_data["person_id"] = train_data["recording_id"].map(
    recording_to_person
)

test_data["person_id"] = test_data["recording_id"].map(
    recording_to_person
)

if train_data.empty or test_data.empty:
    raise ValueError("Training or test data is empty.")

X = train_data[feature_columns]
y = train_data["label"]
groups = train_data["person_id"]

class_counts = (
    train_data[["person_id", "label"]]
    .drop_duplicates("person_id")["label"]
    .value_counts()
)

if len(class_counts) < 2 or class_counts.min() < 5:
    raise ValueError(
        "Five-fold StratifiedGroupKFold requires at least "
        "five training people in each class."
    )

cv = StratifiedGroupKFold(
    n_splits=5,
    shuffle=True,
    random_state=RANDOM_STATE,
)

fold_scores = []

print("\n========== CROSS-VALIDATION ==========")

for fold, (train_idx, val_idx) in enumerate(
    cv.split(X, y, groups=groups),
    start=1,
):
    fold_model = RandomForestClassifier(
        n_estimators=N_ESTIMATORS,
        random_state=RANDOM_STATE,
        n_jobs=-1,
    )

    fold_model.fit(
        X.iloc[train_idx],
        y.iloc[train_idx],
    )

    validation = train_data.iloc[val_idx].copy()

    validation["prediction"] = fold_model.predict(
        X.iloc[val_idx]
    )

    recording = (
        validation.groupby("recording_id")
        .agg(
            person_id=("person_id", "first"),
            actual_label=("label", "first"),
            pd_windows=("prediction", "sum"),
            total_windows=("prediction", "count"),
        )
        .reset_index()
    )

    recording["pd_ratio"] = (
        recording["pd_windows"] / recording["total_windows"]
    )

    recording["prediction"] = (
        recording["pd_ratio"] >= RECORDING_THRESHOLD
    ).astype(int)

    fold_accuracy = accuracy_score(
        recording["actual_label"],
        recording["prediction"],
    )

    fold_balanced_accuracy = balanced_accuracy_score(
        recording["actual_label"],
        recording["prediction"],
    )

    fold_scores.append({
        "fold": fold,
        "recording_accuracy": float(fold_accuracy),
        "recording_balanced_accuracy": float(fold_balanced_accuracy),
        "recordings": int(len(recording)),
        "people": int(recording["person_id"].nunique()),
    })

    print(
        f"Fold {fold}: "
        f"Accuracy = {fold_accuracy * 100:.2f}%, "
        f"Balanced Accuracy = {fold_balanced_accuracy * 100:.2f}%"
    )

cv_accuracies = [
    item["recording_accuracy"] for item in fold_scores
]

cv_balanced_accuracies = [
    item["recording_balanced_accuracy"] for item in fold_scores
]

print(
    f"\nCV Mean Accuracy: "
    f"{np.mean(cv_accuracies) * 100:.2f}%"
)

print(
    f"CV Std Accuracy: "
    f"{np.std(cv_accuracies) * 100:.2f}%"
)

print(
    f"CV Mean Balanced Accuracy: "
    f"{np.mean(cv_balanced_accuracies) * 100:.2f}%"
)

print(
    f"CV Std Balanced Accuracy: "
    f"{np.std(cv_balanced_accuracies) * 100:.2f}%"
)

print("\n========== FINAL MODEL ==========")

model = RandomForestClassifier(
    n_estimators=N_ESTIMATORS,
    random_state=RANDOM_STATE,
    n_jobs=-1,
)

model.fit(
    train_data[feature_columns],
    train_data["label"],
)

test_data["prediction"] = model.predict(
    test_data[feature_columns]
)

test_data["pd_probability"] = model.predict_proba(
    test_data[feature_columns]
)[:, 1]

recording_test = (
    test_data.groupby("recording_id")
    .agg(
        person_id=("person_id", "first"),
        actual_label=("label", "first"),
        pd_windows=("prediction", "sum"),
        total_windows=("prediction", "count"),
        mean_pd_probability=("pd_probability", "mean"),
    )
    .reset_index()
)

recording_test["pd_ratio"] = (
    recording_test["pd_windows"] / recording_test["total_windows"]
)

recording_test["prediction"] = (
    recording_test["pd_ratio"] >= RECORDING_THRESHOLD
).astype(int)

y_true = recording_test["actual_label"]
y_pred = recording_test["prediction"]
y_probability = recording_test["mean_pd_probability"]

cm = confusion_matrix(y_true, y_pred, labels=[0, 1])
tn, fp, fn, tp = cm.ravel()

test_accuracy = accuracy_score(y_true, y_pred)
test_balanced_accuracy = balanced_accuracy_score(y_true, y_pred)
test_precision = precision_score(y_true, y_pred, zero_division=0)
test_recall = recall_score(y_true, y_pred, zero_division=0)
test_f1 = f1_score(y_true, y_pred, zero_division=0)

sensitivity = float(tp / (tp + fn)) if (tp + fn) else None
specificity = float(tn / (tn + fp)) if (tn + fp) else None

try:
    test_roc_auc = float(roc_auc_score(y_true, y_probability))
except ValueError:
    test_roc_auc = None

report = classification_report(
    y_true,
    y_pred,
    labels=[0, 1],
    target_names=["CTRL", "PD"],
    output_dict=True,
    zero_division=0,
)

print("\n========== UNSEEN-PERSON TEST RESULTS ==========")
print(f"Test recordings: {len(recording_test)}")
print(f"Test people: {recording_test['person_id'].nunique()}")
print(f"Accuracy: {test_accuracy:.4f}")
print(f"Balanced Accuracy: {test_balanced_accuracy:.4f}")
print(f"Precision (PD): {test_precision:.4f}")
print(f"Recall / Sensitivity (PD): {test_recall:.4f}")
print(f"F1-score (PD): {test_f1:.4f}")

if specificity is not None:
    print(f"Specificity (CTRL): {specificity:.4f}")

if test_roc_auc is not None:
    print(f"ROC-AUC: {test_roc_auc:.4f}")
else:
    print("ROC-AUC: unavailable")

print("\nConfusion Matrix:")
print(cm)

print("\nClassification Report:")
print(
    classification_report(
        y_true,
        y_pred,
        labels=[0, 1],
        target_names=["CTRL", "PD"],
        zero_division=0,
    )
)

metrics = {
    "model_name": "Finger Tapping Random Forest",
    "model_type": "RandomForestClassifier",
    "dataset": "fingerTappingData",
    "evaluation_unit": "recording",
    "split_strategy": "stratified person-level train/test split",
    "cross_validation_strategy": "StratifiedGroupKFold",
    "random_state": RANDOM_STATE,
    "test_size_fraction": TEST_SIZE,
    "n_estimators": N_ESTIMATORS,
    "recording_threshold": RECORDING_THRESHOLD,
    "feature_columns": feature_columns,
    "number_of_features": len(feature_columns),
    "total_recordings_processed": int(recording_info["recording_id"].nunique()),
    "total_people": int(person_info["person_id"].nunique()),
    "train_recordings": int(train_data["recording_id"].nunique()),
    "test_recordings": int(recording_test["recording_id"].nunique()),
    "train_people": int(train_data["person_id"].nunique()),
    "test_people": int(recording_test["person_id"].nunique()),
    "class_mapping": {
        "0": "CTRL",
        "1": "PD",
    },
    "cross_validation": {
        "folds": fold_scores,
        "mean_accuracy": float(np.mean(cv_accuracies)),
        "std_accuracy": float(np.std(cv_accuracies)),
        "mean_balanced_accuracy": float(np.mean(cv_balanced_accuracies)),
        "std_balanced_accuracy": float(np.std(cv_balanced_accuracies)),
        "standard_deviation_ddof": 0,
    },
    "test_metrics": {
        "accuracy": float(test_accuracy),
        "balanced_accuracy": float(test_balanced_accuracy),
        "precision_pd": float(test_precision),
        "recall_pd": float(test_recall),
        "f1_score_pd": float(test_f1),
        "sensitivity": sensitivity,
        "specificity": specificity,
        "roc_auc": test_roc_auc,
    },
    "confusion_matrix": {
        "labels": ["CTRL", "PD"],
        "matrix": cm.tolist(),
        "true_negative": int(tn),
        "false_positive": int(fp),
        "false_negative": int(fn),
        "true_positive": int(tp),
    },
    "classification_report": report,
    "evaluated_at_utc": datetime.now(timezone.utc).isoformat(),
    "warning": (
        "Experimental research model. Results depend on the dataset and split; "
        "not clinically validated for diagnosis."
    ),
}

model_dir.mkdir(parents=True, exist_ok=True)
metrics_dir.mkdir(parents=True, exist_ok=True)

model_bundle = {
    "model": model,
    "feature_columns": feature_columns,
    "window_size": 500,
    "recording_threshold": RECORDING_THRESHOLD,
    "classes": ["CTRL", "PD"],
}

joblib.dump(model_bundle, model_path)

with open(metrics_path, "w", encoding="utf-8") as f:
    json.dump(metrics, f, indent=4)

print(f"\nModel saved to: {model_path}")
print(f"Metrics saved to: {metrics_path}")
print("\nTraining and evaluation completed successfully.")
