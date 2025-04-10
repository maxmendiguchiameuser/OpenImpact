import streamlit as st
import xarray as xr
import pandas as pd
import numpy as np
import pydeck as pdk
import os

st.set_page_config(page_title="aCCF Map Viewer", layout="wide")
st.title("Flight Climate Impact Dashboard")
st.markdown("#### Visualize atmospheric climate sensitivity data (aCCFs) from NetCDF")

# Debug: File structure
st.markdown("### Debug Info")
st.text(f"Working directory: {os.getcwd()}")
st.text(f"Files in './data': {os.listdir('./data') if os.path.exists('./data') else 'data folder not found'}")

# Load NetCDF
nc_file = "/mount/src/openimpact/data/env_processed_compressed.nc"

@st.cache_data
def load_dataset(path):
    return xr.open_dataset(path)

ds = load_dataset(nc_file)

# Select variable
accf_vars = [v for v in ds.data_vars if v.startswith("aCCF")]
if not accf_vars:
    st.error("No aCCF variables found.")
    st.stop()

selected_var = st.selectbox("Select aCCF variable", accf_vars)

# Select vertical level
if "level" not in ds:
    st.error("No 'level' dimension found in dataset.")
    st.stop()

levels = ds["level"].values
selected_level = st.selectbox("Select vertical level", levels)
var_data = ds[selected_var].sel(level=selected_level)

# Transform to DataFrame
df = var_data.to_dataframe().reset_index()
df = df.dropna(subset=[selected_var])

df = df.rename(columns={
    "latitude": "Latitude",
    "longitude": "Longitude",
    selected_var: "Value"
})

# Normalize values for better visual contrast
df["Value"] = (df["Value"] - df["Value"].min()) / (df["Value"].max() - df["Value"].min())

# Show preview
st.markdown("### Sample of Transformed DataFrame")
st.dataframe(df.head())

# Show distribution
st.markdown("### Value Distribution")
st.write(df["Value"].describe())

# PyDeck Map
st.markdown("### Map Visualization")

view_state = pdk.ViewState(
    latitude=df["Latitude"].mean(),
    longitude=df["Longitude"].mean(),
    zoom=3,
    pitch=0
)

layer = pdk.Layer(
    "ScreenGridLayer",
    data=df,
    get_position=["Longitude", "Latitude"],
    get_weight="Value",
    pickable=True,
    cell_size_pixels=10,
    color_range=[
        [255, 255, 204],
        [161, 218, 180],
        [65, 182, 196],
        [44, 127, 184],
        [37, 52, 148]
    ]
)

tooltip = pdk.Tooltip(
    html="Lat: {Latitude} <br> Lon: {Longitude} <br> Value: {Value}",
    style={"backgroundColor": "steelblue", "color": "white"}
)

deck = pdk.Deck(
    layers=[layer],
    initial_view_state=view_state,
    map_style="mapbox://styles/mapbox/dark-v10",
    tooltip=tooltip
)

st.pydeck_chart(deck)
