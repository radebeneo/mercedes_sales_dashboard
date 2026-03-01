import streamlit as st
import pandas as pd
import plotly.express as px

# --- Page Config ---
st.set_page_config(page_title="Mercedes-Benz Sales Dashboard", layout="wide")


# --- Data Loading (Cached) ---
@st.cache_data
def load_data():
    use_cols = ["Model", "Fuel Type", "Base Price (USD)", "Year", "Sales Volume", "Horsepower", "Color", "Turbo"]
    dtypes = {
        "Model": "category",
        "Fuel Type": "category",
        "Color": "category",
        "Turbo": "category",
        "Base Price (USD)": "int32",
        "Year": "int16",
        "Sales Volume": "int32",
        "Horsepower": "int16",
    }

    # Ensure the parquet file is in the same directory
    df = pd.read_parquet("mercedes_lean.parquet", columns=use_cols, engine='pyarrow')

    for col, dtype in dtypes.items():
        df[col] = df[col].astype(dtype)

    # Numeric downcasting
    df["Sales Volume"] = pd.to_numeric(df["Sales Volume"], downcast="integer")
    df["Year"] = pd.to_numeric(df["Year"], downcast="integer")
    df["Base Price (USD)"] = pd.to_numeric(df["Base Price (USD)"], downcast="integer")
    df["Horsepower"] = pd.to_numeric(df["Horsepower"], downcast="integer")

    return df


df = load_data()

# --- Sidebar / Filters ---
st.sidebar.header("Filter Options")

selected_models = st.sidebar.multiselect(
    "Select Model:", options=sorted(df["Model"].unique())
)

selected_fuels = st.sidebar.multiselect(
    "Select Fuel Type:", options=sorted(df["Fuel Type"].unique())
)

price_options = {
    "30k - 50k": (30000, 50000),
    "50k - 70k": (50000, 70000),
    "70k - 100k": (70000, 100000),
    "100k - 150k": (100000, 150000),
    "150k - 200k": (150000, 200000),
    "200k+": (200000, 999999)
}
selected_price_ranges = st.sidebar.multiselect(
    "Select Price Range:", options=list(price_options.keys())
)

# --- Filter Logic ---
filtered_df = df.copy()

if selected_models:
    filtered_df = filtered_df[filtered_df["Model"].isin(selected_models)]

if selected_fuels:
    filtered_df = filtered_df[filtered_df["Fuel Type"].isin(selected_fuels)]

if selected_price_ranges:
    price_masks = []
    for pr in selected_price_ranges:
        low, high = price_options[pr]
        price_masks.append((filtered_df["Base Price (USD)"] >= low) & (filtered_df["Base Price (USD)"] <= high))

    # Combine all price masks with OR
    if price_masks:
        final_price_mask = price_masks[0]
        for m in price_masks[1:]:
            final_price_mask |= m
        filtered_df = filtered_df[final_price_mask]

# --- Main UI ---
st.title("Mercedes-Benz Global Sales 2020-2025")
st.markdown("---")

# Row 1: Sales Trends & Popularity
col1, col2 = st.columns(2)

with col1:
    st.subheader("Sales Trends")
    sales_trend = filtered_df.groupby(["Year", "Fuel Type"], observed=True)["Sales Volume"].sum().reset_index()
    fig1 = px.line(sales_trend, x="Year", y="Sales Volume", color="Fuel Type", template="plotly")
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    st.subheader("Model Popularity")
    model_popularity = filtered_df.groupby(["Model", "Fuel Type"], observed=True)[
        "Sales Volume"].sum().reset_index().sort_values("Sales Volume", ascending=False)
    fig2 = px.bar(model_popularity, x="Model", y="Sales Volume", color="Fuel Type", barmode="group", template="plotly")
    st.plotly_chart(fig2, use_container_width=True)

# Row 2: Market Share & Price Distribution
col3, col4 = st.columns([1, 2])

with col3:
    st.subheader("Market Share")
    fuel_share = filtered_df.groupby("Fuel Type", observed=True)["Sales Volume"].sum().reset_index()
    fig3 = px.pie(fuel_share, values="Sales Volume", names="Fuel Type", template="plotly")
    st.plotly_chart(fig3, use_container_width=True)

with col4:
    st.subheader("Price Distribution")
    fig4 = px.histogram(filtered_df, x="Base Price (USD)", nbins=20, template="plotly" )
    st.plotly_chart(fig4, use_container_width=True)

# Row 3: Performance Scatter
st.subheader("Performance vs. Price")
# Sampling for performance
scatter_df = filtered_df.sample(min(len(filtered_df), 5000))
fig5 = px.scatter(scatter_df, x="Base Price (USD)", y="Horsepower", color="Fuel Type", hover_name="Model", template="plotly")
st.plotly_chart(fig5, use_container_width=True)

# Row 4: Treemap
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
    color_discrete_map=color_map, template="plotly"
)
st.plotly_chart(fig6, use_container_width=True)

# Assignment of Turbo and Non-Turbo Labels
filtered_df = filtered_df.assign(
        Engine_Type=filtered_df["Turbo"].map({
            "No": "Naturally Aspirated",
            "Yes": "Turbocharged"
        })
)

# Row 5: Turbo Analysis (Boxplot + Stacked Bar)
col5, col6 = st.columns(2)

with col5:
    st.subheader("Price Distribution: Turbocharged vs Naturally Aspirated")

    # Sampling for performance
    if len(filtered_df) > 5000:
        box_df = filtered_df.sample(5000)
    else:
        box_df = filtered_df

    fig7 = px.box(box_df, x="Engine_Type", y="Base Price (USD)", color="Engine_Type", template="plotly")
    fig7.update_layout(xaxis_title="Engine Type",legend_title_text="Engine Type")
    st.plotly_chart(fig7, use_container_width=True)


with col6:
    st.subheader("Total Sales Volume by Model & Engine Type")

    turbo_sales = (filtered_df.groupby(["Model", "Engine_Type"], observed=True)["Sales Volume"].sum().reset_index())
    fig8 = px.bar(turbo_sales, x="Model", y="Sales Volume", color="Engine_Type", barmode="stack", template="plotly")
    fig8.update_layout(legend_title_text="Engine Type", xaxis_title="Model")
    st.plotly_chart(fig8, use_container_width=True)

# Row 6: Turbo Adoption Over Time
st.subheader("Turbo Adoption Over Time")

turbo_year = (filtered_df.groupby(["Year", "Engine_Type"], observed=True)["Sales Volume"].sum().reset_index())
fig9 = px.area(turbo_year, x="Year", y="Sales Volume", color="Engine_Type", template="plotly")
fig9.update_layout(legend_title_text="Engine Type")
st.plotly_chart(fig9, use_container_width=True)


# Row 7: Data Table
st.subheader("Sample Data View")
st.dataframe(filtered_df.head(100), use_container_width=True)