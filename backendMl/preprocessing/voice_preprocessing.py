import pandas as pd
    # 0 = Healthy
    # 1 = Parkinson's




VOICE_FEATURES = [
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
    "hnr"
]

def load_voice_data(data_path):

    df = pd.read_csv(data_path)
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(":", "_", regex=False)
        .str.replace("(", "_", regex=False)
        .str.replace(")", "_", regex=False)
        .str.replace("%", "_", regex=False)
    )

    df["status"] = df["status"].astype(int)

    missing_features = [
        feature
        for feature in VOICE_FEATURES
        if feature not in df.columns
    ]

    if missing_features:
        raise ValueError(
            f"Missing voice features: {missing_features}"
        )

    X = df[VOICE_FEATURES].copy()
    y = df["status"].copy()

    return X, y