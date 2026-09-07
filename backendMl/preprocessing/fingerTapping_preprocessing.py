from pathlib import Path
from scipy.io import loadmat
import numpy as np
import pandas as pd

gyro_features = [
    "gyroThumbX",
    "gyroThumbY",
    "gyroThumbZ",
    "gyroIndexX",
    "gyroIndexY",
    "gyroIndexZ"
]

window_size = 500
min_valid_ratio = 0.90


def create_windows(data, size=window_size, valid_ratio=min_valid_ratio):
    n_samples = data[gyro_features[0]].size

    windows = []

    for start in range(
        0,
        n_samples - size + 1,
        size
    ):

        window = {
            feature: data[feature].flatten()[
                start:start + size
            ]
            for feature in gyro_features
        }

        valid = np.ones(
            size,
            dtype=bool
        )

        for feature in gyro_features:
            valid &= np.isfinite(
                window[feature]
            )

        if valid.mean() >= valid_ratio:
            windows.append(window)

    return windows


def extract_features(window):
    features = {}

    for col in gyro_features:

        signal = window[col]

        features[f"{col}_mean"] = np.mean(signal)
        features[f"{col}_std"] = np.std(signal)
        features[f"{col}_min"] = np.min(signal)
        features[f"{col}_max"] = np.max(signal)

        features[f"{col}_rms"] = np.sqrt(
            np.mean(signal ** 2)
        )

        diff = np.diff(signal)

        features[f"{col}_mean_abs_change"] = np.mean(
            np.abs(diff)
        )

        features[f"{col}_max_abs_change"] = np.max(
            np.abs(diff)
        )

        centered = signal - np.mean(signal)

        features[f"{col}_zero_crossing_rate"] = (
            np.sum(
                centered[:-1] *
                centered[1:] < 0
            )
            / (len(signal) - 1)
        )

    return features


def process_file(file):
    file = Path(file)

    data = loadmat(file)

    rows = []

    for window_id, window in enumerate(
        create_windows(data)
    ):

        features = extract_features(
            window
        )

        rows.append({
            **features,
            "recording_id": file.name,
            "window_id": window_id
        })

    return pd.DataFrame(rows)


def get_person_id(file):
    data = loadmat(file)

    return str(
        data["person_id"].flatten()[0]
    )