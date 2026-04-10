# Customer Churn Prediction Platform

Full-stack churn prediction app with:

- FastAPI backend
- Streamlit frontend
- Login and registration
- Database-backed prediction history
- Retrained telecom churn model
- Default SQLite support and optional MySQL support

## Run

1. Install dependencies:
   `pip install -r requirements.txt`
2. Ensure environment variables are set in `.env`.
   By default this project uses SQLite:
   `DATABASE_URL=sqlite:///./churn.db`
3. Retrain the model if needed:
   `python train_standalone.py`
4. Start the API:
   `uvicorn api.main:app --reload --port 8000`
5. Start the frontend:
   `streamlit run app/app.py`

Frontend: `http://localhost:8501`
API docs: `http://127.0.0.1:8000/docs`

Docker deployment:
- Build and start the app with `docker compose up --build`
- The API is exposed on port `8000` and the frontend on `8501`

## Database

Default local setup:

`DATABASE_URL=sqlite:///./churn.db`

Optional MySQL setup:

`DATABASE_URL=mysql+pymysql://user:password@localhost:3306/churn_prediction`

Tables are created automatically at startup. Existing SQLite databases are lightly migrated for the new auth and prediction fields.

## Main API Routes

- `POST /auth/register`
- `POST /auth/login`
- `POST /predict/`
- `GET /history/`

## Notes

- The prediction pipeline now uses the same feature set during training and inference, which fixes the previous internal server error.
- Password hashing uses `pbkdf2_sha256` for compatibility with the current environment.
