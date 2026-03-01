import pandas as pd
import dash
from dash import dcc, html, Input, Output, State, dash_table
import dash_bootstrap_components as dbc
import plotly.express as px


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

df = pd.read_parquet("mercedes_lean.parquet", columns=use_cols, engine='pyarrow')

for col, dtype in dtypes.items():
    df[col] = df[col].astype(dtype)

df["Sales Volume"] = pd.to_numeric(df["Sales Volume"], downcast="integer")
df["Year"] = pd.to_numeric(df["Year"], downcast="integer")
df["Base Price (USD)"] = pd.to_numeric(df["Base Price (USD)"], downcast="integer")
df["Horsepower"] = pd.to_numeric(df["Horsepower"], downcast="integer")

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.SLATE])


# Helper function to create a graph inside a loading spinner
def loading_graph(id):
    return dcc.Loading(
        id=f"loading-{id}",
        type="circle",
        color="#00adef", # Mercedes-ish blue or silver
        children=[dcc.Graph(id=id)]
    )

app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(html.H1("Mercedes-Benz Global Sales 2020-2025",
        className="text-center my-4",
        style={"color": "#FFFFFF", "fontWeight": "bold"}), width=12),
    ]),


    dbc.Row([
        dbc.Col([
            html.Label("Select Model:"),
            dcc.Dropdown(
                options=[{"label": m, "value": m} for m in sorted(df["Model"].unique())],
                multi=True, id="model-dropdown", className="dash-bootstrap"
            )
        ], width=4),
        dbc.Col([
            html.Label("Select Fuel Type:"),
            dcc.Dropdown(
                options=[{"label": f, "value": f} for f in sorted(df["Fuel Type"].unique())],
                multi=True, id="fuel-dropdown", className="dash-bootstrap"
            )
        ], width=4),
        dbc.Col([
            html.Label("Select Price Range:"),
            dcc.Dropdown(
                options=[
                    {"label": "30k - 50k", "value": "30000-50000"},
                    {"label": "50k - 70k", "value": "50000-70000"},
                    {"label": "70k - 100k", "value": "70000-100000"},
                    {"label": "100k - 150k", "value": "100000-150000"},
                    {"label": "150k - 200k", "value": "150000-200000"},
                    {"label": "200k+", "value": "200000-999999"}
                ],
                multi=True, id="price-range-dropdown", className="dash-bootstrap"
            )
        ], width=4),
    ], className="mb-4"),


    dbc.Row([
        dbc.Col([html.H4("Sales Trends"), loading_graph("sales-line-chart")], width=6),
        dbc.Col([html.H4("Model Popularity"), loading_graph("models-bar-chart")], width=6),
    ]),

    dbc.Row([
        dbc.Col([html.H4("Market Share"), loading_graph("fuel-share-pie-chart")], width=4),
        dbc.Col([html.H4("Price Distribution"), loading_graph("price-histogram")], width=8),
    ], className="mt-4"),

    dbc.Row([
        dbc.Col([html.H4("Performance vs. Price"), loading_graph("price-vs-performance-scatterplot")], width=12),
    ], className="mt-4"),

    dbc.Row([
        dbc.Col([html.H4("Colour Preferences"), loading_graph("colour-treemap")], width=12),
    ], className="mt-4"),


    dbc.Row([
        dbc.Col([
            html.H4("Sample Data View"),
            dash_table.DataTable(
                id="datatable-output",
                columns=[{"name": i, "id": i} for i in df.columns],
                page_size=10,
                style_table={"overflowX": "auto"},
                style_header={'backgroundColor': '#2c3e50', 'color': 'white', 'fontWeight': 'bold'},
                style_cell={'backgroundColor': '#34495e', 'color': 'white', 'textAlign': 'left'}
            )
        ], width=12)
    ], className="my-5"),

    dbc.Row([
        dbc.Col([html.H4("Turbo vs Non-Turbo Price Distribution"),
                 loading_graph("turbo-boxplot")], width=6),
        dbc.Col([html.H4("Sales Volume by Model & Turbo"),
                 loading_graph("turbo-stacked-bar")], width=6),
    ], className="mt-4"),

    dbc.Row([
        dbc.Col([html.H4("Turbo Adoption Over Time (100% Stacked)"),
                 loading_graph("turbo-area-chart")], width=12),
    ], className="mt-4"),

], fluid=True)




