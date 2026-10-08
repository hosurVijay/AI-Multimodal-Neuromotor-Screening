from pathlib import Path

import numpy as np
import pandas as pd
import joblib

from scipy.stats import mannwhitneyu
from statsmodels.stats.multitest import multipletests

from sklearn.model_selection import (
    train_test_split,
    StratifiedKFold,
    GridSearchCV
)

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    roc_auc_score,
    classification_report
)

from xgboost import XGBClassifier


# ============================================================
# 1. PATHS
# ============================================================

ROOT = Path(__file__).resolve().parents[1]

DATA_PATH = ROOT / "dataset" / "balance_window_features.csv"

MODEL_PATH = ROOT / "models" / "balance_xgboost_model.joblib"

MODEL_PATH.parent.mkdir(
    parents=True,
    exist_ok=True
)

print("Project root:", ROOT)
print("Dataset:", DATA_PATH)
print("Model:", MODEL_PATH)


# ============================================================
# 2. LOAD DATA
# ============================================================

df = pd.read_csv(DATA_PATH)

LABEL_COL = "label"

if df[LABEL_COL].dtype == object:
    y = (
        df[LABEL_COL]
        .str.upper()
        .eq("PD")
        .astype(int)
    )
else:
    y = df[LABEL_COL].astype(int)

feature_columns = (
    df
    .drop(columns=[LABEL_COL])
    .select_dtypes(include=np.number)
    .columns
    .tolist()
)

X = df[feature_columns].copy()

print("\n========================================")
print("DATASET")
print("========================================")
print("Total recordings :", len(X))
print("Total features   :", len(feature_columns))
print("Healthy          :", (y == 0).sum())
print("PD               :", (y == 1).sum())


# ============================================================
# 3. TRAIN / TEST SPLIT
# ============================================================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    stratify=y,
    random_state=42
)

print("\n========================================")
print("TRAIN / TEST SPLIT")
print("========================================")
print("Train shape:", X_train.shape)
print("Test shape :", X_test.shape)


# ============================================================
# 4. MANN-WHITNEY + FDR
#    TRAINING DATA ONLY
# ============================================================

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
            alternative="two-sided"
        )

        n_healthy = len(healthy_values)
        n_pd = len(pd_values)

        effect_size = abs(
            (2 * U / (n_healthy * n_pd)) - 1
        )

        results.append({
            "feature": feature,
            "p_value": p_value,
            "effect_size": effect_size
        })

    except Exception:
        continue


stats_df = pd.DataFrame(results)

reject, p_corrected, _, _ = multipletests(
    stats_df["p_value"],
    method="fdr_bh"
)

stats_df["fdr"] = p_corrected
stats_df["significant"] = reject

stats_df = stats_df.sort_values(
    ["significant", "effect_size"],
    ascending=[False, False]
).reset_index(drop=True)

significant_features = stats_df[
    stats_df["significant"]
]["feature"].tolist()

print("\n========================================")
print("STATISTICAL FEATURE SELECTION")
print("========================================")
print(
    "FDR-significant features:",
    len(significant_features)
)


# ============================================================
# 5. SPEARMAN CORRELATION FILTER
#    TRAINING DATA ONLY
# ============================================================

if len(significant_features) > 0:

    corr_matrix = X_train[
        significant_features
    ].corr(
        method="spearman"
    ).abs()

    selected_features = []

    for feature in significant_features:

        keep = True

        for selected in selected_features:

            if corr_matrix.loc[
                feature,
                selected
            ] > 0.90:

                keep = False
                break

        if keep:
            selected_features.append(feature)

else:

    selected_features = (
        stats_df
        .sort_values(
            "effect_size",
            ascending=False
        )
        .head(10)["feature"]
        .tolist()
    )


print(
    "Selected features after correlation filter:",
    len(selected_features)
)

print("\nSelected features:")

for i, feature in enumerate(
    selected_features,
    start=1
):
    print(
        f"{i}. {feature}"
    )


