from datetime import datetime

from sqlalchemy import JSON, Column, DateTime, Float, Integer, String

from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False, default="user")
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)
    customer_name = Column(String(120), nullable=False, default="Anonymous Customer")
    customer_data = Column(JSON, nullable=False)
    churn_probability = Column(Float, nullable=False)
    churn_label = Column(String(30), nullable=False)
    retention_strategy = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
