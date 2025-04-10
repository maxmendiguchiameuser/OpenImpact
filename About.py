import streamlit as st
import xarray as xr
import pandas as pd
import numpy as np
import pydeck as pdk
import os

# Streamlit page setup
st.set_page_config(page_title="aCCF Map Viewer", layout="wide")
st.title("Flight Climate Impact Dashboard")
st.markdown("#### Visualize atmospheric climate sensitivity data (aCCFs) from NetCDF")

# Debug: Show working directory and files
st.markdown("### Debug Info")
st.text(f"Working directory: {os.getcwd()}")
st.text(f"Files in './data': {os.listdir('./data') if os.path.exists('./data') else 'data folder not found'}")

# Load NetCDF
nc_file = "/mount/src/openimpact/data/env_processed_compressed.nc"

@st.cache_data
def load_dataset(path):
    return xr.open_dataset(path)

try:
    ds = load_dataset(nc_file)
except FileNotFoundError:
    st.error(f"NetCDF file not found at: {nc_file}")
    st.stop()

# Select aCCF variable
accf_vars = [v for v in ds.data_vars if v.startswith("aCCF")]
if not accf_vars:
    st.error("No variables starting with 'aCCF' found in dataset.")
    st.stop()

selected_var = st.selectbox("Select aCCF variable", accf_vars)

# Select vertical level
if "level" not in ds:
    st.error("No 'level' dimension found in dataset.")
    st.stop()

levels = ds["level"].values
selected_level = st.selectbox("Select vertical level", levels)
var_data = ds[selected_var].sel(level=selected_level)

# Convert to DataFrame
df = var_data.to_dataframe().reset_index()
df = df.dropna(subset=[selected_var])

df = df.rename(columns={
    "latitude": "Latitude",
    "longitude": "Longitude",
    selected_var: "Value"
})

# Normalize Value column
df["Value"] = (df["Value"] - df["Value"].min()) / (df["Value"].max() - df["Value"].min())

# Show preview and value stats
st.markdown("### Sample of Transformed DataFrame")
st.dataframe(df.head())

st.markdown("### Value Distribution")
st.write(df["Value"].describe())

# Heatmap controls
st.markdown("### Heatmap Settings")
radius = st.slider("Heatmap radius (pixels)", 10, 100, 30)
aggregation = st.selectbox("Aggregation method", ["SUM", "MEAN"])

# Define HeatmapLayer
layer = pdk.Layer(
    "HeatmapLayer",
    data=df,
    get_position=["Longitude", "Latitude"],
    get_weight="Value",
    radiusPixels=radius,
    aggregation=aggregation
)

# Define tooltip as dictionary (NOT a class)
tooltip = {
    "text": "Lat: {Latitude}\nLon: {Longitude}\nValue: {Value:.2f}"
}

# Create and render deck
view_state = pdk.ViewState(
    latitude=df["Latitude"].mean(),
    longitude=df["Longitude"].mean(),
    zoom=3,
    pitch=0
)

deck = pdk.Deck(
    layers=[layer],
    initial_view_state=view_state,
    map_style="mapbox://styles/mapbox/dark-v10",
    tooltip=tooltip
)

st.markdown("### aCCF Heatmap")
st.pydeck_chart(deck)
