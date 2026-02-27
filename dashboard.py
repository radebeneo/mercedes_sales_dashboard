import pandas as pd
import numpy as np
import dash
from dash import dcc, html, Input, Output, dash_table
import plotly.express as px

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

df = pd.read_parquet("mercedes_benz_sales_2020_2025.parquet", dtype={
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



app = dash.Dash(__name__)

app.layout = (
    html.Div([
        html.H1("Mercedes-Benz Global Sales 2020-2025", style={"textAlign": "center"}),

    html.Div([
        html.Label("Select Model:"),
        dcc.Dropdown(
            options=[{"label":model, "value":model} for model in df["Model"].unique()],
            multi=True,
            id="model-dropdown",

        )
    ], style={"width": "30%", "display": "inline-block"}),


    html.Div([
            html.Label("Select Fuel Type:"),
            dcc.Dropdown(
                options=[{"label": fuel, "value": fuel} for fuel in df["Fuel Type"].unique()],
                multi=True,

                id="fuel-dropdown",
            ),
    ], style={"width": "30%", "display": "inline-block", "marginLeft": "5%"}),

    html.Div([
        html.Label("Select Price Range:"),
        dcc.Dropdown(
            options=[
                {"label": "30000 - 50000", "value": "30000-50000"},
                {"label": "50000 - 70000", "value": "50000-70000"},
                {"label": "70000 - 100000", "value": "70000-100000"},
                {"label": "100000 - 150000", "value": "100000-150000"},
                {"label": "150000 - 200000", "value": "150000-200000"},
                {"label": "200000+", "value": "200000-999999"}
            ],

            multi=True,
            id="price-range-dropdown",
        ),
    ], style={"width": "30%", "display": "inline-block", "marginLeft": "5%"}),

    html.H2("Sales Trends over Time"),
    dcc.Graph(id="sales-line-chart"),

    html.H2("Model Popularity"),
    dcc.Graph(id="models-bar-chart"),

    html.H2("Market Share by Fuel Type"),
    dcc.Graph(id="fuel-share-pie-chart"),

    html.H2("Price Distribution"),
    dcc.Graph(id="price-histogram"),

    html.H2("Performance vs. Price"),
    dcc.Graph(id="price-vs-performance-scatterplot"),

    html.H2("Colour Preferences"),
    dcc.Graph(id="colour-treemap"),

    html.H2("Filtered Data Table"),
    dash_table.DataTable(
        id="datatable-output",
        columns=[{"name":i, "id":i} for i in df.columns],
        page_size=10,
        style_table={"overflowX": "auto"},
        style_cell={"textAlign": "left"}
    )
]))




@app.callback(
    [Output("sales-line-chart", "figure"),
     Output("models-bar-chart", "figure"),
     Output("fuel-share-pie-chart", "figure"),
     Output("price-histogram", "figure"),
     Output("price-vs-performance-scatterplot", "figure"),
     Output("colour-treemap", "figure"),
     Output("datatable-output", "data")],
    [Input("model-dropdown", "value"),
     Input("fuel-dropdown", "value"),
     Input("price-range-dropdown", "value")]
)
def update_dashboard(selected_models, selected_fuels, price_range):
    mask = pd.Series(True, index=df.index)

    if selected_models:
        mask &= df["Model"].isin(selected_models)

    if selected_fuels:
        mask &= df["Fuel Type"].isin(selected_fuels)

    if price_range:
        price_mask = pd.Series(False, index=df.index)
        for pr in price_range:
            min_p, max_p = map(int, pr.split("-"))
            price_mask |= (df["Base Price (USD)"] >= min_p) & (df["Base Price (USD)"] <= max_p)
        mask &= price_mask

    filtered_df = df[mask]

    # 1. Sales Trends over Time
    # Aggregate first, then plot
    sales_trend = filtered_df.groupby(["Year", "Fuel Type"], observed=True)["Sales Volume"].sum().reset_index()
    fig1 = px.line(sales_trend, x="Year", y="Sales Volume", color="Fuel Type", title="Total Sales Volume over Years by Fuel Type")

    # 2. Model Popularity
    model_popularity = filtered_df.groupby(["Model", "Fuel Type"], observed=True)["Sales Volume"].sum().reset_index().sort_values("Sales Volume", ascending=False)
    fig2 = px.bar(model_popularity, x="Model", y="Sales Volume", color="Fuel Type", barmode="group", title="Sales Volume by Model and Fuel Type")

    # 3. Market Share by Fuel Type
    fuel_share = filtered_df.groupby("Fuel Type", observed=True)["Sales Volume"].sum().reset_index()
    fig3 = px.pie(fuel_share, values="Sales Volume", names="Fuel Type", title="Market Share by Fuel Type")

    # 4. Price Distribution
    # Histogram on large data can be slow, but let's keep it for now as px.histogram is usually okay if not too many points.
    # Actually, for 12M points, it might be slow.
    fig4 = px.histogram(filtered_df, x="Base Price (USD)", nbins=20, title="Distribution of Base Prices")

    # 5. Performance vs. Price
    # Scatter plot with millions of points will CRASH the browser.
    # We MUST sample this for visualization.
    if len(filtered_df) > 5000:
        scatter_df = filtered_df.sample(5000)
    else:
        scatter_df = filtered_df
    fig5 = px.scatter(scatter_df, x="Base Price (USD)", y="Horsepower", color="Fuel Type", hover_name="Model", title="Price vs. Horsepower (Sampled 5k points)")

    # 6. Colour Preferences
    color_pref = filtered_df.groupby(["Color", "Model"], observed=True)["Sales Volume"].sum().reset_index()
    
    # Plotly Express treemap can fail with non-ordered categorical data when performing internal aggregations.
    # We convert the categorical columns to string to avoid TypeError: Cannot perform max with non-ordered Categorical
    color_pref["Color"] = color_pref["Color"].astype(str)
    color_pref["Model"] = color_pref["Model"].astype(str)

    color_map = {
        "Yellow": "yellow",
        "Black": "black",
        "Grey": "grey",
        "White": "white",
        "Silver": "silver",
        "Brown": "brown",
        "Blue": "blue",
        "Red": "red",
        "Green": "green",
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

    # DataTable - LIMIT TO 1000 ROWS
    table_data = filtered_df.head(1000).to_dict("records")

    return fig1, fig2, fig3, fig4, fig5, fig6, table_data


server = app.server

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8050, debug=False)
