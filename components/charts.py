import pandas as pd

CHART_LAYOUT = dict(
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    font=dict(color="rgba(255,255,255,0.7)", family="Inter"),
    xaxis=dict(gridcolor="rgba(255,255,255,0.06)", showline=False),
    yaxis=dict(gridcolor="rgba(255,255,255,0.06)", showline=False),
    margin=dict(l=0, r=0, t=30, b=0),
    legend=dict(bgcolor="rgba(0,0,0,0)"),
)


def series_to_df(series: list, value_col="value") -> pd.DataFrame:
    if not series:
        return pd.DataFrame(columns=["date", value_col])
    df = pd.DataFrame(series)
    df["date"] = pd.to_datetime(df["date"])
    df = df.sort_values("date")
    return df


def safe_sum(series: list) -> int:
    return sum(v.get("value", 0) for v in (series or []))


def safe_last(series: list) -> int:
    return series[-1].get("value", 0) if series else 0
