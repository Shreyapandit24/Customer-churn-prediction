import pandas as pd

BINARY_COLUMNS = [
    "gender",
    "Partner",
    "Dependents",
    "PhoneService",
    "MultipleLines",
    "OnlineSecurity",
    "OnlineBackup",
    "DeviceProtection",
    "TechSupport",
    "StreamingTV",
    "StreamingMovies",
    "PaperlessBilling",
]

NUMERIC_COLUMNS = ["SeniorCitizen", "tenure", "MonthlyCharges", "TotalCharges"]

CATEGORICAL_OPTIONS = {
    "InternetService": ["DSL", "Fiber optic", "No"],
    "Contract": ["Month-to-month", "One year", "Two year"],
    "PaymentMethod": [
        "Electronic check",
        "Mailed check",
        "Bank transfer (automatic)",
        "Credit card (automatic)",
    ],
}

DEFAULT_VALUES = {
    "gender": "Male",
    "SeniorCitizen": 0,
    "Partner": "No",
    "Dependents": "No",
    "tenure": 12,
    "PhoneService": "Yes",
    "MultipleLines": "No",
    "InternetService": "DSL",
    "OnlineSecurity": "No",
    "OnlineBackup": "No",
    "DeviceProtection": "No",
    "TechSupport": "No",
    "StreamingTV": "No",
    "StreamingMovies": "No",
    "Contract": "Month-to-month",
    "PaperlessBilling": "Yes",
    "PaymentMethod": "Electronic check",
    "MonthlyCharges": 70.0,
}

FEATURE_COLUMNS = [
    *BINARY_COLUMNS,
    *NUMERIC_COLUMNS,
    "InternetService_DSL",
    "InternetService_Fiber optic",
    "InternetService_No",
    "Contract_Month-to-month",
    "Contract_One year",
    "Contract_Two year",
    "PaymentMethod_Bank transfer (automatic)",
    "PaymentMethod_Credit card (automatic)",
    "PaymentMethod_Electronic check",
    "PaymentMethod_Mailed check",
]

YES_NO_MAPPING = {
    "Yes": 1,
    "No": 0,
    "No internet service": 0,
    "No phone service": 0,
    "Male": 1,
    "Female": 0,
}


def _ensure_defaults(df: pd.DataFrame) -> pd.DataFrame:
    prepared = df.copy()

    if "customerID" in prepared.columns:
        prepared = prepared.drop(columns=["customerID"])

    for column, default_value in DEFAULT_VALUES.items():
        if column not in prepared.columns:
            prepared[column] = default_value
        prepared[column] = prepared[column].fillna(default_value)

    if "TotalCharges" not in prepared.columns:
        prepared["TotalCharges"] = prepared["MonthlyCharges"] * prepared["tenure"]

    prepared["TotalCharges"] = pd.to_numeric(prepared["TotalCharges"], errors="coerce")
    prepared["TotalCharges"] = prepared["TotalCharges"].fillna(
        prepared["MonthlyCharges"] * prepared["tenure"]
    )

    prepared["SeniorCitizen"] = pd.to_numeric(
        prepared["SeniorCitizen"], errors="coerce"
    ).fillna(0).astype(int)
    prepared["tenure"] = pd.to_numeric(prepared["tenure"], errors="coerce").fillna(12)
    prepared["MonthlyCharges"] = pd.to_numeric(
        prepared["MonthlyCharges"], errors="coerce"
    ).fillna(70.0)

    return prepared


def preprocess_data(df: pd.DataFrame, for_training: bool = False):
    prepared = _ensure_defaults(df)

    target = None
    if for_training and "Churn" in prepared.columns:
        target = prepared["Churn"].map({"Yes": 1, "No": 0}).fillna(0).astype(int)
        prepared = prepared.drop(columns=["Churn"])

    for column in BINARY_COLUMNS:
        prepared[column] = prepared[column].map(YES_NO_MAPPING).fillna(0).astype(int)

    for column in NUMERIC_COLUMNS:
        prepared[column] = pd.to_numeric(prepared[column], errors="coerce").fillna(0.0)

    for column, options in CATEGORICAL_OPTIONS.items():
        prepared[column] = prepared[column].where(prepared[column].isin(options), options[0])
        for option in options:
            prepared[f"{column}_{option}"] = (prepared[column] == option).astype(int)

    prepared = prepared.drop(columns=list(CATEGORICAL_OPTIONS.keys()), errors="ignore")
    prepared = prepared.reindex(columns=FEATURE_COLUMNS, fill_value=0.0)

    if for_training:
        return prepared, target

    return prepared
