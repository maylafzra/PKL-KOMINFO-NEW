import streamlit as st
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from utils.load_data import load_master
from utils.styling import inject_custom_css, render_custom_sidebar

# Check if xgboost is available
try:
    import xgboost as xgb
    use_xgb = True
except ImportError:
    use_xgb = False

# Page Config (Managed by Home.py)


# Initialize theme mode in session state if not present
if "theme_mode" not in st.session_state:
    st.session_state["theme_mode"] = "Sistem"

# Inject dynamic theme CSS
inject_custom_css(st.session_state["theme_mode"])

# Render custom sidebar
render_custom_sidebar("SPK")

# Load master data
df = load_master()

# Header Banner
st.markdown("""
    <div class="dashboard-banner">
        <div class="banner-title">Decision Matrix Dashboard: SPK</div>
        <div class="banner-desc">
            Sistem pendukung keputusan bagi formulasi kebijakan pembangunan Bappeda Jawa Timur. 
            Gunakan matriks interaktif untuk mengeksplorasi rekomendasi taktis khusus per daerah.
        </div>
    </div>
""", unsafe_allow_html=True)

# Train Model and Get Predictions (Cached)
df_train = df[df['tahun'] < 2025].copy()
features = ['jumlah_penduduk', 'ipm', 'tpt', 'kepadatan_sipil_tahunan', 'rasio_jenis_kelamin', 'laju_pertumbuhan']
target = 'jumlah_penduduk_miskin'

df_train_clean = df_train.dropna(subset=features + [target])
X_train, y_train = df_train_clean[features], df_train_clean[target]

@st.cache_resource
def train_model(use_xgb_flag):
    if use_xgb_flag:
        model_obj = xgb.XGBRegressor(n_estimators=100, max_depth=4, learning_rate=0.08, random_state=42)
    else:
        model_obj = RandomForestRegressor(n_estimators=100, random_state=42)
    model_obj.fit(X_train, y_train)
    return model_obj

model = train_model(use_xgb)

@st.cache_data
def get_projections():
    forecast_results = []
    for code, group in df.groupby('kode_wilayah'):
        proj_features = {}
        group_sorted = group.sort_values(by='tahun')
        years_history = group_sorted['tahun'].values.reshape(-1, 1)
        
        for feat in features:
            feat_history = group_sorted[feat].values
            if np.any(np.isnan(feat_history)):
                feat_df = pd.Series(feat_history).interpolate(method='linear').fillna(method='bfill').fillna(method='ffill')
                feat_history = feat_df.values
                
            reg = LinearRegression().fit(years_history, feat_history)
            proj_features[feat] = reg.predict(np.array([[2026], [2027], [2028]]))
        
        df_future = pd.DataFrame(proj_features)
        df_future['tahun'] = [2026, 2027, 2028]
        df_future['kode_wilayah'] = code
        df_future['nama_wilayah'] = group_sorted['nama_wilayah'].iloc[0]
        df_future['tipe_wilayah'] = group_sorted['tipe_wilayah'].iloc[0]
        
        df_future['jumlah_penduduk_miskin_pred'] = model.predict(df_future[features])
        forecast_results.append(df_future)
        
    return pd.concat(forecast_results).reset_index(drop=True)

df_forecast = get_projections()

# Prioritization classification for 2026
df_2026 = df_forecast[df_forecast['tahun'] == 2026].copy()
q_low = df_2026['jumlah_penduduk_miskin_pred'].quantile(0.33)
q_high = df_2026['jumlah_penduduk_miskin_pred'].quantile(0.66)

def categorize_priority(val):
    if val >= q_high:
        return 'Tinggi'
    elif val >= q_low:
        return 'Sedang'
    else:
        return 'Rendah'

df_2026['prioritas'] = df_2026['jumlah_penduduk_miskin_pred'].apply(categorize_priority)

# Count priority summaries
priority_counts = df_2026['prioritas'].value_counts()
high_count = priority_counts.get('Tinggi', 0)
medium_count = priority_counts.get('Sedang', 0)
low_count = priority_counts.get('Rendah', 0)

