from pathlib import Path

import joblib
import pandas as pd

from sklearn.model_selection import (
    StratifiedKFold,
    cross_validate
)

from sklearn.pipeline import Pipeline
from sklearn.preprocessing import MinMaxScaler
from sklearn.linear_model import LogisticRegression


BASE_DIR = Path(__file__).resolve().parents[1]

DATA_PATH = (
    BASE_DIR /
    "dataset" /
    "gait_v2.csv"
)

MODEL_PATH = (
    BASE_DIR /
    "models" /
    "gait_model.joblib"
)


df = pd.read_csv(DATA_PATH)

X = df.drop(
    columns=["recording_id", "label"]
)

y = df["label"]


model = Pipeline([
    (
        "scaler",
        MinMaxScaler()
    ),
    (
        "lr",
        LogisticRegression(
            C=2,
            penalty="l2",
            solver="liblinear",
            random_state=42,
            max_iter=1000
        )
    )
])


cv = StratifiedKFold(
    n_splits=5,
    shuffle=True,
    random_state=42
)


scoring = [
    "accuracy",
    "precision",
    "recall",
    "f1"
]


results = cross_validate(
    model,
    X,
    y,
    cv=cv,
    scoring=scoring,
    n_jobs=-1
)


print("Gait Model Performance")
print("----------------------")

print(
    f"Accuracy  : "
    f"{results['test_accuracy'].mean() * 100:.2f}% "
    f"+/- "
    f"{results['test_accuracy'].std() * 100:.2f}%"
)

print(
    f"Precision : "
    f"{results['test_precision'].mean() * 100:.2f}% "
    f"+/- "
    f"{results['test_precision'].std() * 100:.2f}%"
)

print(
    f"Recall    : "
    f"{results['test_recall'].mean() * 100:.2f}% "
    f"+/- "
    f"{results['test_recall'].std() * 100:.2f}%"
)

print(
    f"F1-Score  : "
    f"{results['test_f1'].mean() * 100:.2f}% "
    f"+/- "
    f"{results['test_f1'].std() * 100:.2f}%"
)


model.fit(X, y)

MODEL_PATH.parent.mkdir(
    parents=True,
    exist_ok=True
)

joblib.dump(
    model,
    MODEL_PATH
)

print("\nModel saved to:")
print(MODEL_PATH)