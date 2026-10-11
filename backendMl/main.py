# backendMl/main.py

from fastapi import FastAPI, UploadFile, File, HTTPException
import pandas as pd
import numpy as np
import joblib
import tempfile
from pathlib import Path


# ============================================================
# PREPROCESSING IMPORTS
# ============================================================

from backendMl.preprocessing.balance_preprocessing import (
    process_file as process_balance_file
)

from backendMl.preprocessing.fingerTapping_preprocessing import (
    process_file as process_finger_file
)

from backendMl.preprocessing.gait_preprocessing import (
    extract_gait_features_v2
)

from backendMl.preprocessing.voice_feature_extraction import (
    extract_voice_features
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
    version="1.0.0"
)


# ============================================================
# GENERAL HELPER FUNCTIONS
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

    # If the saved object is a dictionary
    if isinstance(model, dict):

        feature_columns = model.get("feature_columns")

        if feature_columns is not None:
            return list(feature_columns)

        feature_names = model.get("feature_names")

        if feature_names is not None:
            return list(feature_names)

    # If it is an sklearn model/pipeline
    actual_model = get_actual_model(model)

    if hasattr(actual_model, "feature_names_in_"):
        return list(actual_model.feature_names_in_)

    return None


def prepare_features(
    data,
    model,
    modality_name
):
    """
    Prepare a DataFrame so that only the features used during
    model training are passed to the ML model.
    """

    if data is None:
        raise ValueError(
            f"No {modality_name} features were generated."
        )

    # Convert dictionary to DataFrame if necessary
    if isinstance(data, dict):
        data = pd.DataFrame([data])

    # Convert numpy array to DataFrame
    elif isinstance(data, np.ndarray):

        if data.ndim == 1:
            data = data.reshape(1, -1)

        data = pd.DataFrame(data)

    # Make sure we have a DataFrame
    elif not isinstance(data, pd.DataFrame):
        data = pd.DataFrame(data)

    if data.empty:
        raise ValueError(
            f"No valid {modality_name} features were generated."
        )

    feature_columns = get_feature_columns(model)

    # --------------------------------------------------------
    # IMPORTANT:
    # If the model tells us the exact training columns,
    # use ONLY those columns and in EXACTLY that order.
    # --------------------------------------------------------

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
            "saved_threshold"
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
        return int(np.asarray(prediction).item())


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
# BALANCE PREDICTION
# ============================================================

@app.post("/predict/balance")
async def predict_balance(
    file: UploadFile = File(...)
):

    if not file.filename.lower().endswith(".csv"):

        raise HTTPException(
            status_code=400,
            detail="Balance file must be a CSV file."
        )

    temp_path = None

    try:

        # ----------------------------------------------------
        # Save uploaded file temporarily
        # ----------------------------------------------------

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".csv"
        ) as temp_file:

            content = await file.read()

            temp_file.write(content)

            temp_path = temp_file.name

        # ----------------------------------------------------
        # Process balance recording
        # ----------------------------------------------------

        balance_windows = process_balance_file(
            temp_path
        )

        if balance_windows is None:

            raise HTTPException(
                status_code=400,
                detail="No balance windows were generated."
            )

        if len(balance_windows) == 0:

            raise HTTPException(
                status_code=400,
                detail="No valid balance windows were generated."
            )

        # ----------------------------------------------------
        # IMPORTANT:
        # Remove metadata columns such as:
        # recording_id
        # window_id
        #
        # and keep ONLY model training features.
        # ----------------------------------------------------

        balance_features = prepare_features(
            balance_windows,
            balance_model,
            "balance"
        )

        # ----------------------------------------------------
        # Get actual model
        # ----------------------------------------------------

        actual_balance_model = get_actual_model(
            balance_model
        )

        # ----------------------------------------------------
        # Predict
        # ----------------------------------------------------

        predictions = actual_balance_model.predict(
            balance_features
        )

        predictions = np.asarray(
            predictions
        ).astype(int)

        total_windows = len(predictions)

        pd_windows = int(
            np.sum(predictions == 1)
        )

        pd_ratio = (
            pd_windows / total_windows
            if total_windows > 0
            else 0
        )

        threshold = get_threshold(
            balance_model,
            default=0.5
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

            "note":
                "Screening result only; not a medical diagnosis."
        }

    except HTTPException:

        raise

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Balance prediction failed: {str(e)}"
        )

    finally:

        if temp_path:

            try:
                Path(temp_path).unlink(
                    missing_ok=True
                )
            except Exception:
                pass


# ============================================================
# GAIT PREDICTION
# ============================================================

