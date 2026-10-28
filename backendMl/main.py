# backendMl/main.py

from fastapi import FastAPI, UploadFile, File, HTTPException, Body, Form
import pandas as pd
import numpy as np
import joblib
import tempfile
from pathlib import Path
import json


# ============================================================
# PREPROCESSING IMPORTS
# ============================================================

from backendMl.preprocessing.balance_preprocessing import (
    create_windows as create_balance_windows,
    extract_features as extract_balance_features,
    balance_features,
)

from backendMl.preprocessing.fingerTapping_preprocessing import (
    create_windows as create_finger_windows,
    extract_features as extract_finger_features,
    gyro_features,
)

from backendMl.preprocessing.gait_preprocessing import (
    extract_gait_features_v2,
)

from backendMl.preprocessing.voice_feature_extraction import (
    extract_voice_features,
)


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
MODEL_DIR = BASE_DIR / "models"


# ============================================================
# LOAD MODELS
# ============================================================

balance_model = joblib.load(
    MODEL_DIR / "balance_model.joblib"
)

gait_model = joblib.load(
    MODEL_DIR / "gait_model.joblib"
)

finger_model = joblib.load(
    MODEL_DIR / "finger_tapping_model.joblib"
)

voice_model = joblib.load(
    MODEL_DIR / "logistic_regression_voice_baseline.joblib"
)


# ============================================================
# FASTAPI APP
# ============================================================

app = FastAPI(
    title="Neuromotor Screening API",
    description="FastAPI backend for neuromotor screening modalities.",
    version="1.0.0",
)


# ============================================================
# GENERAL MODEL HELPERS
# ============================================================

def get_actual_model(model):
    """
    Some saved models are stored directly.
    Some are stored inside a dictionary.

    This function gets the actual ML model.
    """

    if isinstance(model, dict) and "model" in model:
        return model["model"]

    return model


def get_feature_columns(model):
    """
    Get feature column names from a saved model dictionary
    or from sklearn's feature_names_in_.
    """

    if isinstance(model, dict):

        feature_columns = model.get("feature_columns")

        if feature_columns is not None:
            return list(feature_columns)

        feature_names = model.get("feature_names")

        if feature_names is not None:
            return list(feature_names)

    actual_model = get_actual_model(model)

    if hasattr(actual_model, "feature_names_in_"):
        return list(actual_model.feature_names_in_)

    return None


def prepare_features(
    data,
    model,
    modality_name,
):
    """
    Prepare a DataFrame so that only the features used during
    model training are passed to the ML model.
    """

    if data is None:
        raise ValueError(
            f"No {modality_name} features were generated."
        )

    if isinstance(data, dict):
        data = pd.DataFrame([data])

    elif isinstance(data, np.ndarray):

        if data.ndim == 1:
            data = data.reshape(1, -1)

        data = pd.DataFrame(data)

    elif not isinstance(data, pd.DataFrame):
        data = pd.DataFrame(data)

    if data.empty:
        raise ValueError(
            f"No valid {modality_name} features were generated."
        )

    feature_columns = get_feature_columns(model)

    if feature_columns is not None:

        missing_features = [
            feature
            for feature in feature_columns
            if feature not in data.columns
        ]

        if missing_features:
            raise ValueError(
                f"Missing {modality_name} features: "
                + ", ".join(missing_features)
            )

        data = data[feature_columns]

    return data


def get_threshold(model, default=0.5):
    """
    Get saved threshold if the model dictionary contains one.
    Otherwise use the supplied default.
    """

    if isinstance(model, dict):

        for key in [
            "recording_threshold",
            "threshold",
            "saved_threshold",
        ]:

            if key in model:

                value = model[key]

                if value is not None:
                    return float(value)

    return float(default)


def prediction_to_int(prediction):
    """
    Convert numpy/scalar prediction into normal Python int.
    """

    try:
        return int(prediction)

    except Exception:
        return int(
            np.asarray(prediction).item()
        )


