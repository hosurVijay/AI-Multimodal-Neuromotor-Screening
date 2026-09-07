from pathlib import Path
import numpy as np
import pandas as pd

balance_features = [
    "R_Wrist_Acc_X",
    "R_Wrist_Acc_Y",
    "R_Wrist_Acc_Z",
    "R_Wrist_Gyr_X",
    "R_Wrist_Gyr_Y",
    "R_Wrist_Gyr_Z"
]

window_size = 500
min_valid_ratio = 0.90

selected_features = [
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
    "R_Wrist_Acc_Y_mean_abs_change",
    "R_Wrist_Acc_Y_zero_crossing_rate",
    "R_Wrist_Acc_Z_mean_abs_change",
    "Acc_Magnitude_mean",
    "Acc_Magnitude_rms",
    "Acc_Magnitude_mean_abs_change"
]

def create_windows(df, size=window_size, valid_ratio=min_valid_ratio):
    windows = []

    for start in range(0, len(df) - size + 1, size):
        window = df.iloc[start:start + size].copy()

        if window[balance_features].notna().all(axis=1).mean() >= valid_ratio:
            windows.append(window)

    return windows


def extract_features(window):
    features = {}

    for col in balance_features:
        signal = pd.to_numeric(
            window[col],
            errors="coerce"
        ).dropna().values

        if len(signal) < 2:
            continue

        features[f"{col}_mean"] = np.mean(signal)
        features[f"{col}_std"] = np.std(signal)
        features[f"{col}_min"] = np.min(signal)
        features[f"{col}_max"] = np.max(signal)
        features[f"{col}_rms"] = np.sqrt(np.mean(signal ** 2))

        diff = np.diff(signal)

        features[f"{col}_mean_abs_change"] = np.mean(np.abs(diff))
        features[f"{col}_max_abs_change"] = np.max(np.abs(diff))
        features[f"{col}_mad"] = np.median(
            np.abs(signal - np.median(signal))
        )

        centered = signal - np.mean(signal)

        features[f"{col}_zero_crossing_rate"] = (
            np.sum(centered[:-1] * centered[1:] < 0)
            / (len(signal) - 1)
        )

    acc = [
        pd.to_numeric(window[c], errors="coerce").dropna().values
        for c in [
            "R_Wrist_Acc_X",
            "R_Wrist_Acc_Y",
            "R_Wrist_Acc_Z"
        ]
    ]

    n = min(map(len, acc))

    if n > 1:
        acc_mag = np.sqrt(
            acc[0][:n] ** 2 +
            acc[1][:n] ** 2 +
            acc[2][:n] ** 2
        )

        diff = np.diff(acc_mag)

        features["Acc_Magnitude_mean"] = np.mean(acc_mag)
        features["Acc_Magnitude_std"] = np.std(acc_mag)
        features["Acc_Magnitude_rms"] = np.sqrt(
            np.mean(acc_mag ** 2)
        )
        features["Acc_Magnitude_mean_abs_change"] = np.mean(
            np.abs(diff)
        )
        features["Acc_Magnitude_max_abs_change"] = np.max(
            np.abs(diff)
        )
        features["Acc_Magnitude_mad"] = np.median(
            np.abs(acc_mag - np.median(acc_mag))
        )

    return features


def process_file(file):
    file = Path(file)
    df = pd.read_csv(file, usecols=balance_features)

    rows = []

    for window_id, window in enumerate(create_windows(df)):
        features = extract_features(window)

        if all(feature in features for feature in selected_features):
            rows.append({
                **{
                    feature: features[feature]
                    for feature in selected_features
                },
                "recording_id": file.name,
                "window_id": window_id
            })

    return pd.DataFrame(rows)