from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
import pandas as pd
import numpy as np
import joblib
import json
import tempfile
import os
import wave

from backendMl.preprocessing import (
    balance_preprocessing,
    fingerTapping_preprocessing,
    gait_preprocessing,
    voice_feature_extraction
)


# ============================================================
# FASTAPI APP
# ============================================================

app = FastAPI(
    title="Multimodal Neuromotor Screening API",
    version="0.1.0"
)


# ============================================================
# MODEL PATHS
# ============================================================

BALANCE_MODEL_PATH = "backendMl/models/balance_model.joblib"
FINGER_MODEL_PATH = "backendMl/models/finger_tapping_model.joblib"
GAIT_MODEL_PATH = "backendMl/models/gait_model.joblib"
VOICE_MODEL_PATH = "backendMl/models/logistic_regression_voice_baseline.joblib"


# ============================================================
# LOAD MODELS
# ============================================================

balance_bundle = joblib.load(BALANCE_MODEL_PATH)
finger_bundle = joblib.load(FINGER_MODEL_PATH)
gait_model = joblib.load(GAIT_MODEL_PATH)
voice_model = joblib.load(VOICE_MODEL_PATH)


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def get_actual_model(bundle):
    """
    Balance and Finger Tapping models are stored inside
    dictionaries. This function extracts the actual ML model.
    """

    if isinstance(bundle, dict) and "model" in bundle:
        return bundle["model"]

    return bundle


def get_feature_columns(bundle):
    """
    Gets the feature column names stored with the model.
    """

    if isinstance(bundle, dict):
        return bundle.get("feature_columns")

    return None


def get_threshold(bundle):
    """
    Gets the classification threshold stored with the model.
    """

    if isinstance(bundle, dict):
        return bundle.get("recording_threshold", 0.5)

    return 0.5


def prediction_to_int(prediction):
    """
    Converts model prediction into:
    0 = Healthy
    1 = PD
    """

    if isinstance(prediction, str):

        value = prediction.strip().lower()

        if value in ["pd", "parkinson", "parkinson's", "1"]:
            return 1

        if value in ["healthy", "ctrl", "control", "0"]:
            return 0

    try:
        return int(prediction)
    except Exception:
        return 0


def get_pd_probability(model, features):
    """
    Gets PD probability using predict_proba().
    Assumes:
        class 0 = Healthy
        class 1 = PD
    """

    if not hasattr(model, "predict_proba"):
        return None

    probabilities = model.predict_proba(features)

    classes = getattr(model, "classes_", None)

    if classes is None:
        return float(probabilities[0][-1])

    classes = list(classes)

    if 1 in classes:
        pd_index = classes.index(1)
        return float(probabilities[0][pd_index])

    # Fallback if class labels are strings
    class_strings = [str(c).lower() for c in classes]

    if "pd" in class_strings:
        pd_index = class_strings.index("pd")
        return float(probabilities[0][pd_index])

    return float(probabilities[0][-1])


def get_pd_probability_for_prediction(model, features, prediction):
    """
    Returns:
        pd_probability
        healthy_probability
    """

    if hasattr(model, "predict_proba"):

        probabilities = model.predict_proba(features)

        classes = getattr(model, "classes_", None)

        if classes is not None:

            classes = list(classes)

            pd_index = None
            healthy_index = None

            for i, cls in enumerate(classes):

                cls_string = str(cls).lower()

                if cls == 1 or cls_string == "pd":
                    pd_index = i

                elif cls == 0 or cls_string in [
                    "healthy",
                    "ctrl",
                    "control"
                ]:
                    healthy_index = i

            if pd_index is not None:
                pd_probability = float(
                    probabilities[0][pd_index]
                )
            else:
                pd_probability = float(
                    probabilities[0][-1]
                )

            if healthy_index is not None:
                healthy_probability = float(
                    probabilities[0][healthy_index]
                )
            else:
                healthy_probability = 1.0 - pd_probability

            return pd_probability, healthy_probability

        pd_probability = float(probabilities[0][-1])
        healthy_probability = 1.0 - pd_probability

        return pd_probability, healthy_probability

    # Fallback if predict_proba is unavailable
    prediction_int = prediction_to_int(prediction)

    if prediction_int == 1:
        return 1.0, 0.0

    return 0.0, 1.0


