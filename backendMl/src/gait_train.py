
from pathlib import Path
import json

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

DATA_PATH = BASE_DIR / "dataset" / "gait_v2.csv"

MODEL_PATH = BASE_DIR / "models" / "gait_model.joblib"

METRICS_DIR = BASE_DIR / "metrics"
METRICS_PATH = METRICS_DIR / "gait_model_metrics.json"


df = pd.read_csv(DATA_PATH)

X = df.drop(columns=["recording_id", "label"])
y = df["label"]


model = Pipeline([
    ("scaler", MinMaxScaler()),
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


accuracy = results["test_accuracy"].mean()
precision = results["test_precision"].mean()
recall = results["test_recall"].mean()
f1 = results["test_f1"].mean()


print("Gait Model Performance")
print("----------------------")
print(f"Accuracy  : {accuracy * 100:.2f}%")
print(f"Precision : {precision * 100:.2f}%")
print(f"Recall    : {recall * 100:.2f}%")
print(f"F1-Score  : {f1 * 100:.2f}%")


# Train the final model on the complete dataset
model.fit(X, y)

MODEL_PATH.parent.mkdir(
    parents=True,
    exist_ok=True
)

joblib.dump(model, MODEL_PATH)

print("\nModel saved to:")
print(MODEL_PATH)


# Save only the four evaluation metrics
METRICS_DIR.mkdir(
    parents=True,
    exist_ok=True
)

metrics = {
    "accuracy": float(accuracy),
    "precision": float(precision),
    "recall": float(recall),
    "f1_score": float(f1)
}

with open(METRICS_PATH, "w", encoding="utf-8") as f:
    json.dump(metrics, f, indent=4)

print("\nMetrics saved to:")
print(METRICS_PATH)
