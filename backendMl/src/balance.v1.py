import os
import json
import joblib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

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
    roc_curve,
    classification_report
)

from xgboost import XGBClassifier


# ============================================================
# PATHS
# ============================================================

DATA_PATH = "dataset/balance_window_features.csv"

MODEL_DIR = "models"
RESULT_DIR = "results/balance"

os.makedirs(MODEL_DIR, exist_ok=True)
os.makedirs(RESULT_DIR, exist_ok=True)


# ============================================================
# SETTINGS
# ============================================================

RANDOM_STATE = 42
TEST_SIZE = 0.20
CORRELATION_THRESHOLD = 0.90
FDR_THRESHOLD = 0.05


# ============================================================
# LOAD DATA
# ============================================================

df = pd.read_csv(DATA_PATH)

LABEL_COLUMN = "label"

print("=" * 60)
print("BALANCE DISORDER CLASSIFICATION")
print("=" * 60)

print(f"\nTotal recordings: {len(df)}")


# ============================================================
# LABEL MAPPING
# ============================================================

if df[LABEL_COLUMN].dtype == object:

    label_values = (
        df[LABEL_COLUMN]
        .astype(str)
        .str.upper()
        .str.strip()
    )

    y = label_values.map({
        "HEALTHY": 0,
        "BALANCE": 1,
        "BALANCEDISORDER": 1,
        "BALANCE_DISORDER": 1
    })

    if y.isna().any():
        raise ValueError(
            "Unknown labels found: "
            + str(label_values[y.isna()].unique())
        )

    y = y.astype(int)

else:

    y = df[LABEL_COLUMN].astype(int)


# ============================================================
# FEATURE MATRIX
# ============================================================

X = df.drop(
    columns=[LABEL_COLUMN]
).select_dtypes(
    include=np.number
).copy()

print(f"Total features: {X.shape[1]}")

print("\nClass distribution:")

print(
    pd.Series(
        y.map({
            0: "Healthy",
            1: "BalanceDisorder"
        })
    ).value_counts()
)


# ============================================================
# TRAIN / TEST SPLIT
# ============================================================

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=TEST_SIZE,
    stratify=y,
    random_state=RANDOM_STATE
)

print("\n" + "=" * 60)
print("TRAIN / TEST SPLIT")
print("=" * 60)

print(f"Training recordings: {len(X_train)}")
print(f"Test recordings:     {len(X_test)}")

print("\nTraining distribution:")

print(
    y_train.map({
        0: "Healthy",
        1: "BalanceDisorder"
    }).value_counts()
)

print("\nTest distribution:")

print(
    y_test.map({
        0: "Healthy",
        1: "BalanceDisorder"
    }).value_counts()
)


# ============================================================
# FEATURE DISCOVERY
# TRAINING DATA ONLY
# ============================================================

print("\n" + "=" * 60)
print("FEATURE DISCOVERY")
print("=" * 60)

healthy_train = X_train[y_train == 0]
disorder_train = X_train[y_train == 1]

statistical_results = []

for feature in X_train.columns:

    healthy_values = healthy_train[feature].dropna()
    disorder_values = disorder_train[feature].dropna()

    if (
        len(healthy_values) == 0
        or len(disorder_values) == 0
    ):
        continue

    try:

        U, p_value = mannwhitneyu(
            healthy_values,
            disorder_values,
            alternative="two-sided"
        )

        n_healthy = len(healthy_values)
        n_disorder = len(disorder_values)

        effect_size = abs(
            (2 * U / (n_healthy * n_disorder)) - 1
        )

        statistical_results.append({
            "feature": feature,
            "p_value": p_value,
            "effect_size": effect_size
        })

    except Exception:
        continue


stats_df = pd.DataFrame(statistical_results)


# ============================================================
# FDR CORRECTION
# ============================================================

reject, corrected_pvalues, _, _ = multipletests(
    stats_df["p_value"],
    method="fdr_bh"
)

stats_df["fdr"] = corrected_pvalues
stats_df["significant"] = reject

stats_df = stats_df.sort_values(
    by=["significant", "effect_size"],
    ascending=[False, False]
).reset_index(drop=True)


significant_features = stats_df[
    stats_df["fdr"] < FDR_THRESHOLD
]["feature"].tolist()


print(f"\nFDR-significant features: {len(significant_features)}")


stats_df.to_csv(
    os.path.join(
        RESULT_DIR,
        "balance_feature_statistics.csv"
    ),
    index=False
)


# ============================================================
# CORRELATION FILTER
# TRAINING DATA ONLY
# ============================================================

if len(significant_features) == 0:

    raise RuntimeError(
        "No features survived FDR correction."
    )


correlation_matrix = X_train[
    significant_features
].corr(
    method="spearman"
).abs()


selected_features = []

for feature in significant_features:

    keep_feature = True

    for selected_feature in selected_features:

        correlation = correlation_matrix.loc[
            feature,
            selected_feature
        ]

        if correlation > CORRELATION_THRESHOLD:

            keep_feature = False
            break

    if keep_feature:

        selected_features.append(feature)