def build_standard_response(
    modality,
    prediction,
    pd_probability,
    healthy_probability,
    total_windows,
    pd_windows,
    sample_count
):
    """
    Creates the SAME response structure for all four modalities.
    """

    if total_windows > 0:
        pd_ratio = pd_windows / total_windows
    else:
        pd_ratio = 0.0

    return {
        "modality": modality,
        "prediction": prediction,
        "pd_probability": float(pd_probability),
        "healthy_probability": float(healthy_probability),
        "total_windows": int(total_windows),
        "pd_windows": int(pd_windows),
        "pd_ratio": float(pd_ratio),
        "sample_count": int(sample_count),
        "note": "Screening result only; not a medical diagnosis."
    }


def validate_signal_lengths(data, required_columns):
    """
    Checks that all required signal arrays have the same length.
    """

    lengths = []

    for column in required_columns:

        if column not in data:
            raise HTTPException(
                status_code=400,
                detail=f"Missing required signal: {column}"
            )

        if not isinstance(data[column], list):
            raise HTTPException(
                status_code=400,
                detail=f"{column} must be an array."
            )

        lengths.append(len(data[column]))

    if len(set(lengths)) != 1:
        raise HTTPException(
            status_code=400,
            detail="All signal arrays must have the same number of samples."
        )

    return lengths[0]


def get_json_data(data):
    """
    Allows the endpoint to receive either:
    - direct JSON object
    - JSON containing a 'signals' object
    """

    if not isinstance(data, dict):
        raise HTTPException(
            status_code=400,
            detail="Input must be a JSON object."
        )

    if "signals" in data and isinstance(data["signals"], dict):
        return data["signals"]

    return data


def convert_time_column(df):
    """
    Keeps Time as a string in the format expected by
    the existing gait preprocessing.

    Examples:
        0        -> "0 sec"
        0.01     -> "0.01 sec"
        "0 sec"  -> "0 sec"
        "0.01 sec" -> "0.01 sec"
    """

    if "Time" not in df.columns:
        return df

    def convert_value(value):

        value_string = str(value).strip()

        if value_string.lower().endswith("sec"):
            return value_string

        return f"{value_string} sec"

    df["Time"] = df["Time"].apply(convert_value)

    return df


def read_wav_sample_count(file_path):
    """
    Returns number of audio samples in a WAV file.
    """

    try:

        with wave.open(file_path, "rb") as wav_file:

            frames = wav_file.getnframes()

            return int(frames)

    except Exception:
        return 0


# ============================================================
# ROOT
# ============================================================

@app.get("/")
def root():

    return {
        "message": "Multimodal Neuromotor Screening API is running."
    }


# ============================================================
# HEALTH
# ============================================================

@app.get("/health")
def health():

    return {
        "status": "healthy"
    }


# ============================================================
# BALANCE
# ============================================================

