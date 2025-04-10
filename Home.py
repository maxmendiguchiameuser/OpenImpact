st.set_page_config(
    page_title="Flight Climate Impact Dashboard",
    layout="wide",
)



st.markdown("### Climate sensitivity [algorithmic climate change functions")

import streamlit as st
import xarray as xr
import pandas as pd
import pydeck as pdk
import numpy as np

# Load NetCDF data
nc_file = "data/env_processed_compressed.nc"
ds = xr.open_dataset(nc_file)

# Filter variables starting with 'aCCF'
accf_vars = [var for var in ds.data_vars if var.startswith("aCCF")]
selected_var = st.selectbox("Select aCCF variable to visualize", accf_vars)

# Pick one altitude level (e.g., the surface or lowest level)
var_data = ds[selected_var].isel(lev=0)  # Choose first vertical level

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
