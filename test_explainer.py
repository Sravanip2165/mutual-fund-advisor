# test_explainer.py
from metrics import recommend_funds
from explainer import explain_recommendations, explain_tradeoffs

print("=" * 60)
print("TESTING LLM EXPLANATION LAYER")
print("=" * 60)

# simulate user input
amount     = 500000  # ₹5 lakhs
risk_level = "medium"

print(f"\nUser: ₹{amount:,.0f} | Risk: {risk_level}")
print("-" * 60)

# Step 1 — get real recommendations
print("\nStep 1: Getting fund recommendations...")
results = recommend_funds(risk_level=risk_level, top_n=3)

if results.empty:
    print("No results. Check metrics.py")
else:
    print("\nTop 3 funds:")
    print(results[["fund_name", "cagr_%", "volatility_%", "sharpe_ratio"]].to_string(index=False))

    # Step 2 — get LLM explanation
    print("\nStep 2: Generating explanation...")
    explanation = explain_recommendations(results, risk_level, amount,age=65)
    print("\n--- EXPLANATION ---")
    print(explanation)

    # Step 3 — get trade-off explanation
    print("\nStep 3: Generating trade-off analysis...")
    tradeoffs = explain_tradeoffs(results,age=65)
    print("\n--- TRADE-OFFS ---")
    print(tradeoffs)

print("\n" + "=" * 60)
print("TEST DONE")
print("=" * 60)