# ============================================================
# 6. SELECT FEATURES
# ============================================================

X_train_selected = X_train[
    selected_features
].copy()

X_test_selected = X_test[
    selected_features
].copy()


# ============================================================
# 7. XGBOOST
# ============================================================

xgb = XGBClassifier(
    objective="binary:logistic",
    eval_metric="logloss",
    random_state=42,
    n_jobs=-1
)

param_grid = {
    "n_estimators": [
        100,
        200,
        300
    ],

    "max_depth": [
        2,
        3,
        4
    ],

    "learning_rate": [
        0.01,
        0.05,
        0.1
    ],

    "subsample": [
        0.8,
        1.0
    ],

    "colsample_bytree": [
        0.8,
        1.0
    ]
}


# ============================================================
# 8. GRID SEARCH
# ============================================================

cv = StratifiedKFold(
    n_splits=5,
    shuffle=True,
    random_state=42
)

grid = GridSearchCV(
    estimator=xgb,
    param_grid=param_grid,
    scoring="f1",
    cv=cv,
    n_jobs=-1,
    refit=True
)

print("\n========================================")
print("XGBOOST GRID SEARCH")
print("========================================")

grid.fit(
    X_train_selected,
    y_train
)

print("\nBest parameters:")

for key, value in grid.best_params_.items():
    print(
        f"{key}: {value}"
    )

print(
    "\nBest CV F1:",
    round(grid.best_score_, 4)
)


# ============================================================
# 9. FINAL MODEL
# ============================================================

final_model = grid.best_estimator_


# ============================================================
# 10. FINAL TEST
# ============================================================

y_pred = final_model.predict(
    X_test_selected
)

y_probability = final_model.predict_proba(
    X_test_selected
)[:, 1]


# ============================================================
# 11. METRICS
# ============================================================

accuracy = accuracy_score(
    y_test,
    y_pred
)

precision = precision_score(
    y_test,
    y_pred,
    zero_division=0
)

recall = recall_score(
    y_test,
    y_pred,
    zero_division=0
)

f1 = f1_score(
    y_test,
    y_pred,
    zero_division=0
)

roc_auc = roc_auc_score(
    y_test,
    y_probability
)


print("\n========================================")
print("FINAL UNSEEN TEST RESULTS")
print("========================================")

print(
    f"Accuracy : {accuracy:.4f} "
    f"({accuracy * 100:.2f}%)"
)

print(
    f"Precision: {precision:.4f} "
    f"({precision * 100:.2f}%)"
)

print(
    f"Recall   : {recall:.4f} "
    f"({recall * 100:.2f}%)"
)

print(
    f"F1 Score : {f1:.4f} "
    f"({f1 * 100:.2f}%)"
)

print(
    f"ROC-AUC  : {roc_auc:.4f}"
)


# ============================================================
# 12. CONFUSION MATRIX
# ============================================================

cm = confusion_matrix(
    y_test,
    y_pred
)

print("\n========================================")
print("CONFUSION MATRIX")
print("========================================")

print(cm)


# ============================================================
# 13. CLASSIFICATION REPORT
# ============================================================

print("\n========================================")
print("CLASSIFICATION REPORT")
print("========================================")

print(
    classification_report(
        y_test,
        y_pred,
        target_names=[
            "Healthy",
            "PD"
        ],
        zero_division=0
    )
)


# ============================================================
# 14. SAVE / OVERWRITE MODEL
# ============================================================

model_package = {
    "model": final_model,
    "features": selected_features,

    "label_mapping": {
        0: "Healthy",
        1: "PD"
    },

    "metrics": {
        "accuracy": accuracy,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "roc_auc": roc_auc
    }
}

joblib.dump(
    model_package,
    MODEL_PATH
)

print("\n========================================")
print("MODEL SAVED")
print("========================================")

print(
    "Saved / overwritten:",
    MODEL_PATH
)