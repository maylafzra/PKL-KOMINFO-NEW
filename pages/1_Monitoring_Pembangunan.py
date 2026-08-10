import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from utils.load_data import load_master
from utils.styling import inject_custom_css, render_metric_card, render_custom_sidebar

# Page configuration
st.set_page_config(
    page_title="Monitoring Pembangunan - Jawa Timur",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize theme mode in session state if not present
if "theme_mode" not in st.session_state:
    st.session_state["theme_mode"] = "Sistem"

# Inject dynamic theme CSS
inject_custom_css(st.session_state["theme_mode"])
chart_theme = "plotly_dark" if st.session_state["theme_mode"] == "Gelap" else "plotly_white"

# Load master data
df = load_master()

# Header Banner
st.markdown("""
    <div class="dashboard-banner">
        <div class="banner-title">Monitoring Pembangunan</div>
        <div class="banner-desc">
            Pusat pemantauan terpadu indikator makro Jawa Timur. Gunakan panel interaktif untuk menganalisis 
            pemeringkatan wilayah secara real-time dan mengevaluasi visualisasi komparatif pembangunan.
        </div>
    </div>
""", unsafe_allow_html=True)

# Top filters
col_f1, col_f2, col_f3 = st.columns([1, 1, 1])
with col_f1:
    years = sorted(df['tahun'].unique(), reverse=True)
    selected_year = st.selectbox("Tahun Analisis:", years, index=0)
with col_f2:
    indicators = {
        "jumlah_penduduk_miskin": "Jumlah Penduduk Miskin (Ribu Jiwa)",
        "ipm": "Indeks Pembangunan Manusia (IPM)",
        "tpt": "Tingkat Pengangguran Terbuka (%)",
        "kepadatan_sipil_tahunan": "Kepadatan Penduduk (Jiwa/KM²)"
    }
    selected_ind = st.selectbox("Indikator Utama:", list(indicators.keys()), format_func=lambda x: indicators[x])
with col_f3:
    regions = ["Seluruh Jawa Timur"] + sorted(df['nama_wilayah'].unique().tolist())
    selected_region = st.selectbox("Kabupaten/Kota Detail:", regions, index=0)

st.write("")

# Label mapping used across all charts on this page so no raw column names
# (with underscores) ever leak into axis titles, legends, or hover tooltips.
axis_labels = {
    **indicators,
    "tahun": "Tahun",
    "nama_wilayah": "Kabupaten/Kota",
}

# Dynamic data filter
df_year = df[df['tahun'] == selected_year].copy()
max_val = df_year[selected_ind].max()
df_sorted = df_year.sort_values(by=selected_ind, ascending=False).reset_index(drop=True)

# Layout Grid (1/3 Left list, 2/3 Right visual pane)
col_left, col_right = st.columns([1, 2])

with col_left:
    st.markdown(f"<h4 style='font-size:1.1rem; font-weight:700; margin-bottom:15px;'>Pemeringkatan Wilayah ({selected_year})</h4>", unsafe_allow_html=True)
    
    # Render search box for rank list
    search_q = st.text_input("Cari Wilayah:", "", key="rank_search_q", label_visibility="collapsed", placeholder="Cari kabupaten/kota...")
    
    # Filter list
    df_list = df_sorted
    if search_q:
        df_list = df_sorted[df_sorted['nama_wilayah'].str.contains(search_q, case=False)]
    
    # Color mapping for indicators in progress bar
    progress_color = {
        "jumlah_penduduk_miskin": "#ef4444", 
        "ipm": "#0d9488",                    
        "tpt": "#d97706",                    
        "kepadatan_sipil_tahunan": "#8b5cf6"  
    }[selected_ind]
    
    # Scrollable container for rank list (PENTING: Ditulis rapat tanpa indentasi baris baru agar tidak diartikan sebagai blok kode markdown)
    html_list = '<div style="max-height: 520px; overflow-y: auto; padding-right: 5px;">'
    for idx, row in df_list.iterrows():
        val = row[selected_ind]
        pct = (val / max_val * 100) if max_val > 0 else 0
        html_list += f'<div class="list-item-card"><div style="display:flex; justify-content:space-between; font-size:0.85rem; font-weight:600; margin-bottom:4px;"><span>{row["nama_wilayah"]}</span><span>{val:,.2f}</span></div><div class="progress-bar-container"><div class="progress-bar-fill" style="width: {pct}%; background-color: {progress_color};"></div></div></div>'
    html_list += '</div>'
    
    st.markdown(html_list, unsafe_allow_html=True)

with col_right:
    # Segmented visualization selector
    st.markdown("<h4 style='font-size:1.1rem; font-weight:700; margin-bottom:15px;'>Visualisasi Utama Command Center</h4>", unsafe_allow_html=True)
    viz_type = st.radio(
        "Pilih Visualisasi:",
        ["Tren Historis", "Distribusi Bar Chart"],
        horizontal=True,
        label_visibility="collapsed"
    )
    
    st.write("")
    
    if viz_type == "Tren Historis":
        if selected_region == "Seluruh Jawa Timur":
            # Provincial averages
            df_prov = df.groupby('tahun')[[selected_ind]].mean().reset_index()
            fig = px.line(
                df_prov, x='tahun', y=selected_ind,
                title=f"Tren Rata-rata Provinsi: {indicators[selected_ind]} (2018-2025)",
                markers=True, color_discrete_sequence=[progress_color],
                labels=axis_labels
            )
        else:
            # Selected region trends
            df_reg = df[df['nama_wilayah'] == selected_region].sort_values(by='tahun')
            fig = px.line(
                df_reg, x='tahun', y=selected_ind,
                title=f"Tren Wilayah: {selected_region} - {indicators[selected_ind]} (2018-2025)",
                markers=True, color_discrete_sequence=[progress_color],
                labels=axis_labels
            )
        fig.update_layout(template=chart_theme, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)
        
    elif viz_type == "Distribusi Bar Chart":
        # Grouped bar chart for all regions
        fig = px.bar(
            df_sorted, x='nama_wilayah', y=selected_ind,
            color=selected_ind, color_continuous_scale='Reds' if selected_ind in ['jumlah_penduduk_miskin', 'tpt'] else 'Blues',
            title=f"Distribusi Spasial {indicators[selected_ind]} ({selected_year})",
            labels=axis_labels
        )
        fig.update_layout(template=chart_theme, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis_title=None)
        st.plotly_chart(fig, use_container_width=True)

st.write("---")

# Dynamic contextual metrics (Equal heights automatically)
st.subheader(f"Ringkasan Indikator Makro Jawa Timur (Tahun {selected_year})")
df_prov_yr = df[df['tahun'] == selected_year]
total_poverty = df_prov_yr['jumlah_penduduk_miskin'].sum()
avg_ipm_prov = df_prov_yr['ipm'].mean()
avg_tpt_prov = df_prov_yr['tpt'].mean()
avg_dens_prov = df_prov_yr['kepadatan_sipil_tahunan'].mean()

# Percentage changes compared to previous year
prev_yr = selected_year - 1
df_prov_prev = df[df['tahun'] == prev_yr]

change_poverty = None
change_ipm = None
change_tpt = None
change_dens = None

if not df_prov_prev.empty:
    prev_total_poverty = df_prov_prev['jumlah_penduduk_miskin'].sum()
    prev_avg_ipm = df_prov_prev['ipm'].mean()
    prev_avg_tpt = df_prov_prev['tpt'].mean()
    prev_avg_dens = df_prov_prev['kepadatan_sipil_tahunan'].mean()
    
    if prev_total_poverty > 0:
        change_poverty = ((total_poverty - prev_total_poverty) / prev_total_poverty) * 100
    if prev_avg_ipm > 0:
        change_ipm = ((avg_ipm_prov - prev_avg_ipm) / prev_avg_ipm) * 100
    if prev_avg_tpt > 0:
        change_tpt = ((avg_tpt_prov - prev_avg_tpt) / prev_avg_tpt) * 100
    if prev_avg_dens > 0:
        change_dens = ((avg_dens_prov - prev_avg_dens) / prev_avg_dens) * 100

col_m1, col_m2, col_m3, col_m4 = st.columns(4)
with col_m1:
    render_metric_card(
        title="Total Penduduk Miskin Jatim",
        value=f"{total_poverty:,.1f} Ribu",
        change_val=change_poverty,
        is_positive_good=False,
        border_color="#354599"
    )
with col_m2:
    render_metric_card(
        title="Rata-rata IPM Provinsi",
        value=f"{avg_ipm_prov:.2f}",
        change_val=change_ipm,
        is_positive_good=True,
        border_color="#354599"
    )
with col_m3:
    render_metric_card(
        title="Rata-rata TPT Provinsi",
        value=f"{avg_tpt_prov:.2f} %",
        change_val=change_tpt,
        is_positive_good=False,
        border_color="#354599"
    )
with col_m4:
    render_metric_card(
        title="Rerata Kepadatan Penduduk",
        value=f"{avg_dens_prov:,.1f} Jiwa/KM²",
        change_val=change_dens,
        is_positive_good=False,
        border_color="#354599"
    )

st.write("")
st.write("")

# Tabel Tingkat Pengangguran Terbuka (TPT) Kabupaten/Kota
st.markdown(f"<h4 style='font-size:1.15rem; font-weight:700; margin-bottom:12px;'>Tabel Tingkat Pengangguran Terbuka (TPT) Kabupaten/Kota (Tahun {selected_year})</h4>", unsafe_allow_html=True)

df_tpt_table = df_year[['nama_wilayah', 'tpt', 'laju_pertumbuhan']].sort_values(by='nama_wilayah').reset_index(drop=True)
df_tpt_table.columns = ['Kabupaten/Kota', 'Tingkat Pengangguran Terbuka (TPT) (%)', 'Laju Pertumbuhan Penduduk (%)']

df_tpt_table['Tingkat Pengangguran Terbuka (TPT) (%)'] = df_tpt_table['Tingkat Pengangguran Terbuka (TPT) (%)'].round(2)
df_tpt_table['Laju Pertumbuhan Penduduk (%)'] = df_tpt_table['Laju Pertumbuhan Penduduk (%)'].round(2)

st.dataframe(df_tpt_table, use_container_width=True, hide_index=True)
st.markdown("""
    <div style="background-color:rgba(128,128,128,0.05); border-radius:8px; padding:12px 15px; border:1px solid rgba(128,128,128,0.15); font-size:0.8rem; color:#64748b; line-height:1.5; margin-top:20px;">
        <b>ℹ️ Sumber Data Indikator Pembangunan:</b><br>
        1. <b>Indeks Pembangunan Manusia (IPM)</b>, <b>Tingkat Pengangguran Terbuka (TPT)</b>, dan <b>Jumlah Penduduk Miskin</b> bersumber dari <b>Badan Pusat Statistik (BPS) Provinsi Jawa Timur</b> (Periode 2018–2025).<br>
        2. <b>Kepadatan Penduduk Sipil</b> bersumber dari data konsolidasi bersih <b>Dinas Kependudukan dan Pencatatan Sipil (Dispendukcapil) Provinsi Jawa Timur</b>.
    </div>
""", unsafe_allow_html=True)