def get_pd_probability(
    model,
    features,
    prediction,
):
    """
    Get the probability of class 1 (PD).

    If the model supports predict_proba(), use the actual
    probability.

    Otherwise fall back to the hard prediction.
    """

    actual_model = get_actual_model(model)

    if hasattr(actual_model, "predict_proba"):

        probabilities = actual_model.predict_proba(
            features
        )[0]

        classes = actual_model.classes_

        probability_map = {
            int(cls): float(prob)
            for cls, prob in zip(
                classes,
                probabilities,
            )
        }

        return probability_map.get(
            1,
            0.0,
        )

    return (
        1.0
        if prediction == 1
        else 0.0
    )


# ============================================================
# JSON HELPERS
# ============================================================

def get_modality_data(
    payload: dict,
    modality_name: str,
):
    """
    Accept either:

    1. Full report JSON:

       {
           "reportId": ...,
           "patientId": ...,
           "modalities": {
               "balance": {...}
           }
       }

    2. Direct modality JSON:

       {
           "samplingRateHz": 100,
           "sampleCount": 500,
           "signals": {...}
       }

    3. Modality directly inside the report:

       {
           "balance": {
               ...
           }
       }
    """

    if not isinstance(payload, dict):
        raise ValueError(
            "Request body must be a JSON object."
        )

    modalities = payload.get("modalities")

    if isinstance(modalities, dict):

        modality = modalities.get(
            modality_name
        )

        if modality is None:
            raise ValueError(
                f"Missing '{modality_name}' inside 'modalities'."
            )

        if not isinstance(modality, dict):
            raise ValueError(
                f"'{modality_name}' must be a JSON object."
            )

        return modality

    if modality_name in payload:

        modality = payload[
            modality_name
        ]

        if not isinstance(modality, dict):
            raise ValueError(
                f"'{modality_name}' must be a JSON object."
            )

        return modality

    return payload


def get_signal_data(
    modality_data: dict,
    required_columns: list,
):
    """
    Accept both sensor-data formats.

    Format 1:

    {
        "signals": {
            "R_Wrist_Acc_X": [...],
            ...
        }
    }

    Format 2:

    {
        "R_Wrist_Acc_X": [...],
        ...
    }

    This allows the existing overall_test.json to be used
    without recreating or changing it.
    """

    if not isinstance(
        modality_data,
        dict,
    ):
        raise ValueError(
            "Modality data must be a JSON object."
        )

    signals = modality_data.get(
        "signals"
    )

    if isinstance(
        signals,
        dict,
    ):
        return signals

    direct_signals = {}

    for column in required_columns:

        if column in modality_data:
            direct_signals[column] = (
                modality_data[column]
            )

    if direct_signals:
        return direct_signals

    raise ValueError(
        "Sensor data must either be inside a "
        "'signals' object or directly inside the modality."
    )


def validate_signal_lengths(
    signals: dict,
    required_columns: list,
):
    """
    Make sure all required signal arrays exist and have
    the same number of samples.
    """

    missing = [
        column
        for column in required_columns
        if column not in signals
    ]

    if missing:
        raise ValueError(
            "Missing signal fields: "
            + ", ".join(missing)
        )

    lengths = {}

    for column in required_columns:

        values = signals[column]

        if not isinstance(
            values,
            list,
        ):
            raise ValueError(
                f"'{column}' must be an array."
            )

        lengths[column] = len(
            values
        )

    unique_lengths = set(
        lengths.values()
    )

    if len(unique_lengths) != 1:
        raise ValueError(
            "All signal arrays must contain the same "
            "number of samples."
        )

    sample_count = next(
        iter(unique_lengths)
    )

    if sample_count == 0:
        raise ValueError(
            "Signal arrays cannot be empty."
        )

    return sample_count


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/")
def root():

    return {
        "message": "Neuromotor Screening API is running"
    }


@app.get("/health")
def health():

    return {
        "status": "healthy"
    }


# ============================================================
# BALANCE JSON PREDICTION
# ============================================================

