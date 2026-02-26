import streamlit as st
import pandas as pd
import plotly.express as px

# ---------------------------------------------------
# Page Config
# ---------------------------------------------------
st.set_page_config(
    page_title="Mercedes-Benz Global Sales Dashboard",
    layout="wide"
)

# ---------------------------------------------------
# Load Data (Cached)
# ---------------------------------------------------
@st.cache_data
def load_data():
    return pd.read_csv(
        "mercedes_benz_sales_2020_2025.csv",
        dtype={
            "Model": "category",
            "Region": "category",
            "Color": "category",
            "Fuel Type": "category",
            "Turbo": "category",
            "Year": "int16",
            "Base Price (USD)": "int32",
            "Horsepower": "int16",
            "Sales Volume": "int32"
        }
    )

df = load_data()

st.title("Mercedes-Benz Global Sales 2020-2025")

# ---------------------------------------------------
# Sidebar Filters
# ---------------------------------------------------
st.sidebar.header("Filters")

selected_models = st.sidebar.multiselect(
    "Select Model:",
    options=sorted(df["Model"].unique())
)

selected_fuels = st.sidebar.multiselect(
    "Select Fuel Type:",
    options=sorted(df["Fuel Type"].unique())
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
    options=[label for label, _ in price_range_options]
)

run_dashboard = st.sidebar.button("Apply Filters")

# ---------------------------------------------------
# Cached Computation Functions
# ---------------------------------------------------
@st.cache_data
def compute_sales_trend(data):
    return data.groupby(
        ["Year", "Fuel Type"], observed=True
    )["Sales Volume"].sum().reset_index()

@st.cache_data
def compute_fuel_share(data):
    return data.groupby(
        "Fuel Type", observed=True
    )["Sales Volume"].sum().reset_index()

@st.cache_data
def compute_model_popularity(data):
    return (
        data.groupby(
            ["Model", "Fuel Type"], observed=True
        )["Sales Volume"]
        .sum()
        .reset_index()
        .sort_values("Sales Volume", ascending=False)
    )

@st.cache_data
def compute_color_pref(data):
    result = data.groupby(
        ["Color", "Model"], observed=True
    )["Sales Volume"].sum().reset_index()

    result["Color"] = result["Color"].astype(str)
    result["Model"] = result["Model"].astype(str)
    return result


# ---------------------------------------------------
# Run Dashboard Only When Button Clicked
# ---------------------------------------------------
if run_dashboard:

    # -----------------------------
    # Apply Simplified Filtering
    # -----------------------------
    filtered_df = df.copy()

    if selected_models:
        filtered_df = filtered_df[
            filtered_df["Model"].isin(selected_models)
        ]

    if selected_fuels:
        filtered_df = filtered_df[
            filtered_df["Fuel Type"].isin(selected_fuels)
        ]

    if selected_price_labels:
        selected_ranges = [
            val for label, val in price_range_options
            if label in selected_price_labels
        ]

        price_mask = False
        for min_p, max_p in selected_ranges:
            price_mask |= (
                (filtered_df["Base Price (USD)"] >= min_p) &
                (filtered_df["Base Price (USD)"] <= max_p)
            )

        filtered_df = filtered_df[price_mask]

    # ---------------------------------------------------
    # Compute Cached Aggregations
    # ---------------------------------------------------
    sales_trend = compute_sales_trend(filtered_df)
    fuel_share = compute_fuel_share(filtered_df)
    model_popularity = compute_model_popularity(filtered_df)
    color_pref = compute_color_pref(filtered_df)

    # ---------------------------------------------------
    # Layout
    # ---------------------------------------------------
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Sales Trends over Time")
        fig1 = px.line(
            sales_trend,
            x="Year",
            y="Sales Volume",
            color="Fuel Type",
            title="Total Sales Volume over Years by Fuel Type"
        )
        st.plotly_chart(fig1, use_container_width=True, theme="streamlit")

        st.subheader("Market Share by Fuel Type")
        fig3 = px.pie(
            fuel_share,
            values="Sales Volume",
            names="Fuel Type",
            title="Market Share by Fuel Type"
        )
        st.plotly_chart(fig3, use_container_width=True, theme="streamlit")

    with col2:
        st.subheader("Model Popularity")
        fig2 = px.bar(
            model_popularity,
            x="Model",
            y="Sales Volume",
            color="Fuel Type",
            barmode="group",
            title="Sales Volume by Model and Fuel Type"
        )
        st.plotly_chart(fig2, use_container_width=True, theme="streamlit")

        st.subheader("Price Distribution")
        fig4 = px.histogram(
            filtered_df,
            x="Base Price (USD)",
            nbins=20,
            title="Distribution of Base Prices"
        )
        st.plotly_chart(fig4, use_container_width=True, theme="streamlit")

    # ---------------------------------------------------
    # Scatter Plot (Sampled)
    # ---------------------------------------------------
    st.subheader("Performance vs. Price")

    scatter_df = (
        filtered_df.sample(5000)
        if len(filtered_df) > 5000
        else filtered_df
    )

    fig5 = px.scatter(
        scatter_df,
        x="Base Price (USD)",
        y="Horsepower",
        color="Fuel Type",
        hover_name="Model",
        title="Price vs. Horsepower (Sampled 5k points)"
    )

    st.plotly_chart(fig5, use_container_width=True, theme="streamlit")

    # ---------------------------------------------------
    # Colour Preferences
    # ---------------------------------------------------
    st.subheader("Colour Preferences")

    color_map = {
        "Yellow": "yellow", "Black": "black", "Grey": "grey",
        "White": "white", "Silver": "silver", "Brown": "brown",
        "Blue": "blue", "Red": "red", "Green": "green",
        "Orange": "orange"
    }

    fig6 = px.treemap(
        color_pref,
        path=["Color", "Model"],
        values="Sales Volume",
        color="Color",
        color_discrete_map=color_map,
        title="Colour Preferences by Model"
    )

    st.plotly_chart(fig6, use_container_width=True, theme="streamlit")

    # ---------------------------------------------------
    # Data Table
    # ---------------------------------------------------
    st.subheader("Filtered Data Table (Top 1000 rows)")
    st.dataframe(filtered_df.head(1000), use_container_width=True)

else:
    st.info("Select filters and click **Apply Filters** to run the dashboard.")