import os

import joblib
import pandas as pd

from .preprocessing import preprocess_data

MODEL_PATH = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "models", "churn_model.pkl"
)

model = joblib.load(MODEL_PATH)


def prepare_prediction_payload(data: dict) -> pd.DataFrame:
    frame = pd.DataFrame([data])
    return preprocess_data(frame, for_training=False)


def predict_churn(data: dict) -> float:
    features = prepare_prediction_payload(data)
    probability = model.predict_proba(features)[0][1]
    return float(probability)
