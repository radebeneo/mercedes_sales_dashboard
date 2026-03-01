import pandas as pd

#Converted a large csv file to parquet:

df = pd.read_csv("mercedes_benz_sales_2020_2025.csv")

df["Model"] = df["Model"].astype("category")
df["Region"] = df["Region"].astype("category")
df["Color"] = df["Color"].astype("category")
df["Fuel Type"] = df["Fuel Type"].astype("category")
df["Turbo"] = df["Turbo"].astype("category")
df["Year"] = df["Year"].astype("int16")
df["Base Price (USD)"] = df["Base Price (USD)"].astype("int32")
df["Horsepower"] = df["Horsepower"].astype("int16")
df["Sales Volume"] = df["Sales Volume"].astype("int32")

df.to_parquet("mercedes_benz_sales_2020_2025.parquet", index=False)