# %%
import pandas as pd 
import numpy as np
from pathlib import Path

# %%
dataset_path = Path("../dataset/balanceDataset")

# %%
healthy_path = dataset_path/"Healthy"

# %%
pd_path = dataset_path/"PD"

# %%
healthy_files = list(healthy_path.glob("*.csv"))

# %%
pd_files = list(pd_path.glob("*.csv"))

# %%
len(healthy_files)
len(pd_files)

# %%
balance_features = [
    "R_Wrist_Acc_X",
    "R_Wrist_Acc_Y",
    "R_Wrist_Acc_Z",
    "R_Wrist_Gyr_X",
    "R_Wrist_Gyr_Y",
    "R_Wrist_Gyr_Z"
]

# %%
len(list(pd_path.iterdir()))

# %%
from collections import Counter

Counter(file.suffix for file in pd_path.iterdir())

# %%
def extract_feature(df, feature_cols):
    features = {}
    for col in feature_cols:
        signal = pd.to_numeric(
            df[col],
            errors="coerce"
        ).dropna()
        features[f"{col}_mean"] = signal.mean()
        features[f"{col}_std"] = signal.std()
        features[f"{col}_min"] = signal.min()
        features[f"{col}_max"] = signal.max()
        features[f"{col}_rms"] = np.sqrt(np.mean(signal ** 2))

    return features

# %%
df = pd.read_csv(
    healthy_files[0],
    usecols=balance_features
)

# %%
features = extract_feature(df, balance_features)

# %%
print("Number of features", len(features))

# %%
pd.Series(features)

# %%


# %%
test_df = pd.read_csv(healthy_files[0])

print([repr(col) for col in test_df.columns if "Wrist" in col])

# %%
print([repr(col) for col in balance_features])

# %%
test_df = pd.read_csv(healthy_files[0])

print([repr(col) for col in test_df.columns[:20]])

# %%
print([repr(col) for col in test_df.columns if "Wrist" in col])

# %%
print(balance_features == [
    col for col in test_df.columns
    if col in balance_features
])

# %%
for file in healthy_files:
    df_test = pd.read_csv(file, nrows=1)

    missing = [col for col in balance_features if col not in df_test.columns]

    if missing:
        print("Problem file:", file.name)
        print("Missing:", missing)

# %%
problem_file = healthy_path / "HC139_Balance.csv"

problem_df = pd.read_csv(problem_file, nrows=1)

print(problem_df.shape)
print([col for col in problem_df.columns if "Wrist" in col])

# %%
print(problem_df.columns.tolist())

# %%
for file in pd_files:
    df_test = pd.read_csv(file, nrows=1)

    missing = [
        col for col in balance_features
        if col not in df_test.columns
    ]

    if missing:
        print("Problem file:", file.name)
        print("Missing:", missing)

# %%
usable_healthy_files = [
    file for file in healthy_files
    if file.name != "HC139_Balance.csv"
]

usable_pd_files = pd_files.copy()

print("Usable Healthy:", len(usable_healthy_files))
print("Usable PD:", len(usable_pd_files))
print("Total:", len(usable_healthy_files) + len(usable_pd_files))

# %%
print("Excluded Healthy:", set(healthy_files) - set(usable_healthy_files))

# %%
x_data = []
y_data = []
for file in usable_healthy_files:
    df = pd.read_csv(file, usecols=balance_features)
    features = extract_feature(df, balance_features)
    x_data.append(features)
    y_data.append(0)


for file in pd_files:
    df = pd.read_csv(file, usecols=balance_features)
    features = extract_feature(df, balance_features)
    x_data.append(features)
    y_data.append(1)


# %%
len(x_data)

# %%
X= pd.DataFrame(x_data)
Y= pd.Series(y_data, name = "label")

# %%
print("X shape:", X.shape)
print("y shape:", y.shape)


# %%
Y.value_counts()

# %%
print("NaN values:", X.isnull().sum().sum())
print("Infinite values:", np.isinf(X).sum().sum())

# %%
X.head()

# %%
print("X shape:", X.shape)
print("NaN:", X.isnull().sum().sum())
print("Inf:", np.isinf(X).sum().sum())

# %%
from sklearn.model_selection import train_test_split

# %%
X_train, X_test, Y_train, Y_test = train_test_split(
    X, 
    Y,
    test_size=0.2,
    random_state=42,
    stratify=Y
)

# %%
print("X_train:", X_train.shape)
print("X_test :", X_test.shape)
print("Y_train:", Y_train.shape)
print("Y_test :", Y_test.shape)

# %%
print("Train:")
print(Y_train.value_counts())

print("\nTest:")
print(Y_test.value_counts())

# %%
from sklearn.ensemble import RandomForestClassifier

# %%
model = RandomForestClassifier(
    n_estimators= 200,
    random_state=42
)

# %%
model.fit(X_train, Y_train)

# %%
y_pred = model.predict(X_test)

# %%
y_pred

# %%
from sklearn.metrics import(
    accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, classification_report
)

# %%
print("Accuracy :", accuracy_score(Y_test, y_pred))
print("Precision:", precision_score(Y_test, y_pred))
print("Recall   :", recall_score(Y_test, y_pred))
print("F1 Score :", f1_score(Y_test, y_pred))

# %%
cm = confusion_matrix(Y_test, y_pred)

# %%
print(cm)

# %%
print(classification_report(
    Y_test,
    y_pred,
    target_names=["Healthy", "PD"]
))

# %%
def extract_balance_features(df, feature_cols):
    features = {}

    # Convert to numeric
    df = df[feature_cols].apply(pd.to_numeric, errors="coerce")

    # Individual signals
    for col in feature_cols:
        signal = df[col].dropna()

        features[f"{col}_mean"] = signal.mean()
        features[f"{col}_std"] = signal.std()
        features[f"{col}_min"] = signal.min()
        features[f"{col}_max"] = signal.max()
        features[f"{col}_rms"] = np.sqrt(np.mean(signal ** 2))

    # Overall acceleration magnitude
    acc_mag = np.sqrt(
        df["R_Wrist_Acc_X"]**2 +
        df["R_Wrist_Acc_Y"]**2 +
        df["R_Wrist_Acc_Z"]**2
    )

    # Overall gyroscope magnitude
    gyr_mag = np.sqrt(
        df["R_Wrist_Gyr_X"]**2 +
        df["R_Wrist_Gyr_Y"]**2 +
        df["R_Wrist_Gyr_Z"]**2
    )

    # Magnitude statistics
    for name, signal in [
        ("Acc_Magnitude", acc_mag),
        ("Gyr_Magnitude", gyr_mag)
    ]:
        signal = signal.dropna()

        features[f"{name}_mean"] = signal.mean()
        features[f"{name}_std"] = signal.std()
        features[f"{name}_min"] = signal.min()
        features[f"{name}_max"] = signal.max()
        features[f"{name}_rms"] = np.sqrt(np.mean(signal ** 2))

    return features

# %%
df = pd.read_csv(
    usable_healthy_files[0],
    usecols=balance_features
)

features = extract_balance_features(df, balance_features)

print("Number of features:", len(features))

# %%
X_data = []
y_data = []

for file in usable_healthy_files:
    df = pd.read_csv(file, usecols=balance_features)

    features = extract_balance_features(df, balance_features)

    X_data.append(features)
    y_data.append(0)


for file in usable_pd_files:
    df = pd.read_csv(file, usecols=balance_features)

    features = extract_balance_features(df, balance_features)

    X_data.append(features)
    y_data.append(1)

# %%
X = pd.DataFrame(X_data)
y = pd.Series(y_data, name="label")

print(X.shape)
print(y.shape)

# %%
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.2,
    random_state=42,
    stratify=y
)

# %%
model = RandomForestClassifier(
    n_estimators=200,
    random_state=42
)

model.fit(X_train, y_train)

y_pred = model.predict(X_test)

# %%
print("Accuracy :", accuracy_score(y_test, y_pred))
print("Precision:", precision_score(y_test, y_pred))
print("Recall   :", recall_score(y_test, y_pred))
print("F1 Score :", f1_score(y_test, y_pred))

# %%
X_with_label = X.copy()
X_with_label["label"] = y

X_with_label.groupby("label").mean().T

# %%
X_with_label.groupby("label").std().T

# %%
import matplotlib.pyplot as plt

healthy_df = pd.read_csv(
    usable_healthy_files[0],
    usecols=balance_features
)

pd_df = pd.read_csv(
    usable_pd_files[0],
    usecols=balance_features
)

healthy_gyr = np.sqrt(
    healthy_df["R_Wrist_Gyr_X"]**2 +
    healthy_df["R_Wrist_Gyr_Y"]**2 +
    healthy_df["R_Wrist_Gyr_Z"]**2
)

pd_gyr = np.sqrt(
    pd_df["R_Wrist_Gyr_X"]**2 +
    pd_df["R_Wrist_Gyr_Y"]**2 +
    pd_df["R_Wrist_Gyr_Z"]**2
)

# %%
plt.figure(figsize=(12, 4))
plt.plot(healthy_gyr)
plt.title("Healthy - Wrist Gyroscope Magnitude")
plt.xlabel("Sample")
plt.ylabel("Gyroscope Magnitude")
plt.show()

# %%
plt.figure(figsize=(12, 4))
plt.plot(pd_gyr)

plt.title("PD - Wrist Gyroscope Magnitude")
plt.xlabel("Sample")
plt.ylabel("Gyroscope Magnitude")

plt.show()

# %%
df = pd.read_csv(
    usable_healthy_files[0],
    usecols=["Time"] + balance_features
)

print(df["Time"].head(10))

# %%
print(df["Time"].tail())

# %%
def create_window(df, window_size = 500):
    windows = []
    for start in range(0, len(df) - window_size + 1, window_size):
        window = df.iloc[start: start + window_size]
        windows.append(window)
    return windows

# %%
test_df = pd.read_csv(
    usable_healthy_files[0],
    usecols= balance_features
)

windows = create_window(test_df)

print("Number of windows:", len(windows))
print("First window shape:", windows[0].shape)

# %%
def extract_window_feature(window):
    features = {}
    for col in balance_features:
        signal = window[col].dropna()

        features[f"{col}_mean"] = signal.mean()
        features[f"{col}_std"] = signal.std()
        features[f"{col}_min"] = signal.min()
        features[f"{col}_max"] = signal.max()
        features[f"{col}_rms"] = np.sqrt(np.mean(signal ** 2))
    return features

# %%
window_features = extract_window_feature(windows[0])

print("Number of features:", len(window_features))

# %%
pd.Series(window_features)

