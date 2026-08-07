import streamlit as st

# Setup Page Configuration
st.set_page_config(
    page_title="Dashboard Pembangunan Jawa Timur",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize global theme mode
if "theme_mode" not in st.session_state:
    st.session_state["theme_mode"] = "Sistem"

# Define Pages with Material Icons
beranda = st.Page("pages/0_Beranda.py", title="Beranda", icon=":material/home:", default=True)
monitoring = st.Page("pages/1_Monitoring_Pembangunan.py", title="Monitoring Pembangunan", icon=":material/trending_up:")
spasial = st.Page("pages/2_Analisis_Spasial.py", title="Analisis Spasial", icon=":material/map:")
prediksi = st.Page("pages/3_Prediksi_Kemiskinan.py", title="Prediksi Kemiskinan", icon=":material/analytics:")
spk = st.Page("pages/4_Sistem_Pendukung_Keputusan.py", title="Sistem Pendukung Keputusan", icon=":material/gavel:")

# Setup Top Navigation (Moving sidebar menu to the top)
pg = st.navigation([beranda, monitoring, spasial, prediksi, spk], position="top")

# Run the router — this renders whichever page is active.
# Do NOT put page content below this line; it would leak into every page.
pg.run()