@app.post("/predict/balance")
def predict_balance(data: dict):

    required_columns = [
        "R_Wrist_Acc_X",
        "R_Wrist_Acc_Y",
        "R_Wrist_Acc_Z",
        "R_Wrist_Gyr_X",
        "R_Wrist_Gyr_Y",
        "R_Wrist_Gyr_Z"
    ]

    signal_data = get_json_data(data)

    sample_count = validate_signal_lengths(
        signal_data,
        required_columns
    )

    if sample_count < 500:

        raise HTTPException(
            status_code=400,
            detail=(
                "Balance requires at least 500 samples "
                "because the model uses a 500-sample window."
            )
        )

    df = pd.DataFrame(signal_data)

    try:

        windows = balance_preprocessing.create_windows(df)

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Balance window creation failed: {str(e)}"
        )

    model = get_actual_model(balance_bundle)

    predictions = []
    probabilities = []

    for window in windows:

        try:

            features = balance_preprocessing.extract_features(
                window
            )

            if isinstance(features, dict):
                feature_df = pd.DataFrame([features])

            else:
                feature_df = pd.DataFrame(features)

            feature_columns = get_feature_columns(balance_bundle)

            if feature_columns is not None:

                feature_df = feature_df.reindex(
                    columns=feature_columns,
                    fill_value=0
                )

            prediction = model.predict(feature_df)[0]

            predictions.append(
                prediction_to_int(prediction)
            )

            pd_probability, healthy_probability = (
                get_pd_probability_for_prediction(
                    model,
                    feature_df,
                    prediction
                )
            )

            probabilities.append(
                (
                    pd_probability,
                    healthy_probability
                )
            )

        except Exception as e:

            raise HTTPException(
                status_code=500,
                detail=f"Balance prediction failed: {str(e)}"
            )

    total_windows = len(predictions)

    pd_windows = sum(
        1 for prediction in predictions
        if prediction == 1
    )

    pd_ratio = (
        pd_windows / total_windows
        if total_windows > 0
        else 0
    )

    if probabilities:

        pd_probability = float(
            np.mean(
                [p[0] for p in probabilities]
            )
        )

        healthy_probability = float(
            np.mean(
                [p[1] for p in probabilities]
            )
        )

    else:

        pd_probability = 0.0
        healthy_probability = 1.0

    prediction_label = (
        "balance_disorder"
        if pd_ratio >= 0.5
        else "no_balance_disorder"
    )

    return build_standard_response(
        modality="balance",
        prediction=prediction_label,
        pd_probability=pd_probability,
        healthy_probability=healthy_probability,
        total_windows=total_windows,
        pd_windows=pd_windows,
        sample_count=sample_count
    )


# ============================================================
# FINGER TAPPING
# ============================================================

@app.post("/predict/finger-tapping")
def predict_finger_tapping(data: dict):

    required_columns = [
        "gyroThumbX",
        "gyroThumbY",
        "gyroThumbZ",
        "gyroIndexX",
        "gyroIndexY",
        "gyroIndexZ"
    ]

    signal_data = get_json_data(data)

    sample_count = validate_signal_lengths(
        signal_data,
        required_columns
    )

    if sample_count < 500:

        raise HTTPException(
            status_code=400,
            detail=(
                "Finger tapping requires at least 500 samples "
                "because the model uses a 500-sample window."
            )
        )

    # --------------------------------------------------------
    # Convert JSON lists into NumPy arrays.
    # The existing finger-tapping preprocessing expects
    # NumPy arrays and uses the .size attribute.
    # --------------------------------------------------------

    finger_raw_data = {}

    for column in required_columns:

        finger_raw_data[column] = (
            pd.to_numeric(
                pd.Series(signal_data[column]),
                errors="coerce"
            ).to_numpy(dtype=float)
        )

    try:

        windows = fingerTapping_preprocessing.create_windows(
            finger_raw_data
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Finger tapping window creation failed: {str(e)}"
        )

    model = get_actual_model(finger_bundle)

    predictions = []
    probabilities = []

    for window in windows:

        try:

            features = fingerTapping_preprocessing.extract_features(
                window
            )

            if isinstance(features, dict):
                feature_df = pd.DataFrame([features])

            else:
                feature_df = pd.DataFrame(features)

            feature_columns = get_feature_columns(finger_bundle)

            if feature_columns is not None:

                feature_df = feature_df.reindex(
                    columns=feature_columns,
                    fill_value=0
                )

            prediction = model.predict(feature_df)[0]

            predictions.append(
                prediction_to_int(prediction)
            )

            pd_probability, healthy_probability = (
                get_pd_probability_for_prediction(
                    model,
                    feature_df,
                    prediction
                )
            )

            probabilities.append(
                (
                    pd_probability,
                    healthy_probability
                )
            )

        except Exception as e:

            raise HTTPException(
                status_code=500,
                detail=f"Finger tapping prediction failed: {str(e)}"
            )

    total_windows = len(predictions)

    pd_windows = sum(
        1 for prediction in predictions
        if prediction == 1
    )

    if probabilities:

        pd_probability = float(
            np.mean(
                [p[0] for p in probabilities]
            )
        )

        healthy_probability = float(
            np.mean(
                [p[1] for p in probabilities]
            )
        )

    else:

        pd_probability = 0.0
        healthy_probability = 1.0

    prediction_label = (
        "finger_tapping_disorder"
        if pd_windows > total_windows / 2
        else "no_finger_tapping_disorder"
    )

    return build_standard_response(
        modality="finger_tapping",
        prediction=prediction_label,
        pd_probability=pd_probability,
        healthy_probability=healthy_probability,
        total_windows=total_windows,
        pd_windows=pd_windows,
        sample_count=sample_count
    )