# %%
window_data = []
file = usable_healthy_files[0]
df = pd.read_csv(
    file, usecols=balance_features

)

windows = create_window(df, window_size=500)
for window_id, window in enumerate(windows):
    features = extract_window_feature(window)
    features["recording_id"] = file.name
    features["window_id"] = window_id
    features["label"] = 0
    window_data.append(features)

print("Windows created", len(window_data))

# %%
window_df = pd.DataFrame(window_data)
print(window_df.shape)
window_df.head()

# %%
all_window_data = []

for file in usable_healthy_files:

    df = pd.read_csv(
        file,
        usecols=balance_features
    )

    windows = create_window(
        df,
        window_size=500
    )

    for window_id, window in enumerate(windows):

        features = extract_window_feature(window)

        features["recording_id"] = file.name
        features["window_id"] = window_id
        features["label"] = 0

        all_window_data.append(features)


for file in usable_pd_files:

    df = pd.read_csv(
        file,
        usecols=balance_features
    )

    windows = create_window(
        df,
        window_size=500
    )

    for window_id, window in enumerate(windows):

        features = extract_window_feature(window)

        features["recording_id"] = file.name
        features["window_id"] = window_id
        features["label"] = 1

        all_window_data.append(features)


print("Total windows:", len(all_window_data))

# %%
window_df = pd.DataFrame(all_window_data)

print("Shape:", window_df.shape)
print("Number of recordings:", window_df["recording_id"].nunique())

# %%
window_df.groupby("recording_id").size().describe()

# %%
from sklearn.model_selection import train_test_split
recording_ids = window_df["recording_id"].unique()

train_ids, test_ids = train_test_split(
    recording_ids,
    test_size=0.2,
    random_state=42,
    stratify= window_df.groupby("recording_id")["label"].first()
)

print("Train recordings:", len(train_ids))
print("Test recordings", len(test_ids))

# %%
train_df = window_df[
    window_df["recording_id"].isin(train_ids)
].copy()
test_df = window_df[
    window_df["recording_id"].isin(test_ids)
].copy()

print("Train windows:", len(train_df))
print("Test windows:", len(test_df))

# %%
feature_cols = balance_features

feature_cols = [
    col + suffix
    for col in balance_features
    for suffix in ["_mean", "_std", "_min", "_max", "_rms"]
]

print("Number of feature columns:", len(feature_cols))

# %%
X_train = train_df[feature_cols]
y_train = train_df["label"]

X_test = test_df[feature_cols]
y_test = test_df["label"]

print("X_train:", X_train.shape)
print("y_train:", y_train.shape)

print("X_test:", X_test.shape)
print("y_test:", y_test.shape)

# %%
print("Train:")
print(y_train.value_counts())

print("\nTest:")
print(y_test.value_counts())

# %%
from sklearn.ensemble import RandomForestClassifier

model = RandomForestClassifier(
    n_estimators=200,
    random_state= 42,
    n_jobs=-1
)

model.fit(X_train, y_train)

# %%
y_pred = model.predict(X_test)

# %%
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix,
    classification_report
)

print("Accuracy :", accuracy_score(y_test, y_pred))
print("Precision:", precision_score(y_test, y_pred))
print("Recall   :", recall_score(y_test, y_pred))
print("F1 Score :", f1_score(y_test, y_pred))

print("\nConfusion Matrix:")
print(confusion_matrix(y_test, y_pred))

print("\nClassification Report:")
print(
    classification_report(
        y_test,
        y_pred,
        target_names=["Healthy", "PD"]
    )
)

# %%
test_results = test_df[["recording_id", "label"]].copy()

test_results["prediction"] = y_pred

test_results.head()

# %%
recording_results = (
    test_results
    .groupby("recording_id")
    .agg(
        actual_label=("label", "first"),
        pd_windows=("prediction", "sum"),
        total_windows=("prediction", "count")
    )
    .reset_index()
)

recording_results["pd_ratio"] = (
    recording_results["pd_windows"] /
    recording_results["total_windows"]
)

recording_results.head()

# %%
recording_results["final_prediction"] = (
    recording_results["pd_ratio"] >= 0.5
).astype(int)

# %%
from sklearn.metrics import (
    accuracy_score,
    confusion_matrix,
    classification_report
)

recording_accuracy = accuracy_score(
    recording_results["actual_label"],
    recording_results["final_prediction"]
)

print("Recording-level accuracy:", recording_accuracy)

print("\nConfusion Matrix:")
print(
    confusion_matrix(
        recording_results["actual_label"],
        recording_results["final_prediction"]
    )
)

print("\nClassification Report:")
print(
    classification_report(
        recording_results["actual_label"],
        recording_results["final_prediction"],
        target_names=["Healthy", "PD"]
    )
)

# %%
importance = pd.Series(
    model.feature_importances_,
    index=feature_cols
).sort_values(ascending=False)

print(importance.head(15))

# %%
plt.figure(figsize=(10, 6))

importance.head(15).sort_values().plot(kind="barh")

plt.title("Top 15 Feature Importances")
plt.xlabel("Importance")
plt.show()

# %%
def extract_window_features_v2(window):
    features = {}

    for col in balance_features:
        signal = window[col].dropna()

        # Existing features
        features[f"{col}_mean"] = signal.mean()
        features[f"{col}_std"] = signal.std()
        features[f"{col}_min"] = signal.min()
        features[f"{col}_max"] = signal.max()
        features[f"{col}_rms"] = np.sqrt(np.mean(signal ** 2))

        # Movement / dynamic features
        diff = signal.diff().dropna()

        features[f"{col}_diff_mean"] = diff.abs().mean()
        features[f"{col}_diff_std"] = diff.std()
        features[f"{col}_energy"] = np.mean(signal ** 2)

    return features

# %%
test_features = extract_window_features_v2(windows[0])

print("Number of features:", len(test_features))

# %%
pd.Series(test_features)

# %%
all_window_data_v2 = []

# Healthy
for file in usable_healthy_files:

    df = pd.read_csv(
        file,
        usecols=balance_features
    )

    windows = create_window(
        df,
        window_size=500
    )

    for window_id, window in enumerate(windows):

        features = extract_window_features_v2(window)

        features["recording_id"] = file.name
        features["window_id"] = window_id
        features["label"] = 0

        all_window_data_v2.append(features)


# PD
for file in usable_pd_files:

    df = pd.read_csv(
        file,
        usecols=balance_features
    )

    windows = create_window(
        df,
        window_size=500
    )

    for window_id, window in enumerate(windows):

        features = extract_window_features_v2(window)

        features["recording_id"] = file.name
        features["window_id"] = window_id
        features["label"] = 1

        all_window_data_v2.append(features)


window_df_v2 = pd.DataFrame(all_window_data_v2)

print("Shape:", window_df_v2.shape)
print("Recordings:", window_df_v2["recording_id"].nunique())

# %%
train_df_v2 = window_df_v2[
    window_df_v2["recording_id"].isin(train_ids)
].copy()

test_df_v2 = window_df_v2[
    window_df_v2["recording_id"].isin(test_ids)
].copy()

print("Train windows:", len(train_df_v2))
print("Test windows:", len(test_df_v2))

# %%
feature_cols_v2 = [
    col for col in window_df_v2.columns
    if col not in ["recording_id", "window_id", "label"]
]

print("Features:", len(feature_cols_v2))

# %%
X_train_v2 = train_df_v2[feature_cols_v2]
y_train_v2 = train_df_v2["label"]

X_test_v2 = test_df_v2[feature_cols_v2]
y_test_v2 = test_df_v2["label"]

print(X_train_v2.shape)
print(X_test_v2.shape)

# %%
model_v2 = RandomForestClassifier(
    n_estimators=200,
    random_state=42,
    n_jobs=-1
)

model_v2.fit(X_train_v2, y_train_v2)

y_pred_v2 = model_v2.predict(X_test_v2)

# %%
print("Accuracy :", accuracy_score(y_test_v2, y_pred_v2))
print("Precision:", precision_score(y_test_v2, y_pred_v2))
print("Recall   :", recall_score(y_test_v2, y_pred_v2))
print("F1 Score :", f1_score(y_test_v2, y_pred_v2))

print("\nConfusion Matrix:")
print(confusion_matrix(y_test_v2, y_pred_v2))

# %%
test_results_v2 = test_df_v2[
    ["recording_id", "label"]
].copy()

test_results_v2["prediction"] = y_pred_v2

recording_results_v2 = (
    test_results_v2
    .groupby("recording_id")
    .agg(
        actual_label=("label", "first"),
        pd_windows=("prediction", "sum"),
        total_windows=("prediction", "count")
    )
    .reset_index()
)

recording_results_v2["pd_ratio"] = (
    recording_results_v2["pd_windows"] /
    recording_results_v2["total_windows"]
)

recording_results_v2["final_prediction"] = (
    recording_results_v2["pd_ratio"] >= 0.5
).astype(int)

# %%
recording_accuracy_v2 = accuracy_score(
    recording_results_v2["actual_label"],
    recording_results_v2["final_prediction"]
)

print("V2 Recording-level accuracy:", recording_accuracy_v2)

print("\nConfusion Matrix:")
print(
    confusion_matrix(
        recording_results_v2["actual_label"],
        recording_results_v2["final_prediction"]
    )
)

print("\nClassification Report:")
print(
    classification_report(
        recording_results_v2["actual_label"],
        recording_results_v2["final_prediction"],
        target_names=["Healthy", "PD"]
    )
)

# %%
time_values = (
    df["Time"]
    .str.replace(" sec", "", regex=False)
    .astype(float)
)

dt = time_values.diff().median()

print("Sampling interval:", dt)
print("Sampling rate:", 1 / dt)

# %%
sample_df = pd.read_csv(usable_healthy_files[0])

print(sample_df["Time"].head())

# %%
time_values = (
    sample_df["Time"]
    .str.replace(" sec", "", regex=False)
    .astype(float)
)

dt = time_values.diff().median()

print("Sampling interval:", dt)
print("Sampling rate:", 1 / dt)

# %%
from scipy.fft import rfft, rfftfreq

sample_signal = windows[0]["R_Wrist_Acc_X"].values

n = len(sample_signal)

fft_values = np.abs(rfft(sample_signal))
frequencies = rfftfreq(n, d=1/100)

print("Samples:", n)
print("Frequency bins:", len(frequencies))
print("Frequency range:", frequencies[0], "to", frequencies[-1], "Hz")

# %%
power = fft_values ** 2

dominant_idx = np.argmax(power[1:]) + 1

print("Dominant frequency:",
      frequencies[dominant_idx], "Hz")