@app.post("/predict/balance")
async def predict_balance(
    payload: dict = Body(...)
):

    try:

        balance_data = get_modality_data(
            payload,
            "balance",
        )

        signals = get_signal_data(
            balance_data,
            balance_features,
        )

        sample_count = validate_signal_lengths(
            signals,
            balance_features,
        )

        df = pd.DataFrame(
            signals
        )

        for column in balance_features:

            df[column] = pd.to_numeric(
                df[column],
                errors="coerce",
            )

        balance_windows = create_balance_windows(
            df
        )

        if balance_windows is None:

            raise HTTPException(
                status_code=400,
                detail="No balance windows were generated.",
            )

        if len(balance_windows) == 0:

            raise HTTPException(
                status_code=400,
                detail=(
                    "No valid balance windows were generated. "
                    "The recording may need at least 500 samples."
                ),
            )

        rows = []

        selected_features = get_feature_columns(
            balance_model
        )

        if selected_features is None:

            raise ValueError(
                "Could not determine balance model features."
            )

        for window in balance_windows:

            features = extract_balance_features(
                window
            )

            rows.append(
                {
                    feature: features[feature]
                    for feature in selected_features
                }
            )

        balance_features_df = prepare_features(
            pd.DataFrame(rows),
            balance_model,
            "balance",
        )

        actual_balance_model = get_actual_model(
            balance_model
        )

        predictions = actual_balance_model.predict(
            balance_features_df
        )

        predictions = np.asarray(
            predictions
        ).astype(int)

        total_windows = len(
            predictions
        )

        pd_windows = int(
            np.sum(
                predictions == 1
            )
        )

        pd_ratio = (
            pd_windows / total_windows
            if total_windows > 0
            else 0
        )

        threshold = get_threshold(
            balance_model,
            default=0.5,
        )

        if pd_ratio >= threshold:

            result = "balance_disorder"

        else:

            result = "no_balance_disorder"

        return {
            "modality": "balance",
            "prediction": result,
            "total_windows": total_windows,
            "pd_windows": pd_windows,
            "pd_ratio": float(pd_ratio),
            "sample_count": sample_count,
            "note": (
                "Screening result only; "
                "not a medical diagnosis."
            ),
        }

    except HTTPException:
        raise

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Balance prediction failed: {str(e)}",
        )


# ============================================================
# GAIT JSON PREDICTION
# ============================================================

@app.post("/predict/gait")
async def predict_gait(
    payload: dict = Body(...)
):

    try:

        gait_data = get_modality_data(
            payload,
            "gait",
        )

        required_gait_columns = [
            "Time",
            "GeneralEvent",
            "L_Foot_Contact",
            "R_Foot_Contact",
            "L_Foot_Pressure",
            "R_Foot_Pressure",
        ]

        signals = get_signal_data(
            gait_data,
            required_gait_columns,
        )

        sample_count = validate_signal_lengths(
            signals,
            required_gait_columns,
        )

        df = pd.DataFrame(
            signals
        )

        if "Time" in df.columns:

            df["Time"] = df[
                "Time"
            ].astype(str)

            df["Time"] = df[
                "Time"
            ].apply(
                lambda value: (
                    value
                    if value.endswith(" sec")
                    else f"{value} sec"
                )
            )

        for column in [
            "L_Foot_Contact",
            "R_Foot_Contact",
            "L_Foot_Pressure",
            "R_Foot_Pressure",
        ]:

            df[column] = pd.to_numeric(
                df[column],
                errors="coerce",
            )

        gait_features = extract_gait_features_v2(
            df
        )

        if not gait_features:

            raise HTTPException(
                status_code=400,
                detail=(
                    "Could not extract gait features. "
                    "The JSON must contain enough walking/contact "
                    "events for gait feature extraction."
                ),
            )

        gait_features = prepare_features(
            gait_features,
            gait_model,
            "gait",
        )

        actual_gait_model = get_actual_model(
            gait_model
        )

        prediction = actual_gait_model.predict(
            gait_features
        )

        prediction = prediction_to_int(
            prediction[0]
        )

        if prediction == 1:

            result = "gait_disorder"

        else:

            result = "no_gait_disorder"

        return {
            "modality": "gait",
            "prediction": result,
            "sample_count": sample_count,
            "note": (
                "Screening result only; "
                "not a medical diagnosis."
            ),
        }

    except HTTPException:
        raise

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Gait prediction failed: {str(e)}",
        )


# ============================================================
# FINGER TAPPING JSON PREDICTION
# ============================================================

