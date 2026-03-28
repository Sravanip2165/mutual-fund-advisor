# explainer.py
import os
from dotenv import load_dotenv
from groq import Groq
import pandas as pd

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

def explain_recommendations(results: pd.DataFrame, risk_level: str, amount: float, age: int) -> str:
    fund_details = ""
    for i, row in results.iterrows():
        fund_details += f"""
Fund {i+1} - {row['fund_name']}:
  - Category: {row['category']}
  - CAGR: {row['cagr_%']}% (this is how much the fund grew per year on average)
  - Volatility: {row['volatility_%']}% (this is how much the fund value fluctuated)
  - Sharpe Ratio: {row['sharpe_ratio']} (this is the return earned per unit of risk taken)
"""

    prompt = f"""
You are explaining mutual fund results to a first-time investor in India.

The user is {age} years old and wants to invest ₹{amount:,.0f} with {risk_level} risk tolerance.

Our system calculated these metrics from 3 years of real NAV data:
{fund_details}

Write your explanation in this exact structure:

First, write 1 sentence about how the user's age of {age} relates to their ability to handle risk.
Use this logic:
- Age below 30: they have more time to recover from market ups and downs
- Age 30 to 50: they should balance growth and stability
- Age above 50: stability becomes more important than high growth
Do NOT recommend changing their risk level — just explain what their age means for investing.

Then for each fund, write exactly 2 sentences using the ACTUAL FUND NAME:
- Sentence 1: What the CAGR and Volatility numbers mean in plain English for that fund
- Sentence 2: What the Sharpe Ratio tells us about that fund

Rules:
- Use ONLY the numbers provided above
- Use simple words — imagine explaining to someone who has never invested before
- Do not repeat any sentence
- Do not use financial jargon
- Do not predict future returns
- End with exactly this line: "These recommendations are based on historical data only and not financial advice."

Example style (use actual fund names, not Fund 1 or Fund 2):
"Parag Parikh Conservative Hybrid Fund grew at 11.45% per year over the last 3 years, with very low fluctuation of 2.81% — meaning its value stayed fairly stable. Its Sharpe ratio of 1.76 means it gave good returns relative to the risk taken."
"""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=2048,
            temperature=0.3
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Explanation unavailable: {e}"


def explain_tradeoffs(results: pd.DataFrame, age: int) -> str:
    best_sharpe = results.iloc[0]
    best_cagr   = results.loc[results["cagr_%"].idxmax()]
    lowest_risk = results.loc[results["volatility_%"].idxmin()]

    prompt = f"""
Explain this trade-off to a first-time investor aged {age} in simple sentences using ONLY these numbers:

- {best_sharpe['fund_name']} gave the best balance of growth and stability
- {best_cagr['fund_name']} gave the highest growth of {best_cagr['cagr_%']}% per year but its value fluctuated by {best_cagr['volatility_%']}%
- {lowest_risk['fund_name']} was the most stable with only {lowest_risk['volatility_%']}% fluctuation but grew slower at {lowest_risk['cagr_%']}% per year

Rules:
- Write exactly 3 sentences — one for each fund above
- Use the ACTUAL FUND NAME in each sentence
- Explain the trade-off in plain English like talking to a friend
- No repeated sentences
- Do not predict future returns
"""

    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=500,
            temperature=0.3
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"Trade-off explanation unavailable: {e}"