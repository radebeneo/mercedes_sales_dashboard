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



]))
