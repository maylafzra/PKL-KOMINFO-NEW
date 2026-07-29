import base64
from pathlib import Path
import streamlit as st
from utils.styling import inject_custom_css, render_custom_sidebar

# Page Configuration
st.set_page_config(
    page_title="Dashboard Pembangunan Jawa Timur",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize global theme mode in session state
if "theme_mode" not in st.session_state:
    st.session_state["theme_mode"] = "Sistem"

# Inject dynamic theme CSS
inject_custom_css(st.session_state["theme_mode"])

# Render custom sidebar with icons (theme selector moves to the bottom automatically)
render_custom_sidebar("Home")

BASE_DIR = Path(__file__).resolve().parent
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
logo_unair_b64   = find_and_encode(ASSETS_DIR, "logo_unair")
logo_ftmm_b64    = find_and_encode(ASSETS_DIR, "logo_ftmm")
hero_bg_b64      = find_and_encode(ASSETS_DIR, "hero_bromo")

# Header Logos Strip (Kominfo Jatim: bulat, Unair: bulat, FTMM: persegi panjang)
logo_html = '<div style="display: flex; align-items: center; gap: 20px; margin-bottom: 25px; padding-bottom: 15px; border-bottom: 1px solid rgba(128,128,128,0.15);">'
if logo_kominfo_b64:
    logo_html += f'<img src="{logo_kominfo_b64}" style="width: 50px; height: 50px; border-radius: 50%; object-fit: cover; background: white; padding: 2px; border: 1px solid #e2e8f0;" alt="Logo Kominfo">'
if logo_unair_b64:
    logo_html += f'<img src="{logo_unair_b64}" style="width: 50px; height: 50px; border-radius: 50%; object-fit: cover; background: white; padding: 2px; border: 1px solid #e2e8f0;" alt="Logo Unair">'
if logo_ftmm_b64:
    logo_html += f'<img src="{logo_ftmm_b64}" style="height: 50px; width: auto; object-fit: contain; background: white; border-radius: 6px; padding: 4px; border: 1px solid #e2e8f0;" alt="Logo FTMM">'
logo_html += "</div>"

st.markdown(logo_html, unsafe_allow_html=True)

# Custom Hero Card Style with Bromo Background (Using transparent overlays to make mountain visible)
hero_style = ""
if hero_bg_b64:
    hero_style = f"""
    background: var(--hero-gradient), url('{hero_bg_b64}');
    background-size: cover;
    background-position: center;
    """
else:
    hero_style = "background: linear-gradient(180deg, var(--secondary-background-color) 0%, var(--background-color) 100%);"

st.markdown(
    f"""
    <div style="{hero_style} border-radius: 12px; padding: 50px 40px; border: 1px solid rgba(128,128,128,0.2); margin-bottom: 35px;">
        <h1 style="color: #1e3a8a; font-size: 2.2rem; font-weight: 800; margin-bottom: 8px;">
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
    st.markdown("""
        <div class="landing-stat-card">
            <div style="color: #64748b; font-size: 0.72rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em;">Cakupan Wilayah</div>
            <div style="color: #1e3a8a; font-size: 2rem; font-weight: 800; margin: 4px 0;">38</div>
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
    st.markdown("""
        <div class="landing-stat-card">
            <div style="color: #64748b; font-size: 0.72rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em;">Rentang Periode</div>
            <div style="color: #d97706; font-size: 2rem; font-weight: 800; margin: 4px 0;">2018-2025</div>
            <div style="font-size: 0.82rem; opacity: 0.85;">Deret Waktu Historis</div>
        </div>
    """, unsafe_allow_html=True)

with col_stat4:
    st.markdown("""
        <div class="landing-stat-card">
            <div style="color: #64748b; font-size: 0.72rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.05em;">Integrasi Institusi</div>
            <div style="color: #7c3aed; font-size: 2.2rem; font-weight: 800; margin: 4px 0;">BPS & Capil</div>
            <div style="font-size: 0.82rem; opacity: 0.85;">Data Terpadu & Valid</div>
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
            <h4 style="color: #1e3a8a; margin-top: 0; font-weight: 700; font-size: 1.1rem;">Monitoring Pembangunan</h4>
            <p style="font-size: 0.85rem; line-height: 1.5; margin-bottom: 0; opacity: 0.9;">
                Menyajikan visualisasi tren historis provinsi untuk Indeks Pembangunan Manusia (IPM), Tingkat Pengangguran Terbuka (TPT), 
                Jumlah Penduduk Miskin, dan Kepadatan Penduduk Sipil, serta analisis profil rinci tingkat wilayah.
            </p>
        </div>
    """, unsafe_allow_html=True)

with col_f2:
    st.markdown("""
        <div class="landing-feature-card">
            <h4 style="color: #0d9488; margin-top: 0; font-weight: 700; font-size: 1.1rem;">Analisis Geospasial</h4>
            <p style="font-size: 0.85rem; line-height: 1.5; margin-bottom: 0; opacity: 0.9;">
                Melakukan pemetaan tematik interaktif choropleth untuk melihat persebaran geografis indikator pembangunan, kalkulasi Moran's I, serta pendeteksian klaster spasial LISA.
            </p>
        </div>
    """, unsafe_allow_html=True)

with col_f3:
    st.markdown("""
        <div class="landing-feature-card">
            <h4 style="color: #d97706; margin-top: 0; font-weight: 700; font-size: 1.1rem;">Proyeksi & Keputusan</h4>
            <p style="font-size: 0.85rem; line-height: 1.5; margin-bottom: 0; opacity: 0.9;">
                Memproyeksikan data kemiskinan tahun 2026 menggunakan model Machine Learning (XGBoost/Random Forest), serta mengelompokkan urgensi wilayah guna mendukung rekomendasi Bappeda.
            </p>
        </div>
    """, unsafe_allow_html=True)
st.markdown("<p style='font-size:0.85rem;color:#64748b;margin-top:40px;'>Silakan gunakan menu navigasi di sebelah kiri untuk mengakses modul-modul analisis.</p>", unsafe_allow_html=True)
