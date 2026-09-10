import numpy as np
import pandas as pd
from pathlib import Path


def get_walk_bouts(df):
    events = df["GeneralEvent"].values
    bouts = []
    in_walk = False
    start_idx = None

    for i, event in enumerate(events):
        if event == "Walk" and not in_walk:
            start_idx = i
            in_walk = True
        elif event != "Walk" and in_walk:
            end_idx = i - 1
            bouts.append(df.iloc[start_idx:end_idx + 1].copy())
            in_walk = False

    if in_walk:
        bouts.append(df.iloc[start_idx:].copy())

    return bouts


def safe_cv(values):
    values = np.asarray(values, dtype=float)

    if len(values) == 0:
        return np.nan

    mean = np.mean(values)

    if mean == 0:
        return np.nan

    return np.std(values) / mean


def safe_iqr(values):
    values = np.asarray(values, dtype=float)

    if len(values) == 0:
        return np.nan

    return np.percentile(values, 75) - np.percentile(values, 25)


def summarize_distribution(values, prefix):
    values = np.asarray(values, dtype=float)

    if len(values) == 0:
        return {
            f"{prefix}_median": np.nan,
            f"{prefix}_iqr": np.nan,
            f"{prefix}_min": np.nan,
            f"{prefix}_max": np.nan,
            f"{prefix}_range": np.nan,
            f"{prefix}_cv": np.nan
        }

    return {
        f"{prefix}_median": np.median(values),
        f"{prefix}_iqr": safe_iqr(values),
        f"{prefix}_min": np.min(values),
        f"{prefix}_max": np.max(values),
        f"{prefix}_range": np.max(values) - np.min(values),
        f"{prefix}_cv": safe_cv(values)
    }


def extract_contact_events_v2(bout):
    time = bout["Time"].str.replace(" sec", "").astype(float).values

    left = bout["L_Foot_Contact"].astype(int).values
    right = bout["R_Foot_Contact"].astype(int).values

    left_contacts = []
    left_offs = []
    right_contacts = []
    right_offs = []

    for i in range(1, len(left)):
        if left[i - 1] == 0 and left[i] == 1:
            left_contacts.append(time[i])
        elif left[i - 1] == 1 and left[i] == 0:
            left_offs.append(time[i])

    for i in range(1, len(right)):
        if right[i - 1] == 0 and right[i] == 1:
            right_contacts.append(time[i])
        elif right[i - 1] == 1 and right[i] == 0:
            right_offs.append(time[i])

    return (
        np.array(left_contacts),
        np.array(left_offs),
        np.array(right_contacts),
        np.array(right_offs)
    )


def calculate_stance_swing_v2(contacts, offs):
    stance = []
    swing = []

    n = min(len(contacts), len(offs))

    for i in range(n):
        if offs[i] > contacts[i]:
            stance.append(offs[i] - contacts[i])

    for i in range(len(offs) - 1):
        if i + 1 < len(contacts):
            if contacts[i + 1] > offs[i]:
                swing.append(contacts[i + 1] - offs[i])

    return np.array(stance), np.array(swing)


def calculate_step_stride_v2(left_contacts, right_contacts):
    contacts = []

    for t in left_contacts:
        contacts.append((t, "L"))

    for t in right_contacts:
        contacts.append((t, "R"))

    contacts.sort(key=lambda x: x[0])

    step_times = []
    left_steps = []
    right_steps = []

    for i in range(1, len(contacts)):
        step_time = contacts[i][0] - contacts[i - 1][0]
        step_times.append(step_time)

        if contacts[i][1] == "L":
            left_steps.append(step_time)
        else:
            right_steps.append(step_time)

    left_stride = np.diff(left_contacts)
    right_stride = np.diff(right_contacts)

    return (
        np.array(step_times),
        np.array(left_steps),
        np.array(right_steps),
        np.array(left_stride),
        np.array(right_stride)
    )


