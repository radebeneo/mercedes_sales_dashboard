import pandas as pd


df = pd.read_parquet("mercedes_benz_sales_2020_2025.parquet")

# Pre-calculate the sums for every possible combination our filters

summary_df = df.groupby(
    ["Year", "Model", "Fuel Type", "Color", "Base Price (USD)", "Horsepower"],
    observed=True
)["Sales Volume"].sum().reset_index()

# Save the lean version
summary_df.to_parquet("mercedes_lean.parquet", index=False)

print(f"Data shrunk from {len(df)} rows to {len(summary_df)} rows!")