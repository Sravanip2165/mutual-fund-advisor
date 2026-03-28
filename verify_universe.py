# verify_universe.py
import pandas as pd

df = pd.read_csv("fund_universe.csv")

print(f"Total funds: {len(df)}")
print(f"Columns: {list(df.columns)}")
print(f"\nNull values:\n{df.isnull().sum()}")
print(f"\nCategories:\n{df['category'].value_counts()}")
print(f"\nRisk levels:\n{df['risk'].value_counts()}")

# check sample from each category
print("\n--- Sample from each category ---")
for cat in df["category"].unique():
    sample = df[df["category"] == cat].iloc[0]
    print(f"\n{cat}: {sample['fund_name']}")
    print(f"  Risk: {sample['risk']} | NAV: {sample['latest_nav']}")

    