def extract_gait_features_v2(df):
    df = df.copy()

    df.columns = [
        col.replace(" ", "_")
        for col in df.columns
    ]

    bouts = get_walk_bouts(df)

    all_steps = []
    all_left_steps = []
    all_right_steps = []

    all_L_stance = []
    all_R_stance = []

    all_L_swing = []
    all_R_swing = []

    all_L_stride = []
    all_R_stride = []

    all_L_pressure = []
    all_R_pressure = []

    for bout in bouts:

        (
            L_contacts,
            L_offs,
            R_contacts,
            R_offs
        ) = extract_contact_events_v2(bout)

        L_stance, L_swing = calculate_stance_swing_v2(
            L_contacts,
            L_offs
        )

        R_stance, R_swing = calculate_stance_swing_v2(
            R_contacts,
            R_offs
        )

        (
            step_times,
            left_steps,
            right_steps,
            L_stride,
            R_stride
        ) = calculate_step_stride_v2(
            L_contacts,
            R_contacts
        )

        if len(step_times) == 0:
            continue

        all_steps.extend(step_times)
        all_left_steps.extend(left_steps)
        all_right_steps.extend(right_steps)

        all_L_stance.extend(L_stance)
        all_R_stance.extend(R_stance)

        all_L_swing.extend(L_swing)
        all_R_swing.extend(R_swing)

        all_L_stride.extend(L_stride)
        all_R_stride.extend(R_stride)

        left_pressure = bout["L_Foot_Pressure"].values
        right_pressure = bout["R_Foot_Pressure"].values

        left_mask = bout["L_Foot_Contact"].values == 1
        right_mask = bout["R_Foot_Contact"].values == 1

        all_L_pressure.extend(
            left_pressure[left_mask]
        )

        all_R_pressure.extend(
            right_pressure[right_mask]
        )

    all_steps = np.asarray(all_steps)
    all_left_steps = np.asarray(all_left_steps)
    all_right_steps = np.asarray(all_right_steps)

    all_L_stance = np.asarray(all_L_stance)
    all_R_stance = np.asarray(all_R_stance)

    all_L_swing = np.asarray(all_L_swing)
    all_R_swing = np.asarray(all_R_swing)

    all_L_stride = np.asarray(all_L_stride)
    all_R_stride = np.asarray(all_R_stride)

    all_L_pressure = np.asarray(all_L_pressure)
    all_R_pressure = np.asarray(all_R_pressure)

    if len(all_steps) == 0:
        return {}

    features = {}

    features.update(
        summarize_distribution(
            all_L_stance,
            "left_stance"
        )
    )

    features.update(
        summarize_distribution(
            all_R_stance,
            "right_stance"
        )
    )

    features.update(
        summarize_distribution(
            all_L_swing,
            "left_swing"
        )
    )

    features.update(
        summarize_distribution(
            all_R_swing,
            "right_swing"
        )
    )

    features.update(
        summarize_distribution(
            all_steps,
            "step_time"
        )
    )

    all_stride = np.concatenate(
        [all_L_stride, all_R_stride]
    )

    features.update(
        summarize_distribution(
            all_stride,
            "stride_time"
        )
    )

    features["step_count"] = len(all_steps)
    features["stride_count"] = len(all_stride)

    mean_step = np.mean(all_steps)

    features["cadence"] = (
        60 / mean_step
        if mean_step > 0
        else np.nan
    )

    if len(all_L_stance) > 0 and len(all_R_stance) > 0:

        L_mean = np.mean(all_L_stance)
        R_mean = np.mean(all_R_stance)

        mean_value = (L_mean + R_mean) / 2

        features["stance_asymmetry"] = (
            abs(L_mean - R_mean) / mean_value * 100
            if mean_value > 0
            else np.nan
        )

    else:
        features["stance_asymmetry"] = np.nan

    if len(all_L_swing) > 0 and len(all_R_swing) > 0:

        L_mean = np.mean(all_L_swing)
        R_mean = np.mean(all_R_swing)

        mean_value = (L_mean + R_mean) / 2

        features["swing_asymmetry"] = (
            abs(L_mean - R_mean) / mean_value * 100
            if mean_value > 0
            else np.nan
        )

    else:
        features["swing_asymmetry"] = np.nan

    features.update(
        summarize_distribution(
            all_L_pressure,
            "left_pressure"
        )
    )

    features.update(
        summarize_distribution(
            all_R_pressure,
            "right_pressure"
        )
    )

    if len(all_L_pressure) > 0 and len(all_R_pressure) > 0:

        L_mean = np.mean(all_L_pressure)
        R_mean = np.mean(all_R_pressure)

        mean_pressure = (L_mean + R_mean) / 2

        features["pressure_asymmetry"] = (
            abs(L_mean - R_mean) / mean_pressure * 100
            if mean_pressure > 0
            else np.nan
        )

    else:
        features["pressure_asymmetry"] = np.nan

    return features


def process_dataset():
    base_dir = Path(__file__).resolve().parents[1]

    healthy_dir = (
        base_dir /
        "dataset" /
        "gaitDataset" /
        "Gait" /
        "Healthy"
    )

    pd_dir = (
        base_dir /
        "dataset" /
        "gaitDataset" /
        "Gait" /
        "PD"
    )

    output_path = (
        base_dir /
        "dataset" /
        "gait_v2.csv"
    )

    healthy_files = list(
        healthy_dir.glob("*.csv")
    )

    pd_files = list(
        pd_dir.glob("*.csv")
    )

    records = []

    for file_path in healthy_files:

        if file_path.stem == "NLS124_SelfPace":
            continue

        try:
            df = pd.read_csv(file_path)

            features = extract_gait_features_v2(df)

            if features:
                features["recording_id"] = file_path.stem
                features["label"] = 0
                records.append(features)

        except Exception as e:
            print(
                f"Error processing {file_path.name}: {e}"
            )

    for file_path in pd_files:

        if file_path.stem == "NLS124_SelfPace":
            continue

        try:
            df = pd.read_csv(file_path)

            features = extract_gait_features_v2(df)

            if features:
                features["recording_id"] = file_path.stem
                features["label"] = 1
                records.append(features)

        except Exception as e:
            print(
                f"Error processing {file_path.name}: {e}"
            )

    gait_v2 = pd.DataFrame(records)

    columns = [
        "recording_id",
        "label"
    ] + [
        col for col in gait_v2.columns
        if col not in ["recording_id", "label"]
    ]

    gait_v2 = gait_v2[columns]

    gait_v2.to_csv(
        output_path,
        index=False
    )

    print("Gait V2 dataset created")
    print(f"Shape: {gait_v2.shape}")
    print(
        f"Healthy: {(gait_v2['label'] == 0).sum()}"
    )
    print(
        f"Parkinson's: {(gait_v2['label'] == 1).sum()}"
    )
    print(f"Saved to: {output_path}")


if __name__ == "__main__":
    process_dataset()