print(
    f"Selected features after correlation filtering: "
    f"{len(selected_features)}"
)

print("\nSelected features:")

for index, feature in enumerate(
    selected_features,
    start=1
):

    print(
        f"{index}. {feature}"
    )


# ============================================================
# SAVE SELECTED FEATURES
# ============================================================

with open(
    os.path.join(
        RESULT_DIR,
        "balance_selected_features.json"
    ),
    "w"
) as file:

    json.dump(
        selected_features,
        file,
        indent=4
    )


# ============================================================
# SELECT FEATURES
# ============================================================

X_train_selected = X_train[
    selected_features
].copy()

X_test_selected = X_test[
    selected_features
].copy()


# ============================================================
# XGBOOST
# TRAINING DATA ONLY
# ============================================================

print("\n" + "=" * 60)
print("XGBOOST HYPERPARAMETER TUNING")
print("=" * 60)

xgb = XGBClassifier(
    objective="binary:logistic",
    eval_metric="logloss",
    random_state=RANDOM_STATE,
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


inner_cv = StratifiedKFold(
    n_splits=5,
    shuffle=True,
    random_state=RANDOM_STATE
)


grid = GridSearchCV(
    estimator=xgb,
    param_grid=param_grid,
    scoring="f1",
    cv=inner_cv,
    n_jobs=-1,
    refit=True
)


grid.fit(
    X_train_selected,
    y_train
)


final_model = grid.best_estimator_


print("\nBest parameters:")

print(
    grid.best_params_
)


print(
    f"\nBest training CV F1: "
    f"{grid.best_score_:.4f}"
)


# ============================================================
# FINAL TEST
# TEST SET USED FOR THE FIRST TIME
# ============================================================

print("\n" + "=" * 60)
print("FINAL UNSEEN TEST")
print("=" * 60)


y_pred = final_model.predict(
    X_test_selected
)


y_probability = final_model.predict_proba(
    X_test_selected
)[:, 1]


# ============================================================
# METRICS
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


print("\nFinal Test Results:")

print(
    f"Accuracy : {accuracy * 100:.2f}%"
)

print(
    f"Precision: {precision * 100:.2f}%"
)

print(
    f"Recall   : {recall * 100:.2f}%"
)

print(
    f"F1 Score : {f1 * 100:.2f}%"
)

print(
    f"ROC-AUC  : {roc_auc:.3f}"
)


# ============================================================
# CLASSIFICATION REPORT
# ============================================================

print("\nClassification Report:\n")

print(
    classification_report(
        y_test,
        y_pred,
        target_names=[
            "Healthy",
            "BalanceDisorder"
        ],
        zero_division=0
    )
)


# ============================================================
# METRICS TABLE
# ============================================================

metrics_df = pd.DataFrame({
    "Metric": [
        "Accuracy",
        "Precision",
        "Recall",
        "F1 Score",
        "ROC-AUC"
    ],

    "Score": [
        accuracy,
        precision,
        recall,
        f1,
        roc_auc
    ]
})


metrics_df.to_csv(
    os.path.join(
        RESULT_DIR,
        "balance_final_metrics.csv"
    ),
    index=False
)


# ============================================================
# METRICS TABLE IMAGE
# ============================================================

table_values = [
    [
        "Accuracy",
        f"{accuracy * 100:.2f}%"
    ],
    [
        "Precision",
        f"{precision * 100:.2f}%"
    ],
    [
        "Recall",
        f"{recall * 100:.2f}%"
    ],
    [
        "F1 Score",
        f"{f1 * 100:.2f}%"
    ],
    [
        "ROC-AUC",
        f"{roc_auc:.3f}"
    ]
]


fig, ax = plt.subplots(
    figsize=(8, 4)
)

ax.axis("off")

table = ax.table(
    cellText=table_values,
    colLabels=[
        "Metric",
        "Final Test Score"
    ],
    cellLoc="center",
    loc="center"
)

table.auto_set_font_size(False)
table.set_fontsize(12)
table.scale(
    1,
    2
)

plt.title(
    "Balance Disorder Classification - Final Test Metrics",
    pad=20
)

plt.tight_layout()

plt.savefig(
    os.path.join(
        RESULT_DIR,
        "balance_metrics_table.png"
    ),
    dpi=300,
    bbox_inches="tight"
)

plt.show()


# ============================================================
# BENCHMARK PLOT
# ============================================================

benchmark_metrics = {
    "Accuracy": accuracy * 100,
    "Precision": precision * 100,
    "Recall": recall * 100,
    "F1 Score": f1 * 100
}


plt.figure(
    figsize=(8, 6)
)

bars = plt.bar(
    benchmark_metrics.keys(),
    benchmark_metrics.values()
)

plt.ylim(
    0,
    100
)

plt.ylabel(
    "Score (%)"
)

plt.xlabel(
    "Evaluation Metric"
)

plt.title(
    "Balance Disorder XGBoost - Final Test Benchmark"
)

for bar, value in zip(
    bars,
    benchmark_metrics.values()
):

    plt.text(
        bar.get_x() + bar.get_width() / 2,
        value + 1,
        f"{value:.2f}%",
        ha="center",
        va="bottom"
    )


plt.tight_layout()

plt.savefig(
    os.path.join(
        RESULT_DIR,
        "balance_benchmark.png"
    ),
    dpi=300,
    bbox_inches="tight"
)

plt.show()


# ============================================================
# CONFUSION MATRIX
# ============================================================

cm = confusion_matrix(
    y_test,
    y_pred
)


plt.figure(
    figsize=(7, 6)
)

plt.imshow(
    cm
)

plt.title(
    "Balance Disorder XGBoost - Final Test Confusion Matrix"
)

plt.xlabel(
    "Predicted"
)

plt.ylabel(
    "Actual"
)

plt.xticks(
    [0, 1],
    [
        "Healthy",
        "BalanceDisorder"
    ]
)

plt.yticks(
    [0, 1],
    [
        "Healthy",
        "BalanceDisorder"
    ]
)


for i in range(2):

    for j in range(2):

        plt.text(
            j,
            i,
            cm[i, j],
            ha="center",
            va="center",
            fontsize=16
        )


plt.colorbar()

plt.tight_layout()

plt.savefig(
    os.path.join(
        RESULT_DIR,
        "balance_confusion_matrix.png"
    ),
    dpi=300,
    bbox_inches="tight"
)

plt.show()


# ============================================================
# ROC CURVE
# ============================================================

fpr, tpr, thresholds = roc_curve(
    y_test,
    y_probability
)


plt.figure(
    figsize=(8, 6)
)

plt.plot(
    fpr,
    tpr,
    label=f"XGBoost (AUC = {roc_auc:.3f})"
)

plt.plot(
    [0, 1],
    [0, 1],
    linestyle="--",
    label="Random classifier"
)

plt.xlabel(
    "False Positive Rate"
)

plt.ylabel(
    "True Positive Rate / Recall"
)

plt.title(
    "Balance Disorder XGBoost - Final Test ROC Curve"
)

plt.legend()

plt.grid(
    alpha=0.3
)

plt.tight_layout()

plt.savefig(
    os.path.join(
        RESULT_DIR,
        "balance_roc_curve.png"
    ),
    dpi=300,
    bbox_inches="tight"
)

plt.show()


# ============================================================
# FEATURE IMPORTANCE
# ============================================================

feature_importance = pd.Series(
    final_model.feature_importances_,
    index=selected_features
).sort_values(
    ascending=True
)


feature_importance.to_csv(
    os.path.join(
        RESULT_DIR,
        "balance_feature_importance.csv"
    )
)


plt.figure(
    figsize=(10, 7)
)

feature_importance.plot(
    kind="barh"
)

plt.xlabel(
    "Importance"
)

plt.ylabel(
    "Feature"
)

plt.title(
    "XGBoost Feature Importance - Balance Disorder"
)

plt.tight_layout()

plt.savefig(
    os.path.join(
        RESULT_DIR,
        "balance_feature_importance.png"
    ),
    dpi=300,
    bbox_inches="tight"
)

plt.show()


# ============================================================
# SAVE FINAL MODEL
# ============================================================

model_path = os.path.join(
    MODEL_DIR,
    "balance_xgboost_model.joblib"
)

joblib.dump(
    final_model,
    model_path
)


# ============================================================
# SAVE TEST RESULTS
# ============================================================

test_results = pd.DataFrame({
    "actual": y_test.map({
        0: "Healthy",
        1: "BalanceDisorder"
    }).values,

    "predicted": pd.Series(
        y_pred
    ).map({
        0: "Healthy",
        1: "BalanceDisorder"
    }).values,

    "model_estimated_likelihood": y_probability
})


test_results.to_csv(
    os.path.join(
        RESULT_DIR,
        "balance_test_predictions.csv"
    ),
    index=False
)


# ============================================================
# FINAL SUMMARY
# ============================================================

print("\n" + "=" * 60)
print("BALANCE DISORDER MODEL COMPLETE")
print("=" * 60)

print(
    f"\nSelected features: "
    f"{len(selected_features)}"
)

print(
    f"Final accuracy: "
    f"{accuracy * 100:.2f}%"
)

print(
    f"Final precision: "
    f"{precision * 100:.2f}%"
)

print(
    f"Final recall: "
    f"{recall * 100:.2f}%"
)

print(
    f"Final F1: "
    f"{f1 * 100:.2f}%"
)

print(
    f"Final ROC-AUC: "
    f"{roc_auc:.3f}"
)

print(
    f"\nModel saved to:"
    f"\n{model_path}"
)

print(
    f"\nResults saved to:"
    f"\n{RESULT_DIR}"
)

print("\nDone.")