# ============================================================
# GAIT
# ============================================================

@app.post("/predict/gait")
def predict_gait(data: dict):

    required_columns = [
        "Time",
        "GeneralEvent",
        "L_Foot_Contact",
        "R_Foot_Contact",
        "L_Foot_Pressure",
        "R_Foot_Pressure"
    ]

    signal_data = get_json_data(data)

    sample_count = validate_signal_lengths(
        signal_data,
        required_columns
    )

    if sample_count < 10:

        raise HTTPException(
            status_code=400,
            detail="Gait requires at least 10 samples."
        )

    df = pd.DataFrame(signal_data)

    # --------------------------------------------------------
    # IMPORTANT:
    # Gait preprocessing expects Time to be a STRING such as
    # "0 sec", "0.01 sec", etc.
    #
    # Do NOT convert Time into a float here.
    # --------------------------------------------------------

    df = convert_time_column(df)

    # --------------------------------------------------------
    # Make sure numeric gait columns are numeric.
    # --------------------------------------------------------

    numeric_columns = [
        "L_Foot_Contact",
        "R_Foot_Contact",
        "L_Foot_Pressure",
        "R_Foot_Pressure"
    ]

    for column in numeric_columns:

        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        )

    try:

        features = gait_preprocessing.extract_gait_features_v2(
            df
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Gait feature extraction failed: {str(e)}"
        )

    try:

        if isinstance(features, pd.DataFrame):

            feature_df = features.copy()

        elif isinstance(features, dict):

            feature_df = pd.DataFrame([features])

        else:

            feature_df = pd.DataFrame(features)

        if hasattr(gait_model, "feature_names_in_"):

            feature_df = feature_df.reindex(
                columns=gait_model.feature_names_in_,
                fill_value=0
            )

        prediction = gait_model.predict(
            feature_df
        )[0]

        pd_probability, healthy_probability = (
            get_pd_probability_for_prediction(
                gait_model,
                feature_df,
                prediction
            )
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Gait prediction failed: {str(e)}"
        )

    prediction_int = prediction_to_int(
        prediction
    )

    if prediction_int == 1:

        prediction_label = "gait_disorder"
        pd_windows = 1

    else:

        prediction_label = "no_gait_disorder"
        pd_windows = 0

    return build_standard_response(
        modality="gait",
        prediction=prediction_label,
        pd_probability=pd_probability,
        healthy_probability=healthy_probability,
        total_windows=1,
        pd_windows=pd_windows,
        sample_count=sample_count
    )


# ============================================================
# VOICE
# ============================================================