@app.post("/predict/gait")
async def predict_gait(
    file: UploadFile = File(...)
):

    if not file.filename.lower().endswith(".csv"):

        raise HTTPException(
            status_code=400,
            detail="Gait file must be a CSV file."
        )

    temp_path = None

    try:

        # ----------------------------------------------------
        # Save uploaded CSV
        # ----------------------------------------------------

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".csv"
        ) as temp_file:

            content = await file.read()

            temp_file.write(content)

            temp_path = temp_file.name

        # ----------------------------------------------------
        # Read gait data
        # ----------------------------------------------------

        gait_data = pd.read_csv(
            temp_path
        )

        if gait_data.empty:

            raise HTTPException(
                status_code=400,
                detail="Gait CSV is empty."
            )

        # ----------------------------------------------------
        # Extract gait features
        # ----------------------------------------------------

        gait_features = extract_gait_features_v2(
            gait_data
        )

        # ----------------------------------------------------
        # Prepare exact training features
        # ----------------------------------------------------

        gait_features = prepare_features(
            gait_features,
            gait_model,
            "gait"
        )

        # ----------------------------------------------------
        # Get actual model
        # ----------------------------------------------------

        actual_gait_model = get_actual_model(
            gait_model
        )

        # ----------------------------------------------------
        # Predict
        # ----------------------------------------------------

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

            "note":
                "Screening result only; not a medical diagnosis."
        }

    except HTTPException:

        raise

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Gait prediction failed: {str(e)}"
        )

    finally:

        if temp_path:

            try:
                Path(temp_path).unlink(
                    missing_ok=True
                )
            except Exception:
                pass


# ============================================================
# FINGER TAPPING PREDICTION
# ============================================================

@app.post("/predict/finger-tapping")
async def predict_finger_tapping(
    file: UploadFile = File(...)
):

    if not file.filename.lower().endswith(".mat"):

        raise HTTPException(
            status_code=400,
            detail="Finger tapping file must be a MAT file."
        )

    temp_path = None

    try:

        # ----------------------------------------------------
        # Save MAT file
        # ----------------------------------------------------

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".mat"
        ) as temp_file:

            content = await file.read()

            temp_file.write(content)

            temp_path = temp_file.name

        # ----------------------------------------------------
        # Process finger tapping recording
        # ----------------------------------------------------

        finger_windows = process_finger_file(
            temp_path
        )

        if finger_windows is None:

            raise HTTPException(
                status_code=400,
                detail="No finger tapping windows were generated."
            )

        if len(finger_windows) == 0:

            raise HTTPException(
                status_code=400,
                detail="No valid finger tapping windows were generated."
            )

        # ----------------------------------------------------
        # Prepare exact training features
        # ----------------------------------------------------

        finger_features = prepare_features(
            finger_windows,
            finger_model,
            "finger tapping"
        )

        # ----------------------------------------------------
        # Get actual model
        # ----------------------------------------------------

        actual_finger_model = get_actual_model(
            finger_model
        )

        # ----------------------------------------------------
        # Predict
        # ----------------------------------------------------

        predictions = actual_finger_model.predict(
            finger_features
        )

        predictions = np.asarray(
            predictions
        ).astype(int)

        total_windows = len(predictions)

        pd_windows = int(
            np.sum(predictions == 1)
        )

        pd_ratio = (
            pd_windows / total_windows
            if total_windows > 0
            else 0
        )

        threshold = get_threshold(
            finger_model,
            default=0.5
        )

        # ----------------------------------------------------
        # Determine final result
        # ----------------------------------------------------

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

            "note":
                "Screening result only; not a medical diagnosis."
        }

    except HTTPException:

        raise

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Finger tapping prediction failed: {str(e)}"
        )

    finally:

        if temp_path:

            try:
                Path(temp_path).unlink(
                    missing_ok=True
                )
            except Exception:
                pass


# ============================================================
# VOICE PREDICTION
# ============================================================

