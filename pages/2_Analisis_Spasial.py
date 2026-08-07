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
mapbox_style = "carto-positron" # Carto positron provides the most readable base map for labels
if st.session_state["theme_mode"] == "Gelap":
    mapbox_style = "carto-darkmatter"

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

labels_dict = {
    "jumlah_penduduk_miskin": "Jumlah Penduduk Miskin (Ribu Jiwa)",
    "ipm": "Indeks Pembangunan Manusia (IPM)",
    "tpt": "Tingkat Pengangguran Terbuka (%)",
    "kepadatan_sipil_tahunan": "Kepadatan Penduduk (Jiwa/KM²)",
    "lisa_cluster": "Klaster Spasial (LISA)",
    "jumlah_penduduk": "Jumlah Penduduk (Jiwa)"
}

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

# Label text color based on theme
text_label_color = "#1e293b" if st.session_state["theme_mode"] != "Gelap" else "#f8fafc"

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
                hover_name='nama_wilayah', # Menampilkan nama kabupaten/kota sebagai judul tooltip hover
                hover_data={
                    'kode_wilayah_str': False, # Menyembunyikan kode wilayah agar lebih bersih
                    selected_ind: True
                },
                title=f"Peta Sebaran {indicators[selected_ind]} ({selected_year})",
                labels=labels_dict
            )
            # Add text labels on map centroids
            fig.add_trace(go.Scattermapbox(
                lat=df_yr['lat'],
                lon=df_yr['lon'],
                mode='text',
                text=df_yr['nama_wilayah'],
                textposition='middle center',
                textfont=dict(
                    size=8,
                    color=text_label_color,
                    family='Inter, sans-serif',
                    weight='bold'
                ),
                showlegend=False,
                hoverinfo='skip'
            ))
            fig.update_layout(template=chart_theme, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', margin=dict(l=0, r=0, t=40, b=0))
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Koneksi GeoJSON tidak tersedia. Menggunakan Scatter Mapbox.")
            fig = px.scatter_mapbox(
                df_yr, lat='lat', lon='lon', size='jumlah_penduduk', color=selected_ind,
                color_continuous_scale='Blues' if selected_ind in ['ipm', 'kepadatan_sipil_tahunan'] else 'Reds',
                hover_name='nama_wilayah', size_max=25, zoom=7,
                title=f"Distribusi Spasial {indicators[selected_ind]} ({selected_year})",
                labels=labels_dict
            )
            # Add text labels
            fig.add_trace(go.Scattermapbox(
                lat=df_yr['lat'],
                lon=df_yr['lon'],
                mode='text',
                text=df_yr['nama_wilayah'],
                textposition='top center',
                textfont=dict(size=8, color=text_label_color, family='Inter, sans-serif'),
                showlegend=False,
                hoverinfo='skip'
            ))
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

                hover_name='nama_wilayah', # Menampilkan nama kabupaten/kota sebagai judul tooltip hover
                hover_data={
                    'kode_wilayah_str': False, # Menyembunyikan kode wilayah agar lebih bersih
                    'lisa_cluster': True,
                    selected_ind: True
                },
                title=f"Peta Klaster LISA {indicators[selected_ind]} ({selected_year})",
                labels=labels_dict
            )
            # Add text labels on map centroids
            fig.add_trace(go.Scattermapbox(
                lat=df_yr['lat'],
                lon=df_yr['lon'],
                mode='text',
                text=df_yr['nama_wilayah'],
                textposition='middle center',
                textfont=dict(
                    size=8,
                    color=text_label_color,
                    family='Inter, sans-serif',
                    weight='bold'
                ),
                showlegend=False,
                hoverinfo='skip'
            ))
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
                title=f"Klaster LISA {indicators[selected_ind]} ({selected_year})",
                labels=labels_dict
            )
            # Add text labels
            fig.add_trace(go.Scattermapbox(
                lat=df_yr['lat'],
                lon=df_yr['lon'],
                mode='text',
                text=df_yr['nama_wilayah'],
                textposition='top center',
                textfont=dict(size=8, color=text_label_color, family='Inter, sans-serif'),
                showlegend=False,
                hoverinfo='skip'
            ))
            fig.update_layout(mapbox_style=mapbox_style, template=chart_theme, margin=dict(l=0, r=0, t=40, b=0))
            st.plotly_chart(fig, use_container_width=True)

    st.write("")
    st.markdown("""
        <div style="background-color:rgba(128,128,128,0.05); border-radius:8px; padding:12px 15px; border:1px solid rgba(128,128,128,0.15); font-size:0.8rem; color:#64748b; line-height:1.5;">
            <b>ℹ️ Sumber Pemetaan & Analisis Spasial:</b><br>
            - <b>Batas Administratif Wilayah:</b> Peta administrasi (GeoJSON) diperoleh dari repositori publik <i>IndonesiaGeoJSON / GADM</i>.<br>
            - <b>Perhitungan Autokorelasi & LISA:</b> Pendeteksian klaster hotspot (High-High) dan coldspot (Low-Low) dihitung secara komputasional menggunakan matriks bobot spasial <i>k-nearest neighbors (k=4)</i> terhadap data indikator makro yang terintegrasi dari <b>Badan Pusat Statistik (BPS) Jawa Timur</b> dan <b>Dinas Kependudukan dan Pencatatan Sipil (Dispendukcapil) Provinsi Jawa Timur</b>.
        </div>
    """, unsafe_allow_html=True)

