# test_pipeline.py
from metrics import recommend_funds

print("=" * 60)
print("TESTING FULL PIPELINE — ALL 3 RISK LEVELS")
print("=" * 60)

for risk in ["low", "medium", "high"]:
    print(f"\n{'─' * 60}")
    print(f"Test: {risk.upper()} risk user")
    print(f"{'─' * 60}")

    results = recommend_funds(risk_level=risk, top_n=3)

    if not results.empty:
        print(f"\nTop 3 funds:")
        print(results[["fund_name", "cagr_%", "volatility_%", "sharpe_ratio", "category"]].to_string(index=False))
    else:
        print("No results returned.")

print("\n" + "=" * 60)
print("ALL TESTS DONE")
print("=" * 60)