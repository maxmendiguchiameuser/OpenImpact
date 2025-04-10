import streamlit as st
import xarray as xr
import pandas as pd
import pydeck as pdk
import numpy as np

# Streamlit page setup
st.set_page_config(
    page_title="Flight Climate Impact Dashboard",
    layout="wide",
)

st.markdown("### Climate sensitivity [algorithmic climate change functions]")

# Path to NetCDF file
nc_file = "data/env_processed.nc"

# Load dataset
ds = xr.open_dataset(nc_file)

# Select aCCF variables
accf_vars = [var for var in ds.data_vars if var.startswith("aCCF")]
selected_var = st.selectbox("Select aCCF variable", accf_vars)

# Handle pressure level selection
if "level" in ds.dims:
    pressure_levels = ds["level"].values
    selected_level = st.selectbox("Select pressure level (hPa)", pressure_levels)
    var_data = ds[selected_var].sel(level=selected_level)
else:
    st.warning("No 'level' dimension found in this dataset.")
    var_data = ds[selected_var]

# Convert to DataFrame
df = var_data.to_dataframe().reset_index()
df = df.dropna(subset=[selected_var])

# Rename for PyDeck compatibility
df = df.rename(columns={
    "longitude": "Longitude",
    "latitude": "Latitude",
    selected_var: "Value"
})

# Keep only needed columns and ensure types are serializable
df = df[["Longitude", "Latitude", "Value"]].astype({
    "Longitude": float,
    "Latitude": float,
    "Value": float
})

# Normalize value to [0, 1]
val_min, val_max = df["Value"].min(), df["Value"].max()
df["Value"] = (df["Value"] - val_min) / (val_max - val_min + 1e-10)  # avoid div by zero

# Create pydeck chart
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
