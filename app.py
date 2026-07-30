import streamlit as st
from utils.styling import render_theme_selector

# Page Configuration — HARUS dipanggil sekali saja di file entry point ini,
# jangan dipanggil lagi di Home.py atau di dalam pages/*.py
st.set_page_config(
    page_title="Dashboard Pembangunan Jawa Timur",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Inisialisasi mode tema global (dipakai oleh semua halaman)
if "theme_mode" not in st.session_state:
    st.session_state["theme_mode"] = "Sistem"

# Panel kecil di sidebar kiri khusus untuk pengaturan tema
# (navigasi antar halaman sekarang ada di navbar atas, bukan di sidebar lagi)
render_theme_selector()

# Daftar halaman dashboard. Urutan di sini = urutan tampil di navbar atas.
pages = [
    st.Page("Home.py", title="Beranda", default=True),
    st.Page("pages/1_Monitoring_Pembangunan.py", title="Monitoring Pembangunan"),
    st.Page("pages/2_Analisis_Spasial.py", title="Analisis Spasial"),
    st.Page("pages/3_Prediksi_Kemiskinan.py", title="Prediksi Kemiskinan"),
    st.Page("pages/4_Sistem_Pendukung_Keputusan.py", title="Sistem Pendukung Keputusan"),
]

# position="top" -> ini yang membuat menu navigasi tampil sebagai navbar di atas,
# bukan lagi sebagai daftar link di sidebar kiri.
pg = st.navigation(pages, position="top")
pg.run()
