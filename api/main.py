import os
import sys
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import func
from sqlalchemy.orm import Session

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.auth import create_access_token, hash_password, verify_password
from src.config import API_TITLE, DATABASE_URL
from src.database import get_db, init_db
from src.models import Prediction, User
from src.predict import predict_churn
from src.retention_engine import retention_strategy
from src.schemas import (
    DashboardSummary,
    HistoryResponse,
    PredictionInput,
    PredictionResponse,
    TokenResponse,
    UserLogin,
    UserRegister,
)


@asynccontextmanager
async def lifespan(_: FastAPI):
    init_db()
    yield


app = FastAPI(title=API_TITLE, lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def home():
    return {
        "message": "Customer churn prediction API is running.",
        "database": DATABASE_URL,
        "status": "ok",
    }


@app.post("/auth/register", response_model=TokenResponse)
def register_user(payload: UserRegister, db: Session = Depends(get_db)):
    existing_user = (
        db.query(User)
        .filter((User.username == payload.username) | (User.email == payload.email))
        .first()
    )
    if existing_user:
        raise HTTPException(status_code=400, detail="Username or email already exists.")

    user = User(
        username=payload.username,
        email=payload.email,
        hashed_password=hash_password(payload.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token({"sub": user.username, "role": user.role})
    return TokenResponse(access_token=token, username=user.username)


@app.post("/auth/login", response_model=TokenResponse)
def login_user(payload: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == payload.username).first()
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid username or password.")

    token = create_access_token({"sub": user.username, "role": user.role})
    return TokenResponse(access_token=token, username=user.username)


@app.post("/predict/", response_model=PredictionResponse)
def predict(payload: PredictionInput, db: Session = Depends(get_db)):
    customer_data = payload.model_dump()
    if customer_data["TotalCharges"] is None:
        customer_data["TotalCharges"] = (
            customer_data["MonthlyCharges"] * customer_data["tenure"]
        )

    churn_probability = predict_churn(customer_data)
    churn_label = "High Risk" if churn_probability >= 0.6 else "Low Risk"
    strategy = retention_strategy(customer_data, churn_probability)

    prediction = Prediction(
        customer_name=customer_data["customer_name"],
        customer_data=customer_data,
        churn_probability=churn_probability,
        churn_label=churn_label,
        retention_strategy=strategy,
    )
    db.add(prediction)
    db.commit()
    db.refresh(prediction)
    return prediction


@app.get("/history/", response_model=HistoryResponse)
def get_history(db: Session = Depends(get_db)):
    predictions = (
        db.query(Prediction).order_by(Prediction.created_at.desc()).limit(50).all()
    )

    total_predictions = db.query(func.count(Prediction.id)).scalar() or 0
    average_probability = db.query(func.avg(Prediction.churn_probability)).scalar() or 0.0
    high_risk_customers = (
        db.query(func.count(Prediction.id))
        .filter(Prediction.churn_probability >= 0.6)
        .scalar()
        or 0
    )
    low_risk_customers = max(total_predictions - high_risk_customers, 0)

    return HistoryResponse(
        summary=DashboardSummary(
            total_predictions=total_predictions,
            average_churn_probability=float(average_probability),
            high_risk_customers=high_risk_customers,
            low_risk_customers=low_risk_customers,
        ),
        predictions=predictions,
    )
