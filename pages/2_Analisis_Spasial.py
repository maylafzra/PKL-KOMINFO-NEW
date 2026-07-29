import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import urllib.request
import json
from utils.load_data import load_master
from utils.styling import inject_custom_css, render_custom_sidebar

# Page Configuration
st.set_page_config(
    page_title="Analisis Spasial - Jawa Timur",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize theme mode in session state if not present
if "theme_mode" not in st.session_state:
    st.session_state["theme_mode"] = "Sistem"

# Inject dynamic theme CSS
inject_custom_css(st.session_state["theme_mode"])
chart_theme = "plotly_dark" if st.session_state["theme_mode"] == "Gelap" else "plotly_white"
mapbox_style = "carto-darkmatter" if st.session_state["theme_mode"] == "Gelap" else "carto-positron"

# Render custom sidebar
render_custom_sidebar("Spasial")

# Load master data
df = load_master()

# Header Banner
st.markdown("""
    <div class="dashboard-banner">
        <div class="banner-title">GIS Control Center: Analisis Spasial</div>
        <div class="banner-desc">
            Pusat analisis keterkaitan spasial kependudukan Jawa Timur. Pantau persebaran geografis indikator 
            dan deteksi klaster autokorelasi (Hotspot/Coldspot) menggunakan Moran's I Gauge.
        </div>
    </div>
""", unsafe_allow_html=True)

# Centroids for regions
centroids = {
    '3501': (111.1, -8.2), '3502': (111.5, -7.9), '3503': (111.7, -8.1), '3504': (111.9, -8.1),
    '3505': (112.2, -8.1), '3506': (112.0, -7.8), '3507': (112.6, -8.1), '3508': (113.2, -8.1),
    '3509': (113.6, -8.2), '3510': (114.3, -8.2), '3511': (113.8, -7.9), '3512': (114.0, -7.7),
    '3513': (113.3, -7.9), '3514': (112.9, -7.7), '3515': (112.7, -7.4), '3516': (112.5, -7.5),
    '3517': (112.2, -7.5), '3518': (111.9, -7.6), '3519': (111.6, -7.6), '3520': (111.3, -7.6),
    '3521': (111.4, -7.4), '3522': (111.9, -7.2), '3523': (112.0, -6.9), '3524': (112.3, -7.1),
    '3525': (112.6, -7.2), '3526': (112.8, -7.0), '3527': (113.2, -7.1), '3528': (113.5, -7.1),
    '3529': (113.9, -7.0), '3571': (112.0, -7.8), '3572': (112.2, -8.1), '3573': (112.6, -8.0),
    '3574': (113.2, -7.7), '3575': (112.9, -7.7), '3576': (112.4, -7.5), '3577': (111.5, -7.6),
    '3578': (112.7, -7.3), '3579': (112.5, -7.9)
}

df['lon'] = df['kode_wilayah'].astype(str).map(lambda x: centroids.get(x, (112.0, -7.5))[0])
df['lat'] = df['kode_wilayah'].astype(str).map(lambda x: centroids.get(x, (112.0, -7.5))[1])

@st.cache_data(show_spinner="Memuat data geospasial Jawa Timur...")
def get_geojson_jt():
    url = 'https://raw.githubusercontent.com/TheMaggieSimpson/IndonesiaGeoJSON/master/kota-kabupaten.json'
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
            data['features'] = [f for f in data['features'] if f['properties'].get('NAME_1') == 'Jawa Timur']
            return data, True
    except Exception:
        return None, False

geojson_jt, geojson_success = get_geojson_jt()

# Top Filters
col_tf1, col_tf2 = st.columns(2)
with col_tf1:
    years = sorted(df['tahun'].unique(), reverse=True)
    selected_year = st.selectbox("Tahun Analisis Spasial:", years, index=0)
with col_tf2:
    indicators = {
        "jumlah_penduduk_miskin": "Jumlah Penduduk Miskin (Ribu Jiwa)",
        "ipm": "Indeks Pembangunan Manusia (IPM)",
        "tpt": "Tingkat Pengangguran Terbuka (%)",
        "kepadatan_sipil_tahunan": "Kepadatan Penduduk (Jiwa/KM²)"
    }
    selected_ind = st.selectbox("Pilih Indikator:", list(indicators.keys()), format_func=lambda x: indicators[x])

# Calculate Moran's I & LISA Clusters
df_yr = df[df['tahun'] == selected_year].copy().reset_index(drop=True)
num_regions = len(df_yr)

# Spatial Weights Matrix (k=4 Nearest Neighbors)
W = np.zeros((num_regions, num_regions))
codes = list(df_yr['kode_wilayah'].astype(str))

for i in range(num_regions):
    c1 = codes[i]
    coord1 = np.array(centroids.get(c1, (112.0, -7.5)))
    distances = []
    for j in range(num_regions):
        if i == j:
            distances.append((np.inf, j))
            continue
        c2 = codes[j]
        coord2 = np.array(centroids.get(c2, (112.0, -7.5)))
        dist = np.linalg.norm(coord1 - coord2)
        distances.append((dist, j))
    distances.sort()
    for d, idx in distances[:4]:
        W[i, idx] = 1.0

# Row standardization
for i in range(num_regions):
    row_sum = W[i, :].sum()
    if row_sum > 0:
        W[i, :] /= row_sum

x = df_yr[selected_ind].values
z = x - x.mean()
spatial_lag = W.dot(z)
morans_i = np.sum(z * spatial_lag) / np.sum(z**2)

lisa_types = []
z_std = z / np.std(x)
lag_std = spatial_lag / np.std(x)

for i in range(num_regions):
    if z_std[i] > 0 and lag_std[i] > 0:
        lisa_types.append('High-High (Hotspot)')
    elif z_std[i] < 0 and lag_std[i] < 0:
        lisa_types.append('Low-Low (Coldspot)')
    elif z_std[i] > 0 and lag_std[i] < 0:
        lisa_types.append('High-Low (Outlier)')
    else:
        lisa_types.append('Low-High (Outlier)')

df_yr['lisa_cluster'] = lisa_types
df_yr['kode_wilayah_str'] = df_yr['kode_wilayah'].astype(str)

# Layout Grid (2/3 Left Map, 1/3 Right Insights Panel)
col_left, col_right = st.columns([2, 1])

with col_left:
    st.markdown("<h4 style='font-size:1.1rem; font-weight:700; margin-bottom:15px;'>Peta Tematik Spasial</h4>", unsafe_allow_html=True)
    map_toggle = st.radio(
        "Pilih Jenis Peta:",
        ["Sebaran Indikator", "Klaster Spasial (LISA)"],
        horizontal=True,
        label_visibility="collapsed"
    )
    
    st.write("")
    
    if map_toggle == "Sebaran Indikator":
        if geojson_success:
            fig = px.choropleth_mapbox(
                df_yr, geojson=geojson_jt, locations='kode_wilayah_str',
                featureidkey='properties.CC_2', color=selected_ind,
                color_continuous_scale='Blues' if selected_ind in ['ipm', 'kepadatan_sipil_tahunan'] else 'Reds',
                mapbox_style=mapbox_style,
                center={"lat": -7.7, "lon": 112.5},
                zoom=6.8,
                title=f"Peta Sebaran {indicators[selected_ind]} ({selected_year})"
            )
            fig.update_layout(template=chart_theme, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(l=0, r=0, t=40, b=0))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Koneksi GeoJSON tidak tersedia. Menggunakan Scatter Mapbox.")
            fig = px.scatter_mapbox(
                df_yr, lat='lat', lon='lon', size='jumlah_penduduk', color=selected_ind,
                color_continuous_scale='Blues' if selected_ind in ['ipm', 'kepadatan_sipil_tahunan'] else 'Reds',
                hover_name='nama_wilayah', size_max=25, zoom=7,
                title=f"Distribusi Spasial {indicators[selected_ind]} ({selected_year})"
            )
            fig.update_layout(mapbox_style=mapbox_style, template=chart_theme, margin=dict(l=0, r=0, t=40, b=0))
            st.plotly_chart(fig, use_container_width=True)
    else:
        # LISA Map
        if geojson_success:
            fig = px.choropleth_mapbox(
                df_yr, geojson=geojson_jt, locations='kode_wilayah_str',
                featureidkey='properties.CC_2', color='lisa_cluster',
                color_discrete_map={
                    'High-High (Hotspot)': '#ef4444',
                    'Low-Low (Coldspot)': '#0d9488',
                    'High-Low (Outlier)': '#d97706',
                    'Low-High (Outlier)': '#3b82f6'
                },
                mapbox_style=mapbox_style,
                center={"lat": -7.7, "lon": 112.5},
                zoom=6.8,
                title=f"Peta Klaster LISA {indicators[selected_ind]} ({selected_year})"
            )
            fig.update_layout(template=chart_theme, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(l=0, r=0, t=40, b=0))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Koneksi GeoJSON tidak tersedia. Menggunakan Scatter Mapbox.")
            fig = px.scatter_mapbox(
                df_yr, lat='lat', lon='lon', size='jumlah_penduduk', color='lisa_cluster',
                color_discrete_map={
                    'High-High (Hotspot)': '#ef4444',
                    'Low-Low (Coldspot)': '#0d9488',
                    'High-Low (Outlier)': '#d97706',
                    'Low-High (Outlier)': '#3b82f6'
                },
                hover_name='nama_wilayah', size_max=25, zoom=7,
                title=f"Klaster LISA {indicators[selected_ind]} ({selected_year})"
            )
            fig.update_layout(mapbox_style=mapbox_style, template=chart_theme, margin=dict(l=0, r=0, t=40, b=0))
            st.plotly_chart(fig, use_container_width=True)

with col_right:
    st.markdown("<h4 style='font-size:1.1rem; font-weight:700; margin-bottom:15px;'>Spatial Insights</h4>", unsafe_allow_html=True)
    
    # 1. Moran's I Gauge Chart (Plotly go.Indicator)
    gauge_bg = "#1e293b" if st.session_state["theme_mode"] == "Gelap" else "#ffffff"
    gauge_axis_color = "#94a3b8" if st.session_state["theme_mode"] == "Gelap" else "#64748b"
    
    fig_gauge = go.Figure(go.Indicator(
        mode="gauge+number",
        value=morans_i,
        domain={'x': [0, 1], 'y': [0, 1]},
        gauge={
            'axis': {'range': [-1, 1], 'tickwidth': 1, 'tickcolor': gauge_axis_color, 'tickfont': {'color': gauge_axis_color}},
            'bar': {'color': '#3b82f6'},
            'bgcolor': gauge_bg,
            'borderwidth': 1,
            'bordercolor': '#cbd5e1' if st.session_state["theme_mode"] != "Gelap" else '#475569',
            'steps': [
                {'range': [-1, 0], 'color': 'rgba(239, 68, 68, 0.08)'},
                {'range': [0, 1], 'color': 'rgba(16, 185, 129, 0.08)'}
            ]
        }
    ))
    fig_gauge.update_layout(
        height=180, margin=dict(l=15, r=15, t=10, b=10),
        paper_bgcolor='rgba(0,0,0,0)',
        title={'text': "Indeks Moran's I", 'font': {'size': 12, 'color': gauge_axis_color}, 'x': 0.5, 'y': 0.95}
    )
    st.plotly_chart(fig_gauge, use_container_width=True)
    
    # Interpretation text
    moran_text = "Autokorelasi Spasial Positif" if morans_i > 0 else "Autokorelasi Spasial Negatif"
    st.markdown(f"""
        <div style='font-size:0.82rem; line-height:1.4; opacity:0.85; margin-bottom:15px;'>
            Nilai Moran's I sebesar <b>{morans_i:.4f}</b> menunjukkan pola <b>{moran_text}</b>. Wilayah dengan karakteristik serupa cenderung berkelompok secara geografis.
        </div>
    """, unsafe_allow_html=True)
    
    # 2. Cluster Hotspot & Coldspot Lists
    st.markdown("<h5 style='font-size:0.92rem; font-weight:700;'>Identifikasi Daerah Hotspot (High-High)</h5>", unsafe_allow_html=True)
    hh_districts = df_yr[df_yr['lisa_cluster'] == 'High-High (Hotspot)']['nama_wilayah'].tolist()
    if hh_districts:
        hh_html = '<div style="display:flex; flex-wrap:wrap; gap:6px; margin-bottom:15px;">'
        for d in hh_districts[:8]: # Cap at 8 for layout elegance
            hh_html += f'<span class="priority-badge priority-high">{d}</span>'
        if len(hh_districts) > 8:
            hh_html += f'<span class="priority-badge priority-high">+{len(hh_districts)-8} Lainnya</span>'
        hh_html += '</div>'
        st.markdown(hh_html, unsafe_allow_html=True)
    else:
        st.markdown("<div style='font-size:0.8rem; color:#64748b; margin-bottom:15px;'>Tidak terdeteksi wilayah hotspot.</div>", unsafe_allow_html=True)
        
    st.markdown("<h5 style='font-size:0.92rem; font-weight:700;'>Identifikasi Daerah Coldspot (Low-Low)</h5>", unsafe_allow_html=True)
    ll_districts = df_yr[df_yr['lisa_cluster'] == 'Low-Low (Coldspot)']['nama_wilayah'].tolist()
    if ll_districts:
        ll_html = '<div style="display:flex; flex-wrap:wrap; gap:6px;">'
        for d in ll_districts[:8]:
            ll_html += f'<span class="priority-badge priority-low">{d}</span>'
        if len(ll_districts) > 8:
            ll_html += f'<span class="priority-badge priority-low">+{len(ll_districts)-8} Lainnya</span>'
        ll_html += '</div>'
        st.markdown(ll_html, unsafe_allow_html=True)
    else:
        st.markdown("<div style='font-size:0.8rem; color:#64748b;'>Tidak terdeteksi wilayah coldspot.</div>", unsafe_allow_html=True)