print("Dominant power:",
      power[dominant_idx])

# %%
# Ignore frequencies below 1 Hz
valid = frequencies >= 1.0

freq_valid = frequencies[valid]
power_valid = power[valid]

dominant_idx = np.argmax(power_valid)

print("Dominant frequency above 1 Hz:",
      freq_valid[dominant_idx], "Hz")

print("Dominant power:",
      power_valid[dominant_idx])

# %%
top_indices = np.argsort(power_valid)[-10:][::-1]

for i in top_indices:
    print(
        f"{freq_valid[i]:.2f} Hz -> "
        f"{power_valid[i]:.2f}"
    )

# %%
from scipy.fft import rfft, rfftfreq

def extract_frequency_features(window, sampling_rate=100):
    features = {}

    for col in balance_features:

        signal = window[col].values

        n = len(signal)

        # Remove mean/DC component
        signal = signal - np.mean(signal)

        # FFT
        fft_values = np.abs(rfft(signal))
        power = fft_values ** 2

        frequencies = rfftfreq(
            n,
            d=1 / sampling_rate
        )

        # Ignore frequencies below 1 Hz
        valid = frequencies >= 1.0

        freq_valid = frequencies[valid]
        power_valid = power[valid]

        # Dominant frequency
        dominant_idx = np.argmax(power_valid)

        dominant_frequency = freq_valid[dominant_idx]
        dominant_power = power_valid[dominant_idx]

        # Spectral entropy
        power_sum = np.sum(power_valid)

        if power_sum > 0:
            probability = power_valid / power_sum
            spectral_entropy = -np.sum(
                probability * np.log2(probability + 1e-12)
            )
        else:
            spectral_entropy = 0

        features[f"{col}_dominant_freq"] = dominant_frequency
        features[f"{col}_dominant_power"] = dominant_power
        features[f"{col}_spectral_entropy"] = spectral_entropy

    return features

# %%
freq_features = extract_frequency_features(windows[0])

print("Number of frequency features:", len(freq_features))

pd.Series(freq_features)

# %%
def extract_window_features_v3(window):
    features = {}

    # Original 30 statistical features
    basic_features = extract_window_feature(window)
    features.update(basic_features)

    # 18 frequency features
    frequency_features = extract_frequency_features(window)
    features.update(frequency_features)

    return features

# %%
test_v3 = extract_window_features_v3(windows[0])

print("Total features:", len(test_v3))

# %%
all_window_data_v3 = []

# Healthy
for file in usable_healthy_files:

    df = pd.read_csv(
        file,
        usecols=balance_features
    )

    windows = create_window(df, 500)

    for window_id, window in enumerate(windows):

        features = extract_window_features_v3(window)

        features["recording_id"] = file.name
        features["window_id"] = window_id
        features["label"] = 0

        all_window_data_v3.append(features)


# PD
for file in usable_pd_files:

    df = pd.read_csv(
        file,
        usecols=balance_features
    )

    windows = create_window(df, 500)

    for window_id, window in enumerate(windows):

        features = extract_window_features_v3(window)

        features["recording_id"] = file.name
        features["window_id"] = window_id
        features["label"] = 1

        all_window_data_v3.append(features)


window_df_v3 = pd.DataFrame(all_window_data_v3)

print("Shape:", window_df_v3.shape)
print("Recordings:", window_df_v3["recording_id"].nunique())

# %%
train_df_v3 = window_df_v3[
    window_df_v3["recording_id"].isin(train_ids)
].copy()

test_df_v3 = window_df_v3[
    window_df_v3["recording_id"].isin(test_ids)
].copy()

feature_cols_v3 = [
    col for col in window_df_v3.columns
    if col not in ["recording_id", "window_id", "label"]
]

X_train_v3 = train_df_v3[feature_cols_v3]
y_train_v3 = train_df_v3["label"]

X_test_v3 = test_df_v3[feature_cols_v3]
y_test_v3 = test_df_v3["label"]

print("Features:", len(feature_cols_v3))
print("Train:", X_train_v3.shape)
print("Test:", X_test_v3.shape)

# %%
model_v3 = RandomForestClassifier(
    n_estimators=200,
    random_state=42,
    n_jobs=-1
)

model_v3.fit(X_train_v3, y_train_v3)

y_pred_v3 = model_v3.predict(X_test_v3)

# %%
print("Accuracy :", accuracy_score(y_test_v3, y_pred_v3))

# %%
test_results_v3 = test_df_v3[
    ["recording_id", "label"]
].copy()

test_results_v3["prediction"] = y_pred_v3

recording_results_v3 = (
    test_results_v3
    .groupby("recording_id")
    .agg(
        actual_label=("label", "first"),
        pd_windows=("prediction", "sum"),
        total_windows=("prediction", "count")
    )
    .reset_index()
)

recording_results_v3["pd_ratio"] = (
    recording_results_v3["pd_windows"] /
    recording_results_v3["total_windows"]
)

print(recording_results_v3.head())

# %%
recording_results_v3["final_prediction"] = (
    recording_results_v3["pd_ratio"] >= 0.5
).astype(int)

# %%
recording_accuracy_v3 = accuracy_score(
    recording_results_v3["actual_label"],
    recording_results_v3["final_prediction"]
)

print("V3 Recording-level accuracy:", recording_accuracy_v3)

print("\nConfusion Matrix:")
print(
    confusion_matrix(
        recording_results_v3["actual_label"],
        recording_results_v3["final_prediction"]
    )
)

print("\nClassification Report:")
print(
    classification_report(
        recording_results_v3["actual_label"],
        recording_results_v3["final_prediction"],
        target_names=["Healthy", "PD"]
    )
)

# %%
importance_v3 = pd.Series(
    model_v3.feature_importances_,
    index=feature_cols_v3
).sort_values(ascending=False)

print(importance_v3.head(20))

# %%
plt.figure(figsize=(10, 7))

importance_v3.head(20).sort_values().plot(
    kind="barh"
)

plt.title("V3 Top 20 Feature Importances")
plt.xlabel("Importance")

plt.show()

# %%
from sklearn.model_selection import StratifiedGroupKFold
from sklearn.metrics import accuracy_score
import numpy as np

X_cv = train_df_v3[feature_cols_v3]
y_cv = train_df_v3["label"]
groups = train_df_v3["recording_id"]

cv = StratifiedGroupKFold(
    n_splits=5,
    shuffle=True,
    random_state=42
)

fold_scores = []

for fold, (train_idx, val_idx) in enumerate(
    cv.split(X_cv, y_cv, groups=groups),
    start=1
):

    X_fold_train = X_cv.iloc[train_idx]
    y_fold_train = y_cv.iloc[train_idx]

    X_fold_val = X_cv.iloc[val_idx]
    y_fold_val = y_cv.iloc[val_idx]

    fold_train_df = train_df_v3.iloc[train_idx].copy()
    fold_val_df = train_df_v3.iloc[val_idx].copy()

    model_fold = RandomForestClassifier(
        n_estimators=200,
        random_state=42,
        n_jobs=-1
    )

    model_fold.fit(
        X_fold_train,
        y_fold_train
    )

    val_pred = model_fold.predict(X_fold_val)

    # Put predictions back with recording IDs
    fold_results = fold_val_df[
        ["recording_id", "label"]
    ].copy()

    fold_results["prediction"] = val_pred

    # Aggregate windows → recording
    recording_fold = (
        fold_results
        .groupby("recording_id")
        .agg(
            actual_label=("label", "first"),
            pd_windows=("prediction", "sum"),
            total_windows=("prediction", "count")
        )
        .reset_index()
    )

    recording_fold["pd_ratio"] = (
        recording_fold["pd_windows"] /
        recording_fold["total_windows"]
    )

    recording_fold["final_prediction"] = (
        recording_fold["pd_ratio"] >= 0.5
    ).astype(int)

    fold_accuracy = accuracy_score(
        recording_fold["actual_label"],
        recording_fold["final_prediction"]
    )

    fold_scores.append(fold_accuracy)

    print(
        f"Fold {fold}: "
        f"{fold_accuracy:.4f} "
        f"({fold_accuracy * 100:.2f}%)"
    )

# %%
print("\nCV Mean Accuracy:",
      np.mean(fold_scores))

print("CV Std:",
      np.std(fold_scores))

# %%
basic_feature_cols = [
    col for col in feature_cols_v3
    if not (
        col.endswith("_dominant_freq") or
        col.endswith("_dominant_power") or
        col.endswith("_spectral_entropy")
    )
]

print("V1 features:", len(basic_feature_cols))

# %%
X_cv_v1 = train_df_v3[basic_feature_cols]
y_cv_v1 = train_df_v3["label"]
groups_v1 = train_df_v3["recording_id"]

# %%
from sklearn.model_selection import StratifiedGroupKFold
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
import numpy as np

cv_v1 = StratifiedGroupKFold(
    n_splits=5,
    shuffle=True,
    random_state=42
)

fold_scores_v1 = []

for fold, (train_idx, val_idx) in enumerate(
    cv_v1.split(X_cv_v1, y_cv_v1, groups=groups_v1),
    start=1
):

    X_fold_train = X_cv_v1.iloc[train_idx]
    y_fold_train = y_cv_v1.iloc[train_idx]

    X_fold_val = X_cv_v1.iloc[val_idx]
    y_fold_val = y_cv_v1.iloc[val_idx]

    fold_train_df = train_df_v3.iloc[train_idx].copy()
    fold_val_df = train_df_v3.iloc[val_idx].copy()

    model_v1_cv = RandomForestClassifier(
        n_estimators=200,
        random_state=42,
        n_jobs=-1
    )

    model_v1_cv.fit(
        X_fold_train,
        y_fold_train
    )

    val_pred = model_v1_cv.predict(X_fold_val)

    # Window predictions
    fold_results = fold_val_df[
        ["recording_id", "label"]
    ].copy()

    fold_results["prediction"] = val_pred

    # Window → recording
    recording_fold = (
        fold_results
        .groupby("recording_id")
        .agg(
            actual_label=("label", "first"),
            pd_windows=("prediction", "sum"),
            total_windows=("prediction", "count")
        )
        .reset_index()
    )

    recording_fold["pd_ratio"] = (
        recording_fold["pd_windows"] /
        recording_fold["total_windows"]
    )

    recording_fold["final_prediction"] = (
        recording_fold["pd_ratio"] >= 0.5
    ).astype(int)

    fold_accuracy = accuracy_score(
        recording_fold["actual_label"],
        recording_fold["final_prediction"]
    )

    fold_scores_v1.append(fold_accuracy)

    print(
        f"V1 Fold {fold}: "
        f"{fold_accuracy:.4f} "
        f"({fold_accuracy * 100:.2f}%)"
    )

