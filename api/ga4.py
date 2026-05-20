"""
api/ga4.py — Google Analytics 4 data fetching.
Uses OAuth token from ga4_token.json (local) or Streamlit secrets (cloud).
"""
import os
import json
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import DateRange, Metric, RunReportRequest
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

GA4_PROPERTY_ID = "377768319"
_TOKEN_PATH     = "ga4_token.json"
_SCOPES         = ["https://www.googleapis.com/auth/analytics.readonly"]


def _get_credentials():
    token_data = None
    secrets_error = None

    try:
        import streamlit as st
        raw = st.secrets["ga4"]["token_json"]
        token_data = json.loads(raw)
    except Exception as e:
        secrets_error = str(e)

    if token_data is None:
        if not os.path.exists(_TOKEN_PATH):
            raise RuntimeError(
                f"No GA4 token: Streamlit secret failed ({secrets_error}), "
                f"and ga4_token.json not found locally."
            )
        with open(_TOKEN_PATH) as f:
            token_data = json.load(f)

    creds = Credentials(
        token=token_data.get("token"),
        refresh_token=token_data.get("refresh_token"),
        token_uri=token_data.get("token_uri", "https://oauth2.googleapis.com/token"),
        client_id=token_data.get("client_id"),
        client_secret=token_data.get("client_secret"),
        scopes=token_data.get("scopes", _SCOPES),
    )
    creds.refresh(Request())
    if os.path.exists(_TOKEN_PATH):
        with open(_TOKEN_PATH, "w") as f:
            f.write(creds.to_json())
    return creds


def fetch_ga4_engagement(start: str, end: str) -> dict:
    """
    Fetch engagement metrics from GA4 for the given date range.
    Returns: sessions, bounce_rate (%), avg_session_duration (seconds), page_views.
    Raises on any failure so the caller can surface the error.
    """
    creds = _get_credentials()
    client = BetaAnalyticsDataClient(credentials=creds)
    request = RunReportRequest(
        property=f"properties/{GA4_PROPERTY_ID}",
        date_ranges=[DateRange(start_date=start, end_date=end)],
        metrics=[
            Metric(name="sessions"),
            Metric(name="bounceRate"),
            Metric(name="averageSessionDuration"),
            Metric(name="screenPageViews"),
        ],
    )
    response = client.run_report(request)

    if not response.rows:
        return {}

    row = response.rows[0].metric_values
    return {
        "sessions":             int(float(row[0].value)),
        "bounce_rate":          round(float(row[1].value) * 100, 2),
        "avg_session_duration": round(float(row[2].value), 0),
        "page_views":           int(float(row[3].value)),
    }
