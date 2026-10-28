
from pathlib import Path
import json
from datetime import datetime, timezone

import numpy as np
import pandas as pd
import joblib

from scipy.stats import mannwhitneyu
from statsmodels.stats.multitest import multipletests

from sklearn.model_selection import (
    train_test_split,
    StratifiedKFold,
    GridSearchCV,
)

from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    roc_auc_score,
    classification_report,
)

from xgboost import XGBClassifier


ROOT = Path(__file__).resolve().parents[1]

DATA_PATH = ROOT / "dataset" / "balance_window_features.csv"
MODEL_PATH = ROOT / "models" / "balance_xgboost_model.joblib"
METRICS_DIR = ROOT / "metrics"
METRICS_PATH = METRICS_DIR / "balance_xgboost_model_metrics.json"

RANDOM_STATE = 42
TEST_SIZE = 0.20

MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
METRICS_DIR.mkdir(parents=True, exist_ok=True)

print("Project root:", ROOT)
print("Dataset:", DATA_PATH)
print("Model:", MODEL_PATH)
print("Metrics:", METRICS_PATH)

if not DATA_PATH.exists():
    raise FileNotFoundError(f"Dataset not found: {DATA_PATH}")

df = pd.read_csv(DATA_PATH)

LABEL_COL = "label"

if LABEL_COL not in df.columns:
    raise ValueError(f"Dataset must contain a '{LABEL_COL}' column.")

if df[LABEL_COL].dtype == object:
    labels = df[LABEL_COL].astype(str).str.strip().str.upper()

    invalid_labels = ~labels.isin(["PD", "HEALTHY", "CTRL", "CONTROL"])

    if invalid_labels.any():
        raise ValueError(
            f"Unexpected label values: {labels[invalid_labels].unique().tolist()}"
        )

    y = labels.isin(["PD"]).astype(int)
else:
    y = pd.to_numeric(df[LABEL_COL], errors="coerce")

    if y.isna().any() or not y.isin([0, 1]).all():
        raise ValueError("Numeric labels must be 0 (Healthy) or 1 (PD).")

    y = y.astype(int)

feature_columns = (
    df.drop(columns=[LABEL_COL])
    .select_dtypes(include=np.number)
    .columns.tolist()
)

if not feature_columns:
    raise ValueError("No numeric feature columns found.")

X = df[feature_columns].copy()

if X.isna().any().any():
    raise ValueError("Missing feature values found in the dataset.")

if not np.isfinite(X.to_numpy(dtype=float)).all():
    raise ValueError("Infinite or non-finite feature values found.")

if y.nunique() != 2:
    raise ValueError("The dataset must contain both Healthy and PD samples.")

print("\nDATASET")
print("Total samples:", len(X))
print("Total features:", len(feature_columns))
print("Healthy:", int((y == 0).sum()))
print("PD:", int((y == 1).sum()))

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=TEST_SIZE,
    stratify=y,
    random_state=RANDOM_STATE,
)

print("\nTRAIN / TEST SPLIT")
print("Train shape:", X_train.shape)
print("Test shape:", X_test.shape)

healthy_train = X_train[y_train == 0]
pd_train = X_train[y_train == 1]

results = []

for feature in X_train.columns:
    healthy_values = healthy_train[feature].dropna()
    pd_values = pd_train[feature].dropna()

    if len(healthy_values) == 0 or len(pd_values) == 0:
        continue

    try:
        U, p_value = mannwhitneyu(
            healthy_values,
            pd_values,
            alternative="two-sided",
        )

        n_healthy = len(healthy_values)
        n_pd = len(pd_values)

        effect_size = abs(
            (2 * U / (n_healthy * n_pd)) - 1
        )

        results.append({
            "feature": feature,
            "p_value": float(p_value),
            "effect_size": float(effect_size),
        })

    except (ValueError, TypeError):
        continue

stats_df = pd.DataFrame(results)

if stats_df.empty:
    raise ValueError("No features could be evaluated statistically.")

reject, p_corrected, _, _ = multipletests(
    stats_df["p_value"],
    method="fdr_bh",
)

stats_df["fdr"] = p_corrected
stats_df["significant"] = reject

stats_df = stats_df.sort_values(
    ["significant", "effect_size"],
    ascending=[False, False],
).reset_index(drop=True)

significant_features = stats_df[
    stats_df["significant"]
]["feature"].tolist()

print("\nSTATISTICAL FEATURE SELECTION")
print("FDR-significant features:", len(significant_features))

if significant_features:
    corr_matrix = X_train[significant_features].corr(
        method="spearman"
    ).abs()

    selected_features = []

    for feature in significant_features:
        keep = True

        for selected in selected_features:
            correlation = corr_matrix.loc[feature, selected]

            if pd.notna(correlation) and correlation > 0.90:
                keep = False
                break

        if keep:
            selected_features.append(feature)
else:
    selected_features = (
        stats_df.sort_values("effect_size", ascending=False)
        .head(10)["feature"]
        .tolist()
    )

if not selected_features:
    raise ValueError("No features were selected.")

print("Selected features after correlation filter:", len(selected_features))
print("\nSelected features:")

for i, feature in enumerate(selected_features, start=1):
    print(f"{i}. {feature}")

X_train_selected = X_train[selected_features].copy()
X_test_selected = X_test[selected_features].copy()

xgb = XGBClassifier(
    objective="binary:logistic",
    eval_metric="logloss",
    random_state=RANDOM_STATE,
    n_jobs=-1,
)