# %%
print(
    "\nV1 CV Mean Accuracy:",
    np.mean(fold_scores_v1)
)

print(
    "V1 CV Std:",
    np.std(fold_scores_v1)
)

# %%
from sklearn.linear_model import LogisticRegression

# %%
cv_lr = StratifiedGroupKFold(
    n_splits=5,
    shuffle=True,
    random_state=42
)

fold_scores_lr = []

for fold, (train_idx, val_idx) in enumerate(
    cv_lr.split(X_cv_v1, y_cv_v1, groups=groups_v1),
    start=1
):

    X_fold_train = X_cv_v1.iloc[train_idx]
    y_fold_train = y_cv_v1.iloc[train_idx]

    X_fold_val = X_cv_v1.iloc[val_idx]
    y_fold_val = y_cv_v1.iloc[val_idx]

    fold_val_df = train_df_v3.iloc[val_idx].copy()

    model_lr = LogisticRegression(
        max_iter=2000,
        random_state=42
    )

    model_lr.fit(
        X_fold_train,
        y_fold_train
    )

    val_pred = model_lr.predict(X_fold_val)

    # Window predictions → recording predictions
    fold_results = fold_val_df[
        ["recording_id", "label"]
    ].copy()

    fold_results["prediction"] = val_pred

    recording_fold = (
        fold_results
        .groupby("recording_id")
        .agg(
            actual_label=("label", "first"),
            pd_windows=("prediction", "sum"),
            total_windows=("prediction", "count")
        )
        .reset_index()
    )

    recording_fold["pd_ratio"] = (
        recording_fold["pd_windows"] /
        recording_fold["total_windows"]
    )

    recording_fold["final_prediction"] = (
        recording_fold["pd_ratio"] >= 0.5
    ).astype(int)

    fold_accuracy = accuracy_score(
        recording_fold["actual_label"],
        recording_fold["final_prediction"]
    )

    fold_scores_lr.append(fold_accuracy)

    print(
        f"LR Fold {fold}: "
        f"{fold_accuracy:.4f} "
        f"({fold_accuracy * 100:.2f}%)"
    )

# %%
print("NaN values:", X_cv_v1.isna().sum().sum())
print("\nFeatures with NaN:")
print(X_cv_v1.columns[X_cv_v1.isna().any()].tolist())

# %%
print("Inf values:", np.isinf(X_cv_v1).sum().sum())

# %%
nan_rows = train_df_v3[
    train_df_v3[feature_cols_v3].isna().any(axis=1)
]

print("Bad windows:", len(nan_rows))

print(
    nan_rows[
        ["recording_id", "window_id", "label"]
    ].head(20)
)

# %%
print(
    nan_rows["recording_id"].value_counts()
)

# %%
bad_file = next(
    f for f in usable_healthy_files + usable_pd_files
    if f.name == "HC111_Balance.csv"
)

bad_df = pd.read_csv(
    bad_file,
    usecols=balance_features
)

print("Shape:", bad_df.shape)
print("\nNaN count:")
print(bad_df.isna().sum())

print("\nInf count:")
print(np.isinf(bad_df).sum())

# %%
print(
    bad_df.iloc[12*500:13*500].isna().sum()
)

# %%
for window_id in [11, 12, 13, 22, 23, 24, 25]:
    
    start = window_id * 500
    end = start + 500
    
    window = bad_df.iloc[start:end]

    print(
        f"Window {window_id}:",
        "rows =", len(window),
        "valid =", window.notna().sum().min(),
        "NaN =", window.isna().sum().max()
    )

# %%
def create_windows(df, window_size=500, min_valid_ratio=0.90):

    windows = []

    for start in range(0, len(df) - window_size + 1, window_size):

        window = df.iloc[start:start + window_size].copy()

        valid_ratio = (
            window[balance_features]
            .notna()
            .all(axis=1)
            .mean()
        )

        if valid_ratio >= min_valid_ratio:
            windows.append(window)

    return windows

# %%
hc111_windows = create_windows(
    bad_df,
    window_size=500,
    min_valid_ratio=0.90
)

print("Usable windows:", len(hc111_windows))

# %%


# %%
all_window_data_clean = []

for file in usable_healthy_files:

    df = pd.read_csv(
        file,
        usecols=balance_features
    )

    windows = create_windows(
        df,
        window_size=500,
        min_valid_ratio=0.90
    )

    for window_id, window in enumerate(windows):

        features = extract_window_features_v3(window)

        features["recording_id"] = file.name
        features["window_id"] = window_id
        features["label"] = 0

        all_window_data_clean.append(features)


for file in usable_pd_files:

    df = pd.read_csv(
        file,
        usecols=balance_features
    )

    windows = create_windows(
        df,
        window_size=500,
        min_valid_ratio=0.90
    )

    for window_id, window in enumerate(windows):

        features = extract_window_features_v3(window)

        features["recording_id"] = file.name
        features["window_id"] = window_id
        features["label"] = 1

        all_window_data_clean.append(features)


clean_window_df = pd.DataFrame(all_window_data_clean)

print("Shape:", clean_window_df.shape)
print("Recordings:", clean_window_df["recording_id"].nunique())
print("NaN:", clean_window_df.isna().sum().sum())
print("Inf:", np.isinf(
    clean_window_df.select_dtypes(include=np.number)
).sum().sum())

# %%
print("Clean windows:", len(clean_window_df))

# %%
nan_counts = clean_window_df.isna().sum()

print(
    nan_counts[nan_counts > 0]
)

# %%
bad_clean_windows = clean_window_df[
    clean_window_df.isna().any(axis=1)
]

print("Bad windows:", len(bad_clean_windows))

print(
    bad_clean_windows[
        ["recording_id", "window_id", "label"]
    ]
)

# %%
bad_features = clean_window_df.loc[
    bad_clean_windows.index
].isna().sum()

print(bad_features[bad_features > 0])

# %%
print(
    clean_window_df.loc[
        bad_clean_windows.index,
        ["recording_id", "window_id"] +
        [col for col in feature_cols_v3
         if clean_window_df.loc[bad_clean_windows.index, col].isna().any()]
    ]
)

# %%
clean_window_df = clean_window_df.drop(
    index=bad_clean_windows.index
).reset_index(drop=True)

print("Final windows:", len(clean_window_df))
print("NaN:", clean_window_df.isna().sum().sum())
print(
    "Inf:",
    np.isinf(
        clean_window_df.select_dtypes(include=np.number)
    ).sum().sum()
)

# %%
train_clean = clean_window_df[
    clean_window_df["recording_id"].isin(train_ids)
].copy()

test_clean = clean_window_df[
    clean_window_df["recording_id"].isin(test_ids)
].copy()

print("Train windows:", len(train_clean))
print("Test windows:", len(test_clean))

print("Train recordings:", train_clean["recording_id"].nunique())
print("Test recordings:", test_clean["recording_id"].nunique())

# %%
X_train_clean_v1 = train_clean[basic_feature_cols]
y_train_clean = train_clean["label"]

X_test_clean_v1 = test_clean[basic_feature_cols]
y_test_clean = test_clean["label"]

print("V1 features:", len(basic_feature_cols))
print("Train:", X_train_clean_v1.shape)
print("Test:", X_test_clean_v1.shape)

# %%
print("Train NaN:", X_train_clean_v1.isna().sum().sum())
print("Test NaN :", X_test_clean_v1.isna().sum().sum())

print("Train Inf:", np.isinf(X_train_clean_v1).sum().sum())
print("Test Inf :", np.isinf(X_test_clean_v1).sum().sum())

# %%


# %%
X_cv_v1_clean = train_clean[basic_feature_cols]
y_cv_v1_clean = train_clean["label"]
groups_v1_clean = train_clean["recording_id"]

# %%
from sklearn.model_selection import StratifiedGroupKFold
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score
import numpy as np

cv_lr = StratifiedGroupKFold(
    n_splits=5,
    shuffle=True,
    random_state=42
)

fold_scores_lr = []

for fold, (train_idx, val_idx) in enumerate(
    cv_lr.split(
        X_cv_v1_clean,
        y_cv_v1_clean,
        groups=groups_v1_clean
    ),
    start=1
):

    X_fold_train = X_cv_v1_clean.iloc[train_idx]
    y_fold_train = y_cv_v1_clean.iloc[train_idx]

    X_fold_val = X_cv_v1_clean.iloc[val_idx]

    fold_val_df = train_clean.iloc[val_idx].copy()

    model_lr = LogisticRegression(
        max_iter=2000,
        random_state=42
    )

    model_lr.fit(
        X_fold_train,
        y_fold_train
    )

    val_pred = model_lr.predict(X_fold_val)

    fold_results = fold_val_df[
        ["recording_id", "label"]
    ].copy()

    fold_results["prediction"] = val_pred

    recording_fold = (
        fold_results
        .groupby("recording_id")
        .agg(
            actual_label=("label", "first"),
            pd_windows=("prediction", "sum"),
            total_windows=("prediction", "count")
        )
        .reset_index()
    )

    recording_fold["pd_ratio"] = (
        recording_fold["pd_windows"] /
        recording_fold["total_windows"]
    )

    recording_fold["final_prediction"] = (
        recording_fold["pd_ratio"] >= 0.5
    ).astype(int)

    fold_accuracy = accuracy_score(
        recording_fold["actual_label"],
        recording_fold["final_prediction"]
    )

    fold_scores_lr.append(fold_accuracy)

    print(
        f"LR Fold {fold}: "
        f"{fold_accuracy:.4f} "
        f"({fold_accuracy * 100:.2f}%)"
    )

# %%
print(
    "\nLogistic Regression CV Mean:",
    np.mean(fold_scores_lr)
)

print(
    "Logistic Regression CV Std:",
    np.std(fold_scores_lr)
)

# %%
X_train_v4 = train_clean[feature_cols_v3]
y_train_v4 = train_clean["label"]

X_test_v4 = test_clean[feature_cols_v3]
y_test_v4 = test_clean["label"]

print("Train:", X_train_v4.shape)
print("Test :", X_test_v4.shape)
print("NaN:", X_train_v4.isna().sum().sum())
print("Inf:", np.isinf(X_train_v4).sum().sum())

# %%
model_v4 = RandomForestClassifier(
    n_estimators=200,
    random_state=42,
    n_jobs=-1
)

model_v4.fit(
    X_train_v4,
    y_train_v4
)

y_pred_v4 = model_v4.predict(X_test_v4)

