import pandas as pd
import numpy as np
import dash
from dash import dcc, html, Input, Output, dash_table
import plotly.express as px

df = pd.read_csv("mercedes_benz_sales_2020_2025.csv")


app = dash.Dash(__name__)

app.layout = (
    html.Div([
        html.H1("Mercedes-Benz Global Sales 2020-2025", style={"textAlign": "center"}),

    html.Div([
        html.Label("Select Model:"),
        dcc.Dropdown(
            options=[{"label":model, "value":model} for model in df["Model"].unique()],
            value="A-Class",
            id="model-dropdown"
        )
    ], style={"width": "30%", "display": "inline-block"}),


        html.Div([
            html.Label("Select Fuel Type:"),
            dcc.Dropdown(
                options=[{"label": f, "value": f} for f in df["Fuel Type"].unique()],
                multi=True,
                placeholder="Select fuel types...",
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
            placeholder="Select a price range...",
            id="price-range-dropdown",
        ),
    ], style={"width": "30%", "display": "block", "marginLeft": "35%", "marginTop": "10px"}),

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
