import pandas as pd
import plotly.express as px

# Minimal reproduction based on dashboard.py logic
df = pd.DataFrame({
    "Color": ["Red", "Red", "Blue", "Blue"],
    "Model": ["A", "B", "A", "C"],
    "Sales Volume": [10, 20, 30, 40]
})

# Convert to non-ordered Categorical as done in dashboard.py
df["Color"] = df["Color"].astype("category")
df["Model"] = df["Model"].astype("category")

# Fix: Convert categorical columns used in path to string
df["Color"] = df["Color"].astype(str)
df["Model"] = df["Model"].astype(str)

color_map = {
    "Red": "red",
    "Blue": "blue"
}

try:
    fig6 = px.treemap(
        df, 
        path=["Color", "Model"], 
        values="Sales Volume", 
        color="Color",
        color_discrete_map=color_map
    )
    print("Treemap created successfully")
except Exception as e:
    import traceback
    traceback.print_exc()
