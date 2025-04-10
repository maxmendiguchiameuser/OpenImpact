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


st.markdown("### Debugging File Paths")
st.text(f"Current working directory: {os.getcwd()}")
st.text(f"Files in current directory: {os.listdir('.')}")
st.text(f"Files in 'data/' directory: {os.listdir('./data') if os.path.exists('./data') else 'data folder not found'}")

