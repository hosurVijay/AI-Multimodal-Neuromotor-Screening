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

from preprocessing.fingerTapping_preprocessing import (
    process_file,
    get_person_id
)

dataset_path = root / "dataset" / "fingerTappingData"

ctrl_path = dataset_path / "CTRL"
pd_path = dataset_path / "PD"

model_path = root / "models" / "finger_tapping_model.joblib"

ctrl_files = list(
    ctrl_path.glob("*.mat")
)

pd_files = list(
    pd_path.glob("*.mat")
)

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
        "label": 0
    })


for file in pd_files:

    data = process_file(file)

    if not data.empty:
        data["label"] = 1
        rows.append(data)

    recording_info.append({
        "recording_id": file.name,
        "person_id": get_person_id(file),
        "label": 1
    })


data = pd.concat(
    rows,
    ignore_index=True
)

feature_columns = [
    column
    for column in data.columns
    if column not in [
        "recording_id",
        "window_id",
        "label"
    ]
]

recording_info = pd.DataFrame(
    recording_info
)

person_info = (
    recording_info[
        ["person_id", "label"]
    ]
    .drop_duplicates("person_id")
)

train_persons, test_persons = train_test_split(
    person_info["person_id"].values,
    test_size=0.20,
    random_state=42,
    stratify=person_info["label"]
)

train_recordings = recording_info[
    recording_info["person_id"].isin(
        train_persons
    )
]["recording_id"].tolist()

test_recordings = recording_info[
    recording_info["person_id"].isin(
        test_persons
    )
]["recording_id"].tolist()

recording_to_person = dict(
    zip(
        recording_info["recording_id"],
        recording_info["person_id"]
    )
)

train_data = data[
    data["recording_id"].isin(
        train_recordings
    )
].copy()

test_data = data[
    data["recording_id"].isin(
        test_recordings
    )
].copy()

train_data["person_id"] = (
    train_data["recording_id"]
    .map(recording_to_person)
)

test_data["person_id"] = (
    test_data["recording_id"]
    .map(recording_to_person)
)

X = train_data[
    feature_columns
]

y = train_data[
    "label"
]

groups = train_data[
    "person_id"
]

cv = StratifiedGroupKFold(
    n_splits=5,
    shuffle=True,
    random_state=42
)

fold_scores = []

for fold, (train_idx, val_idx) in enumerate(
    cv.split(
        X,
        y,
        groups=groups
    ),
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

    validation = train_data.iloc[
        val_idx
    ].copy()

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
    train_data[feature_columns],
    train_data["label"]
)

test_data["prediction"] = model.predict(
    test_data[feature_columns]
)

recording_test = (
    test_data
    .groupby("recording_id")
    .agg(
        person_id=("person_id", "first"),
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

y_true = recording_test[
    "actual_label"
]

y_pred = recording_test[
    "prediction"
]

print(
    f"\nCV Mean: "
    f"{np.mean(fold_scores) * 100:.2f}%"
)

print(
    f"CV Std: "
    f"{np.std(fold_scores) * 100:.2f}%"
)

print(
    f"Unseen-Person Recording Accuracy: "
    f"{accuracy_score(y_true, y_pred) * 100:.2f}%"
)

print("\nConfusion Matrix:")
print(
    confusion_matrix(
        y_true,
        y_pred
    )
)

print("\nClassification Report:")
print(
    classification_report(
        y_true,
        y_pred,
        target_names=[
            "CTRL",
            "PD"
        ]
    )
)

joblib.dump(
    {
        "model": model,
        "feature_columns": feature_columns,
        "window_size": 500,
        "recording_threshold": 0.5,
        "classes": [
            "CTRL",
            "PD"
        ]
    },
    model_path
)

print(
    f"\nModel saved to: {model_path}"
)