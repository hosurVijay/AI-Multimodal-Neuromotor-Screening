
"""
Voice Feature Extraction and Preprocessing
Project: AI-Multimodal-Neuromotor-Screening

Labels:
    0 = Healthy
    1 = Parkinson's-labelled recording

IMPORTANT:
Praat-derived features are candidate proxies for MDVP features.
They have NOT been validated as numerically equivalent to MDVP.
This project is for experimental research, not clinical diagnosis.
"""

from pathlib import Path

import numpy as np
import pandas as pd
import parselmouth


# ============================================================
# 1. CONFIGURATION
# ============================================================

FEATURE_NAMES = [
    "mdvp_fo_hz_",
    "mdvp_fhi_hz_",
    "mdvp_flo_hz_",
    "mdvp_jitter___",
    "mdvp_jitter_abs_",
    "mdvp_rap",
    "mdvp_ppq",
    "jitter_ddp",
    "mdvp_shimmer",
    "mdvp_shimmer_db_",
    "shimmer_apq3",
    "shimmer_apq5",
    "mdvp_apq",
    "shimmer_dda",
    "nhr",
    "hnr",
]

HEALTHY_FOLDER = "HC_AH"
PD_FOLDER = "PD_AH"


# ============================================================
# 2. SAFE PRAAT CALL
# ============================================================

def safe_praat_call(objects, command, *args):
    """Return a finite float, or NaN if Praat cannot calculate it."""

    try:
        value = float(
            parselmouth.praat.call(objects, command, *args)
        )

        if np.isfinite(value):
            return value

        return np.nan

    except Exception:
        return np.nan


# ============================================================
# 3. EXTRACT JITTER AND SHIMMER FEATURES
# ============================================================

def extract_praat_features(wav_path):
    """Extract jitter and shimmer measurements using Praat."""

    wav_path = Path(wav_path)

    if not wav_path.is_file():
        raise FileNotFoundError(
            f"Audio file not found: {wav_path}"
        )

    sound = parselmouth.Sound(str(wav_path))

    point_process = parselmouth.praat.call(
        sound,
        "To PointProcess (periodic, cc)",
        60,
        500,
    )

    jitter_args = (0, 0, 0.0001, 0.02, 1.3)
    shimmer_args = (0, 0, 0.0001, 0.02, 1.3, 1.6)

    features = {
        "duration_sec": sound.get_total_duration(),

        # Jitter
        "jitter_local": safe_praat_call(
            point_process,
            "Get jitter (local)",
            *jitter_args,
        ),

        "jitter_absolute": safe_praat_call(
            point_process,
            "Get jitter (local, absolute)",
            *jitter_args,
        ),

        "jitter_rap": safe_praat_call(
            point_process,
            "Get jitter (rap)",
            *jitter_args,
        ),

        "jitter_ppq5": safe_praat_call(
            point_process,
            "Get jitter (ppq5)",
            *jitter_args,
        ),

        "jitter_ddp": safe_praat_call(
            point_process,
            "Get jitter (ddp)",
            *jitter_args,
        ),

        # Shimmer
        "shimmer_local": safe_praat_call(
            [sound, point_process],
            "Get shimmer (local)",
            *shimmer_args,
        ),

        "shimmer_local_db": safe_praat_call(
            [sound, point_process],
            "Get shimmer (local_dB)",
            *shimmer_args,
        ),

        "shimmer_apq3": safe_praat_call(
            [sound, point_process],
            "Get shimmer (apq3)",
            *shimmer_args,
        ),

        "shimmer_apq5": safe_praat_call(
            [sound, point_process],
            "Get shimmer (apq5)",
            *shimmer_args,
        ),

        "shimmer_apq11": safe_praat_call(
            [sound, point_process],
            "Get shimmer (apq11)",
            *shimmer_args,
        ),

        "shimmer_dda": safe_praat_call(
            [sound, point_process],
            "Get shimmer (dda)",
            *shimmer_args,
        ),
    }

    return features


# ============================================================
# 4. EXTRACT ALL 16 MODEL FEATURES FROM ONE WAV
# ============================================================

