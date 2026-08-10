import base64
from pathlib import Path

import streamlit as st

from utils.styling import inject_custom_css, render_custom_sidebar
from utils.load_data import load_master

# Inject dynamic theme CSS (theme_mode is already initialized in app.py)
inject_custom_css(st.session_state["theme_mode"])

# Render custom sidebar (if you're using the icon sidebar in addition to top nav)
render_custom_sidebar("Home")

# Load master data to dynamically highlight counts
try:
    df = load_master()
    total_records = len(df)
    total_regions = df['nama_wilayah'].nunique()
    df_2025 = df[df['tahun'] == 2025]
    total_population_2025 = df_2025['jumlah_penduduk'].sum() / 1e6  # Juta
except Exception:
    total_records = 304
    total_regions = 38
    total_population_2025 = 42.09

BASE_DIR = Path(__file__).resolve().parent.parent
ASSETS_DIR = BASE_DIR / "assets"


def to_base64(path: Path):
    """Encode image to base64 data URI."""
    ext = path.suffix.lower().lstrip(".")
    mime = "jpeg" if ext in ("jpg", "jpeg") else ext
    with open(path, "rb") as f:
        encoded = base64.b64encode(f.read()).decode()
    return f"data:image/{mime};base64,{encoded}"


def find_and_encode(assets_dir: Path, base_name: str):
    """Search for base_name image across extensions and return base64 URI."""
    for ext in (".png", ".jpg", ".jpeg", ".webp", ".svg"):
        candidate = assets_dir / f"{base_name}{ext}"
        if candidate.exists():
            return to_base64(candidate)
    return None


logo_kominfo_b64 = find_and_encode(ASSETS_DIR, "logo_kominfo")
logo_unair_b64 = find_and_encode(ASSETS_DIR, "logo_unair")
logo_ftmm_b64 = find_and_encode(ASSETS_DIR, "logo_ftmm")
logo_lengkap_b64 = find_and_encode(ASSETS_DIR, "logo_lengkap")
hero_bg_b64 = find_and_encode(ASSETS_DIR, "logo_pembangunan")

# Header Logos Strip with Rentang Periode & Integrasi on the top-right
logo_html = '<div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 25px; padding-bottom: 15px; border-bottom: 1px solid rgba(128,128,128,0.15);">'
logo_html += '<div style="display: flex; align-items: center; gap: 20px;">'
if logo_lengkap_b64:
    logo_html += f'<img src="{logo_lengkap_b64}" style="height: 65px; width: auto; object-fit: contain;" alt="Logo Lengkap">'
else:
    if logo_kominfo_b64:
        logo_html += f'<img src="{logo_kominfo_b64}" style="height: 65px; width: auto; object-fit: contain;" alt="Logo Kominfo">'
    if logo_unair_b64:
        logo_html += f'<img src="{logo_unair_b64}" style="height: 50px; width: auto; object-fit: contain;" alt="Logo Unair">'
    if logo_ftmm_b64:
        logo_html += f'<img src="{logo_ftmm_b64}" style="height: 65px; width: auto; object-fit: contain;" alt="Logo FTMM">'
logo_html += '</div>'
logo_html += """
<div style="display: flex; gap: 12px; font-size: 0.82rem; align-items: center;">
    <div style="background: rgba(217, 119, 6, 0.08); color: #d97706; padding: 6px 12px; border-radius: 6px; border: 1px solid rgba(217, 119, 6, 0.2); font-weight: 600; display: flex; align-items: center; gap: 6px;">
        <span>📅</span>
        <span>Periode: 2018-2025</span>
    </div>
    <div style="background: rgba(124, 58, 237, 0.08); color: #7c3aed; padding: 6px 12px; border-radius: 6px; border: 1px solid rgba(124, 58, 237, 0.2); font-weight: 600; display: flex; align-items: center; gap: 6px;">
        <span>🔗</span>
        <span>Integrasi: BPS & Capil</span>
    </div>
</div>
"""
logo_html += "</div>"

st.markdown(logo_html, unsafe_allow_html=True)