@app.post("/predict/finger-tapping")
async def predict_finger_tapping(
    payload: dict = Body(...)
):

    try:

        finger_data = get_modality_data(
            payload,
            "finger_tapping",
        )

        # Finger-tapping data is expected directly
        # inside the modality object.

        sample_count = validate_signal_lengths(
            finger_data,
            gyro_features,
        )

        data = {}

        for feature in gyro_features:

            values = pd.to_numeric(
                pd.Series(
                    finger_data[feature]
                ),
                errors="coerce",
            ).to_numpy(
                dtype=float
            )

            data[feature] = values

        finger_windows = create_finger_windows(
            data
        )

        if finger_windows is None:

            raise HTTPException(
                status_code=400,
                detail=(
                    "No finger-tapping windows were generated."
                ),
            )

        if len(finger_windows) == 0:

            raise HTTPException(
                status_code=400,
                detail=(
                    "No valid finger-tapping windows were generated. "
                    "The recording may need at least 500 samples."
                ),
            )

        rows = []

        for window in finger_windows:

            features = extract_finger_features(
                window
            )

            rows.append(
                features
            )

        finger_features_df = pd.DataFrame(
            rows
        )

        finger_features_df = prepare_features(
            finger_features_df,
            finger_model,
            "finger tapping",
        )

        actual_finger_model = get_actual_model(
            finger_model
        )

        predictions = actual_finger_model.predict(
            finger_features_df
        )

        predictions = np.asarray(
            predictions
        ).astype(int)

        total_windows = len(
            predictions
        )

        pd_windows = int(
            np.sum(
                predictions == 1
            )
        )

        pd_ratio = (
            pd_windows / total_windows
            if total_windows > 0
            else 0
        )

        threshold = get_threshold(
            finger_model,
            default=0.5,
        )

        if pd_ratio >= threshold:

            result = "finger_tapping_disorder"

        else:

            result = "no_finger_tapping_disorder"

        return {
            "modality": "finger_tapping",
            "prediction": result,
            "total_windows": total_windows,
            "pd_windows": pd_windows,
            "pd_ratio": float(pd_ratio),
            "sample_count": sample_count,
            "note": (
                "Screening result only; "
                "not a medical diagnosis."
            ),
        }

    except HTTPException:
        raise

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=(
                "Finger tapping prediction failed: "
                f"{str(e)}"
            ),
        )


# ============================================================
# VOICE WAV PREDICTION
# ============================================================

@app.post("/predict/voice")
async def predict_voice(
    file: UploadFile = File(...)
):

    if not file.filename.lower().endswith(".wav"):

        raise HTTPException(
            status_code=400,
            detail="Voice file must be a WAV file.",
        )

    temp_path = None

    try:

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".wav",
        ) as temp_file:

            content = await file.read()

            temp_file.write(
                content
            )

            temp_path = temp_file.name

        voice_features = extract_voice_features(
            temp_path
        )

        voice_features = prepare_features(
            voice_features,
            voice_model,
            "voice",
        )

        actual_voice_model = get_actual_model(
            voice_model
        )

        prediction = actual_voice_model.predict(
            voice_features
        )

        prediction = prediction_to_int(
            prediction[0]
        )

        pd_probability = get_pd_probability(
            voice_model,
            voice_features,
            prediction,
        )

        healthy_probability = (
            1.0 - pd_probability
        )

        if prediction == 1:

            result = "voice_pd"

        else:

            result = "voice_healthy"

        return {
            "modality": "voice",
            "prediction": result,
            "pd_probability": float(
                pd_probability
            ),
            "healthy_probability": float(
                healthy_probability
            ),
            "note": (
                "Screening result only; "
                "not a medical diagnosis."
            ),
        }

    except HTTPException:
        raise

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Voice prediction failed: {str(e)}",
        )

    finally:

        if temp_path:

            try:

                Path(
                    temp_path
                ).unlink(
                    missing_ok=True
                )

            except Exception:
                pass


# ============================================================
# OVERALL PREDICTION
#
# IMPORTANT:
# - data is sent as a multipart FORM FIELD
# - voice_file is sent as a WAV FILE
#
# Overall score uses probability fusion:
#
#   0.25 * Balance PD probability
# + 0.25 * Finger PD probability
# + 0.25 * Gait PD probability
# + 0.25 * Voice PD probability
#
# The existing overall_test.json can be used.
#
# ============================================================

