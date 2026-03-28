# metrics.py
import requests
import pandas as pd
import numpy as np
import os
import json
from datetime import datetime, timedelta, date

RISK_FREE_RATE = 0.065
CACHE_FILE = "nav_cache.json"

# ─────────────────────────────────────────
# Cache helpers
# ─────────────────────────────────────────
def load_cache() -> dict:
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r") as f:
            return json.load(f)
    return {}

def save_cache(cache: dict):
    with open(CACHE_FILE, "w") as f:
        json.dump(cache, f)


# ─────────────────────────────────────────
# 1. Fetch NAV for a single fund on demand
# ─────────────────────────────────────────
def fetch_nav(scheme_code: str, years: int = 3) -> pd.DataFrame:
    url = f"https://api.mfapi.in/mf/{scheme_code}"
    try:
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
        data = resp.json()["data"]
    except Exception as e:
        print(f"  Could not fetch {scheme_code}: {e}")
        return pd.DataFrame()

    df = pd.DataFrame(data)
    df["date"] = pd.to_datetime(df["date"], format="%d-%m-%Y", errors="coerce")
    df["nav"]  = pd.to_numeric(df["nav"], errors="coerce")
    df = df.dropna().sort_values("date").reset_index(drop=True)

    cutoff = datetime.today() - timedelta(days=years * 365)
    return df[df["date"] >= cutoff]


# ─────────────────────────────────────────
# 2. Calculate CAGR
# ─────────────────────────────────────────
def calculate_cagr(df: pd.DataFrame, years: int = 3) -> float:
    if len(df) < 2:
        return None
    start_nav = df.iloc[0]["nav"]
    end_nav   = df.iloc[-1]["nav"]
    if start_nav <= 0:
        return None
    cagr = (end_nav / start_nav) ** (1 / years) - 1
    return round(cagr * 100, 2)


# ─────────────────────────────────────────
# 3. Calculate annualised volatility
# ─────────────────────────────────────────
def calculate_volatility(df: pd.DataFrame) -> float:
    if len(df) < 2:
        return None
    daily_returns = df["nav"].pct_change().dropna()
    volatility = daily_returns.std() * np.sqrt(252)
    return round(volatility * 100, 2)


# ─────────────────────────────────────────
# 4. Calculate Sharpe ratio
# ─────────────────────────────────────────
def calculate_sharpe(cagr: float, volatility: float) -> float:
    if volatility is None or volatility == 0 or cagr is None:
        return None
    sharpe = (cagr - (RISK_FREE_RATE * 100)) / volatility
    return round(sharpe, 4)


# ─────────────────────────────────────────
# 5. Full pipeline for one fund
# ─────────────────────────────────────────
def analyse_fund(scheme_code: str, fund_name: str) -> dict:
    df = fetch_nav(scheme_code)
    if df.empty:
        return None

    cagr       = calculate_cagr(df)
    volatility = calculate_volatility(df)
    sharpe     = calculate_sharpe(cagr, volatility)

    return {
        "fund_name":    fund_name,
        "scheme_code":  scheme_code,
        "cagr_%":       cagr,
        "volatility_%": volatility,
        "sharpe_ratio": sharpe,
        "data_points":  len(df),
        "start_date":   df.iloc[0]["date"].strftime("%Y-%m-%d"),
        "end_date":     df.iloc[-1]["date"].strftime("%Y-%m-%d"),
    }


# ─────────────────────────────────────────
# 6. Analyse with cache
# ─────────────────────────────────────────
def analyse_fund_cached(scheme_code: str, fund_name: str) -> dict:
    cache = load_cache()
    today = str(date.today())

    # return cached result if fetched today
    if scheme_code in cache and cache[scheme_code]["date"] == today:
        return cache[scheme_code]["result"]

    # otherwise fetch fresh and cache it
    result = analyse_fund(scheme_code, fund_name)

    if result:
        cache[scheme_code] = {"date": today, "result": result}
        save_cache(cache)

    return result


# ─────────────────────────────────────────
# 7. Main function — user gives risk level
# ─────────────────────────────────────────
RISK_TO_CATEGORY = {
    "low":    ["Large Cap", "Liquid", "Debt"],
    "medium": ["Flexi Cap", "Hybrid", "ELSS"],
    "high":   ["Mid Cap", "Small Cap"],
}

def recommend_funds(risk_level: str, top_n: int = 5) -> pd.DataFrame:
    risk_level = risk_level.lower().strip()

    if risk_level not in RISK_TO_CATEGORY:
        print("Invalid risk level. Choose: low / medium / high")
        return pd.DataFrame()

    universe   = pd.read_csv("fund_universe.csv")
    categories = RISK_TO_CATEGORY[risk_level]
    filtered   = universe[universe["category"].isin(categories)].reset_index(drop=True)

    print(f"\nRisk: {risk_level} | Categories: {categories}")
    print(f"Total funds in universe: {len(filtered)}")

    # take 20 funds per category — sample without groupby to avoid column drop
    sampled_list = []
    for cat in categories:
        cat_funds = filtered[filtered["category"] == cat]
        sample    = cat_funds.sample(min(len(cat_funds), 20), random_state=42)
        sampled_list.append(sample)

    sampled = pd.concat(sampled_list).reset_index(drop=True)

    print(f"Analysing sample of: {len(sampled)} funds")
    print(f"Fetching metrics (cached where possible)...\n")

    results = []
    for _, row in sampled.iterrows():
        result = analyse_fund_cached(str(row["scheme_code"]), row["fund_name"])
        if result:
            result["category"] = row["category"]
            results.append(result)

    if not results:
        print("No results.")
        return pd.DataFrame()

    df_results = pd.DataFrame(results)
    df_results = df_results.sort_values("sharpe_ratio", ascending=False)
    return df_results.head(top_n).reset_index(drop=True)