# Layout Grid: Left Column (Decision Matrix), Right Column (Dynamic Recommendations)
col_left, col_right = st.columns([1, 1])

with col_left:
    st.markdown("<h4 style='font-size:1.1rem; font-weight:700; margin-bottom:15px;'>Matriks Pengelompokan Wilayah (2026)</h4>", unsafe_allow_html=True)
    
    # 3 Summary stats
    col_s1, col_s2, col_s3 = st.columns(3)
    with col_s1:
        st.markdown(f"""
            <div class="spk-urgency-card" style="border-left: 4px solid #ef4444;">
                <div style="color:#ef4444; font-size:0.75rem; font-weight:700; letter-spacing:0.05em;">TINGGI</div>
                <div style="font-size:1.8rem; font-weight:800; color:var(--text-color); margin:2px 0;">{high_count}</div>
                <div style="font-size:0.7rem; color:#64748b;">Daerah Sangat Urgen</div>
            </div>
        """, unsafe_allow_html=True)
    with col_s2:
        st.markdown(f"""
            <div class="spk-urgency-card" style="border-left: 4px solid #d97706;">
                <div style="color:#d97706; font-size:0.75rem; font-weight:700; letter-spacing:0.05em;">SEDANG</div>
                <div style="font-size:1.8rem; font-weight:800; color:var(--text-color); margin:2px 0;">{medium_count}</div>
                <div style="font-size:0.7rem; color:#64748b;">Daerah Pemantauan</div>
            </div>
        """, unsafe_allow_html=True)
    with col_s3:
        st.markdown(f"""
            <div class="spk-urgency-card" style="border-left: 4px solid #0d9488;">
                <div style="color:#0d9488; font-size:0.75rem; font-weight:700; letter-spacing:0.05em;">RENDAH</div>
                <div style="font-size:1.8rem; font-weight:800; color:var(--text-color); margin:2px 0;">{low_count}</div>
                <div style="font-size:0.7rem; color:#64748b;">Daerah Relatif Stabil</div>
            </div>
        """, unsafe_allow_html=True)
        
    st.write("")
    
    # Selection of District to show Dynamic Recommendation
    list_districts = sorted(df_2026['nama_wilayah'].unique().tolist())
    selected_district = st.selectbox("Pilih Kabupaten/Kota untuk Analisis Kebijakan:", list_districts, index=0)
    
    # Priority matrix list
    st.markdown("<h5 style='font-size:0.92rem; font-weight:700; margin-bottom:10px;'>Status Prioritas Kabupaten/Kota</h5>", unsafe_allow_html=True)
    
    df_sorted = df_2026.sort_values(by='jumlah_penduduk_miskin_pred', ascending=False).reset_index(drop=True)
    df_show = df_sorted[['nama_wilayah', 'prioritas', 'jumlah_penduduk_miskin_pred']].rename(columns={
        'nama_wilayah': 'Kabupaten/Kota',
        'prioritas': 'Kelas Prioritas',
        'jumlah_penduduk_miskin_pred': 'Prediksi Kemiskinan 2026 (Ribu Jiwa)'
    })
    
    search_q = st.text_input("Saring Berdasarkan Nama Daerah:", "", key="spk_search", placeholder="Cari kabupaten/kota...")
    if search_q:
        df_show = df_show[df_show['Kabupaten/Kota'].str.contains(search_q, case=False)]
        
    st.dataframe(df_show, use_container_width=True, hide_index=True)

