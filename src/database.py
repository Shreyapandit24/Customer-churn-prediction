from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import declarative_base, sessionmaker

from .config import DATABASE_URL

engine_kwargs = {}
if DATABASE_URL.startswith("sqlite"):
    engine_kwargs["connect_args"] = {"check_same_thread": False}

engine = create_engine(DATABASE_URL, **engine_kwargs)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def init_db() -> None:
    from . import models  # noqa: F401

    Base.metadata.create_all(bind=engine)
    _apply_lightweight_migrations()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def _apply_lightweight_migrations() -> None:
    inspector = inspect(engine)

    if "predictions" in inspector.get_table_names():
        prediction_columns = {
            column["name"] for column in inspector.get_columns("predictions")
        }
        with engine.begin() as connection:
            if "customer_name" not in prediction_columns:
                connection.execute(
                    text(
                        "ALTER TABLE predictions "
                        "ADD COLUMN customer_name VARCHAR(120) "
                        "DEFAULT 'Anonymous Customer'"
                    )
                )
            if "churn_label" not in prediction_columns:
                connection.execute(
                    text(
                        "ALTER TABLE predictions "
                        "ADD COLUMN churn_label VARCHAR(30) DEFAULT 'Low Risk'"
                    )
                )

    if "users" in inspector.get_table_names():
        user_columns = {column["name"] for column in inspector.get_columns("users")}
        if "created_at" not in user_columns:
            with engine.begin() as connection:
                connection.execute(
                    text(
                        "ALTER TABLE users "
                        "ADD COLUMN created_at DATETIME DEFAULT CURRENT_TIMESTAMP"
                    )
                )