# %%
print("Accuracy :", accuracy_score(y_test_v4, y_pred_v4))
print("Precision:", precision_score(y_test_v4, y_pred_v4))
print("Recall   :", recall_score(y_test_v4, y_pred_v4))
print("F1 Score :", f1_score(y_test_v4, y_pred_v4))

print("\nConfusion Matrix:")
print(confusion_matrix(y_test_v4, y_pred_v4))

# %%
test_results_v4 = test_clean[
    ["recording_id", "label"]
].copy()

test_results_v4["prediction"] = y_pred_v4

recording_results_v4 = (
    test_results_v4
    .groupby("recording_id")
    .agg(
        actual_label=("label", "first"),
        pd_windows=("prediction", "sum"),
        total_windows=("prediction", "count")
    )
    .reset_index()
)

recording_results_v4["pd_ratio"] = (
    recording_results_v4["pd_windows"] /
    recording_results_v4["total_windows"]
)

recording_results_v4["final_prediction"] = (
    recording_results_v4["pd_ratio"] >= 0.5
).astype(int)

# %%
recording_accuracy_v4 = accuracy_score(
    recording_results_v4["actual_label"],
    recording_results_v4["final_prediction"]
)

print(
    "V4 Recording-level accuracy:",
    recording_accuracy_v4
)

print("\nConfusion Matrix:")
print(
    confusion_matrix(
        recording_results_v4["actual_label"],
        recording_results_v4["final_prediction"]
    )
)

print("\nClassification Report:")
print(
    classification_report(
        recording_results_v4["actual_label"],
        recording_results_v4["final_prediction"],
        target_names=["Healthy", "PD"]
    )
)

# %%
X_cv_clean = train_clean[basic_feature_cols]
y_cv_clean = train_clean["label"]
groups_clean = train_clean["recording_id"]

# %%
X_cv_clean = train_clean[basic_feature_cols]
y_cv_clean = train_clean["label"]
groups_clean = train_clean["recording_id"]

print("Features:", X_cv_clean.shape[1])
print("NaN:", X_cv_clean.isna().sum().sum())
print("Inf:", np.isinf(X_cv_clean).sum().sum())

# %%
cv_clean_rf = StratifiedGroupKFold(
    n_splits=5,
    shuffle=True,
    random_state=42
)

fold_scores_clean_rf = []

for fold, (train_idx, val_idx) in enumerate(
    cv_clean_rf.split(
        X_cv_clean,
        y_cv_clean,
        groups=groups_clean
    ),
    start=1
):

    X_fold_train = X_cv_clean.iloc[train_idx]
    y_fold_train = y_cv_clean.iloc[train_idx]

    X_fold_val = X_cv_clean.iloc[val_idx]

    fold_val_df = train_clean.iloc[val_idx].copy()

    model_clean_rf = RandomForestClassifier(
        n_estimators=200,
        random_state=42,
        n_jobs=-1
    )

    model_clean_rf.fit(
        X_fold_train,
        y_fold_train
    )

    val_pred = model_clean_rf.predict(X_fold_val)

    # Window → recording
    fold_results = fold_val_df[
        ["recording_id", "label"]
    ].copy()

    fold_results["prediction"] = val_pred

    recording_fold = (
        fold_results
        .groupby("recording_id")
        .agg(
            actual_label=("label", "first"),
            pd_windows=("prediction", "sum"),
            total_windows=("prediction", "count")
        )
        .reset_index()
    )

    recording_fold["pd_ratio"] = (
        recording_fold["pd_windows"] /
        recording_fold["total_windows"]
    )

    recording_fold["final_prediction"] = (
        recording_fold["pd_ratio"] >= 0.5
    ).astype(int)

    fold_accuracy = accuracy_score(
        recording_fold["actual_label"],
        recording_fold["final_prediction"]
    )

    fold_scores_clean_rf.append(fold_accuracy)

    print(
        f"Clean V1 Fold {fold}: "
        f"{fold_accuracy:.4f} "
        f"({fold_accuracy * 100:.2f}%)"
    )

# %%
print(
    "\nClean V1 RF Mean:",
    np.mean(fold_scores_clean_rf)
)

print(
    "Clean V1 RF Std:",
    np.std(fold_scores_clean_rf)
)

# %%
X_cv_v4 = train_clean[feature_cols_v3]
y_cv_v4 = train_clean["label"]
groups_v4 = train_clean["recording_id"]

print("Features:", X_cv_v4.shape[1])
print("NaN:", X_cv_v4.isna().sum().sum())
print("Inf:", np.isinf(X_cv_v4).sum().sum())

# %%
cv_v4 = StratifiedGroupKFold(
    n_splits=5,
    shuffle=True,
    random_state=42
)

fold_scores_v4 = []

for fold, (train_idx, val_idx) in enumerate(
    cv_v4.split(
        X_cv_v4,
        y_cv_v4,
        groups=groups_v4
    ),
    start=1
):

    X_fold_train = X_cv_v4.iloc[train_idx]
    y_fold_train = y_cv_v4.iloc[train_idx]

    X_fold_val = X_cv_v4.iloc[val_idx]

    fold_val_df = train_clean.iloc[val_idx].copy()

    model_v4_cv = RandomForestClassifier(
        n_estimators=200,
        random_state=42,
        n_jobs=-1
    )

    model_v4_cv.fit(
        X_fold_train,
        y_fold_train
    )

    val_pred = model_v4_cv.predict(X_fold_val)

    fold_results = fold_val_df[
        ["recording_id", "label"]
    ].copy()

    fold_results["prediction"] = val_pred

    recording_fold = (
        fold_results
        .groupby("recording_id")
        .agg(
            actual_label=("label", "first"),
            pd_windows=("prediction", "sum"),
            total_windows=("prediction", "count")
        )
        .reset_index()
    )

    recording_fold["pd_ratio"] = (
        recording_fold["pd_windows"] /
        recording_fold["total_windows"]
    )

    recording_fold["final_prediction"] = (
        recording_fold["pd_ratio"] >= 0.5
    ).astype(int)

    fold_accuracy = accuracy_score(
        recording_fold["actual_label"],
        recording_fold["final_prediction"]
    )

    fold_scores_v4.append(fold_accuracy)

    print(
        f"Clean V4 Fold {fold}: "
        f"{fold_accuracy:.4f} "
        f"({fold_accuracy * 100:.2f}%)"
    )

# %%
print(
    "\nClean V4 RF Mean:",
    np.mean(fold_scores_v4)
)

print(
    "Clean V4 RF Std:",
    np.std(fold_scores_v4)
)

# %%
thresholds = [0.30, 0.40, 0.50, 0.60, 0.70]

cv_threshold = StratifiedGroupKFold(
    n_splits=5,
    shuffle=True,
    random_state=42
)

threshold_scores = {
    threshold: []
    for threshold in thresholds
}

for fold, (train_idx, val_idx) in enumerate(
    cv_threshold.split(
        X_cv_clean,
        y_cv_clean,
        groups=groups_clean
    ),
    start=1
):

    X_fold_train = X_cv_clean.iloc[train_idx]
    y_fold_train = y_cv_clean.iloc[train_idx]

    X_fold_val = X_cv_clean.iloc[val_idx]

    fold_val_df = train_clean.iloc[val_idx].copy()

    model = RandomForestClassifier(
        n_estimators=200,
        random_state=42,
        n_jobs=-1
    )

    model.fit(
        X_fold_train,
        y_fold_train
    )

    val_pred = model.predict(X_fold_val)

    fold_results = fold_val_df[
        ["recording_id", "label"]
    ].copy()

    fold_results["prediction"] = val_pred

    recording_fold = (
        fold_results
        .groupby("recording_id")
        .agg(
            actual_label=("label", "first"),
            pd_windows=("prediction", "sum"),
            total_windows=("prediction", "count")
        )
        .reset_index()
    )

    recording_fold["pd_ratio"] = (
        recording_fold["pd_windows"] /
        recording_fold["total_windows"]
    )

    for threshold in thresholds:

        recording_fold["final_prediction"] = (
            recording_fold["pd_ratio"] >= threshold
        ).astype(int)

        accuracy = accuracy_score(
            recording_fold["actual_label"],
            recording_fold["final_prediction"]
        )

        threshold_scores[threshold].append(accuracy)

    print(f"Fold {fold} completed")

# %%
threshold_summary = []

for threshold in thresholds:

    scores = threshold_scores[threshold]

    threshold_summary.append({
        "threshold": threshold,
        "mean_accuracy": np.mean(scores),
        "std": np.std(scores)
    })

threshold_results = pd.DataFrame(
    threshold_summary
)

print(threshold_results)

# %%
final_model = RandomForestClassifier(
    n_estimators=200,
    random_state=42,
    n_jobs=-1
)

final_model.fit(
    X_train_clean_v1,
    y_train_clean
)

final_test_pred = final_model.predict(
    X_test_clean_v1
)

# %%
final_test_results = test_clean[
    ["recording_id", "label"]
].copy()

final_test_results["prediction"] = final_test_pred

final_recording_results = (
    final_test_results
    .groupby("recording_id")
    .agg(
        actual_label=("label", "first"),
        pd_windows=("prediction", "sum"),
        total_windows=("prediction", "count")
    )
    .reset_index()
)

final_recording_results["pd_ratio"] = (
    final_recording_results["pd_windows"] /
    final_recording_results["total_windows"]
)

# IMPORTANT: selected from CV, NOT from test set
FINAL_THRESHOLD = 0.40

final_recording_results["final_prediction"] = (
    final_recording_results["pd_ratio"] >= FINAL_THRESHOLD
).astype(int)

# %%
final_accuracy = accuracy_score(
    final_recording_results["actual_label"],
    final_recording_results["final_prediction"]
)

print(
    "FINAL Recording-level accuracy:",
    final_accuracy
)

print("\nConfusion Matrix:")
print(
    confusion_matrix(
        final_recording_results["actual_label"],
        final_recording_results["final_prediction"]
    )
)

print("\nClassification Report:")
print(
    classification_report(
        final_recording_results["actual_label"],
        final_recording_results["final_prediction"],
        target_names=["Healthy", "PD"]
    )
)

# %%
final_recording_results[
    [
        "recording_id",
        "actual_label",
        "pd_windows",
        "total_windows",
        "pd_ratio",
        "final_prediction"
    ]
].sort_values("pd_ratio")

# %%
print(
    final_recording_results
    .groupby("actual_label")["total_windows"]
    .describe()
)

# %%
final_recording_results["correct"] = (
    final_recording_results["actual_label"]
    ==
    final_recording_results["final_prediction"]
)