@app.post("/predict/voice")
async def predict_voice(
    file: UploadFile = File(...)
):

    if not file.filename.lower().endswith(".wav"):

        raise HTTPException(
            status_code=400,
            detail="Voice file must be a WAV file."
        )

    temp_path = None

    try:

        # ----------------------------------------------------
        # Save WAV temporarily
        # ----------------------------------------------------

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".wav"
        ) as temp_file:

            content = await file.read()

            temp_file.write(content)

            temp_path = temp_file.name

        # ----------------------------------------------------
        # Extract the 16 voice features
        # ----------------------------------------------------

        voice_features = extract_voice_features(
            temp_path
        )

        if voice_features is None:

            raise HTTPException(
                status_code=400,
                detail="Could not extract voice features."
            )

        if len(voice_features) == 0:

            raise HTTPException(
                status_code=400,
                detail="No voice features were extracted."
            )

        # ----------------------------------------------------
        # Prepare exact model features
        # ----------------------------------------------------

        voice_features = prepare_features(
            voice_features,
            voice_model,
            "voice"
        )

        # ----------------------------------------------------
        # Predict
        # ----------------------------------------------------

        prediction = voice_model.predict(
            voice_features
        )

        prediction = prediction_to_int(
            prediction[0]
        )

        # ----------------------------------------------------
        # Probability
        # ----------------------------------------------------

        probabilities = voice_model.predict_proba(
            voice_features
        )[0]

        classes = voice_model.classes_

        healthy_probability = 0.0
        pd_probability = 0.0

        for class_value, probability in zip(
            classes,
            probabilities
        ):

            if int(class_value) == 0:

                healthy_probability = float(
                    probability
                )

            elif int(class_value) == 1:

                pd_probability = float(
                    probability
                )

        # ----------------------------------------------------
        # Result
        # ----------------------------------------------------

        if prediction == 1:

            result = "voice_disorder"

        else:

            result = "no_voice_disorder"

        return {

            "modality": "voice",

            "prediction": result,

            "pd_probability":
                float(pd_probability),

            "healthy_probability":
                float(healthy_probability),

            "note":
                "Screening result only; not a medical diagnosis."
        }

    except HTTPException:

        raise

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Voice prediction failed: {str(e)}"
        )

    finally:

        if temp_path:

            try:
                Path(temp_path).unlink(
                    missing_ok=True
                )
            except Exception:
                pass


# ============================================================
# OVERALL SCREENING
# ============================================================

