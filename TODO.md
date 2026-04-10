# Churn Prediction Project Status

## Completed

- [x] Fixed prediction pipeline mismatch causing the internal server error
- [x] Rebuilt FastAPI backend with auth, prediction, and history endpoints
- [x] Added automatic database initialization and lightweight schema migration
- [x] Redesigned Streamlit app with a login page and smoother dashboard flow
- [x] Retrained the churn model and verified backend requests
- [x] Added SQLite default support and MySQL-ready configuration

## Run Commands

1. `.\venv\Scripts\python.exe train_standalone.py`
2. `.\venv\Scripts\python.exe -m uvicorn api.main:app --reload --port 8000`
3. `.\venv\Scripts\streamlit.exe run app/app.py`

## Verified

- [x] `POST /auth/register`
- [x] `POST /auth/login`
- [x] `POST /predict/`
- [x] `GET /history/`