print(
    final_recording_results
    .groupby("correct")["total_windows"]
    .describe()
)

# %%
print(
    final_recording_results[
        final_recording_results["total_windows"] <= 10
    ][
        [
            "recording_id",
            "actual_label",
            "pd_windows",
            "total_windows",
            "pd_ratio",
            "final_prediction"
        ]
    ]
)

# %%
feature_comparison = (
    clean_window_df
    .groupby("label")[basic_feature_cols]
    .mean()
    .T
)

feature_comparison.columns = [
    "Healthy",
    "PD"
]

feature_comparison["difference"] = (
    feature_comparison["PD"]
    -
    feature_comparison["Healthy"]
)

feature_comparison["abs_difference"] = (
    feature_comparison["difference"].abs()
)

feature_comparison = feature_comparison.sort_values(
    "abs_difference",
    ascending=False
)

feature_comparison.head(15)

# %%
from sklearn.preprocessing import StandardScaler

effect_sizes = []

for feature in basic_feature_cols:

    healthy = clean_window_df.loc[
        clean_window_df["label"] == 0,
        feature
    ]

    pd_group = clean_window_df.loc[
        clean_window_df["label"] == 1,
        feature
    ]

    pooled_std = np.sqrt(
        (
            healthy.var() +
            pd_group.var()
        ) / 2
    )

    effect = (
        pd_group.mean() -
        healthy.mean()
    ) / pooled_std

    effect_sizes.append({
        "feature": feature,
        "effect_size": effect,
        "abs_effect": abs(effect)
    })

effect_df = pd.DataFrame(effect_sizes)

effect_df = effect_df.sort_values(
    "abs_effect",
    ascending=False
)

effect_df.head(15)

# %%
def extract_dynamic_features(window):

    features = {}

    # ------------------------------------------------
    # Individual IMU channels
    # ------------------------------------------------

    for col in balance_features:

        signal = window[col].dropna().values

        if len(signal) < 2:
            continue

        diff = np.diff(signal)

        # Mean absolute change
        features[f"{col}_mean_abs_change"] = np.mean(
            np.abs(diff)
        )

        # Maximum absolute change
        features[f"{col}_max_abs_change"] = np.max(
            np.abs(diff)
        )

        # Median absolute deviation
        median = np.median(signal)

        features[f"{col}_mad"] = np.median(
            np.abs(signal - median)
        )

        # Zero crossing around the signal mean
        centered = signal - np.mean(signal)

        zero_crossings = np.sum(
            centered[:-1] * centered[1:] < 0
        )

        features[f"{col}_zero_crossing_rate"] = (
            zero_crossings / (len(signal) - 1)
        )

    # ------------------------------------------------
    # Acceleration magnitude
    # ------------------------------------------------

    acc_x = window["R_Wrist_Acc_X"].dropna().values
    acc_y = window["R_Wrist_Acc_Y"].dropna().values
    acc_z = window["R_Wrist_Acc_Z"].dropna().values

    min_len = min(
        len(acc_x),
        len(acc_y),
        len(acc_z)
    )

    if min_len > 1:

        acc_x = acc_x[:min_len]
        acc_y = acc_y[:min_len]
        acc_z = acc_z[:min_len]

        acc_mag = np.sqrt(
            acc_x**2 +
            acc_y**2 +
            acc_z**2
        )

        acc_diff = np.diff(acc_mag)

        features["Acc_Magnitude_mean"] = np.mean(acc_mag)
        features["Acc_Magnitude_std"] = np.std(acc_mag)
        features["Acc_Magnitude_rms"] = np.sqrt(
            np.mean(acc_mag**2)
        )

        features["Acc_Magnitude_mean_abs_change"] = np.mean(
            np.abs(acc_diff)
        )

        features["Acc_Magnitude_max_abs_change"] = np.max(
            np.abs(acc_diff)
        )

        features["Acc_Magnitude_mad"] = np.median(
            np.abs(
                acc_mag - np.median(acc_mag)
            )
        )

    # ------------------------------------------------
    # Gyroscope magnitude
    # ------------------------------------------------

    gyr_x = window["R_Wrist_Gyr_X"].dropna().values
    gyr_y = window["R_Wrist_Gyr_Y"].dropna().values
    gyr_z = window["R_Wrist_Gyr_Z"].dropna().values

    min_len = min(
        len(gyr_x),
        len(gyr_y),
        len(gyr_z)
    )

    if min_len > 1:

        gyr_x = gyr_x[:min_len]
        gyr_y = gyr_y[:min_len]
        gyr_z = gyr_z[:min_len]

        gyr_mag = np.sqrt(
            gyr_x**2 +
            gyr_y**2 +
            gyr_z**2
        )

        gyr_diff = np.diff(gyr_mag)

        features["Gyr_Magnitude_mean"] = np.mean(gyr_mag)
        features["Gyr_Magnitude_std"] = np.std(gyr_mag)
        features["Gyr_Magnitude_rms"] = np.sqrt(
            np.mean(gyr_mag**2)
        )

        features["Gyr_Magnitude_mean_abs_change"] = np.mean(
            np.abs(gyr_diff)
        )

        features["Gyr_Magnitude_max_abs_change"] = np.max(
            np.abs(gyr_diff)
        )

        features["Gyr_Magnitude_mad"] = np.median(
            np.abs(
                gyr_mag - np.median(gyr_mag)
            )
        )

    return pd.Series(features)

# %%
print([
    name for name in globals()
    if "window" in name.lower()
])

# %%
print("Healthy files:", len(usable_healthy_files))
print("PD files:", len(usable_pd_files))

# %%
clean_raw_windows = []

for file in usable_healthy_files:

    df = pd.read_csv(
        file,
        usecols=balance_features
    )

    windows = create_windows(
        df,
        window_size=500,
        min_valid_ratio=0.90
    )

    for window_id, window in enumerate(windows):

        # Extract V5 dynamic features
        features = extract_dynamic_features(window)

        features["recording_id"] = file.name
        features["window_id"] = window_id
        features["label"] = 0

        clean_raw_windows.append(features)


for file in usable_pd_files:

    df = pd.read_csv(
        file,
        usecols=balance_features
    )

    windows = create_windows(
        df,
        window_size=500,
        min_valid_ratio=0.90
    )

    for window_id, window in enumerate(windows):

        features = extract_dynamic_features(window)

        features["recording_id"] = file.name
        features["window_id"] = window_id
        features["label"] = 1

        clean_raw_windows.append(features)


v5_dynamic_df = pd.DataFrame(clean_raw_windows)

print("V5 dynamic shape:", v5_dynamic_df.shape)
print("Recordings:", v5_dynamic_df["recording_id"].nunique())


# %%
print(
    "NaN:",
    v5_dynamic_df.isna().sum().sum()
)

print(
    "Inf:",
    np.isinf(
        v5_dynamic_df.select_dtypes(
            include=np.number
        )
    ).sum().sum()
)

# %%
v1_features = clean_window_df[
    ["recording_id", "window_id", "label"] + basic_feature_cols
].copy()

v5_features = v5_dynamic_df[
    ["recording_id", "window_id", "label"] +
    [
        col for col in v5_dynamic_df.columns
        if col not in ["recording_id", "window_id", "label"]
    ]
].copy()

v5_combined = v1_features.merge(
    v5_features,
    on=["recording_id", "window_id", "label"],
    how="inner"
)

print("V5 shape:", v5_combined.shape)
print("Recordings:", v5_combined["recording_id"].nunique())

# %%
print(
    "Duplicate windows:",
    v5_combined.duplicated(
        ["recording_id", "window_id"]
    ).sum()
)

# %%
v5_feature_cols = [
    col for col in v5_combined.columns
    if col not in [
        "recording_id",
        "window_id",
        "label"
    ]
]

print("Total features:", len(v5_feature_cols))

print(
    "NaN:",
    v5_combined[v5_feature_cols].isna().sum().sum()
)

print(
    "Inf:",
    np.isinf(
        v5_combined[v5_feature_cols]
        .select_dtypes(include=np.number)
    ).sum().sum()
)

# %%
X_cv_v5 = v5_combined[v5_feature_cols]
y_cv_v5 = v5_combined["label"]
groups_v5 = v5_combined["recording_id"]

cv_v5 = StratifiedGroupKFold(
    n_splits=5,
    shuffle=True,
    random_state=42
)

fold_scores_v5 = []

for fold, (train_idx, val_idx) in enumerate(
    cv_v5.split(
        X_cv_v5,
        y_cv_v5,
        groups=groups_v5
    ),
    start=1
):

    X_fold_train = X_cv_v5.iloc[train_idx]
    y_fold_train = y_cv_v5.iloc[train_idx]

    X_fold_val = X_cv_v5.iloc[val_idx]

    fold_val_df = v5_combined.iloc[val_idx].copy()

    model_v5 = RandomForestClassifier(
        n_estimators=200,
        random_state=42,
        n_jobs=-1
    )

    model_v5.fit(
        X_fold_train,
        y_fold_train
    )

    val_pred = model_v5.predict(X_fold_val)

    # Window → recording
    fold_results = fold_val_df[
        ["recording_id", "label"]
    ].copy()

    fold_results["prediction"] = val_pred

    recording_fold = (
        fold_results
        .groupby("recording_id")
        .agg(
            actual_label=("label", "first"),
            pd_windows=("prediction", "sum"),
            total_windows=("prediction", "count")
        )
        .reset_index()
    )

    recording_fold["pd_ratio"] = (
        recording_fold["pd_windows"] /
        recording_fold["total_windows"]
    )

    # Keep the original 0.5 threshold for a fair
    # comparison with Clean V1
    recording_fold["final_prediction"] = (
        recording_fold["pd_ratio"] >= 0.5
    ).astype(int)

    fold_accuracy = accuracy_score(
        recording_fold["actual_label"],
        recording_fold["final_prediction"]
    )

    fold_scores_v5.append(fold_accuracy)

    print(
        f"V5 Fold {fold}: "
        f"{fold_accuracy:.4f} "
        f"({fold_accuracy * 100:.2f}%)"
    )

# %%
X_train_v5 = v5_combined[
    v5_combined["recording_id"].isin(train_ids)
][v5_feature_cols]

y_train_v5 = v5_combined[
    v5_combined["recording_id"].isin(train_ids)
]["label"]

test_v5 = v5_combined[
    v5_combined["recording_id"].isin(test_ids)
].copy()

X_test_v5 = test_v5[v5_feature_cols]
y_test_v5 = test_v5["label"]

