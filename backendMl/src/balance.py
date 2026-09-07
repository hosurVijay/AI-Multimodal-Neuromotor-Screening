from pathlib import Path
import sys
import numpy as np
import pandas as pd
import joblib

from sklearn.model_selection import train_test_split, StratifiedGroupKFold
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report

root = Path(__file__).resolve().parents[1]

sys.path.insert(0, str(root))

from preprocessing.balance_preprocessing import (
    selected_features,
    process_file
)

dataset_path = root / "dataset" / "balanceDataset"

healthy_path = dataset_path / "Healthy"
pd_path = dataset_path / "PD"

model_path = root / "models" / "balance_model.joblib"

healthy_files = [
    file
    for file in healthy_path.glob("*.csv")
    if file.name != "HC139_Balance.csv"
]

pd_files = list(pd_path.glob("*.csv"))

rows = []

for file in healthy_files:
    data = process_file(file)

    if not data.empty:
        data["label"] = 0
        rows.append(data)

for file in pd_files:
    data = process_file(file)

    if not data.empty:
        data["label"] = 1
        rows.append(data)

data = pd.concat(rows, ignore_index=True)

data = data.dropna(
    subset=selected_features
).reset_index(drop=True)

recording_ids = data["recording_id"].unique()

recording_labels = (
    data
    .groupby("recording_id")["label"]
    .first()
)

train_ids, test_ids = train_test_split(
    recording_ids,
    test_size=0.20,
    random_state=42,
    stratify=recording_labels
)

train_data = data[
    data["recording_id"].isin(train_ids)
].copy()

test_data = data[
    data["recording_id"].isin(test_ids)
].copy()

X = train_data[selected_features]
y = train_data["label"]
groups = train_data["recording_id"]

cv = StratifiedGroupKFold(
    n_splits=5,
    shuffle=True,
    random_state=42
)

fold_scores = []

for fold, (train_idx, val_idx) in enumerate(
    cv.split(X, y, groups=groups),
    start=1
):

    model = RandomForestClassifier(
        n_estimators=200,
        random_state=42,
        n_jobs=-1
    )

    model.fit(
        X.iloc[train_idx],
        y.iloc[train_idx]
    )

    validation = train_data.iloc[val_idx].copy()

    validation["prediction"] = model.predict(
        X.iloc[val_idx]
    )

    recording = (
        validation
        .groupby("recording_id")
        .agg(
            actual_label=("label", "first"),
            pd_windows=("prediction", "sum"),
            total_windows=("prediction", "count")
        )
        .reset_index()
    )

    recording["pd_ratio"] = (
        recording["pd_windows"] /
        recording["total_windows"]
    )

    recording["prediction"] = (
        recording["pd_ratio"] >= 0.5
    ).astype(int)

    score = accuracy_score(
        recording["actual_label"],
        recording["prediction"]
    )

    fold_scores.append(score)

    print(
        f"Fold {fold}: "
        f"{score * 100:.2f}%"
    )

model = RandomForestClassifier(
    n_estimators=200,
    random_state=42,
    n_jobs=-1
)

model.fit(
    train_data[selected_features],
    train_data["label"]
)

test_data["prediction"] = model.predict(
    test_data[selected_features]
)

recording_test = (
    test_data
    .groupby("recording_id")
    .agg(
        actual_label=("label", "first"),
        pd_windows=("prediction", "sum"),
        total_windows=("prediction", "count")
    )
    .reset_index()
)

recording_test["pd_ratio"] = (
    recording_test["pd_windows"] /
    recording_test["total_windows"]
)

recording_test["prediction"] = (
    recording_test["pd_ratio"] >= 0.5
).astype(int)

y_true = recording_test["actual_label"]
y_pred = recording_test["prediction"]

print(
    f"\nCV Mean: "
    f"{np.mean(fold_scores) * 100:.2f}%"
)

print(
    f"CV Std: "
    f"{np.std(fold_scores) * 100:.2f}%"
)

print(
    f"Recording Accuracy: "
    f"{accuracy_score(y_true, y_pred) * 100:.2f}%"
)

print("\nConfusion Matrix:")
print(confusion_matrix(y_true, y_pred))

print("\nClassification Report:")
print(
    classification_report(
        y_true,
        y_pred,
        target_names=["Healthy", "PD"]
    )
)

joblib.dump(
    {
        "model": model,
        "feature_columns": selected_features,
        "window_size": 500,
        "recording_threshold": 0.5,
        "classes": ["Healthy", "PD"]
    },
    model_path
)

print(f"\nModel saved to: {model_path}")