def extract_voice_features(wav_path):
    """
    Extract a single recording's 16 features.

    Returns:
        One-row pandas DataFrame with FEATURE_NAMES column order.
    """

    wav_path = Path(wav_path)

    praat_features = extract_praat_features(wav_path)

    sound = parselmouth.Sound(str(wav_path))

    # --------------------------------------------------------
    # Pitch features
    # --------------------------------------------------------

    pitch = sound.to_pitch(
        time_step=0.01,
        pitch_floor=60,
        pitch_ceiling=500,
    )

    f0 = np.asarray(
        pitch.selected_array["frequency"],
        dtype=float,
    )

    # Remove unvoiced frames and invalid values.
    f0 = f0[
        np.isfinite(f0) & (f0 > 0)
    ]

    if f0.size == 0:
        raise ValueError(
            f"No voiced pitch frames found: {wav_path.name}"
        )

    mean_f0 = float(np.mean(f0))
    max_f0 = float(np.max(f0))
    min_f0 = float(np.min(f0))

    # --------------------------------------------------------
    # HNR and candidate NHR approximation
    # --------------------------------------------------------

    harmonicity = sound.to_harmonicity_cc(
        time_step=0.01,
        minimum_pitch=60,
    )

    hnr_frames = np.asarray(
        harmonicity.values[0],
        dtype=float,
    )

    # Exclude Praat sentinel values and extreme measurements.
    hnr_frames = hnr_frames[
        np.isfinite(hnr_frames)
        & (hnr_frames > -50)
        & (hnr_frames < 100)
    ]

    if hnr_frames.size == 0:
        raise ValueError(
            f"No valid HNR frames found: {wav_path.name}"
        )

    mean_hnr = float(np.mean(hnr_frames))

    # Candidate approximation only; not verified as MDVP-equivalent.
    candidate_nhr = float(
        np.mean(10 ** (-hnr_frames / 10))
    )

    # --------------------------------------------------------
    # Map measurements to the 16-column model schema
    # --------------------------------------------------------

    feature_row = {
        "mdvp_fo_hz_": mean_f0,
        "mdvp_fhi_hz_": max_f0,
        "mdvp_flo_hz_": min_f0,

        "mdvp_jitter___":
            praat_features["jitter_local"],

        "mdvp_jitter_abs_":
            praat_features["jitter_absolute"],

        "mdvp_rap":
            praat_features["jitter_rap"],

        "mdvp_ppq":
            praat_features["jitter_ppq5"],

        "jitter_ddp":
            praat_features["jitter_ddp"],

        "mdvp_shimmer":
            praat_features["shimmer_local"],

        "mdvp_shimmer_db_":
            praat_features["shimmer_local_db"],

        "shimmer_apq3":
            praat_features["shimmer_apq3"],

        "shimmer_apq5":
            praat_features["shimmer_apq5"],

        "mdvp_apq":
            praat_features["shimmer_apq11"],

        "shimmer_dda":
            praat_features["shimmer_dda"],

        "nhr": candidate_nhr,
        "hnr": mean_hnr,
    }

    # Enforce the exact model feature order.
    feature_df = pd.DataFrame(
        [feature_row],
        columns=FEATURE_NAMES,
    )

    feature_df = feature_df.apply(
        pd.to_numeric,
        errors="coerce",
    )

    # Never silently pass invalid features to the model.
    values = feature_df.to_numpy(dtype=float)

    if not np.isfinite(values).all():
        invalid_columns = feature_df.columns[
            ~np.isfinite(values).all(axis=0)
        ].tolist()

        raise ValueError(
            f"Invalid features for {wav_path.name}: "
            f"{invalid_columns}"
        )

    return feature_df


# ============================================================
# 5. FIND ALL WAV FILES AND ASSIGN LABELS
# ============================================================

def discover_wavs(dataset_dir):
    """
    Expected structure:

    dataset/parkinson_voice_files/
        HC_AH/
            recording.wav
        PD_AH/
            recording.wav

    Returns:
        List of (wav_path, status) tuples.
        Healthy = 0, PD = 1.
    """

    dataset_dir = Path(dataset_dir)

    healthy_dir = dataset_dir / HEALTHY_FOLDER
    pd_dir = dataset_dir / PD_FOLDER

    if not healthy_dir.is_dir():
        raise FileNotFoundError(
            f"Healthy folder not found: {healthy_dir}"
        )

    if not pd_dir.is_dir():
        raise FileNotFoundError(
            f"PD folder not found: {pd_dir}"
        )

    healthy_files = sorted(
        healthy_dir.glob("*.wav")
    )

    pd_files = sorted(
        pd_dir.glob("*.wav")
    )

    if not healthy_files or not pd_files:
        raise FileNotFoundError(
            "No WAV files found in one or both class folders."
        )

    records = []

    for wav_path in healthy_files:
        records.append((wav_path, 0))

    for wav_path in pd_files:
        records.append((wav_path, 1))

    return records


# ============================================================
# 6. BUILD THE COMPLETE FEATURE DATASET
# ============================================================

def build_feature_dataset(dataset_dir):
    """
    Extract features from all WAV recordings.

    Returns a DataFrame containing:
        filename, path, status, and the 16 model features.

    Extraction errors stop execution rather than silently
    skipping recordings.
    """

    records = discover_wavs(dataset_dir)

    rows = []

    for index, (wav_path, status) in enumerate(
        records,
        start=1,
    ):

        features = extract_voice_features(wav_path)

        row = features.iloc[0].to_dict()

        row["filename"] = wav_path.name
        row["path"] = str(wav_path.resolve())
        row["status"] = int(status)

        rows.append(row)

        print(
            f"[{index}/{len(records)}] "
            f"Extracted: {wav_path.name}"
        )

    dataset_df = pd.DataFrame(rows)

    # Metadata first, followed by exact feature order.
    dataset_df = dataset_df[
        ["filename", "path", "status"] + FEATURE_NAMES
    ]

    X = dataset_df[FEATURE_NAMES].to_numpy(dtype=float)

    if not np.isfinite(X).all():
        raise ValueError(
            "The extracted dataset contains invalid feature values."
        )

    return dataset_df


# ============================================================
# 7. OPTIONAL: RUN THIS FILE DIRECTLY TO TEST EXTRACTION
# ============================================================

if __name__ == "__main__":

    BACKEND_ROOT = Path(__file__).resolve().parents[1]

    DATASET_DIR = (
        BACKEND_ROOT
        / "dataset"
        / "parkinson_voice_files"
    )

    OUTPUT_CSV = (
        BACKEND_ROOT
        / "dataset"
        / "voice_wav_features.csv"
    )

    print("Dataset directory:", DATASET_DIR)

    df = build_feature_dataset(DATASET_DIR)

    OUTPUT_CSV.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    df.to_csv(OUTPUT_CSV, index=False)

    print("\nFeature extraction completed.")
    print("Dataset shape:", df.shape)
    print("\nClass distribution:")
    print(df["status"].value_counts().sort_index())
    print("\nFeature columns:")
    print(FEATURE_NAMES)
    print("\nSaved to:", OUTPUT_CSV)