print("Train:", X_train_v5.shape)
print("Test :", X_test_v5.shape)

# %%
final_model_v5 = RandomForestClassifier(
    n_estimators=200,
    random_state=42,
    n_jobs=-1
)

final_model_v5.fit(
    X_train_v5,
    y_train_v5
)

test_pred_v5 = final_model_v5.predict(
    X_test_v5
)

# %%
test_results_v5 = test_v5[
    ["recording_id", "label"]
].copy()

test_results_v5["prediction"] = test_pred_v5

recording_results_v5 = (
    test_results_v5
    .groupby("recording_id")
    .agg(
        actual_label=("label", "first"),
        pd_windows=("prediction", "sum"),
        total_windows=("prediction", "count")
    )
    .reset_index()
)

recording_results_v5["pd_ratio"] = (
    recording_results_v5["pd_windows"] /
    recording_results_v5["total_windows"]
)

recording_results_v5["final_prediction"] = (
    recording_results_v5["pd_ratio"] >= 0.5
).astype(int)

# %%
print(
    "V5 Recording-level accuracy:",
    accuracy_score(
        recording_results_v5["actual_label"],
        recording_results_v5["final_prediction"]
    )
)

print("\nConfusion Matrix:")
print(
    confusion_matrix(
        recording_results_v5["actual_label"],
        recording_results_v5["final_prediction"]
    )
)

print("\nClassification Report:")
print(
    classification_report(
        recording_results_v5["actual_label"],
        recording_results_v5["final_prediction"],
        target_names=["Healthy", "PD"]
    )
)

# %%
feature_importance_v5 = pd.DataFrame({
    "feature": v5_feature_cols,
    "importance": final_model_v5.feature_importances_
})

feature_importance_v5 = feature_importance_v5.sort_values(
    "importance",
    ascending=False
)

print(feature_importance_v5.head(20))

# %%
dynamic_cols = [
    col for col in v5_feature_cols
    if col not in basic_feature_cols
]

feature_importance_v5["type"] = feature_importance_v5[
    "feature"
].apply(
    lambda x: "Dynamic" if x in dynamic_cols else "Statistical"
)

print(
    feature_importance_v5.head(20)
)

# %%
v6_feature_cols = [
    # Acceleration statistical
    "R_Wrist_Acc_X_mean",
    "R_Wrist_Acc_X_std",
    "R_Wrist_Acc_X_min",
    "R_Wrist_Acc_X_max",
    "R_Wrist_Acc_X_rms",

    "R_Wrist_Acc_Y_mean",
    "R_Wrist_Acc_Y_std",
    "R_Wrist_Acc_Y_min",
    "R_Wrist_Acc_Y_max",
    "R_Wrist_Acc_Y_rms",

    "R_Wrist_Acc_Z_mean",
    "R_Wrist_Acc_Z_std",
    "R_Wrist_Acc_Z_min",
    "R_Wrist_Acc_Z_max",
    "R_Wrist_Acc_Z_rms",

    # Dynamic acceleration
    "R_Wrist_Acc_Y_mean_abs_change",
    "R_Wrist_Acc_Y_zero_crossing_rate",
    "R_Wrist_Acc_Z_mean_abs_change",

    # Acceleration magnitude
    "Acc_Magnitude_mean",
    "Acc_Magnitude_rms",
    "Acc_Magnitude_mean_abs_change"
]

print("V6 features:", len(v6_feature_cols))

# %%
X_cv_v6 = v5_combined[v6_feature_cols]
y_cv_v6 = v5_combined["label"]
groups_v6 = v5_combined["recording_id"]

print("Shape:", X_cv_v6.shape)
print("NaN:", X_cv_v6.isna().sum().sum())
print(
    "Inf:",
    np.isinf(X_cv_v6).sum().sum()
)

# %%
cv_v6 = StratifiedGroupKFold(
    n_splits=5,
    shuffle=True,
    random_state=42
)

fold_scores_v6 = []

for fold, (train_idx, val_idx) in enumerate(
    cv_v6.split(
        X_cv_v6,
        y_cv_v6,
        groups=groups_v6
    ),
    start=1
):

    X_fold_train = X_cv_v6.iloc[train_idx]
    y_fold_train = y_cv_v6.iloc[train_idx]

    X_fold_val = X_cv_v6.iloc[val_idx]

    fold_val_df = v5_combined.iloc[val_idx].copy()

    model_v6 = RandomForestClassifier(
        n_estimators=200,
        random_state=42,
        n_jobs=-1
    )

    model_v6.fit(
        X_fold_train,
        y_fold_train
    )

    val_pred = model_v6.predict(X_fold_val)

    fold_results = fold_val_df[
        ["recording_id", "label"]
    ].copy()

    fold_results["prediction"] = val_pred

    recording_fold = (
        fold_results
        .groupby("recording_id")
        .agg(
            actual_label=("label", "first"),
            pd_windows=("prediction", "sum"),
            total_windows=("prediction", "count")
        )
        .reset_index()
    )

    recording_fold["pd_ratio"] = (
        recording_fold["pd_windows"] /
        recording_fold["total_windows"]
    )

    recording_fold["final_prediction"] = (
        recording_fold["pd_ratio"] >= 0.5
    ).astype(int)

    score = accuracy_score(
        recording_fold["actual_label"],
        recording_fold["final_prediction"]
    )

    fold_scores_v6.append(score)

    print(
        f"V6 Fold {fold}: "
        f"{score:.4f} "
        f"({score * 100:.2f}%)"
    )

print(
    "\nV6 Mean:",
    np.mean(fold_scores_v6)
)

print(
    "V6 Std:",
    np.std(fold_scores_v6)
)

# %%
train_v6 = v5_combined[
    v5_combined["recording_id"].isin(train_ids)
].copy()

test_v6 = v5_combined[
    v5_combined["recording_id"].isin(test_ids)
].copy()

X_train_v6 = train_v6[v6_feature_cols]
y_train_v6 = train_v6["label"]

X_test_v6 = test_v6[v6_feature_cols]
y_test_v6 = test_v6["label"]

print("Train:", X_train_v6.shape)
print("Test :", X_test_v6.shape)

# %%
final_model_v6 = RandomForestClassifier(
    n_estimators=200,
    random_state=42,
    n_jobs=-1
)

final_model_v6.fit(
    X_train_v6,
    y_train_v6
)

test_pred_v6 = final_model_v6.predict(
    X_test_v6
)

# %%
test_results_v6 = test_v6[
    ["recording_id", "label"]
].copy()

test_results_v6["prediction"] = test_pred_v6

recording_results_v6 = (
    test_results_v6
    .groupby("recording_id")
    .agg(
        actual_label=("label", "first"),
        pd_windows=("prediction", "sum"),
        total_windows=("prediction", "count")
    )
    .reset_index()
)

recording_results_v6["pd_ratio"] = (
    recording_results_v6["pd_windows"] /
    recording_results_v6["total_windows"]
)

recording_results_v6["final_prediction"] = (
    recording_results_v6["pd_ratio"] >= 0.5
).astype(int)

# %%
print(
    "V6 Recording-level accuracy:",
    accuracy_score(
        recording_results_v6["actual_label"],
        recording_results_v6["final_prediction"]
    )
)

print("\nConfusion Matrix:")
print(
    confusion_matrix(
        recording_results_v6["actual_label"],
        recording_results_v6["final_prediction"]
    )
)

print("\nClassification Report:")
print(
    classification_report(
        recording_results_v6["actual_label"],
        recording_results_v6["final_prediction"],
        target_names=["Healthy", "PD"]
    )
)

# %%
v6_importance = pd.DataFrame({
    "feature": v6_feature_cols,
    "importance": final_model_v6.feature_importances_
}).sort_values(
    "importance",
    ascending=False
)

print(v6_importance)

# %%
from sklearn.model_selection import GridSearchCV

rf = RandomForestClassifier(
    random_state=42,
    n_jobs=-1
)

param_grid = {
    "n_estimators": [200, 400],
    "max_depth": [None, 5, 10, 15],
    "min_samples_split": [2, 5, 10],
    "min_samples_leaf": [1, 2, 4],
    "max_features": ["sqrt", "log2"]
}

grid = GridSearchCV(
    estimator=rf,
    param_grid=param_grid,
    scoring="accuracy",
    cv=cv_v6,
    n_jobs=-1,
    verbose=1
)

grid.fit(
    X_cv_v6,
    y_cv_v6,
    groups=groups_v6
)

print("Best parameters:")
print(grid.best_params_)

print("\nBest CV accuracy:")
print(grid.best_score_)

# %%
best_params = {
    "n_estimators": 200,
    "max_depth": 10,
    "max_features": "sqrt",
    "min_samples_leaf": 1,
    "min_samples_split": 10
}

# %%
tuned_scores = []

cv_tuned = StratifiedGroupKFold(
    n_splits=5,
    shuffle=True,
    random_state=42
)

for fold, (train_idx, val_idx) in enumerate(
    cv_tuned.split(
        X_cv_v6,
        y_cv_v6,
        groups=groups_v6
    ),
    start=1
):

    X_train = X_cv_v6.iloc[train_idx]
    y_train = y_cv_v6.iloc[train_idx]

    X_val = X_cv_v6.iloc[val_idx]

    val_df = v5_combined.iloc[val_idx].copy()

    tuned_model = RandomForestClassifier(
        n_estimators=200,
        max_depth=10,
        max_features="sqrt",
        min_samples_leaf=1,
        min_samples_split=10,
        random_state=42,
        n_jobs=-1
    )

    tuned_model.fit(X_train, y_train)

    val_pred = tuned_model.predict(X_val)

    fold_results = val_df[
        ["recording_id", "label"]
    ].copy()

    fold_results["prediction"] = val_pred

    recording_fold = (
        fold_results
        .groupby("recording_id")
        .agg(
            actual_label=("label", "first"),
            pd_windows=("prediction", "sum"),
            total_windows=("prediction", "count")
        )
        .reset_index()
    )

    recording_fold["pd_ratio"] = (
        recording_fold["pd_windows"] /
        recording_fold["total_windows"]
    )

    recording_fold["final_prediction"] = (
        recording_fold["pd_ratio"] >= 0.5
    ).astype(int)

    score = accuracy_score(
        recording_fold["actual_label"],
        recording_fold["final_prediction"]
    )

    tuned_scores.append(score)

    print(
        f"Tuned V6 Fold {fold}: "
        f"{score:.4f} "
        f"({score * 100:.2f}%)"
    )

print(
    "\nTuned V6 Recording CV Mean:",
    np.mean(tuned_scores)
)

