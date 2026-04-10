import os

import joblib
import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

from src.preprocessing import FEATURE_COLUMNS, preprocess_data


def train_model():
    dataframe = pd.read_csv("data/telecom_churn.csv")
    features, target = preprocess_data(dataframe, for_training=True)

    X_train, X_test, y_train, y_test = train_test_split(
        features, target, test_size=0.2, random_state=42, stratify=target
    )

    model = RandomForestClassifier(
        n_estimators=300,
        random_state=42,
        class_weight="balanced",
    )
    model.fit(X_train, y_train)

    os.makedirs("models", exist_ok=True)
    joblib.dump(model, "models/churn_model.pkl")

    accuracy = model.score(X_test, y_test)
    print("Model trained and saved to models/churn_model.pkl")
    print("Feature count:", len(FEATURE_COLUMNS))
    print("Accuracy:", round(accuracy, 4))


if __name__ == "__main__":
    train_model()
