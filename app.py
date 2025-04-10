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

# === 3D Trajectory with Tooltip ===
import matplotlib.cm as cm
import matplotlib.colors as mcolors

st.markdown("### 🚨️ 3D Trajectory Visualization with Tooltip")

# Choose coloring mode
color_by = st.radio("Color trajectory by:", ["Altitude", "Climate Impact (pATR20_total)"], horizontal=True)
color_col = "alt" if "Altitude" in color_by else "pATR20_total"

# Clean and ensure correct types
df_line = df.dropna(subset=["poslat", "poslon", "alt", color_col]).copy()
df_line = df_line.astype({ "poslat": float, "poslon": float, "alt": float, color_col: float })

# Normalize and apply Viridis colormap
vmin, vmax = df_line[color_col].min(), df_line[color_col].max()
norm = mcolors.Normalize(vmin=vmin, vmax=vmax)
cmap = cm.get_cmap("viridis")

segments = []
for i in range(len(df_line) - 1):
    start = df_line.iloc[i]
    end = df_line.iloc[i + 1]
    color_rgb = cmap(norm(start[color_col]))[:3]  # RGBA to RGB
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

# Define the 3D LineLayer with tooltip support
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

# Camera setup
view_state = pdk.ViewState(
    latitude=df_line["poslat"].mean(),
    longitude=df_line["poslon"].mean(),
    zoom=6,
    pitch=60,
)

# === Add vertical colorbar ===
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
        height: 260px;
        border-radius: 5px;
        box-shadow: 0 0 4px rgba(0,0,0,0.3);
        margin: 4px 0;
    "></div>
    <div>{vmin_scaled:.2f}</div>
    <div style="margin-top: 4px;">{scale_label}</div>
</div>
"""
st.markdown(colorbar_html, unsafe_allow_html=True)

# Deck with tooltip
map_style_option = st.selectbox(
    "Map background style:",
    options=[
        "light-v10",
        "streets-v12",
        "outdoors-v12",
        "navigation-day-v1",
        "dark-v10",
        "navigation-night-v1",
        "satellite-streets-v12"
    ],
    index=0,
    format_func=lambda x: x.replace("-v", " v").replace("streets", "Streets").title()
)

st.pydeck_chart(pdk.Deck(
    layers=[layer],
    initial_view_state=view_state,
    map_style=f"mapbox://styles/mapbox/{map_style_option}","mapbox://styles/mapbox/light-v10",  # changed from dark-v10 to light-v10 for a slightly lighter look
    tooltip={
        "html": "<b>lat:</b> {lat}<br><b>lon:</b> {lon}<br><b>alt:</b> {alt} ft",
        "style": {"color": "white"}
    }
))

...


# === Developer Section ===
st.markdown("### 👩‍💻 Acknowledgements & References")

st.markdown("""
Lorem ipsum dolor sit amet, consectetur adipiscing elit. Sed non risus. Suspendisse lectus tortor, dignissim sit amet, adipiscing nec, ultricies sed, dolor. Cras elementum ultrices diam. 
Maecenas ligula massa, varius a, semper congue, euismod non, mi. Proin porttitor, orci nec nonummy molestie, enim est eleifend mi, non fermentum diam nisl sit amet erat. 
Duis semper. Duis arcu massa, scelerisque vitae, consequat in, pretium a, enim. Pellentesque congue. Ut in risus volutpat libero pharetra tempor. Cras vestibulum bibendum augue. 
Praesent egestas leo in pede. Praesent blandit odio eu enim. Pellentesque sed dui ut augue blandit sodales. 
Vestibulum ante ipsum primis in faucibus orci luctus et ultrices posuere cubilia Curae; Aliquam nibh. 
Mauris ac mauris sed pede pellentesque fermentum. Maecenas adipiscing ante non diam sodales hendrerit. 

**Key Contributors:**
- Dr. Junzi Sun (FastMeteo)
- Gabriel Jarry (Acropole)
- DLR Team (CLIMaCCF)
- ECMWF (ERA5)
- OpenSky Network (ADS-B data)

**Selected References on Non-CO₂ Effects of Aviation:**
1. Lee et al. (2021) – The contribution of global aviation to climate change.
2. Grewe et al. (2017) – Mitigating the climate impact from aviation NOₓ emissions.
3. Matthes et al. (2021) – Potential climate impact reductions from optimized flight planning.
4. Burkhardt & Kärcher (2011) – Global radiative forcing from contrail cirrus.
5. Brasseur et al. (2016) – Impact of aviation on climate: FAATC White Paper.
""")
