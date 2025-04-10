import streamlit as st
import pandas as pd
import plotly.express as px
import base64
import pydeck as pdk
import matplotlib.cm as cm
import matplotlib.colors as mcolors
import plotly.graph_objects as go
import math
import numpy as np

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
with open("data/image.jpg", "rb") as img_file:
    image_bytes = img_file.read()
encoded_image = base64.b64encode(image_bytes).decode()
img_width_percent = 50

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

# === Load Data ===
@st.cache_data
def load_data():
    return pd.read_csv("data/test_trajectory.csv")

df = load_data()

# === Flight Visualizations ===
st.markdown("## 📊 Flight Overview")
col1, col2 = st.columns(2)

with col1:
    st.markdown("### Vertical Profile")
    fig_alt = px.line(df, x="sim_time", y="alt", title=None,
                      labels={"sim_time": "Simulation Time", "alt": "Altitude (ft)"})
    fig_alt.update_layout(
        paper_bgcolor='#595959',
        plot_bgcolor='#595959',
        font_color='#f2f2f2',
        xaxis=dict(color='#f0f0f0'),
        yaxis=dict(color='#f0f0f0'),
    )
    st.plotly_chart(fig_alt, use_container_width=True)

with col2:
    st.markdown("### Horizontal Path")
    st.map(df.rename(columns={"poslat": "latitude", "poslon": "longitude"}))

# === 3D Trajectory with Tooltip and Viridis Colors ===
st.markdown("### 🛨️ 3D Trajectory Visualization with Tooltip")
color_by = st.radio("Color trajectory by:", ["Altitude", "Climate Impact (pATR20_total)"], horizontal=True)
color_col = "alt" if "Altitude" in color_by else "pATR20_total"

df_line = df.dropna(subset=["poslat", "poslon", "alt", color_col]).copy()
df_line = df_line.astype({"poslat": float, "poslon": float, "alt": float, color_col: float})

vmin, vmax = df_line[color_col].min(), df_line[color_col].max()
norm = mcolors.Normalize(vmin=vmin, vmax=vmax)
cmap = cm.get_cmap("viridis")

segments = []
for i in range(len(df_line) - 1):
    start = df_line.iloc[i]
    end = df_line.iloc[i + 1]
    color_rgb = cmap(norm(start[color_col]))[:3]
    color_rgb_255 = [int(255 * c) for c in color_rgb]
    segments.append({
        "start": [start["poslon"], start["poslat"], start["alt"]],
        "end": [end["poslon"], end["poslat"], end["alt"]],
        "r": color_rgb_255[0],
        "g": color_rgb_255[1],
        "b": color_rgb_255[2],
        "lat": start["poslat"],
        "lon": start["poslon"],
        "alt": start["alt"]
    })

segment_df = pd.DataFrame(segments)
layer = pdk.Layer(
    "LineLayer",
    data=segment_df,
    get_source_position="start",
    get_target_position="end",
    get_color="[r, g, b]",
    get_width=4,
    pickable=True,
    auto_highlight=True,
)

view_state = pdk.ViewState(
    latitude=df_line["poslat"].mean(),
    longitude=df_line["poslon"].mean(),
    zoom=6,
    pitch=60,
)

# === Vertical Colorbar Overlay ===
vmin_scaled, vmax_scaled = vmin, vmax
scale_label = color_by
if "Climate" in color_by:
    try:
        if vmax > 0:
            exp = int(math.floor(math.log10(vmax)))
            scale_factor = 10 ** exp
            vmin_scaled = vmin / scale_factor
            vmax_scaled = vmax / scale_factor
            scale_label = f"{color_by} (×10<sup>{exp}</sup>)"
    except Exception:
        scale_label = color_by

colorbar_html = f"""
<div style="
    position: absolute;
    top: 120px;
    left: 20px;
    z-index: 1000;
    display: flex;
    flex-direction: column;
    align-items: center;
    font-size: 10px;
    color: #ddd;
">
    <div>{vmax_scaled:.2f}</div>
    <div style="
        background: linear-gradient(to top, #440154, #31688e, #35b779, #fde725);
        width: 10px;
        height: 360px;
        border-radius: 5px;
        box-shadow: 0 0 4px rgba(0,0,0,0.3);
        margin: 4px 0;
    "></div>
    <div>{vmin_scaled:.2f}</div>
    <div style="margin-top: 4px;">{scale_label}</div>
</div>
"""
st.markdown(colorbar_html, unsafe_allow_html=True)

st.pydeck_chart(pdk.Deck(
    layers=[layer],
    initial_view_state=view_state,
    map_style="mapbox://styles/mapbox/dark-v10",
    tooltip={
        "html": "<b>lat:</b> {lat}<br><b>lon:</b> {lon}<br><b>alt:</b> {alt} ft",
        "style": {"color": "white"}
    }
))

# === Climate Impact Horizontal Stacked Bar (F-ATR) ===
st.markdown("## 🔬 Species-Level Climate Impact")
horizon = st.selectbox("Select climate metric horizon", ["F-ATR20", "F-ATR50", "F-ATR100"])
log_scale = st.checkbox("Log scale", value=False)

conversion_factors = {
    "F-ATR20": {"CO₂": 9.4, "NOₓ": 14.5 + 10.8 + 10.8, "H₂O": 14.5, "Contrail": 13.6},
    "F-ATR50": {"CO₂": 44.0, "NOₓ": 34.1 + 42.5 + 42.5, "H₂O": 34.1, "Contrail": 30.16},
    "F-ATR100": {"CO₂": 125.0, "NOₓ": 58.3 + 98.2 + 98.2, "H₂O": 58.3, "Contrail": 48.9}
}

impact_totals = {
    "CO₂": df["pATR20_CO2"].sum(),
    "NOₓ": df["pATR20_NOx"].sum(),
    "H₂O": df["pATR20_H2O"].sum(),
    "Contrail": df["pATR20_CiC"].sum()
}

scaled = {
    species: impact_totals[species] * conversion_factors[horizon][species]
    for species in impact_totals
}

species = list(scaled.keys())
values = list(scaled.values())
colors = ['#440154', '#31688e', '#35b779', '#fde725']
fig = go.Figure()

for sp, val, col in zip(species, values, colors):
    fig.add_trace(go.Bar(
        name=sp,
        y=["Climate Impact [K]"],
        x=[val],
        orientation='h',
        marker_color=col,
        text=f"{val:.2e} K",
        textposition='inside' if not log_scale else 'auto',
        hovertemplate=f"{sp}: {{x:.2e}} K<br>"
    ))

fig.update_layout(
    barmode='stack',
    title=f"Effective Climate Impact by Species ({horizon})",
    xaxis_title="Kelvin (cumulative)",
    yaxis=dict(showticklabels=True),
    plot_bgcolor="#1e1e1e",
    paper_bgcolor="#1e1e1e",
    font=dict(color="white")
)
if log_scale:
    fig.update_xaxes(type="log")
st.plotly_chart(fig, use_container_width=True)

# === Climate Metrics Summary ===
st.markdown("## 🌍 Climate Impact Estimation")
c1, c2 = st.columns(2)
c1.metric("Total pATR20 (non-CO₂)", f"{df['pATR20_total'].sum():.2e}")
c2.metric("Max aCCF Contrail (night)", f"{df['FATR100_nightaCCF_Cont'].max():.2e}")

st.markdown("---")
st.markdown("This dashboard is based on open ADS-B data and custom climate impact calculations. For scientific use only.")