@app.post("/predict/overall")
async def predict_overall(

    balance_file: UploadFile = File(...),

    gait_file: UploadFile = File(...),

    finger_tapping_file: UploadFile = File(...),

    voice_file: UploadFile = File(...)
):

    balance_temp_path = None
    gait_temp_path = None
    finger_temp_path = None
    voice_temp_path = None

    try:

        # ====================================================
        # 1. SAVE BALANCE FILE
        # ====================================================

        if not balance_file.filename.lower().endswith(
            ".csv"
        ):

            raise HTTPException(
                status_code=400,
                detail="Balance file must be a CSV file."
            )

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".csv"
        ) as temp_file:

            temp_file.write(
                await balance_file.read()
            )

            balance_temp_path = temp_file.name

        # ====================================================
        # 2. SAVE GAIT FILE
        # ====================================================

        if not gait_file.filename.lower().endswith(
            ".csv"
        ):

            raise HTTPException(
                status_code=400,
                detail="Gait file must be a CSV file."
            )

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".csv"
        ) as temp_file:

            temp_file.write(
                await gait_file.read()
            )

            gait_temp_path = temp_file.name

        # ====================================================
        # 3. SAVE FINGER TAPPING FILE
        # ====================================================

        if not finger_tapping_file.filename.lower().endswith(
            ".mat"
        ):

            raise HTTPException(
                status_code=400,
                detail="Finger tapping file must be a MAT file."
            )

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".mat"
        ) as temp_file:

            temp_file.write(
                await finger_tapping_file.read()
            )

            finger_temp_path = temp_file.name

        # ====================================================
        # 4. SAVE VOICE FILE
        # ====================================================

        if not voice_file.filename.lower().endswith(
            ".wav"
        ):

            raise HTTPException(
                status_code=400,
                detail="Voice file must be a WAV file."
            )

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".wav"
        ) as temp_file:

            temp_file.write(
                await voice_file.read()
            )

            voice_temp_path = temp_file.name

        # ====================================================
        # BALANCE
        # ====================================================

        balance_windows = process_balance_file(
            balance_temp_path
        )

        if balance_windows is None:

            raise ValueError(
                "No balance windows were generated."
            )

        if len(balance_windows) == 0:

            raise ValueError(
                "No valid balance windows were generated."
            )

        # ----------------------------------------------------
        # CRITICAL:
        # recording_id and window_id are metadata.
        # They are NOT model input features.
        # prepare_features() removes them by selecting
        # the exact training feature columns.
        # ----------------------------------------------------

        balance_features = prepare_features(
            balance_windows,
            balance_model,
            "balance"
        )

        actual_balance_model = get_actual_model(
            balance_model
        )

        balance_predictions = (
            actual_balance_model.predict(
                balance_features
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

        balance_score = (
            balance_pd_windows /
            balance_total_windows
        )

        # ====================================================
        # GAIT
        # ====================================================

        gait_data = pd.read_csv(
            gait_temp_path
        )

        if gait_data.empty:

            raise ValueError(
                "Gait CSV is empty."
            )

        gait_features = extract_gait_features_v2(
            gait_data
        )

        gait_features = prepare_features(
            gait_features,
            gait_model,
            "gait"
        )

        actual_gait_model = get_actual_model(
            gait_model
        )

        gait_prediction = (
            actual_gait_model.predict(
                gait_features
            )
        )

        gait_prediction = prediction_to_int(
            gait_prediction[0]
        )

        # Binary score:
        # 0 = no gait disorder
        # 1 = gait disorder

        gait_score = float(
            gait_prediction
        )

        if gait_prediction == 1:

            gait_result = "gait_disorder"

        else:

            gait_result = "no_gait_disorder"

        # ====================================================
        # FINGER TAPPING
        # ====================================================

        finger_windows = process_finger_file(
            finger_temp_path
        )

        if finger_windows is None:

            raise ValueError(
                "No finger tapping windows were generated."
            )

        if len(finger_windows) == 0:

            raise ValueError(
                "No valid finger tapping windows were generated."
            )

        # ----------------------------------------------------
        # Again, select only the exact model features.
        # This protects against metadata columns.
        # ----------------------------------------------------

        finger_features = prepare_features(
            finger_windows,
            finger_model,
            "finger tapping"
        )

        actual_finger_model = get_actual_model(
            finger_model
        )

        finger_predictions = (
            actual_finger_model.predict(
                finger_features
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

        finger_score = (
            finger_pd_windows /
            finger_total_windows
        )

        # ====================================================
        # VOICE
        # ====================================================

        voice_features = extract_voice_features(
            voice_temp_path
        )

        if voice_features is None:

            raise ValueError(
                "Could not extract voice features."
            )

        if len(voice_features) == 0:

            raise ValueError(
                "No voice features were extracted."
            )

        voice_features = prepare_features(
            voice_features,
            voice_model,
            "voice"
        )

        voice_prediction = voice_model.predict(
            voice_features
        )

        voice_prediction = prediction_to_int(
            voice_prediction[0]
        )

        voice_probabilities = (
            voice_model.predict_proba(
                voice_features
            )[0]
        )

        voice_classes = voice_model.classes_

        voice_healthy_probability = 0.0
        voice_pd_probability = 0.0

        for class_value, probability in zip(
            voice_classes,
            voice_probabilities
        ):

            if int(class_value) == 0:

                voice_healthy_probability = float(
                    probability
                )

            elif int(class_value) == 1:

                voice_pd_probability = float(
                    probability
                )

        # Voice score is probability of class 1
        voice_score = voice_pd_probability

        if voice_prediction == 1:

            voice_result = "voice_disorder"

        else:

            voice_result = "no_voice_disorder"

        # ====================================================
        # OVERALL SCORE
        # ====================================================

        # Equal weight for all four modalities.
        #
        # Balance  -> PD window ratio
        # Gait     -> 0 or 1
        # Finger   -> PD window ratio
        # Voice    -> PD probability
        #
        # This is an experimental screening score.
        # It is NOT a medically validated probability.

        overall_score = (
            balance_score
            + gait_score
            + finger_score
            + voice_score
        ) / 4.0

        healthy_score = 1.0 - overall_score

        # ----------------------------------------------------
        # Overall decision
        # ----------------------------------------------------

        if overall_score >= 0.5:

            overall_result = "screening_positive"

        else:

            overall_result = "screening_negative"

        # ====================================================
        # RETURN RESULT
        # ====================================================

        return {

            "overall_result":
                overall_result,

            "pd_score":
                float(overall_score),

            "healthy_score":
                float(healthy_score),

            "modalities": {

                "balance": {

                    "prediction":
                        (
                            "balance_disorder"
                            if balance_score >= 0.5
                            else "no_balance_disorder"
                        ),

                    "total_windows":
                        balance_total_windows,

                    "pd_windows":
                        balance_pd_windows,

                    "pd_ratio":
                        float(balance_score)
                },

                "gait": {

                    "prediction":
                        gait_result,

                    "score":
                        float(gait_score)
                },

                "finger_tapping": {

                    "prediction":
                        (
                            "finger_tapping_disorder"
                            if finger_score >= 0.5
                            else "no_finger_tapping_disorder"
                        ),

                    "total_windows":
                        finger_total_windows,

                    "pd_windows":
                        finger_pd_windows,

                    "pd_ratio":
                        float(finger_score)
                },

                "voice": {

                    "prediction":
                        voice_result,

                    "pd_probability":
                        float(
                            voice_pd_probability
                        ),

                    "healthy_probability":
                        float(
                            voice_healthy_probability
                        )
                }
            },

            "note":
                "Overall screening score only; "
                "not a medically validated probability "
                "or medical diagnosis."
        }

    except HTTPException:

        raise

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Overall prediction failed: {str(e)}"
        )

    finally:

        # ----------------------------------------------------
        # Delete temporary files
        # ----------------------------------------------------

        for temp_path in [
            balance_temp_path,
            gait_temp_path,
            finger_temp_path,
            voice_temp_path
        ]:

            if temp_path:

                try:

                    Path(temp_path).unlink(
                        missing_ok=True
                    )

                except Exception:

                    pass