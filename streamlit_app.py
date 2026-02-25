import streamlit as st
import pandas as pd
import plotly.express as px

# Set page configuration
st.set_page_config(page_title="Mercedes-Benz Global Sales Dashboard", layout="wide")

# Load data
@st.cache_data
def load_data():
    df = pd.read_csv("mercedes_benz_sales_2020_2025.csv", dtype={
        "Model": "category",
        "Region": "category",
        "Color": "category",
        "Fuel Type": "category",
        "Turbo": "category",
        "Year": "int16",
        "Base Price (USD)": "int32",
        "Horsepower": "int16",
        "Sales Volume": "int32"
    })
    return df

df = load_data()

st.title("Mercedes-Benz Global Sales 2020-2025")

# Sidebar filters
st.sidebar.header("Filters")

selected_models = st.sidebar.multiselect(
    "Select Model:",
    options=sorted(df["Model"].unique()),
    placeholder="Select model..."
)

selected_fuels = st.sidebar.multiselect(
    "Select Fuel Type:",
    options=sorted(df["Fuel Type"].unique()),
    placeholder="Select fuel types..."
)

price_range_options = [
    ("30000 - 50000", (30000, 50000)),
    ("50000 - 70000", (50000, 70000)),
    ("70000 - 100000", (70000, 100000)),
    ("100000 - 150000", (100000, 150000)),
    ("150000 - 200000", (150000, 200000)),
    ("200000+", (200000, 999999))
]

selected_price_labels = st.sidebar.multiselect(
    "Select Price Range:",
    options=[label for label, val in price_range_options],
    placeholder="Select a price range..."
)

# Apply filters
mask = pd.Series(True, index=df.index)

if selected_models:
    mask &= df["Model"].isin(selected_models)

if selected_fuels:
    mask &= df["Fuel Type"].isin(selected_fuels)

if selected_price_labels:
    price_mask = pd.Series(False, index=df.index)
    selected_ranges = [val for label, val in price_range_options if label in selected_price_labels]
    for min_p, max_p in selected_ranges:
        price_mask |= (df["Base Price (USD)"] >= min_p) & (df["Base Price (USD)"] <= max_p)
    mask &= price_mask

filtered_df = df[mask]

# Dashboard layout
col1, col2 = st.columns(2)

with col1:
    st.subheader("Sales Trends over Time")
    sales_trend = filtered_df.groupby(["Year", "Fuel Type"], observed=True)["Sales Volume"].sum().reset_index()
    fig1 = px.line(sales_trend, x="Year", y="Sales Volume", color="Fuel Type", title="Total Sales Volume over Years by Fuel Type")
    st.plotly_chart(fig1, use_container_width=True)

    st.subheader("Market Share by Fuel Type")
    fuel_share = filtered_df.groupby("Fuel Type", observed=True)["Sales Volume"].sum().reset_index()
    fig3 = px.pie(fuel_share, values="Sales Volume", names="Fuel Type", title="Market Share by Fuel Type")
    st.plotly_chart(fig3, use_container_width=True)

with col2:
    st.subheader("Model Popularity")
    model_popularity = filtered_df.groupby(["Model", "Fuel Type"], observed=True)["Sales Volume"].sum().reset_index().sort_values("Sales Volume", ascending=False)
    fig2 = px.bar(model_popularity, x="Model", y="Sales Volume", color="Fuel Type", barmode="group", title="Sales Volume by Model and Fuel Type")
    st.plotly_chart(fig2, use_container_width=True)

    st.subheader("Price Distribution")
    fig4 = px.histogram(filtered_df, x="Base Price (USD)", nbins=20, title="Distribution of Base Prices")
    st.plotly_chart(fig4, use_container_width=True)

st.subheader("Performance vs. Price")
if len(filtered_df) > 5000:
    scatter_df = filtered_df.sample(5000)
else:
    scatter_df = filtered_df
fig5 = px.scatter(scatter_df, x="Base Price (USD)", y="Horsepower", color="Fuel Type", hover_name="Model", title="Price vs. Horsepower (Sampled 5k points)")
st.plotly_chart(fig5, use_container_width=True)

st.subheader("Colour Preferences")
color_pref = filtered_df.groupby(["Color", "Model"], observed=True)["Sales Volume"].sum().reset_index()
color_pref["Color"] = color_pref["Color"].astype(str)
color_pref["Model"] = color_pref["Model"].astype(str)

color_map = {
    "Yellow": "yellow", "Black": "black", "Grey": "grey", "White": "white",
    "Silver": "silver", "Brown": "brown", "Blue": "blue", "Red": "red",
    "Green": "green", "Orange": "orange"
}
fig6 = px.treemap(
    color_pref, path=["Color", "Model"], values="Sales Volume", color="Color",
    color_discrete_map=color_map, title="Colour Preferences by Model"
)
st.plotly_chart(fig6, use_container_width=True)

st.subheader("Filtered Data Table (Top 1000 rows)")
st.dataframe(filtered_df.head(1000), use_container_width=True)