@app.callback(
    [Output("sales-line-chart", "figure"),
     Output("models-bar-chart", "figure"),
     Output("fuel-share-pie-chart", "figure"),
     Output("price-histogram", "figure"),
     Output("price-vs-performance-scatterplot", "figure"),
     Output("colour-treemap", "figure"),
     Output("turbo-area-chart", "figure"),
     Output("turbo-stacked-bar", "figure"),
     Output("turbo-boxplot", "figure"),
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
    fig1 = px.line(sales_trend, x="Year", y="Sales Volume", color="Fuel Type", title="Total Sales Volume over Years by Fuel Type", template="plotly_dark")

    # 2. Model Popularity
    model_popularity = filtered_df.groupby(["Model", "Fuel Type"], observed=True)["Sales Volume"].sum().reset_index().sort_values("Sales Volume", ascending=False)
    fig2 = px.bar(model_popularity, x="Model", y="Sales Volume", color="Fuel Type", barmode="group", title="Sales Volume by Model and Fuel Type", template="plotly_dark")

    # 3. Market Share by Fuel Type
    fuel_share = filtered_df.groupby("Fuel Type", observed=True)["Sales Volume"].sum().reset_index()
    fig3 = px.pie(fuel_share, values="Sales Volume", names="Fuel Type", title="Market Share by Fuel Type", template="plotly_dark")

    # 4. Price Distribution
    # Histogram on large data can be slow, but let's keep it for now as px.histogram is usually okay if not too many points.
    # Actually, for 12M points, it might be slow.
    fig4 = px.histogram(filtered_df, x="Base Price (USD)", nbins=20, title="Distribution of Base Prices", template="plotly_dark")

    # 5. Performance vs. Price
    # Scatter plot with millions of points will CRASH the browser.
    # We MUST sample this for visualization.
    if len(filtered_df) > 5000:
        scatter_df = filtered_df.sample(5000)
    else:
        scatter_df = filtered_df
    fig5 = px.scatter(scatter_df, x="Base Price (USD)", y="Horsepower", color="Fuel Type", hover_name="Model", title="Price vs. Horsepower (Sampled 5k points)", template="plotly_dark")

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
        title="Colour Preferences by Model",
        template="plotly_dark"
    )

    # 7. Turbo Adoption Over Time
    turbo_year = (
        filtered_df
        .groupby(["Year", "Turbo"], observed=True)["Sales Volume"]
        .sum()
        .reset_index()
    )

    fig7 = px.area(
        turbo_year,
        x="Year",
        y="Sales Volume",
        color="Turbo",
        title="Turbo Adoption Over Time ",
        template="plotly_dark"
    )

    fig7.update_layout(yaxis_title="Total Sales Volume", xaxis_title="Year")

    # 8. Sales Volume by Model & Turbo
    turbo_sales = ( filtered_df.groupby(["Model", "Turbo"], observed=True)["Sales Volume"].sum().reset_index())

    fig8 = px.bar(
        turbo_sales,
        x="Model",
        y="Sales Volume",
        color="Turbo",
        barmode="stack",
        title="Total Sales Volume by Model & Turbo",
        template="plotly_dark"
    )

    # 9. Turbo vs. Non-Turbo Price Distribution

    # --- Turbo Boxplot (sample for performance) ---
    if len(filtered_df) > 100000:
        box_df = filtered_df.sample(100000)
    else:
        box_df = filtered_df

    fig9 = px.box(
        box_df,
        x="Turbo",
        y="Base Price (USD)",
        color="Turbo",
        title="Price Distribution: Turbocharged vs Naturally Aspirated",
        template="plotly_dark"
    )

    # DataTable - LIMIT TO 1000 ROWS
    table_data = filtered_df.head(1000).to_dict("records")

    return fig1, fig2, fig3, fig4, fig5, fig6, fig7, fig8, fig9, table_data


server = app.server

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8050, debug=False)
