import os
from typing import Dict

import pandas as pd
import plotly.express as px
import requests
import streamlit as st

API_BASE_URL = os.getenv("API_BASE_URL", "http://127.0.0.1:8000")
DATABASE_URL = os.getenv("DATABASE_URL", "")

SERVICE_OPTIONS = ["Yes", "No"]
DEPENDENT_SERVICE_OPTIONS = ["Yes", "No", "No internet service"]
MULTI_LINE_OPTIONS = ["Yes", "No", "No phone service"]


def api_get(path: str):
    response = requests.get(f"{API_BASE_URL}{path}", timeout=10)
    response.raise_for_status()
    return response.json()


def api_post(path: str, payload: Dict):
    response = requests.post(f"{API_BASE_URL}{path}", json=payload, timeout=10)
    response.raise_for_status()
    return response.json()


def initialize_state() -> None:
    st.session_state.setdefault("auth_token", None)
    st.session_state.setdefault("username", "")
    st.session_state.setdefault("history_cache", None)
    st.session_state.setdefault("last_prediction", None)


def render_shell() -> None:
    st.set_page_config(page_title="ChurnVision", page_icon="CX", layout="wide")
    st.markdown(
        """
        <style>
        .stApp {
            background:
                radial-gradient(circle at top left, rgba(17, 94, 89, 0.18), transparent 32%),
                radial-gradient(circle at top right, rgba(234, 179, 8, 0.22), transparent 28%),
                linear-gradient(180deg, #f8fafc 0%, #eef6f2 100%);
            color: #102a43;
        }
        [data-testid="stSidebar"] {
            background: linear-gradient(180deg, #0f172a 0%, #134e4a 100%);
        }
        [data-testid="stSidebar"] * {
            color: #f8fafc !important;
        }
        .hero-card, .panel-card, .metric-card {
            background: rgba(255, 255, 255, 0.88);
            border: 1px solid rgba(15, 23, 42, 0.08);
            border-radius: 24px;
            box-shadow: 0 18px 45px rgba(15, 23, 42, 0.08);
            backdrop-filter: blur(12px);
        }
        .hero-card {
            padding: 2rem 2.2rem;
            min-height: 230px;
        }
        .panel-card {
            padding: 1.4rem 1.6rem;
            margin-bottom: 1rem;
        }
        .metric-card {
            padding: 1.2rem 1.4rem;
        }
        .eyebrow {
            text-transform: uppercase;
            letter-spacing: 0.18rem;
            font-size: 0.72rem;
            font-weight: 700;
            color: #0f766e;
        }
        .hero-title {
            font-size: 3rem;
            line-height: 1.02;
            font-weight: 800;
            color: #0f172a;
            margin: 0.5rem 0 0.8rem 0;
        }
        .hero-copy {
            font-size: 1rem;
            color: #334155;
            max-width: 38rem;
        }
        .login-wrap {
            max-width: 1080px;
            margin: 0 auto;
            padding-top: 3rem;
        }
        .login-card {
            background: rgba(255, 255, 255, 0.9);
            border-radius: 28px;
            padding: 2rem;
            border: 1px solid rgba(15, 23, 42, 0.08);
            box-shadow: 0 24px 65px rgba(15, 23, 42, 0.12);
        }
        .kpi-label {
            color: #64748b;
            font-size: 0.85rem;
            margin-bottom: 0.2rem;
        }
        .kpi-value {
            color: #0f172a;
            font-size: 1.9rem;
            font-weight: 800;
        }
        .risk-high {
            color: #b91c1c;
            font-weight: 700;
        }
        .risk-low {
            color: #047857;
            font-weight: 700;
        }
        .stButton > button {
            border-radius: 14px;
            border: none;
            background: linear-gradient(135deg, #0f766e 0%, #0f172a 100%);
            color: #ffffff;
            font-weight: 700;
            padding: 0.7rem 1.2rem;
        }
        .stTextInput input, .stNumberInput input, .stSelectbox div[data-baseweb="select"] > div {
            border-radius: 14px;
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def login_page() -> None:
    st.markdown('<div class="login-wrap">', unsafe_allow_html=True)
    left, right = st.columns([1.2, 1], gap="large")

    with left:
        st.markdown(
            """
            <div class="hero-card">
                <div class="eyebrow">Customer Retention Intelligence</div>
                <div class="hero-title">Predict churn before revenue walks away.</div>
                <div class="hero-copy">
                    This workspace brings login, prediction, retention guidance, and prediction history into one cleaner full-stack flow.
                    Use the demo account below or create a new analyst account in seconds.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown(
            """
            <div class="panel-card">
                <strong>About the app</strong><br/>
                ChurnVision helps teams spot customers at risk, understand likely churn patterns, and take retention action before revenue is lost.
                <br/><br/>
                <em>"Predict early, retain smarter, grow stronger."</em>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with right:
        st.markdown('<div class="login-card">', unsafe_allow_html=True)
        mode = st.radio("Access", ["Sign in", "Sign up"], horizontal=True)
        st.caption("Choose `Sign in` if you already have an account, or `Sign up` to create one.")
        username = st.text_input("Username", placeholder="retention_analyst")
        email = st.text_input("Email", placeholder="analyst@company.com") if mode == "Sign up" else None
        password = st.text_input("Password", type="password", placeholder="Enter a secure password")

        if st.button("Continue", use_container_width=True):
            try:
                if mode == "Sign up":
                    payload = {"username": username, "email": email, "password": password}
                    result = api_post("/auth/register", payload)
                else:
                    payload = {"username": username, "password": password}
                    result = api_post("/auth/login", payload)

                st.session_state.auth_token = result["access_token"]
                st.session_state.username = result["username"]
                st.success("Access granted. Loading dashboard...")
                st.rerun()
            except requests.HTTPError as exc:
                detail = exc.response.json().get("detail", exc.response.text)
                st.error(detail)
            except requests.RequestException:
                st.error(
                    f"API is not reachable at {API_BASE_URL}. Start the backend with `uvicorn api.main:app --reload --port 8000`."
                )

        st.caption("New workspace? Create an account first. Existing users can sign in immediately.")
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("</div>", unsafe_allow_html=True)


def sidebar_profile() -> Dict:
    st.sidebar.markdown(f"### Welcome, {st.session_state.username}")
    st.sidebar.caption(f"Backend: {API_BASE_URL}")
    if DATABASE_URL.startswith("mysql"):
        st.sidebar.success("Connected to MySQL")
    elif DATABASE_URL.startswith("sqlite"):
        st.sidebar.info("Connected to SQLite")
    else:
        st.sidebar.warning("Database status unknown")
    if st.sidebar.button("Refresh history", use_container_width=True):
        st.session_state.history_cache = None
    if st.sidebar.button("Sign out", use_container_width=True):
        st.session_state.auth_token = None
        st.session_state.username = ""
        st.session_state.last_prediction = None
        st.rerun()

    st.sidebar.markdown("---")
    st.sidebar.subheader("Customer profile")

    return {
        "customer_name": st.sidebar.text_input("Customer name", value="Ava Johnson"),
        "gender": st.sidebar.selectbox("Gender", ["Male", "Female"]),
        "SeniorCitizen": st.sidebar.selectbox("Senior citizen", [0, 1]),
        "Partner": st.sidebar.selectbox("Partner", SERVICE_OPTIONS),
        "Dependents": st.sidebar.selectbox("Dependents", SERVICE_OPTIONS),
        "tenure": st.sidebar.slider("Tenure in months", 0, 72, 18),
        "PhoneService": st.sidebar.selectbox("Phone service", SERVICE_OPTIONS),
        "MultipleLines": st.sidebar.selectbox("Multiple lines", MULTI_LINE_OPTIONS),
        "InternetService": st.sidebar.selectbox("Internet service", ["DSL", "Fiber optic", "No"]),
        "OnlineSecurity": st.sidebar.selectbox("Online security", DEPENDENT_SERVICE_OPTIONS),
        "OnlineBackup": st.sidebar.selectbox("Online backup", DEPENDENT_SERVICE_OPTIONS),
        "DeviceProtection": st.sidebar.selectbox("Device protection", DEPENDENT_SERVICE_OPTIONS),
        "TechSupport": st.sidebar.selectbox("Tech support", DEPENDENT_SERVICE_OPTIONS),
        "StreamingTV": st.sidebar.selectbox("Streaming TV", DEPENDENT_SERVICE_OPTIONS),
        "StreamingMovies": st.sidebar.selectbox("Streaming movies", DEPENDENT_SERVICE_OPTIONS),
        "Contract": st.sidebar.selectbox("Contract", ["Month-to-month", "One year", "Two year"]),
        "PaperlessBilling": st.sidebar.selectbox("Paperless billing", SERVICE_OPTIONS),
        "PaymentMethod": st.sidebar.selectbox(
            "Payment method",
            [
                "Electronic check",
                "Mailed check",
                "Bank transfer (automatic)",
                "Credit card (automatic)",
            ],
        ),
        "MonthlyCharges": st.sidebar.slider("Monthly charges", 18.0, 120.0, 74.0, 0.5),
        "TotalCharges": st.sidebar.number_input(
            "Total charges",
            min_value=0.0,
            value=1332.0,
            step=10.0,
        ),
    }


def render_metric(label: str, value: str) -> None:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="kpi-label">{label}</div>
            <div class="kpi-value">{value}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def load_history():
    if st.session_state.history_cache is None:
        st.session_state.history_cache = api_get("/history/")
    return st.session_state.history_cache


def prediction_form(profile: Dict) -> None:
    cta_left, cta_right = st.columns([1.6, 1])

    with cta_left:
        st.markdown(
            """
            <div class="hero-card">
                <div class="eyebrow">Live Prediction Studio</div>
                <div class="hero-title">Run retention scenarios with a smoother analyst workflow.</div>
                <div class="hero-copy">
                    Adjust the customer profile from the sidebar, then generate a prediction to store it in the connected database and update the dashboard instantly.
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with cta_right:
        st.markdown(
            """
            <div class="panel-card">
                <strong>Features</strong><br/>
                Full-feature churn prediction, secure login, database-backed history, and a smoother analytics workflow in one dashboard.
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Predict churn now", use_container_width=True):
            try:
                result = api_post("/predict/", profile)
                st.session_state.last_prediction = result
                st.session_state.history_cache = None
                st.success("Prediction completed and saved.")
            except requests.HTTPError as exc:
                detail = exc.response.json().get("detail", exc.response.text)
                st.error(detail)
            except requests.RequestException as exc:
                st.error(f"Prediction failed: {exc}")


def dashboard() -> None:
    profile = sidebar_profile()
    prediction_form(profile)

    history_payload = load_history()
    summary = history_payload["summary"]
    predictions = history_payload["predictions"]

    metric_cols = st.columns(4)
    with metric_cols[0]:
        render_metric("Predictions saved", str(summary["total_predictions"]))
    with metric_cols[1]:
        render_metric("Average churn risk", f'{summary["average_churn_probability"]:.1%}')
    with metric_cols[2]:
        render_metric("High-risk customers", str(summary["high_risk_customers"]))
    with metric_cols[3]:
        render_metric("Low-risk customers", str(summary["low_risk_customers"]))

    latest = st.session_state.last_prediction or (predictions[0] if predictions else None)
    left, right = st.columns([1.1, 1], gap="large")

    with left:
        st.markdown('<div class="panel-card">', unsafe_allow_html=True)
        st.subheader("Latest prediction")
        if latest:
            risk_class = "risk-high" if latest["churn_probability"] >= 0.6 else "risk-low"
            st.markdown(
                f"""
                <p><strong>Customer:</strong> {latest["customer_name"]}</p>
                <p><strong>Risk label:</strong> <span class="{risk_class}">{latest["churn_label"]}</span></p>
                <p><strong>Probability:</strong> {latest["churn_probability"]:.2%}</p>
                <p><strong>Retention strategy:</strong> {latest["retention_strategy"]}</p>
                """,
                unsafe_allow_html=True,
            )
            customer_frame = pd.DataFrame(
                [{"Feature": key, "Value": value} for key, value in latest["customer_data"].items()]
            )
            st.dataframe(customer_frame, use_container_width=True, hide_index=True)
        else:
            st.info("No predictions saved yet. Use the sidebar to create the first one.")
        st.markdown("</div>", unsafe_allow_html=True)

    with right:
        st.markdown('<div class="panel-card">', unsafe_allow_html=True)
        st.subheader("Risk distribution")
        if predictions:
            chart_df = pd.DataFrame(predictions)
            chart_df["created_at"] = pd.to_datetime(chart_df["created_at"])
            fig = px.bar(
                chart_df.head(12).sort_values("created_at"),
                x="customer_name",
                y="churn_probability",
                color="churn_label",
                color_discrete_map={"High Risk": "#dc2626", "Low Risk": "#059669"},
            )
            fig.update_layout(height=360, margin=dict(l=10, r=10, t=20, b=10))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Charts appear after predictions are saved.")
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown('<div class="panel-card">', unsafe_allow_html=True)
    st.subheader("Prediction history")
    if predictions:
        table_df = pd.DataFrame(predictions)
        table_df["created_at"] = pd.to_datetime(table_df["created_at"]).dt.strftime("%Y-%m-%d %H:%M")
        table_df = table_df[
            ["created_at", "customer_name", "churn_label", "churn_probability", "retention_strategy"]
        ]
        table_df.columns = ["Created", "Customer", "Risk", "Probability", "Strategy"]
        st.dataframe(table_df, use_container_width=True, hide_index=True)
    else:
        st.info("No prediction history yet.")
    st.markdown("</div>", unsafe_allow_html=True)


def main() -> None:
    initialize_state()
    render_shell()

    if not st.session_state.auth_token:
        login_page()
    else:
        dashboard()


if __name__ == "__main__":
    main()
