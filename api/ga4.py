"""
api/ga4.py — Google Analytics 4 data fetching.
Uses OAuth token saved by ga4_auth.py.
"""
import os
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import DateRange, Metric, RunReportRequest
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request

GA4_PROPERTY_ID = "377768319"
_TOKEN_PATH     = "ga4_token.json"
_SCOPES         = ["https://www.googleapis.com/auth/analytics.readonly"]


def _get_credentials():
    if not os.path.exists(_TOKEN_PATH):
        print("DEBUG ga4: ga4_token.json not found — run ga4_auth.py first")
        return None
    creds = Credentials.from_authorized_user_file(_TOKEN_PATH, _SCOPES)
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
        with open(_TOKEN_PATH, "w") as f:
            f.write(creds.to_json())
    return creds if (creds and creds.valid) else None


def fetch_ga4_engagement(start: str, end: str) -> dict:
    """
    Fetch engagement metrics from GA4 for the given date range.
    Returns: sessions, bounce_rate (%), avg_session_duration (seconds), page_views.
    Returns {} if token not found or request fails.
    """
    try:
        creds = _get_credentials()
        if not creds:
            return {}

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
            "sessions":            int(float(row[0].value)),
            "bounce_rate":         round(float(row[1].value) * 100, 2),
            "avg_session_duration": round(float(row[2].value), 0),
            "page_views":          int(float(row[3].value)),
        }
    except Exception as e:
        print(f"DEBUG ga4: fetch error: {e}")
        return {}