# Custom Hero Card Style with pembangunan Background
hero_style = f"""
background: var(--hero-gradient), url('{hero_bg_b64}');
background-size: 100% auto;
background-position: center bottom;
background-repeat: no-repeat;
background-color: #eaf3f8;
"""
st.markdown(
    f"""
    <div style="{hero_style}  min-height: 430px; border-radius: 12px; padding: 50px 40px; border: 1px solid rgba(128,128,128,0.2); margin-bottom: 35px; overflow: hidden;">
        <h1 style="color: #354599; font-size: 2.2rem; font-weight: 800; margin-bottom: 8px;">
            Sistem Informasi Monitoring Pembangunan Daerah
        </h1>
        <h2 style="color: var(--text-color); font-size: 1.25rem; font-weight: 600; margin-bottom: 20px; opacity: 0.85;">
            Dinas Komunikasi dan Informatika Provinsi Jawa Timur
        </h2>
        <div style="font-size: 0.98rem; color: var(--text-color); max-width: 800px; line-height: 1.6; margin-bottom: 30px; opacity: 0.9;">
            Platform analitik ini dirancang untuk memantau, memvisualisasikan, dan menganalisis perkembangan indikator makro 
            kesejahteraan masyarakat di Provinsi Jawa Timur. Sistem ini mengintegrasikan data registrasi sipil kependudukan 
            serta sensus nasional guna menghasilkan analisis spasial dan proyeksi pembangunan daerah.
        </div>
    </div>
    """,
    unsafe_allow_html=True
)

st.subheader("Cakupan Parameter Utama")

# Stat Grid (landing-stat-card class for equal height)
col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)

with col_stat1:
    st.markdown(f"""
        <div class="landing-stat-card">
            <div style="color: #64748b; font-size: 0.72rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em;">Cakupan Wilayah</div>
            <div style="color: #354599; font-size: 2rem; font-weight: 800; margin: 4px 0;">{total_regions}</div>
            <div style="font-size: 0.82rem; opacity: 0.85;">Kabupaten dan Kota</div>
        </div>
    """, unsafe_allow_html=True)

with col_stat2:
    st.markdown("""
        <div class="landing-stat-card">
            <div style="color: #64748b; font-size: 0.72rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em;">Parameter Utama</div>
            <div style="color: #0d9488; font-size: 2rem; font-weight: 800; margin: 4px 0;">4</div>
            <div style="font-size: 0.82rem; opacity: 0.85;">Indikator Pembangunan</div>
        </div>
    """, unsafe_allow_html=True)

with col_stat3:
    st.markdown(f"""
        <div class="landing-stat-card">
            <div style="color: #64748b; font-size: 0.72rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em;">Total Rekam Data</div>
            <div style="color: #d97706; font-size: 2rem; font-weight: 800; margin: 4px 0;">{total_records}</div>
            <div style="font-size: 0.82rem; opacity: 0.85;">Baris Data Terintegrasi</div>
        </div>
    """, unsafe_allow_html=True)

with col_stat4:
    st.markdown(f"""
        <div class="landing-stat-card">
            <div style="color: #64748b; font-size: 0.72rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em;">Jumlah Penduduk</div>
            <div style="color: #7c3aed; font-size: 2rem; font-weight: 800; margin: 4px 0;">{total_population_2025:.2f} Jt</div>
            <div style="font-size: 0.82rem; opacity: 0.85;">Jiwa Jawa Timur (2025)</div>
        </div>
    """, unsafe_allow_html=True)

st.write("")
st.write("")

# Modul Analitik (landing-feature-card class for equal height)
st.subheader("Modul Analitik Sistem")
col_f1, col_f2, col_f3 = st.columns(3)