@app.post("/predict/voice")
async def predict_voice(
    voice_file: UploadFile = File(...)
):

    if not voice_file.filename.lower().endswith(".wav"):

        raise HTTPException(
            status_code=400,
            detail="Please upload a WAV audio file."
        )

    temp_path = None

    try:

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".wav"
        ) as temp_file:

            temp_path = temp_file.name

            contents = await voice_file.read()

            temp_file.write(contents)

        sample_count = read_wav_sample_count(
            temp_path
        )

        features = voice_feature_extraction.extract_voice_features(
            temp_path
        )

        if isinstance(features, pd.DataFrame):

            feature_df = features.copy()

        elif isinstance(features, dict):

            feature_df = pd.DataFrame([features])

        else:

            feature_df = pd.DataFrame(features)

        prediction = voice_model.predict(
            feature_df
        )[0]

        pd_probability, healthy_probability = (
            get_pd_probability_for_prediction(
                voice_model,
                feature_df,
                prediction
            )
        )

        prediction_int = prediction_to_int(
            prediction
        )

        if prediction_int == 1:

            prediction_label = "voice_pd"
            pd_windows = 1

        else:

            prediction_label = "voice_healthy"
            pd_windows = 0

        return build_standard_response(
            modality="voice",
            prediction=prediction_label,
            pd_probability=pd_probability,
            healthy_probability=healthy_probability,
            total_windows=1,
            pd_windows=pd_windows,
            sample_count=sample_count
        )

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Voice prediction failed: {str(e)}"
        )

    finally:

        if temp_path is not None and os.path.exists(temp_path):

            os.remove(temp_path)


# ============================================================
# OVERALL SCREENING
# ============================================================

@app.post("/predict/overall")
async def predict_overall(
    data: str,
    voice_file: UploadFile = File(...)
):

    try:

        payload = json.loads(data)

    except Exception:

        raise HTTPException(
            status_code=400,
            detail="Invalid JSON in 'data'."
        )

    results = {}

    # --------------------------------------------------------
    # BALANCE
    # --------------------------------------------------------

    if "balance" in payload:

        balance_result = predict_balance(
            payload["balance"]
        )

        results["balance"] = balance_result

    # --------------------------------------------------------
    # FINGER TAPPING
    # --------------------------------------------------------

    if "finger_tapping" in payload:

        finger_result = predict_finger_tapping(
            payload["finger_tapping"]
        )

        results["finger_tapping"] = finger_result

    # --------------------------------------------------------
    # GAIT
    # --------------------------------------------------------

    if "gait" in payload:

        gait_result = predict_gait(
            payload["gait"]
        )

        results["gait"] = gait_result

    # --------------------------------------------------------
    # VOICE
    # --------------------------------------------------------

    if voice_file is not None:

        voice_result = await predict_voice(
            voice_file
        )

        results["voice"] = voice_result

    if not results:

        raise HTTPException(
            status_code=400,
            detail="No modality data was provided."
        )

    # ========================================================
    # F1-BASED WEIGHTS
    # ========================================================

    weights = {
        "balance": 0.2813,
        "finger_tapping": 0.2133,
        "gait": 0.2792,
        "voice": 0.2262
    }

    # ========================================================
    # WEIGHTED OVERALL SCORE
    # ========================================================

    total_weight = 0.0
    weighted_pd_score = 0.0

    for modality, result in results.items():

        if modality in weights:

            weight = weights[modality]

            weighted_pd_score += (
                weight *
                result["pd_probability"]
            )

            total_weight += weight

    if total_weight > 0:

        overall_pd_score = (
            weighted_pd_score / total_weight
        )

    else:

        overall_pd_score = 0.0

    overall_healthy_score = (
        1.0 - overall_pd_score
    )

    # --------------------------------------------------------
    # Current screening threshold
    # --------------------------------------------------------

    if overall_pd_score >= 0.50:

        overall_result = "screening_positive"

    else:

        overall_result = "screening_negative"

    return {
        "overall_result": overall_result,
        "pd_score": float(overall_pd_score),
        "healthy_score": float(overall_healthy_score),
        "weights": {
            modality: weights[modality]
            for modality in results
            if modality in weights
        },
        "modalities": results,
        "note": (
            "Overall screening score only; "
            "not a medically validated probability "
            "or medical diagnosis."
        )
    }