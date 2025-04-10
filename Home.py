import streamlit as st
import xarray as xr
import pandas as pd
import pydeck as pdk

# Load NetCDF file
@st.cache_data
def load_data():
    ds = xr.open_dataset(nc_file, engine="netCDF4")
    return ds

ds = load_data()

# Find all aCCF variables
accf_vars = [var for var in ds.data_vars if var.startswith("aCCF")]
st.sidebar.title("Settings")
selected_var = st.sidebar.selectbox("Select aCCF variable", accf_vars)

# Get available pressure levels
levels = ds['level'].values
selected_level = st.sidebar.select_slider("Select pressure level (hPa)", options=levels)

# Extract data
subset = ds[selected_var].sel(level=selected_level)

# Convert to DataFrame
df = subset.to_dataframe().reset_index()
df = df.dropna(subset=[selected_var])  # Drop missing values

# Rename for pydeck
df = df.rename(columns={
    "longitude": "lon",
    "latitude": "lat",
    selected_var: "value"
})

# Normalize value for color/weight scaling
df["weight"] = (df["value"] - df["value"].min()) / (df["value"].max() - df["value"].min())

# Display map
st.pydeck_chart(pdk.Deck(
    map_style='mapbox://styles/mapbox/dark-v10',
    initial_view_state=pdk.ViewState(
        latitude=0,
        longitude=0,
        zoom=1,
        pitch=0,
    ),
    layers=[
        pdk.Layer(
            "ScreenGridLayer",
            data=df,
            get_position='[lon, lat]',
            get_weight='weight',
            cell_size_pixels=10,
        )
    ],
))