with col_f1:
    st.markdown("""
        <div class="landing-feature-card">
            <div>
                <h4 style="color: #354599; margin-top: 0; font-weight: 700; font-size: 1.15rem;">Monitoring Pembangunan</h4>
                <p style="font-size: 0.85rem; line-height: 1.5; margin-bottom: 12px; opacity: 0.9; min-height: 60px;">
                    Menyajikan visualisasi tren historis provinsi untuk Indeks Pembangunan Manusia (IPM), Tingkat Pengangguran Terbuka (TPT), 
                    Jumlah Penduduk Miskin, dan Kepadatan Penduduk.
                </p>
            </div>
            <div style="border-top: 1px solid rgba(128,128,128,0.15); padding-top: 10px; margin-top: 10px;">
                <span style="font-size: 0.75rem; font-weight: 700; color: #64748b; text-transform: uppercase; letter-spacing: 0.03em;">Review Data Makro (2025):</span>
                <div style="display: flex; flex-direction: column; gap: 4px; margin-top: 6px;">
                    <div style="display: flex; justify-content: space-between; font-size: 0.8rem;">
                        <span>📈 Rata-rata IPM</span><b style="color: #0d9488;">76.01 (Tinggi)</b>
                    </div>
                    <div style="display: flex; justify-content: space-between; font-size: 0.8rem;">
                        <span>💼 Rata-rata TPT</span><b style="color: #d97706;">3.78%</b>
                    </div>
                    <div style="display: flex; justify-content: space-between; font-size: 0.8rem;">
                        <span>👥 Total Penduduk Miskin</span><b style="color: #be123c;">3.88 Juta Jiwa</b>
                    </div>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

with col_f2:
    st.markdown("""
        <div class="landing-feature-card">
            <div>
                <h4 style="color: #0d9488; margin-top: 0; font-weight: 700; font-size: 1.15rem;">Analisis Geospasial</h4>
                <p style="font-size: 0.85rem; line-height: 1.5; margin-bottom: 12px; opacity: 0.9; min-height: 60px;">
                    Melakukan pemetaan tematik interaktif choropleth untuk melihat persebaran geografis indikator pembangunan serta analisis LISA.
                </p>
            </div>
            <div style="border-top: 1px solid rgba(128,128,128,0.15); padding-top: 10px; margin-top: 10px;">
                <span style="font-size: 0.75rem; font-weight: 700; color: #64748b; text-transform: uppercase; letter-spacing: 0.03em;">Review Metode & Peta:</span>
                <div style="display: flex; flex-direction: column; gap: 4px; margin-top: 6px;">
                    <div style="display: flex; justify-content: space-between; font-size: 0.8rem;">
                        <span>🗺️ Model Spasial</span><b style="color: #0d9488;">Moran's I & LISA</b>
                    </div>
                    <div style="display: flex; justify-content: space-between; font-size: 0.8rem;">
                        <span>🔴 Deteksi Klaster</span><b style="color: #be123c;">Hotspot (High-High)</b>
                    </div>
                    <div style="display: flex; justify-content: space-between; font-size: 0.8rem;">
                        <span>📍 Sumber Peta</span><b style="color: #7c3aed;">BPS Jawa Timur</b>
                    </div>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

with col_f3:
    st.markdown("""
        <div class="landing-feature-card">
            <div>
                <h4 style="color: #d97706; margin-top: 0; font-weight: 700; font-size: 1.15rem;">Proyeksi & Keputusan</h4>
                <p style="font-size: 0.85rem; line-height: 1.5; margin-bottom: 12px; opacity: 0.9; min-height: 60px;">
                    Memproyeksikan data kemiskinan tahun 2026-2028 menggunakan Machine Learning serta mengelompokkan urgensi wilayah.
                </p>
            </div>
            <div style="border-top: 1px solid rgba(128,128,128,0.15); padding-top: 10px; margin-top: 10px;">
                <span style="font-size: 0.75rem; font-weight: 700; color: #64748b; text-transform: uppercase; letter-spacing: 0.03em;">Review Model & Prioritas:</span>
                <div style="display: flex; flex-direction: column; gap: 4px; margin-top: 6px;">
                    <div style="display: flex; justify-content: space-between; font-size: 0.8rem;">
                        <span>🤖 Algoritma Utama</span><b style="color: #d97706;">Random Forest</b>
                    </div>
                    <div style="display: flex; justify-content: space-between; font-size: 0.8rem;">
                        <span>🎯 Target Proyeksi</span><b style="color: #0d9488;">Tahun 2026 - 2028</b>
                    </div>
                    <div style="display: flex; justify-content: space-between; font-size: 0.8rem;">
                        <span>⚖️ Output Rekomendasi</span><b style="color: #7c3aed;">Prioritas Bappeda</b>
                    </div>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

st.markdown("<p style='font-size:0.85rem;color:#64748b;margin-top:40px;'>Silakan gunakan menu navigasi di bagian atas untuk mengakses modul-modul analisis.</p>", unsafe_allow_html=True)