@app.post("/predict/overall")
async def predict_overall(
    data: str = Form(
        ...,
        description=(
            "Paste the complete contents of the existing "
            "overall_test.json file here."
        ),
    ),
    voice_file: UploadFile = File(
        ...,
        description="Upload the WAV voice recording.",
    ),
):

    try:

        # ====================================================
        # VALIDATE FORM DATA
        # ====================================================

        if not isinstance(
            data,
            str,
        ):

            raise HTTPException(
                status_code=400,
                detail=(
                    "The overall JSON must be sent in "
                    "the 'data' form field."
                ),
            )

        data = data.strip()

        if not data:

            raise HTTPException(
                status_code=400,
                detail="The 'data' form field is empty.",
            )

        # ====================================================
        # PARSE JSON
        # ====================================================

        try:

            payload = json.loads(
                data
            )

        except json.JSONDecodeError as e:

            raise HTTPException(
                status_code=400,
                detail=(
                    "Invalid JSON in 'data' form field: "
                    f"{str(e)}"
                ),
            )

        if not isinstance(
            payload,
            dict,
        ):

            raise HTTPException(
                status_code=400,
                detail=(
                    "The overall JSON must contain "
                    "a JSON object."
                ),
            )

        # ====================================================
        # BALANCE
        # ====================================================

        balance_data = get_modality_data(
            payload,
            "balance",
        )

        balance_signals = get_signal_data(
            balance_data,
            balance_features,
        )

        validate_signal_lengths(
            balance_signals,
            balance_features,
        )

        balance_df = pd.DataFrame(
            balance_signals
        )

        for column in balance_features:

            balance_df[column] = pd.to_numeric(
                balance_df[column],
                errors="coerce",
            )

        balance_windows = create_balance_windows(
            balance_df
        )

        if balance_windows is None:

            raise HTTPException(
                status_code=400,
                detail=(
                    "No balance windows generated."
                ),
            )

        if len(balance_windows) == 0:

            raise HTTPException(
                status_code=400,
                detail=(
                    "No valid balance windows generated. "
                    "The balance data may need at least 500 samples."
                ),
            )

        balance_rows = []

        selected_balance_features = (
            get_feature_columns(
                balance_model
            )
        )

        if selected_balance_features is None:

            raise ValueError(
                "Could not determine balance model features."
            )

        for window in balance_windows:

            features = extract_balance_features(
                window
            )

            balance_rows.append(
                {
                    feature: features[feature]
                    for feature in selected_balance_features
                }
            )

        balance_features_df = prepare_features(
            pd.DataFrame(
                balance_rows
            ),
            balance_model,
            "balance",
        )

        actual_balance_model = get_actual_model(
            balance_model
        )

        balance_predictions = (
            actual_balance_model.predict(
                balance_features_df
            )
        )

        balance_predictions = np.asarray(
            balance_predictions
        ).astype(int)

        balance_total_windows = len(
            balance_predictions
        )

        balance_pd_windows = int(
            np.sum(
                balance_predictions == 1
            )
        )

        balance_pd_ratio = (
            balance_pd_windows
            / balance_total_windows
            if balance_total_windows > 0
            else 0.0
        )

        # ----------------------------------------------------
        # Balance probability
        # ----------------------------------------------------

        balance_probabilities = (
            actual_balance_model.predict_proba(
                balance_features_df
            )
        )

        balance_classes = (
            actual_balance_model.classes_
        )

        balance_probability_map = {
            int(cls): np.asarray(
                balance_probabilities
            )[:, index]
            for index, cls in enumerate(
                balance_classes
            )
        }

        balance_pd_probability = float(
            np.mean(
                balance_probability_map.get(
                    1,
                    np.zeros(
                        balance_total_windows
                    ),
                )
            )
        )

        balance_healthy_probability = (
            1.0 - balance_pd_probability
        )

        # ====================================================
        # GAIT
        # ====================================================

        gait_data = get_modality_data(
            payload,
            "gait",
        )

        required_gait_columns = [
            "Time",
            "GeneralEvent",
            "L_Foot_Contact",
            "R_Foot_Contact",
            "L_Foot_Pressure",
            "R_Foot_Pressure",
        ]

        gait_signals = get_signal_data(
            gait_data,
            required_gait_columns,
        )

        validate_signal_lengths(
            gait_signals,
            required_gait_columns,
        )

        gait_df = pd.DataFrame(
            gait_signals
        )

        gait_df["Time"] = (
            gait_df["Time"]
            .astype(str)
            .apply(
                lambda value: (
                    value
                    if value.endswith(" sec")
                    else f"{value} sec"
                )
            )
        )

        for column in [
            "L_Foot_Contact",
            "R_Foot_Contact",
            "L_Foot_Pressure",
            "R_Foot_Pressure",
        ]:

            gait_df[column] = pd.to_numeric(
                gait_df[column],
                errors="coerce",
            )

        gait_features = extract_gait_features_v2(
            gait_df
        )

        if not gait_features:

            raise HTTPException(
                status_code=400,
                detail="Could not generate gait features.",
            )

        gait_features = prepare_features(
            gait_features,
            gait_model,
            "gait",
        )

        actual_gait_model = get_actual_model(
            gait_model
        )

        gait_prediction = prediction_to_int(
            actual_gait_model.predict(
                gait_features
            )[0]
        )

        # ----------------------------------------------------
        # Gait probability
        # ----------------------------------------------------

        gait_probabilities = (
            actual_gait_model.predict_proba(
                gait_features
            )[0]
        )

        gait_classes = (
            actual_gait_model.classes_
        )

        gait_probability_map = {
            int(cls): float(prob)
            for cls, prob in zip(
                gait_classes,
                gait_probabilities,
            )
        }

        gait_pd_probability = (
            gait_probability_map.get(
                1,
                0.0,
            )
        )

        gait_healthy_probability = (
            1.0 - gait_pd_probability
        )

        # ====================================================
        # FINGER TAPPING
        # ====================================================

        finger_data = get_modality_data(
            payload,
            "finger_tapping",
        )

        validate_signal_lengths(
            finger_data,
            gyro_features,
        )

        finger_raw_data = {}

        for feature in gyro_features:

            finger_raw_data[feature] = (
                pd.to_numeric(
                    pd.Series(
                        finger_data[feature]
                    ),
                    errors="coerce",
                ).to_numpy(
                    dtype=float
                )
            )

        finger_windows = create_finger_windows(
            finger_raw_data
        )

        if finger_windows is None:

            raise HTTPException(
                status_code=400,
                detail=(
                    "No finger-tapping windows generated."
                ),
            )

        if len(finger_windows) == 0:

            raise HTTPException(
                status_code=400,
                detail=(
                    "No valid finger-tapping windows generated. "
                    "The finger-tapping data may need at least 500 samples."
                ),
            )

        finger_rows = []

        for window in finger_windows:

            features = extract_finger_features(
                window
            )

            finger_rows.append(
                features
            )

        finger_features_df = prepare_features(
            pd.DataFrame(
                finger_rows
            ),
            finger_model,
            "finger tapping",
        )

        actual_finger_model = get_actual_model(
            finger_model
        )

        finger_predictions = (
            actual_finger_model.predict(
                finger_features_df
            )
        )

        finger_predictions = np.asarray(
            finger_predictions
        ).astype(int)

        finger_total_windows = len(
            finger_predictions
        )

        finger_pd_windows = int(
            np.sum(
                finger_predictions == 1
            )
        )

        finger_pd_ratio = (
            finger_pd_windows
            / finger_total_windows
            if finger_total_windows > 0
            else 0.0
        )

        # ----------------------------------------------------
        # Finger probability
        # ----------------------------------------------------

        finger_probabilities = (
            actual_finger_model.predict_proba(
                finger_features_df
            )
        )

        finger_classes = (
            actual_finger_model.classes_
        )

        finger_probability_map = {
            int(cls): np.asarray(
                finger_probabilities
            )[:, index]
            for index, cls in enumerate(
                finger_classes
            )
        }

        finger_pd_probability = float(
            np.mean(
                finger_probability_map.get(
                    1,
                    np.zeros(
                        finger_total_windows
                    ),
                )
            )
        )

        finger_healthy_probability = (
            1.0 - finger_pd_probability
        )

        # ====================================================
        # VOICE
        # ====================================================

        if not voice_file.filename:

            raise HTTPException(
                status_code=400,
                detail="Voice file is required.",
            )

        if not voice_file.filename.lower().endswith(
            ".wav"
        ):

            raise HTTPException(
                status_code=400,
                detail="Voice file must be a WAV file.",
            )

        voice_temp_path = None

        try:

            with tempfile.NamedTemporaryFile(
                delete=False,
                suffix=".wav",
            ) as temp_file:

                voice_content = await voice_file.read()

                if not voice_content:

                    raise HTTPException(
                        status_code=400,
                        detail="Voice file is empty.",
                    )

                temp_file.write(
                    voice_content
                )

                voice_temp_path = temp_file.name

            voice_features = extract_voice_features(
                voice_temp_path
            )

            voice_features = prepare_features(
                voice_features,
                voice_model,
                "voice",
            )

            actual_voice_model = get_actual_model(
                voice_model
            )

            voice_prediction = prediction_to_int(
                actual_voice_model.predict(
                    voice_features
                )[0]
            )

            voice_pd_probability = (
                get_pd_probability(
                    voice_model,
                    voice_features,
                    voice_prediction,
                )
            )

            voice_healthy_probability = (
                1.0 - voice_pd_probability
            )

        finally:

            if voice_temp_path:

                try:

                    Path(
                        voice_temp_path
                    ).unlink(
                        missing_ok=True
                    )

                except Exception:
                    pass

        # ====================================================
        # OVERALL SCORE
        # ====================================================
        #
        # Equal-weight probability fusion:
        #
        # Balance       = 25%
        # Finger        = 25%
        # Gait          = 25%
        # Voice         = 25%
        #
        # IMPORTANT:
        # We combine PD probabilities from all four models.
        # We do NOT combine hard predictions.
        # ====================================================

        balance_weight =  0.2813
        finger_weight =  0.2133
        gait_weight = 0.2792
        voice_weight = 0.2262

        overall_score = (
            balance_weight
            * balance_pd_probability
            +
            finger_weight
            * finger_pd_probability
            +
            gait_weight
            * gait_pd_probability
            +
            voice_weight
            * voice_pd_probability
        )

        healthy_score = (
            1.0 - overall_score
        )

        if overall_score >= 0.50:

            overall_result = (
                "screening_positive"
            )

        else:

            overall_result = (
                "screening_negative"
            )

        # ====================================================
        # RESPONSE
        # ====================================================

        return {

            "overall_result": overall_result,

            "pd_score": float(
                overall_score
            ),

            "healthy_score": float(
                healthy_score
            ),

            "weights": {
                "balance": balance_weight,
                "finger_tapping": finger_weight,
                "gait": gait_weight,
                "voice": voice_weight,
            },

            "modalities": {

                "balance": {

                    "prediction": (
                        "balance_disorder"
                        if balance_pd_ratio >= 0.5
                        else "no_balance_disorder"
                    ),

                    "pd_probability": float(
                        balance_pd_probability
                    ),

                    "healthy_probability": float(
                        balance_healthy_probability
                    ),

                    "pd_ratio": float(
                        balance_pd_ratio
                    ),

                    "total_windows": (
                        balance_total_windows
                    ),

                    "pd_windows": (
                        balance_pd_windows
                    ),
                },

                "gait": {

                    "prediction": (
                        "gait_disorder"
                        if gait_prediction == 1
                        else "no_gait_disorder"
                    ),

                    "pd_probability": float(
                        gait_pd_probability
                    ),

                    "healthy_probability": float(
                        gait_healthy_probability
                    ),
                },

                "finger_tapping": {

                    "prediction": (
                        "finger_tapping_disorder"
                        if finger_pd_ratio >= 0.5
                        else "no_finger_tapping_disorder"
                    ),

                    "pd_probability": float(
                        finger_pd_probability
                    ),

                    "healthy_probability": float(
                        finger_healthy_probability
                    ),

                    "pd_ratio": float(
                        finger_pd_ratio
                    ),

                    "total_windows": (
                        finger_total_windows
                    ),

                    "pd_windows": (
                        finger_pd_windows
                    ),
                },

                "voice": {

                    "prediction": (
                        "voice_pd"
                        if voice_prediction == 1
                        else "voice_healthy"
                    ),

                    "pd_probability": float(
                        voice_pd_probability
                    ),

                    "healthy_probability": float(
                        voice_healthy_probability
                    ),
                },
            },

            "note": (
                "Overall screening score only; "
                "not a medically validated probability "
                "or medical diagnosis."
            ),
        }

    except HTTPException:
        raise

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=(
                "Overall prediction failed: "
                f"{str(e)}"
            ),
        )