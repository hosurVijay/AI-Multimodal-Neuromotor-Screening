import joblib

from sklearn.model_selection import (
    train_test_split,
    StratifiedKFold,
    cross_val_score
)

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    classification_report,
    confusion_matrix
)

from xgboost import XGBClassifier

from preprocessing.voice_preprocessing import (
    load_voice_data,
    VOICE_FEATURES
)

DATA_PATH = "dataset/voiceDataset/parkinsons(1).data"

MODEL_PATH = "models/xgboot_VOICEmodel.joblib"



X, y = load_voice_data(DATA_PATH)


print("Dataset shape:", X.shape)

print("Number of features:", len(VOICE_FEATURES))



X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42,
    stratify=y
)


print("\nTraining samples:", len(X_train))
print("Testing samples:", len(X_test))


model = XGBClassifier(
    n_estimators=300,
    max_depth=3,
    learning_rate=0.05,
    subsample=0.8,
    colsample_bytree=0.8,
    objective="binary:logistic",
    eval_metric="logloss",
    random_state=42,
    n_jobs=-1
)


cv = StratifiedKFold(
    n_splits=10,
    shuffle=True,
    random_state=42
)


cv_scores = cross_val_score(
    model,
    X_train,
    y_train,
    cv=cv,
    scoring="accuracy",
    n_jobs=-1
)


print("\nCross Validation Results")
print("------------------------")

print(
    f"CV Accuracy: "
    f"{cv_scores.mean() * 100:.2f}%"
)

print(
    f"CV Std: "
    f"{cv_scores.std() * 100:.2f}%"
)


model.fit(
    X_train,
    y_train
)


y_pred = model.predict(X_test)


accuracy = accuracy_score(
    y_test,
    y_pred
)

precision = precision_score(
    y_test,
    y_pred,
    pos_label=1
)

recall = recall_score(
    y_test,
    y_pred,
    pos_label=1
)

f1 = f1_score(
    y_test,
    y_pred,
    pos_label=1
)


print("\nFinal Test Results")
print("------------------")

print(
    f"Test Accuracy : "
    f"{accuracy * 100:.2f}%"
)

print(
    f"Precision     : "
    f"{precision * 100:.2f}%"
)

print(
    f"Recall        : "
    f"{recall * 100:.2f}%"
)

print(
    f"F1 Score      : "
    f"{f1 * 100:.2f}%"
)


print("\nClassification Report")

print(
    classification_report(
        y_test,
        y_pred,
        target_names=[
            "Healthy",
            "Parkinson's"
        ]
    )
)


print("\nConfusion Matrix")

print(
    confusion_matrix(
        y_test,
        y_pred
    )
)


print("\nFeature Importance")

for feature, importance in sorted(
    zip(
        VOICE_FEATURES,
        model.feature_importances_
    ),
    key=lambda x: x[1],
    reverse=True
):

    print(
        f"{feature:<25} "
        f"{importance:.4f}"
    )

joblib.dump(
    model,
    MODEL_PATH
)


print("\nModel saved successfully:")
print(MODEL_PATH)