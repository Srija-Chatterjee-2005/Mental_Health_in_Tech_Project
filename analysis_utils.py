"""Reusable data preparation and metrics for the Mental Health in Tech project."""
from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd


GENDER_MAP = {
    "female": "Female", "f": "Female", "woman": "Female", "female (cis)": "Female",
    "cis female": "Female", "cis-female/femme": "Female", "femake": "Female",
    "male": "Male", "m": "Male", "man": "Male", "male (cis)": "Male",
    "cis male": "Male", "mal": "Male", "male-ish": "Male", "maile": "Male",
    "make": "Male", "msle": "Male", "mail": "Male", "malr": "Male",
    "cis man": "Male", "m|": "Male",
}

SUPPORT_MAPS = {
    "benefits": {"Yes": 1, "Don't know": 0.5, "No": 0},
    "care_options": {"Yes": 1, "Not sure": 0.5, "No": 0},
    "wellness_program": {"Yes": 1, "Don't know": 0.5, "No": 0},
    "seek_help": {"Yes": 1, "Don't know": 0.5, "No": 0},
    "anonymity": {"Yes": 1, "Don't know": 0.5, "No": 0},
    "leave": {"Very easy": 1, "Somewhat easy": 0.75, "Don't know": 0.5,
              "Somewhat difficult": 0.25, "Very difficult": 0},
    "mental_health_consequence": {"No": 1, "Maybe": 0.5, "Yes": 0},
    "coworkers": {"Yes": 1, "Some of them": 0.5, "No": 0},
    "supervisor": {"Yes": 1, "Some of them": 0.5, "No": 0},
    "mental_vs_physical": {"Yes": 1, "Don't know": 0.5, "No": 0},
    "obs_consequence": {"No": 1, "Yes": 0},
}


def normalize_gender(value: object) -> str:
    """Consolidate free-text gender responses without inferring unknown identities."""
    if pd.isna(value):
        return "Other / self-described"
    raw = str(value).strip()
    key = raw.lower()
    if key in GENDER_MAP:
        return GENDER_MAP[key]
    if any(token in key for token in ("female", "woman", "femail")):
        return "Female"
    if any(token in key for token in ("male", "man", "guy")) and not any(
        token in key for token in ("female", "woman")
    ):
        return "Male"
    return "Other / self-described"


def load_data(path_or_buffer: str | Path | object) -> pd.DataFrame:
    """Load the survey CSV and validate the minimum expected schema."""
    df = pd.read_csv(path_or_buffer)
    required = {"Age", "Gender", "Country", "treatment", "family_history"}
    missing = required.difference(df.columns)
    if missing:
        raise ValueError(f"Missing required columns: {', '.join(sorted(missing))}")
    return df


def clean_data(raw: pd.DataFrame) -> pd.DataFrame:
    """Return an analysis-ready copy while retaining the source columns."""
    df = raw.copy()
    df.columns = df.columns.str.strip()
    df["Timestamp"] = pd.to_datetime(df["Timestamp"], errors="coerce")
    df["Age"] = pd.to_numeric(df["Age"], errors="coerce")
    df.loc[~df["Age"].between(18, 75), "Age"] = np.nan
    df["Gender_clean"] = df["Gender"].map(normalize_gender)
    df["self_employed"] = df["self_employed"].fillna("Unknown")
    df["work_interfere"] = df["work_interfere"].fillna("Not reported")
    df["state"] = df["state"].fillna("Not applicable / missing")
    df["comments"] = df["comments"].fillna("")

    score_parts = pd.DataFrame(index=df.index)
    for column, mapping in SUPPORT_MAPS.items():
        score_parts[column] = df[column].map(mapping)
    df["support_index"] = (score_parts.mean(axis=1) * 100).round(1)
    df["support_band"] = pd.cut(
        df["support_index"], bins=[-0.1, 39.9, 69.9, 100],
        labels=["Low", "Moderate", "High"]
    )
    df["age_group"] = pd.cut(
        df["Age"], bins=[17, 24, 34, 44, 54, 75],
        labels=["18–24", "25–34", "35–44", "45–54", "55–75"]
    )
    return df


def pct(series: pd.Series, value: object = "Yes") -> float:
    """Percentage of non-null values equal to the chosen response."""
    valid = series.dropna()
    return float(valid.eq(value).mean() * 100) if len(valid) else 0.0


def treatment_rate_table(df: pd.DataFrame, column: str, min_count: int = 10) -> pd.DataFrame:
    """Treatment-seeking rate and sample size by a categorical dimension."""
    out = (
        df.dropna(subset=[column, "treatment"])
        .groupby(column, observed=True)["treatment"]
        .agg(responses="size", treatment_rate=lambda s: s.eq("Yes").mean() * 100)
        .reset_index()
    )
    return out.loc[out["responses"] >= min_count].sort_values("treatment_rate", ascending=False)


def cramers_v(x: pd.Series, y: pd.Series) -> float:
    """Bias-corrected Cramér's V for two categorical variables."""
    from scipy.stats import chi2_contingency
    table = pd.crosstab(x, y)
    if min(table.shape) < 2 or table.to_numpy().sum() == 0:
        return 0.0
    chi2 = chi2_contingency(table, correction=False)[0]
    n = table.to_numpy().sum()
    phi2 = chi2 / n
    r, k = table.shape
    phi2corr = max(0, phi2 - ((k - 1) * (r - 1)) / max(n - 1, 1))
    rcorr = r - ((r - 1) ** 2) / max(n - 1, 1)
    kcorr = k - ((k - 1) ** 2) / max(n - 1, 1)
    denom = min(kcorr - 1, rcorr - 1)
    return float(np.sqrt(phi2corr / denom)) if denom > 0 else 0.0

