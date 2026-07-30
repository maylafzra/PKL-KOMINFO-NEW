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
        <div class="banner-title">Command Center: Monitoring Pembangunan</div>
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
        ["Tren Historis", "Distribusi Bar Chart", "Komparasi Radar Wilayah"],
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
                markers=True, color_discrete_sequence=[progress_color]
            )
        else:
            # Selected region trends
            df_reg = df[df['nama_wilayah'] == selected_region].sort_values(by='tahun')
            fig = px.line(
                df_reg, x='tahun', y=selected_ind,
                title=f"Tren Wilayah: {selected_region} - {indicators[selected_ind]} (2018-2025)",
                markers=True, color_discrete_sequence=[progress_color]
            )
        fig.update_layout(template=chart_theme, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig, use_container_width=True)
        
    elif viz_type == "Distribusi Bar Chart":
        # Grouped bar chart for all regions
        fig = px.bar(
            df_sorted, x='nama_wilayah', y=selected_ind,
            color=selected_ind, color_continuous_scale='Reds' if selected_ind in ['jumlah_penduduk_miskin', 'tpt'] else 'Blues',
            title=f"Distribusi Spasial {indicators[selected_ind]} ({selected_year})"
        )
        fig.update_layout(template=chart_theme, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', xaxis_title=None)
        st.plotly_chart(fig, use_container_width=True)
        
    else:
        # Radar Chart comparison
        # Provincial averages
        avg_miskin = df_year['jumlah_penduduk_miskin'].mean()
        avg_ipm = df_year['ipm'].mean()
        avg_tpt = df_year['tpt'].mean()
        avg_density = df_year['kepadatan_sipil_tahunan'].mean()
        avg_pop = df_year['jumlah_penduduk'].mean()
        
        categories = ['IPM', 'TPT', 'Penduduk Miskin', 'Kepadatan Penduduk', 'Total Penduduk']
        
        if selected_region == "Seluruh Jawa Timur":
            # Compare highest poverty vs highest IPM dynamically
            dist_max_poverty = df_year.loc[df_year['jumlah_penduduk_miskin'].idxmax()]
            dist_max_ipm = df_year.loc[df_year['ipm'].idxmax()]
            
            val_pov_ipm = (dist_max_poverty['ipm'] / avg_ipm) * 100
            val_pov_tpt = (dist_max_poverty['tpt'] / avg_tpt) * 100
            val_pov_miskin = (dist_max_poverty['jumlah_penduduk_miskin'] / avg_miskin) * 100
            val_pov_density = (dist_max_poverty['kepadatan_sipil_tahunan'] / avg_density) * 100
            val_pov_pop = (dist_max_poverty['jumlah_penduduk'] / avg_pop) * 100
            values_poverty = [val_pov_ipm, val_pov_tpt, val_pov_miskin, val_pov_density, val_pov_pop]
            
            val_ipm_ipm = (dist_max_ipm['ipm'] / avg_ipm) * 100
            val_ipm_tpt = (dist_max_ipm['tpt'] / avg_tpt) * 100
            val_ipm_miskin = (dist_max_ipm['jumlah_penduduk_miskin'] / avg_miskin) * 100
            val_ipm_density = (dist_max_ipm['kepadatan_sipil_tahunan'] / avg_density) * 100
            val_ipm_pop = (dist_max_ipm['jumlah_penduduk'] / avg_pop) * 100
            values_ipm = [val_ipm_ipm, val_ipm_tpt, val_ipm_miskin, val_ipm_density, val_ipm_pop]
            
            values_province = [100, 100, 100, 100, 100]
            
            fig = go.Figure()
            fig.add_trace(go.Scatterpolar(
                r=values_poverty, theta=categories, fill='toself',
                name=f"Kemiskinan Tertinggi ({dist_max_poverty['nama_wilayah']})",
                fillcolor='rgba(239, 68, 68, 0.15)',
                line=dict(color='#ef4444', width=2)
            ))
            fig.add_trace(go.Scatterpolar(
                r=values_ipm, theta=categories, fill='toself',
                name=f"IPM Tertinggi ({dist_max_ipm['nama_wilayah']})",
                fillcolor='rgba(13, 148, 136, 0.15)',
                line=dict(color='#0d9488', width=2)
            ))
            fig.add_trace(go.Scatterpolar(
                r=values_province, theta=categories, fill='toself',
                name='Rata-rata Jawa Timur', fillcolor='rgba(148, 163, 184, 0.05)',
                line=dict(color='#94a3b8', width=1.5, dash='dash')
            ))
            
            max_val_range = max(max(values_poverty), max(values_ipm))
            fig.update_layout(
                polar=dict(radialaxis=dict(visible=True, range=[0, max(max_val_range + 20, 140)])),
                template=chart_theme, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                title=f"Profil Radar: Perbandingan Wilayah Ekstrem vs Rata-rata Provinsi (Rasio %)"
            )
            st.plotly_chart(fig, use_container_width=True)
            
            st.markdown("""
                <div style="background-color:rgba(59,130,246,0.06); border-radius:8px; padding:15px; border:1px solid rgba(59,130,246,0.15); font-size:0.85rem; line-height:1.5;">
                    <b>Penjelasan Grafik Radar:</b><br>
                    Grafik radar membandingkan profil multi-dimensi wilayah berdasarkan rasio persen (%) terhadap rata-rata provinsi (garis abu-abu putus-putus = 100%). 
                    Grafik di atas membandingkan wilayah dengan angka <b>Kemiskinan Tertinggi</b> (Merah) dan <b>IPM Tertinggi</b> (Hijau Toska) 
                    untuk melihat kontras struktur sosial kependudukan secara visual. Anda dapat memilih kabupaten/kota tertentu di dropdown atas untuk melihat profil daerah Anda sendiri.
                </div>
            """, unsafe_allow_html=True)
            
        else:
            df_reg_sel = df_year[df_year['nama_wilayah'] == selected_region].iloc[0]
            
            val_ipm = (df_reg_sel['ipm'] / avg_ipm) * 100
            val_tpt = (df_reg_sel['tpt'] / avg_tpt) * 100
            val_miskin = (df_reg_sel['jumlah_penduduk_miskin'] / avg_miskin) * 100
            val_density = (df_reg_sel['kepadatan_sipil_tahunan'] / avg_density) * 100
            val_pop = (df_reg_sel['jumlah_penduduk'] / avg_pop) * 100
            
            values_region = [val_ipm, val_tpt, val_miskin, val_density, val_pop]
            values_province = [100, 100, 100, 100, 100]
            
            fig = go.Figure()
            fig.add_trace(go.Scatterpolar(
                r=values_region, theta=categories, fill='toself',
                name=selected_region, fillcolor='rgba(59, 130, 246, 0.2)',
                line=dict(color='#3b82f6', width=2)
            ))
            fig.add_trace(go.Scatterpolar(
                r=values_province, theta=categories, fill='toself',
                name='Rata-rata Jawa Timur', fillcolor='rgba(148, 163, 184, 0.1)',
                line=dict(color='#94a3b8', width=1.5, dash='dash')
            ))
            fig.update_layout(
                polar=dict(radialaxis=dict(visible=True, range=[0, max(max(values_region) + 20, 140)])),
                template=chart_theme, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                title=f"Profil Radar: {selected_region} vs Provinsi (Rasio %)"
            )
            st.plotly_chart(fig, use_container_width=True)
            
            st.markdown("""
                <div style="background-color:rgba(59,130,246,0.06); border-radius:8px; padding:15px; border:1px solid rgba(59,130,246,0.15); font-size:0.85rem; line-height:1.5;">
                    <b>Penjelasan Grafik Radar:</b><br>
                    Grafik radar di atas menunjukkan profil daerah <b>%s</b> terhadap rata-rata provinsi (100%%). 
                    Sumbu yang menjorok keluar menunjukkan aspek di mana wilayah ini melebihi rata-rata provinsi, sedangkan sumbu yang menjorok ke dalam menunjukkan aspek di bawah rata-rata.
                </div>
            """ % selected_region, unsafe_allow_html=True)

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
        border_color="#ef4444"
    )
with col_m2:
    render_metric_card(
        title="Rata-rata IPM Provinsi",
        value=f"{avg_ipm_prov:.2f}",
        change_val=change_ipm,
        is_positive_good=True,
        border_color="#0d9488"
    )
with col_m3:
    render_metric_card(
        title="Rata-rata TPT Provinsi",
        value=f"{avg_tpt_prov:.2f} %",
        change_val=change_tpt,
        is_positive_good=False,
        border_color="#d97706"
    )
with col_m4:
    render_metric_card(
        title="Rerata Kepadatan Penduduk",
        value=f"{avg_dens_prov:,.1f} Jiwa/KM²",
        change_val=change_dens,
        is_positive_good=False,
        border_color="#8b5cf6"
    )
