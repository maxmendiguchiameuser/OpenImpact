import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(layout="wide")
st.title("Flight Climate Impact Dashboard")

# Load trajectory
@st.cache_data
def load_data():
    df = pd.read_csv("data/test_trajectory.csv")
    return df

df = load_data()

# Layout
col1, col2 = st.columns(2)

with col1:
    st.subheader("Altitude Profile")
    fig_alt = px.line(df, x="sim_time", y="alt", title="Altitude over Time")
    st.plotly_chart(fig_alt, use_container_width=True)

with col2:
    st.subheader("Horizontal Path")
    st.map(df.rename(columns={"poslat": "latitude", "poslon": "longitude"}))

st.subheader("Climate Impact Summary")
st.metric("Total pATR20 (non-CO₂)", f"{df['pATR20_total'].sum():.2e}")
st.metric("Max aCCF Contrail (night)", f"{df['FATR100_nightaCCF_Cont'].max():.2e}")