with col_right:
    st.markdown("<h4 style='font-size:1.1rem; font-weight:700; margin-bottom:15px;'>Spatial Insights</h4>", unsafe_allow_html=True)
    
    # 1. Moran's I — Donut Ring KPI (custom CSS, bukan gauge speedometer)
    is_dark = st.session_state["theme_mode"] == "Gelap"
    ring_track_color = "rgba(148,163,184,0.18)" if not is_dark else "rgba(148,163,184,0.15)"
    ring_inner_bg = "#ffffff" if not is_dark else "#1e293b"
    ring_label_color = "#94a3b8" if is_dark else "#64748b"
    ring_border_color = "#e2e8f0" if not is_dark else "#334155"

    # Magnitude 0-1 dipetakan ke 0-360 derajat; arah warna beda utk positif/negatif
    magnitude_pct = min(abs(morans_i), 1.0) * 100
    ring_angle = magnitude_pct * 3.6

    if morans_i > 0.02:
        ring_color_start, ring_color_end = "#3b82f6", "#0d9488"
        moran_badge_bg, moran_badge_color = "rgba(13,148,136,0.1)", "#0d9488"
        moran_badge_text = "Autokorelasi Positif"
    elif morans_i < -0.02:
        ring_color_start, ring_color_end = "#ef4444", "#d97706"
        moran_badge_bg, moran_badge_color = "rgba(239,68,68,0.1)", "#ef4444"
        moran_badge_text = "Autokorelasi Negatif"
    else:
        ring_color_start, ring_color_end = "#94a3b8", "#64748b"
        moran_badge_bg, moran_badge_color = "rgba(100,116,139,0.1)", "#64748b"
        moran_badge_text = "Pola Acak (Tidak Signifikan)"

    st.markdown(f"""
        <div style="display:flex; flex-direction:column; align-items:center; padding:6px 0 14px 0;">
            <div style="font-size:0.72rem; font-weight:700; color:{ring_label_color}; text-transform:uppercase; letter-spacing:0.06em; margin-bottom:14px;">
                Indeks Moran's I
            </div>
            <div style="position:relative; width:168px; height:168px;">
                <div style="width:168px; height:168px; border-radius:50%;
                            background: conic-gradient(from 0deg,
                                {ring_color_start} 0deg,
                                {ring_color_end} {ring_angle}deg,
                                {ring_track_color} {ring_angle}deg 360deg);
                            display:flex; align-items:center; justify-content:center;
                            box-shadow: 0 2px 10px rgba(0,0,0,0.06);">
                    <div style="width:124px; height:124px; border-radius:50%; background:{ring_inner_bg};
                                border:1px solid {ring_border_color};
                                display:flex; flex-direction:column; align-items:center; justify-content:center;">
                        <div style="font-size:1.9rem; font-weight:800; color:{ring_color_start}; line-height:1;">
                            {morans_i:.3f}
                        </div>
                        <div style="font-size:0.62rem; color:{ring_label_color}; margin-top:4px;">rentang -1 s/d 1</div>
                    </div>
                </div>
            </div>
            <div style="margin-top:14px; background:{moran_badge_bg}; color:{moran_badge_color}; font-size:0.78rem; font-weight:700; padding:5px 14px; border-radius:20px;">
                {moran_badge_text}
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Interpretation text
    moran_text = "Autokorelasi Spasial Positif" if morans_i > 0 else "Autokorelasi Spasial Negatif"
    st.markdown(f"""
        <div style='font-size:0.82rem; line-height:1.4; opacity:0.85; margin-bottom:10px;'>
            Nilai Moran's I sebesar <b>{morans_i:.4f}</b> menunjukkan pola <b>{moran_text}</b> untuk indikator <b>{indicators[selected_ind]}</b> tahun <b>{selected_year}</b>. Wilayah dengan karakteristik serupa cenderung berkelompok secara geografis.
        </div>
    """, unsafe_allow_html=True)

    # Source & methodology note for the Moran's I index
    st.markdown("""
        <div style="background-color:rgba(128,128,128,0.05); border-radius:8px; padding:10px 12px; border:1px solid rgba(128,128,128,0.15); font-size:0.75rem; color:#64748b; line-height:1.5; margin-bottom:15px;">
            <b>ℹ️ Metode & Sumber Indeks:</b> Indeks Moran's I dihitung dari data indikator makro <b>BPS Jawa Timur</b> dan <b>Dispendukcapil Provinsi Jawa Timur</b>, menggunakan matriks bobot spasial <i>k-nearest neighbors (k=4)</i> berbasis titik pusat (centroid) tiap kabupaten/kota. Nilai berkisar dari -1 (autokorelasi negatif sempurna) hingga +1 (autokorelasi positif sempurna); nilai mendekati 0 menandakan pola acak (tidak ada autokorelasi spasial).
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