# build_universe.py
# Fetches fund universe directly from AMFI — official government source

import requests
import pandas as pd
import io

def fetch_amfi_universe() -> pd.DataFrame:
    print("Fetching fund list directly from AMFI...")

    url = "https://www.amfiindia.com/spages/NAVAll.txt"
    
    try:
        resp = requests.get(url, timeout=30)
        resp.raise_for_status()
    except Exception as e:
        print(f"ERROR: {e}")
        return pd.DataFrame()

    lines = resp.text.strip().split("\n")

    funds = []
    current_category = ""

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # category headers look like: "Open Ended Schemes(Equity Scheme - Large Cap Fund)"
        if line.startswith("Open Ended") or line.startswith("Close Ended") or line.startswith("Interval"):
            current_category = line
            continue

        parts = line.split(";")
        if len(parts) >= 5:
            scheme_code = parts[0].strip()
            fund_name   = parts[3].strip()
            nav         = parts[4].strip()

            # only keep Direct Growth funds
            if "Direct" in fund_name and "Growth" in fund_name:
                funds.append({
                    "scheme_code": scheme_code,
                    "fund_name":   fund_name,
                    "latest_nav":  nav,
                    "amfi_category": current_category
                })

    df = pd.DataFrame(funds)
    print(f"Direct Growth funds found: {len(df)}")
    return df


# --- category mapping ---
CATEGORY_KEYWORDS = {
    "Large Cap":  ["large cap"],
    "Mid Cap":    ["mid cap"],
    "Small Cap":  ["small cap"],
    "Flexi Cap":  ["flexi cap", "multi cap"],
    "Liquid":     ["liquid"],
    "ELSS":       ["elss", "tax"],
    "Hybrid":     ["hybrid", "balanced", "aggressive"],
    "Debt":       ["debt", "short duration", "corporate bond"],
}

RISK_MAPPING = {
    "Large Cap":  "Low",
    "Liquid":     "Low",
    "Debt":       "Low",
    "Flexi Cap":  "Medium",
    "Hybrid":     "Medium",
    "ELSS":       "Medium",
    "Mid Cap":    "Medium",
    "Small Cap":  "High",
}

def assign_category(amfi_category: str) -> str:
    amfi_lower = amfi_category.lower()
    for category, keywords in CATEGORY_KEYWORDS.items():
        for kw in keywords:
            if kw in amfi_lower:
                return category
    return "Other"


# --- run ---
df = fetch_amfi_universe()

if df.empty:
    print("No data fetched.")
else:
    # assign our clean category
    df["category"] = df["amfi_category"].apply(assign_category)
    df["risk"]     = df["category"].map(RISK_MAPPING).fillna("Unknown")

    # drop uncategorized
    df = df[df["category"] != "Other"].reset_index(drop=True)

    # save full universe
    df.to_csv("fund_universe.csv", index=False)

    print(f"\nFund universe saved: {len(df)} funds")
    print("\nBreakdown by category:")
    print(df["category"].value_counts().to_string())
    print("\nBreakdown by risk:")
    print(df["risk"].value_counts().to_string())
    print("\nSample funds:")
    print(df[["fund_name", "category", "risk"]].head(10).to_string(index=False))