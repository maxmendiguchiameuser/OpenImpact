import streamlit as st
import xarray as xr
import pydeck as pdk
import pandas as pd

st.set_page_config(page_title="Flight Climate Impact Dashboard", layout="wide")
st.markdown("### Climate sensitivity [algorithmic climate change functions]")

# Load NetCDF data
nc_file = "data/env_processed_compressed.nc"  # Adjust if necessary
ds = xr.open_dataset(nc_file, engine="netcdf4")

# List aCCF variables
accf_vars = [var for var in ds.data_vars if var.lower().startswith("accf")]
if not accf_vars:
    st.error("No variables starting with 'aCCF' found in dataset.")
    st.stop()

selected_var = st.selectbox("Select aCCF variable", accf_vars)

# Select pressure level
if "level" in ds.coords:
    pressure_levels = ds["level"].values
    level = st.selectbox("Select pressure level (hPa)", pressure_levels)
    var_data = ds[selected_var].sel(level=level)
else:
    st.warning("No 'level' coordinate found.")
    var_data = ds[selected_var]

# Convert to DataFrame
df = var_data.to_dataframe().reset_index()
df = df.dropna(subset=[selected_var])

# Rename for PyDeck compatibility
if "longitude" in df.columns and "latitude" in df.columns:
    df = df.rename(columns={
        "longitude": "Longitude",
        "latitude": "Latitude",
        selected_var: "Value"
    })
else:
    st.error("Missing required 'latitude' and 'longitude' columns.")
    st.stop()

# Normalize 'Value' column for consistent coloring
df["Value"] = (df["Value"] - df["Value"].min()) / (df["Value"].max() - df["Value"].min())

# Render map
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

