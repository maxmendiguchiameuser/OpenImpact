import streamlit as st
import pandas as pd
import plotly.express as px
import base64

st.set_page_config(
    page_title="Flight Climate Impact Dashboard",
    layout="wide",
)

# === Dark Theme Styling ===
st.markdown("""
    <style>
        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
            background-color: #1e1e1e;
            color: #f0f0f0;
        }
        h1, h2, h3 {
            color: #ffffff;
        }
        .block-container {
            padding: 2rem 3rem;
        }
        .metric {
            font-size: 1.5rem !important;
            color: #ffffff;
        }
        .stMetric label {
            color: #ffffff !important;
        }
    </style>
""", unsafe_allow_html=True)

# === Mission Section ===
# Load image and encode in base64
with open("data/image.png", "rb") as img_file:
    image_bytes = img_file.read()
encoded_image = base64.b64encode(image_bytes).decode()

# Image width scaling factor (adjust here as needed)
img_width_percent = 70  # use values like 60, 80, 100

# Mission HTML block
st.markdown(f"""
<div style='padding: 2rem 0 1rem 0; border-bottom: 1px solid #444;'>
    <div style='color: #f75e00; font-size: 0.9rem; font-weight: 600;'>■ Our Mission</div>
    <h1 style='font-size: 3rem; font-weight: 300; margin-bottom: 1rem; color: white;'>
        Turning contrail research into <br> climate action.
    </h1>
    <div style='display: flex; justify-content: center;'>
        <img src='data:image/png;base64,{encoded_image}' style='width: {img_width_percent}%; border-radius: 4px; margin: 2rem 0;' />
    </div>
    <div style='display: flex; justify-content: flex-end;'>
        <div style='border-left: 3px solid #f75e00; padding-left: 1rem; max-width: 400px; font-size: 1rem; color: #ccc;'>
            We, along with a broad range of collaborators, are working to build the most up-to-date science into contrail management solutions that can be used by the aviation industry to significantly—and immediately—reduce their climate impact.
        </div>
    </div>
</div>

<div style='margin-top: 4rem; color: #f75e00; font-size: 0.9rem; font-weight: 600;'>■ Contributors</div>
<h2 style='font-size: 1.6rem; font-weight: 300; color: white;'>
    We are part of a multi-disciplinary network of organizations collaborating on contrail management.
</h2>
""", unsafe_allow_html=True)

# === Load Trajectory Data ===
@st.cache_data
def load_data():
    df = pd.read_csv("data/test_trajectory.csv")
    return df

df = load_data()

# === Flight Visualizations ===
st.markdown("## 📊 Flight Overview")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### Altitude Profile")
    fig_alt = px.line(df, x="sim_time", y="alt", title=None,
                      labels={"sim_time": "Simulation Time", "alt": "Altitude (ft)"})
    fig_alt.update_layout(
        paper_bgcolor='#1e1e1e',
        plot_bgcolor='#1e1e1e',
        font_color='#f0f0f0',
        xaxis=dict(color='#f0f0f0'),
        yaxis=dict(color='#f0f0f0'),
    )
    st.plotly_chart(fig_alt, use_container_width=True)

with col2:
    st.markdown("### Horizontal Path")
    st.map(df.rename(columns={"poslat": "latitude", "poslon": "longitude"}))

# === Climate Metrics ===
st.markdown("## 🌍 Climate Impact Summary")

c1, c2 = st.columns(2)
c1.metric("Total pATR20 (non-CO₂)", f"{df['pATR20_total'].sum():.2e}")
c2.metric("Max aCCF Contrail (night)", f"{df['FATR100_nightaCCF_Cont'].max():.2e}")

st.markdown("---")
st.markdown("This dashboard is based on open ADS-B data and custom climate impact calculations. For scientific use only.")
