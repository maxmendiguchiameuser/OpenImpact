import streamlit as st
import xarray as xr
import pandas as pd
import pydeck as pdk
import numpy as np


st.set_page_config(
    page_title="Flight Climate Impact Dashboard",
    layout="wide",
)

st.markdown("### Climate sensitivity [algorithmic climate change functions")

# Load NetCDF data
nc_file = "data/env_processed_compressed.nc"
ds = xr.open_dataset(nc_file, engine="netcdf4")

import xarray as xr
import streamlit as st

# Load netCDF file
nc_file = "data/env_processed.nc"
ds = xr.open_dataset(nc_file)

# Select aCCF variables
accf_vars = [var for var in ds.data_vars if var.startswith("aCCF")]
selected_var = st.selectbox("Select aCCF variable", accf_vars)

# Get available pressure levels from 'lev' (in hPa)
if "lev" in ds.dims:
    pressure_levels = ds["lev"].values
    level_hpa = st.selectbox("Select pressure level (hPa)", pressure_levels)
    var_data = ds[selected_var].sel(lev=level_hpa)
else:
    st.warning("No 'lev' dimension found in this dataset.")
    var_data = ds[selected_var]
    
# Flatten to DataFrame
df = var_data.to_dataframe().reset_index()
df = df.dropna(subset=[selected_var])

# Rename for PyDeck
df = df.rename(columns={"lon": "Longitude", "lat": "Latitude", selected_var: "Value"})

# Normalize values for better grid visibility
df["Value"] = (df["Value"] - df["Value"].min()) / (df["Value"].max() - df["Value"].min())

# Set the map style and initial view
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
