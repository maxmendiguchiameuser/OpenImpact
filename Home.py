import streamlit as st
import xarray as xr
import pandas as pd
import pydeck as pdk
import numpy as np

st.set_page_config(
    page_title="Flight Climate Impact Dashboard",
    layout="wide",
)

st.markdown("### Climate sensitivity [algorithmic climate change functions]")

# Load NetCDF data
nc_file = "data/env_processed.nc"
ds = xr.open_dataset(nc_file)

# Select the first aCCF variable available
accf_vars = [var for var in ds.data_vars if var.startswith("aCCF")]
if not accf_vars:
    st.warning("No aCCF variables found in the dataset.")
    st.stop()

selected_var = accf_vars[0]

# Extract first level if 'level' is present
if "level" in ds.dims:
    var_data = ds[selected_var].isel(level=0)
else:
    var_data = ds[selected_var]

# Flatten to DataFrame
df = var_data.to_dataframe().reset_index()
df = df.dropna(subset=[selected_var])

# Rename for PyDeck
df = df.rename(columns={"longitude": "Longitude", "latitude": "Latitude", selected_var: "Value"})

# Normalize values for better grid visibility
df["Value"] = (df["Value"] - df["Value"].min()) / (df["Value"].max() - df["Value"].min())

# Display map
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