param_grid = {
    "n_estimators": [100, 200, 300],
    "max_depth": [2, 3, 4],
    "learning_rate": [0.01, 0.05, 0.1],
    "subsample": [0.8, 1.0],
    "colsample_bytree": [0.8, 1.0],
}

class_counts = y_train.value_counts()

if class_counts.min() < 5:
    raise ValueError(
        "At least five training samples per class are required "
        "for five-fold stratified cross-validation."
    )

cv = StratifiedKFold(
    n_splits=5,
    shuffle=True,
    random_state=RANDOM_STATE,
)

grid = GridSearchCV(
    estimator=xgb,
    param_grid=param_grid,
    scoring="f1",
    cv=cv,
    n_jobs=-1,
    refit=True,
)

print("\nXGBOOST GRID SEARCH")
grid.fit(X_train_selected, y_train)

print("\nBest parameters:")
for key, value in grid.best_params_.items():
    print(f"{key}: {value}")

print("Best CV F1:", round(grid.best_score_, 4))

final_model = grid.best_estimator_

y_pred = final_model.predict(X_test_selected)
y_probability = final_model.predict_proba(X_test_selected)[:, 1]

accuracy = accuracy_score(y_test, y_pred)
balanced_accuracy = balanced_accuracy_score(y_test, y_pred)
precision = precision_score(y_test, y_pred, zero_division=0)
recall = recall_score(y_test, y_pred, zero_division=0)
f1 = f1_score(y_test, y_pred, zero_division=0)

try:
    roc_auc = roc_auc_score(y_test, y_probability)
except ValueError:
    roc_auc = None

cm = confusion_matrix(y_test, y_pred, labels=[0, 1])
tn, fp, fn, tp = cm.ravel()

sensitivity = float(tp / (tp + fn)) if (tp + fn) else None
specificity = float(tn / (tn + fp)) if (tn + fp) else None

report = classification_report(
    y_test,
    y_pred,
    labels=[0, 1],
    target_names=["Healthy", "PD"],
    output_dict=True,
    zero_division=0,
)

print("\nFINAL UNSEEN TEST RESULTS")
print(f"Accuracy:          {accuracy:.4f} ({accuracy * 100:.2f}%)")
print(f"Balanced accuracy: {balanced_accuracy:.4f}")
print(f"Precision:         {precision:.4f}")
print(f"Recall:            {recall:.4f}")
print(f"F1 score:          {f1:.4f}")

if roc_auc is not None:
    print(f"ROC-AUC:           {roc_auc:.4f}")
else:
    print("ROC-AUC: unavailable")

if sensitivity is not None:
    print(f"Sensitivity:       {sensitivity:.4f}")

if specificity is not None:
    print(f"Specificity:       {specificity:.4f}")

print("\nCONFUSION MATRIX")
print(cm)

print("\nCLASSIFICATION REPORT")
print(
    classification_report(
        y_test,
        y_pred,
        labels=[0, 1],
        target_names=["Healthy", "PD"],
        zero_division=0,
    )
)

model_package = {
    "model": final_model,
    "features": selected_features,
    "label_mapping": {
        0: "Healthy",
        1: "PD",
    },
    "metrics": {
        "accuracy": float(accuracy),
        "balanced_accuracy": float(balanced_accuracy),
        "precision": float(precision),
        "recall": float(recall),
        "f1": float(f1),
        "roc_auc": float(roc_auc) if roc_auc is not None else None,
        "sensitivity": sensitivity,
        "specificity": specificity,
    },
}

metrics = {
    "model_name": "Balance XGBoost",
    "dataset": DATA_PATH.name,
    "evaluation_method": "Stratified 80/20 train-test split",
    "random_state": RANDOM_STATE,
    "test_size_fraction": TEST_SIZE,
    "dataset_size": int(len(X)),
    "train_size": int(len(X_train)),
    "test_size": int(len(X_test)),
    "original_feature_count": int(len(feature_columns)),
    "selected_feature_count": int(len(selected_features)),
    "selected_features": selected_features,
    "feature_selection": {
        "statistical_test": "Mann-Whitney U",
        "multiple_testing_correction": "Benjamini-Hochberg FDR",
        "correlation_method": "Spearman",
        "correlation_threshold": 0.90,
        "fdr_significant_feature_count": int(len(significant_features)),
        "feature_statistics": stats_df.to_dict(orient="records"),
    },
    "best_parameters": grid.best_params_,
    "best_cv_f1": float(grid.best_score_),
    "test_metrics": {
        "accuracy": float(accuracy),
        "balanced_accuracy": float(balanced_accuracy),
        "precision": float(precision),
        "recall": float(recall),
        "f1": float(f1),
        "roc_auc": float(roc_auc) if roc_auc is not None else None,
        "sensitivity": sensitivity,
        "specificity": specificity,
    },
    "confusion_matrix": {
        "labels": ["Healthy", "PD"],
        "matrix": cm.tolist(),
        "true_negative": int(tn),
        "false_positive": int(fp),
        "false_negative": int(fn),
        "true_positive": int(tp),
    },
    "classification_report": report,
    "evaluated_at_utc": datetime.now(timezone.utc).isoformat(),
    "warning": (
        "Experimental research model. Results depend on the dataset and "
        "evaluation split and are not clinical validation."
    ),
}

joblib.dump(model_package, MODEL_PATH)

with open(METRICS_PATH, "w", encoding="utf-8") as f:
    json.dump(metrics, f, indent=4, allow_nan=False)

print("\nMODEL SAVED")
print("Saved / overwritten:", MODEL_PATH)
print("Metrics saved:", METRICS_PATH)
