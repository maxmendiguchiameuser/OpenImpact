import streamlit as st
import xarray as xr
import pandas as pd
import numpy as np
import folium
from folium.plugins import HeatMap
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

# Heatmap settings
st.markdown("### Heatmap Settings")
radius = st.slider("Heatmap radius (pixels)", 10, 100, 30)

# Create a Folium map centered on the mean latitude and longitude
m = folium.Map(location=[df["Latitude"].mean(), df["Longitude"].mean()], zoom_start=3, control_scale=True)

# Create heatmap data
heat_data = [[row["Latitude"], row["Longitude"], row["Value"]] for index, row in df.iterrows()]

# Add HeatMap layer to the map
HeatMap(heat_data, radius=radius).add_to(m)

# Render the map in Streamlit
st.markdown("### aCCF Heatmap")
folium_static(m)
