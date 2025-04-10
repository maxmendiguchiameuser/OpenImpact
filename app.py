import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Flight Climate Impact Dashboard",
    layout="wide",
)

# CSS styling inspired by contrails.org
st.markdown("""
    <style>
        html, body, [class*="css"]  {
            font-family: 'Inter', sans-serif;
            background-color: #f4f7f8;
        }
        h1, h2, h3 {
            color: #2b2f38;
        }
        .block-container {
            padding: 2rem 3rem;
        }
        .metric {
            font-size: 1.5rem !important;
        }
    </style>
""", unsafe_allow_html=True)

# Header
st.markdown("# ✈️ Flight Climate Impact Dashboard")
st.markdown("A scientific tool to explore the climate effects of individual flights, including CO₂ and non-CO₂ impacts.")

# Load data
@st.cache_data
def load_data():
    df = pd.read_csv("data/test_trajectory.csv")
    return df

df = load_data()

# Layout
st.markdown("## 📊 Flight Overview")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### Altitude Profile")
    fig_alt = px.line(df, x="sim_time", y="alt", title=None,
                      labels={"sim_time": "Simulation Time", "alt": "Altitude (ft)"})
    st.plotly_chart(fig_alt, use_container_width=True)

with col2:
    st.markdown("### Horizontal Path")
    st.map(df.rename(columns={"poslat": "latitude", "poslon": "longitude"}))

st.markdown("## 🌍 Climate Impact Summary")

c1, c2 = st.columns(2)
c1.metric("Total pATR20 (non-CO₂)", f"{df['pATR20_total'].sum():.2e}")
c2.metric("Max aCCF Contrail (night)", f"{df['FATR100_nightaCCF_Cont'].max():.2e}")

st.markdown("---")
st.markdown("This dashboard is based on open ADS-B data and custom climate impact calculations. For scientific use only.")
