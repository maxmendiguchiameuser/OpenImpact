import streamlit as st
import xarray as xr
import pandas as pd
import pydeck as pdk
import numpy as np
import os

st.set_page_config(
    page_title="Flight Climate Impact Dashboard",
    layout="wide",
)

st.markdown("### Climate sensitivity [algorithmic climate change functions")

# Debug file paths
st.markdown("### Debugging File Paths")
st.text(f"Current working directory: {os.getcwd()}")
st.text(f"Files in current directory: {os.listdir('.')}")
st.text(f"Files in 'data/' directory: {os.listdir('./data') if os.path.exists('./data') else 'data folder not found'}")

# Load NetCDF data
nc_file = "/mount/src/openimpact/data/env_processed_compressed.nc"
ds = xr.open_dataset(nc_file, engine="netcdf4")  # <- using correct engine

# Check required dimensions
required_coords = ['latitude', 'longitude', 'level']
for coord in required_coords:
    if coord not in ds.coords and coord not in ds.dims:
        st.error(f"Missing required coordinate/dimension: {coord}")
        st.stop()

# Filter variables starting with 'aCCF'
accf_vars = [var for var in ds.data_vars if var.startswith("aCCF")]
if not accf_vars:
    st.error("No variables starting with 'aCCF' found in dataset.")
    st.stop()

selected_var = st.selectbox("Select aCCF variable to visualize", accf_vars)

# Select first level
var_data = ds[selected_var].isel(level=0)

# Rename dimensions to standard names for consistency
var_data = var_data.rename({'latitude': 'lat', 'longitude': 'lon'})

# Flatten to DataFrame
df = var_data.to_dataframe().reset_index()
df = df.dropna(subset=[selected_var])

# Rename for PyDeck
df = df.rename(columns={"lon": "Longitude", "lat": "Latitude", selected_var: "Value"})

# Normalize values
df["Value"] = (df["Value"] - df["Value"].min()) / (df["Value"].max() - df["Value"].min())

# Display interactive map
st.pydeck_chart(pdk.Deck(
    map_style="mapbox://styles/mapbox/dark-v10",
    initial_view_state=pdk.ViewState(
        latitude=df["Latitude"].mean(),
        longitude=df["Longitude"].mean(),
        zoom=3,
        pitch=0,
    ),
    layers=[
        pdk.Layer(
            "ScreenGridLayer",
            data=df,
            pickable=True,
            cell_size_pixels=10,
            color_range=[
                [255, 255, 204],
                [161, 218, 180],
                [65, 182, 196],
                [44, 127, 184],
                [37, 52, 148]
            ],
            get_position="[Longitude, Latitude]",
            get_weight="Value",
        )
    ]
))
