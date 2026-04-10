import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from .preprocessing import preprocess_data

def train_model():
    df = pd.read_csv("data/telecom_churn.csv")
    X, y = preprocess_data(df, for_training=True)

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2)

    model = RandomForestClassifier()
    model.fit(X_train, y_train)

    joblib.dump(model, "models/churn_model.pkl")