import streamlit as st
import xarray as xr
import pandas as pd
import pydeck as pdk
import numpy as np

# Streamlit page configuration
st.set_page_config(
    page_title="Flight Climate Impact Dashboard",
    layout="wide",
)

st.markdown("### Climate Sensitivity (Algorithmic Climate Change Functions)")

# Load NetCDF file
nc_file = "data/env_processed_compressed.nc"
try:
    ds = xr.open_dataset(nc_file)  # Use default engine for better compatibility
except Exception as e:
    st.error(f"Failed to open NetCDF file: {e}")
    st.stop()

# Filter for variables starting with 'aCCF'
accf_vars = [var for var in ds.data_vars if var.startswith("aCCF")]
if not accf_vars:
    st.warning("No aCCF variables found in the dataset.")
    st.stop()

# Variable selector
selected_var = st.selectbox("Select aCCF variable", accf_vars)

# Check if 'level' dimension exists for vertical selection
if "level" in ds.dims:
    pressure_levels = ds["level"].values
    selected_level = st.selectbox("Select pressure level (hPa)", pressure_levels)
    var_data = ds[selected_var].sel(level=selected_level)
else:
    st.warning("No 'level' dimension found in this dataset.")
    var_data = ds[selected_var]

# Convert to DataFrame and drop NaNs
df = var_data.to_dataframe().reset_index()
df = df.dropna(subset=[selected_var])

# Rename columns for pydeck
df = df.rename(columns={
    "longitude": "Longitude",
    "latitude": "Latitude",
    selected_var: "Value"
})

# Check required columns exist
if not all(col in df.columns for col in ["Longitude", "Latitude", "Value"]):
    st.error("Missing required columns in data.")
    st.stop()

# Ensure correct types
df = df.astype({"Longitude": float, "Latitude": float, "Value": float})

# Normalize value for color scaling
min_val = df["Value"].min()
max_val = df["Value"].max()
if max_val - min_val == 0:
    df["Value"] = 0  # Avoid division by zero
else:
    df["Value"] = (df["Value"] - min_val) / (max_val - min_val)

# PyDeck Map Plot
st.pydeck_chart(pdk.Deck(
    map_style="mapbox://styles/mapbox/dark-v10",
    initial_view_state=pdk.ViewState(
        latitude=float(df["Latitude"].mean()),
        longitude=float(df["Longitude"].mean()),
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