with col_right:
    st.markdown("<h4 style='font-size:1.1rem; font-weight:700; margin-bottom:15px;'>Rekomendasi Kebijakan Dinamis Bappeda</h4>", unsafe_allow_html=True)
    
    # Get details for selected district
    row_district = df_2026[df_2026['nama_wilayah'] == selected_district].iloc[0]
    prio_class = row_district['prioritas']
    pred_val = row_district['jumlah_penduduk_miskin_pred']
    
    # Historical data to find the trend
    df_hist_reg = df[(df['nama_wilayah'] == selected_district) & (df['tahun'] == 2025)].iloc[0]
    act_val = df_hist_reg['jumlah_penduduk_miskin']
    
    # Customized recommendation plan based on priority class
    if prio_class == 'Tinggi':
        prio_badge = '<span class="priority-badge priority-high">Tinggi (Sangat Urgen)</span>'
        prio_border = "#ef4444"
        prio_details = f'<li><b>Perluasan Bantuan Sosial Terpadu:</b> Menjangkau target sasaran proyeksi sebesar <b>{pred_val:,.2f} ribu jiwa</b> miskin di {selected_district}.</li><li><b>Akselerasi Program Padat Karya:</b> Penyediaan lapangan kerja temporer guna menekan tingkat pengangguran daerah.</li><li><b>Pemenuhan Infrastruktur Dasar:</b> Mempercepat pembangunan akses air bersih, sanitasi, dan fasilitas sekolah guna mendongkrak IPM wilayah.</li>'
    elif prio_class == 'Sedang':
        prio_badge = '<span class="priority-badge priority-medium">Sedang (Pemantauan)</span>'
        prio_border = "#d97706"
        prio_details = f'<li><b>Pemberdayaan Ekonomi Lokal & UMKM:</b> Stimulus permodalan usaha mikro guna menjaga ketahanan ekonomi keluarga pra-sejahtera di {selected_district}.</li><li><b>Program Pelatihan Kerja Tematik:</b> Pelatihan vokasi kerja berbasis kompetensi lokal guna mencegah pengangguran.</li><li><b>Sistem Pemantauan Spasial:</b> Melakukan analisis kerawanan kemiskinan bulanan agar tidak merosot ke zona prioritas tinggi.</li>'
    else:
        prio_badge = '<span class="priority-badge priority-low">Rendah (Relatif Stabil)</span>'
        prio_border = "#0d9488"
        prio_details = f'<li><b>Inovasi Layanan Publik (Smart City):</b> Mendorong pelayanan publik berbasis digital penuh guna efisiensi layanan sipil di {selected_district}.</li><li><b>Investasi Bernilai Tambah Tinggi:</b> Mendorong investasi padat teknologi yang ramah lingkungan untuk keberlanjutan wilayah.</li><li><b>Penguatan Logistik Wilayah:</b> Meningkatkan infrastruktur logistik penunjang distribusi barang antar-kabupaten.</li>'
        
    recommendation_html = f'<div class="premium-card" style="border-top: 5px solid {prio_border};"><h5 style="font-size:1.15rem; font-weight:700; margin-top:0; margin-bottom:8px;">{selected_district}</h5><div style="margin-bottom:15px;">Status Prioritas: {prio_badge}</div><div style="font-size:0.88rem; line-height:1.5; margin-bottom:15px; opacity:0.9;">Berdasarkan evaluasi model, jumlah penduduk miskin di {selected_district} pada tahun 2026 diproyeksikan mencapai <b>{pred_val:,.3f} ribu jiwa</b> (dibandingkan tahun 2025 sebesar <b>{act_val:,.3f} ribu jiwa</b>). Tingkat prioritas pembangunan untuk wilayah ini diklasifikasikan sebagai <b>{prio_class}</b>.</div><h6 style="font-size:0.92rem; font-weight:700; margin-bottom:8px;">Usulan Agenda Taktis Bappeda:</h6><ul style="font-size:0.85rem; line-height:1.6; padding-left:18px; margin-bottom:0; opacity:0.85;">{prio_details}</ul></div>'
    
    st.markdown(recommendation_html, unsafe_allow_html=True)
    
    # Extra Bappeda RPJMD target guidelines
    st.markdown("""
        <div style="background-color:rgba(128,128,128,0.05); border-radius:8px; padding:15px; border:1px solid rgba(128,128,128,0.12); font-size:0.82rem; line-height:1.4; opacity:0.85;">
            <b>Panduan Strategis RPJMD Jatim:</b><br>
            Setiap agenda taktis di atas harus diintegrasikan ke dalam Rencana Kerja Pemerintah Daerah (RKPD) tahunan 
            dan diprioritaskan alokasinya melalui skema Anggaran Pendapatan dan Belanja Daerah (APBD) Jawa Timur.
        </div>
    """, unsafe_allow_html=True)