print(
    "Tuned V6 Recording CV Std:",
    np.std(tuned_scores)
)

# %%
tuned_final_v6 = RandomForestClassifier(
    n_estimators=200,
    max_depth=10,
    max_features="sqrt",
    min_samples_leaf=1,
    min_samples_split=10,
    random_state=42,
    n_jobs=-1
)

tuned_final_v6.fit(
    X_train_v6,
    y_train_v6
)

tuned_test_pred = tuned_final_v6.predict(
    X_test_v6
)

# %%
tuned_test_results = test_v6[
    ["recording_id", "label"]
].copy()

tuned_test_results["prediction"] = tuned_test_pred

tuned_recording_results = (
    tuned_test_results
    .groupby("recording_id")
    .agg(
        actual_label=("label", "first"),
        pd_windows=("prediction", "sum"),
        total_windows=("prediction", "count")
    )
    .reset_index()
)

tuned_recording_results["pd_ratio"] = (
    tuned_recording_results["pd_windows"] /
    tuned_recording_results["total_windows"]
)

tuned_recording_results["final_prediction"] = (
    tuned_recording_results["pd_ratio"] >= 0.5
).astype(int)

# %%
print(
    "Tuned V6 Recording-level accuracy:",
    accuracy_score(
        tuned_recording_results["actual_label"],
        tuned_recording_results["final_prediction"]
    )
)

print("\nConfusion Matrix:")
print(
    confusion_matrix(
        tuned_recording_results["actual_label"],
        tuned_recording_results["final_prediction"]
    )
)

print("\nClassification Report:")
print(
    classification_report(
        tuned_recording_results["actual_label"],
        tuned_recording_results["final_prediction"],
        target_names=["Healthy", "PD"]
    )
)

# %%
print("V6 features:", len(v6_feature_cols))

fft_cols = [
    col for col in window_df_v3.columns
    if col not in basic_feature_cols
    and col not in ["recording_id", "window_id", "label"]
]

print("Possible FFT features:")
print(fft_cols)
print("Count:", len(fft_cols))

# %%
v7_fft = window_df_v3[
    ["recording_id", "window_id", "label"] + fft_cols
].copy()

v7_base = v5_combined[
    ["recording_id", "window_id", "label"] + v6_feature_cols
].copy()

v7_combined = v7_base.merge(
    v7_fft,
    on=["recording_id", "window_id", "label"],
    how="inner"
)

v7_feature_cols = (
    v6_feature_cols +
    fft_cols
)

print("V7 shape:", v7_combined.shape)
print("Features:", len(v7_feature_cols))
print("Recordings:", v7_combined["recording_id"].nunique())
print(
    "Duplicate windows:",
    v7_combined.duplicated(
        ["recording_id", "window_id"]
    ).sum()
)

# %%
print(
    "NaN:",
    v7_combined[v7_feature_cols]
    .isna()
    .sum()
    .sum()
)

print(
    "Inf:",
    np.isinf(
        v7_combined[v7_feature_cols]
        .select_dtypes(include=np.number)
    )
    .sum()
    .sum()
)

# %%
nan_info = v7_combined[v7_feature_cols].isna().sum()

print(
    nan_info[nan_info > 0]
)

# %%
bad_fft_rows = v7_combined[
    v7_combined[fft_cols].isna().any(axis=1)
]

print("Bad FFT windows:", len(bad_fft_rows))

print(
    bad_fft_rows[
        ["recording_id", "window_id", "label"]
        + [
            col for col in fft_cols
            if bad_fft_rows[col].isna().any()
        ]
    ].head(20)
)

# %%
print(
    v7_combined.loc[
        v7_combined[fft_cols].isna().any(axis=1),
        [
            "recording_id",
            "window_id"
        ] + fft_cols
    ].to_string()
)

# %%
print(
    v7_combined.loc[
        (v7_combined["recording_id"] == "HC111_Balance.csv") &
        (v7_combined["window_id"] == 13)
    ][v6_feature_cols].T
)

# %%
import inspect

print(inspect.getsource(extract_window_features_v3))

# %%
bad_fft_mask = v7_combined[fft_cols].isna().any(axis=1)

print("Removing FFT-bad windows:", bad_fft_mask.sum())

v7_clean = v7_combined.loc[~bad_fft_mask].copy()

print("V7 clean shape:", v7_clean.shape)
print("NaN:", v7_clean[v7_feature_cols].isna().sum().sum())
print("Inf:", np.isinf(v7_clean[v7_feature_cols]).sum().sum())
print("Recordings:", v7_clean["recording_id"].nunique())

# %%
X_cv_v7 = v7_clean[v7_feature_cols]
y_cv_v7 = v7_clean["label"]
groups_v7 = v7_clean["recording_id"]

# %%
cv_v7 = StratifiedGroupKFold(
    n_splits=5,
    shuffle=True,
    random_state=42
)

fold_scores_v7 = []

for fold, (train_idx, val_idx) in enumerate(
    cv_v7.split(
        X_cv_v7,
        y_cv_v7,
        groups=groups_v7
    ),
    start=1
):

    X_fold_train = X_cv_v7.iloc[train_idx]
    y_fold_train = y_cv_v7.iloc[train_idx]

    X_fold_val = X_cv_v7.iloc[val_idx]

    fold_val_df = v7_clean.iloc[val_idx].copy()

    model_v7 = RandomForestClassifier(
        n_estimators=200,
        random_state=42,
        n_jobs=-1
    )

    model_v7.fit(
        X_fold_train,
        y_fold_train
    )

    val_pred = model_v7.predict(X_fold_val)

    fold_results = fold_val_df[
        ["recording_id", "label"]
    ].copy()

    fold_results["prediction"] = val_pred

    recording_fold = (
        fold_results
        .groupby("recording_id")
        .agg(
            actual_label=("label", "first"),
            pd_windows=("prediction", "sum"),
            total_windows=("prediction", "count")
        )
        .reset_index()
    )

    recording_fold["pd_ratio"] = (
        recording_fold["pd_windows"] /
        recording_fold["total_windows"]
    )

    recording_fold["final_prediction"] = (
        recording_fold["pd_ratio"] >= 0.5
    ).astype(int)

    score = accuracy_score(
        recording_fold["actual_label"],
        recording_fold["final_prediction"]
    )

    fold_scores_v7.append(score)

    print(
        f"V7 Fold {fold}: "
        f"{score:.4f} "
        f"({score * 100:.2f}%)"
    )

print(
    "\nV7 Mean:",
    np.mean(fold_scores_v7)
)

print(
    "V7 Std:",
    np.std(fold_scores_v7)
)

# %%
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.svm import SVC

svm_v6 = Pipeline([
    ("scaler", StandardScaler()),
    ("svm", SVC(
        kernel="rbf",
        C=1.0,
        gamma="scale"
    ))
])

# %%
svm_scores = []

cv_svm = StratifiedGroupKFold(
    n_splits=5,
    shuffle=True,
    random_state=42
)

for fold, (train_idx, val_idx) in enumerate(
    cv_svm.split(
        X_cv_v6,
        y_cv_v6,
        groups=groups_v6
    ),
    start=1
):

    X_fold_train = X_cv_v6.iloc[train_idx]
    y_fold_train = y_cv_v6.iloc[train_idx]

    X_fold_val = X_cv_v6.iloc[val_idx]

    fold_val_df = v5_combined.iloc[val_idx].copy()

    # Train SVM
    svm_v6.fit(
        X_fold_train,
        y_fold_train
    )

    # Window predictions
    val_pred = svm_v6.predict(X_fold_val)

    # Store predictions
    fold_results = fold_val_df[
        ["recording_id", "label"]
    ].copy()

    fold_results["prediction"] = val_pred

    # Window → recording
    recording_fold = (
        fold_results
        .groupby("recording_id")
        .agg(
            actual_label=("label", "first"),
            pd_windows=("prediction", "sum"),
            total_windows=("prediction", "count")
        )
        .reset_index()
    )

    # PD ratio
    recording_fold["pd_ratio"] = (
        recording_fold["pd_windows"] /
        recording_fold["total_windows"]
    )

    # Recording prediction
    recording_fold["final_prediction"] = (
        recording_fold["pd_ratio"] >= 0.5
    ).astype(int)

    # Recording-level accuracy
    score = accuracy_score(
        recording_fold["actual_label"],
        recording_fold["final_prediction"]
    )

    svm_scores.append(score)

    print(
        f"SVM Fold {fold}: "
        f"{score:.4f} "
        f"({score * 100:.2f}%)"
    )

print(
    "\nSVM Mean:",
    np.mean(svm_scores)
)

print(
    "SVM Std:",
    np.std(svm_scores)
)

# %%
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression

lr_v6 = Pipeline([
    ("scaler", StandardScaler()),
    ("lr", LogisticRegression(
        max_iter=2000,
        random_state=42
    ))
])

# %%
lr_scores = []

cv_lr = StratifiedGroupKFold(
    n_splits=5,
    shuffle=True,
    random_state=42
)

for fold, (train_idx, val_idx) in enumerate(
    cv_lr.split(
        X_cv_v6,
        y_cv_v6,
        groups=groups_v6
    ),
    start=1
):

    X_fold_train = X_cv_v6.iloc[train_idx]
    y_fold_train = y_cv_v6.iloc[train_idx]

    X_fold_val = X_cv_v6.iloc[val_idx]

    fold_val_df = v5_combined.iloc[val_idx].copy()

    # Train
    lr_v6.fit(
        X_fold_train,
        y_fold_train
    )

    # Window predictions
    val_pred = lr_v6.predict(X_fold_val)

    fold_results = fold_val_df[
        ["recording_id", "label"]
    ].copy()

    fold_results["prediction"] = val_pred

    # Window → recording
    recording_fold = (
        fold_results
        .groupby("recording_id")
        .agg(
            actual_label=("label", "first"),
            pd_windows=("prediction", "sum"),
            total_windows=("prediction", "count")
        )
        .reset_index()
    )

    recording_fold["pd_ratio"] = (
        recording_fold["pd_windows"] /
        recording_fold["total_windows"]
    )

    recording_fold["final_prediction"] = (
        recording_fold["pd_ratio"] >= 0.5
    ).astype(int)

    score = accuracy_score(
        recording_fold["actual_label"],
        recording_fold["final_prediction"]
    )

    lr_scores.append(score)

    print(
        f"LR Fold {fold}: "
        f"{score:.4f} "
        f"({score * 100:.2f}%)"
    )

print(
    "\nLR Mean:",
    np.mean(lr_scores)
)

print(
    "LR Std:",
    np.std(lr_scores)
)

# %%



