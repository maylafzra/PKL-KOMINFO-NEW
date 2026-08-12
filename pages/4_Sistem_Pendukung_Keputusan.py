import streamlit as st
import pandas as pd
import numpy as np
import urllib.request
import json
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from utils.load_data import load_master
from utils.styling import inject_custom_css

# Page Config (Managed by Home.py)

# Initialize theme mode in session state if not present
if "theme_mode" not in st.session_state:
    st.session_state["theme_mode"] = "Sistem"

# Inject dynamic theme CSS
inject_custom_css(st.session_state["theme_mode"])

# Load master data
df = load_master()

# Header Banner
st.markdown("""
    <div class="dashboard-banner">
        <div class="banner-title">Sistem Pendukung Keputusan</div>
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
def train_model():
    model_obj = RandomForestRegressor(n_estimators=100, random_state=42)
    model_obj.fit(X_train, y_train)
    return model_obj

model = train_model()

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

# Centroids for fallback nearest neighbors (consistent with page 2)
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

@st.cache_data(show_spinner="Memuat data geospasial Jawa Timur untuk SPK...")
def get_geojson_jt_spk():
    url = 'https://raw.githubusercontent.com/TheMaggieSimpson/IndonesiaGeoJSON/master/kota-kabupaten.json'
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode('utf-8'))
            data['features'] = [f for f in data['features'] if f['properties'].get('NAME_1') == 'Jawa Timur']
            return data, True
    except Exception:
        return None, False

@st.cache_data(show_spinner="Menghitung matriks ketetanggaan wilayah untuk SPK...")
def get_spatial_adjacency_spk(_geojson):
    from shapely.geometry import shape
    feats = _geojson['features']
    codes = [f['properties'].get('CC_2') for f in feats]
    polys = [shape(f['geometry']).buffer(0) for f in feats]
    n = len(feats)
    W = np.zeros((n, n))
    BUFFER = 0.001  # Queen Contiguity yang akurat
    for i in range(n):
        for j in range(n):
            if i == j:
                continue
            if polys[i].distance(polys[j]) < BUFFER:
                W[i, j] = 1.0
    return codes, W

# Prioritization classification for 2026 using LISA clusters
df_2026 = df_forecast[df_forecast['tahun'] == 2026].copy().reset_index(drop=True)
num_regions = len(df_2026)

geojson_jt, geojson_success = get_geojson_jt_spk()

# Spatial Weights Matrix (Queen Contiguity)
if geojson_success:
    codes_geo, W_geo = get_spatial_adjacency_spk(geojson_jt)
    code_to_geo_idx = {c: i for i, c in enumerate(codes_geo)}
    df_2026_codes = df_2026['kode_wilayah'].astype(str).tolist()
    order = [code_to_geo_idx[c] for c in df_2026_codes]
    W = W_geo[np.ix_(order, order)]
else:
    # Fallback nearest neighbors (k=4)
    codes = list(df_2026['kode_wilayah'].astype(str))
    W = np.zeros((num_regions, num_regions))
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

x = df_2026['jumlah_penduduk_miskin_pred'].values
z = x - x.mean()
spatial_lag = W.dot(z)
z_std = z / np.std(x)
lag_std = spatial_lag / np.std(x)

lisa_types = []
for i in range(num_regions):
    if z_std[i] > 0 and lag_std[i] > 0:
        lisa_types.append('High-High (Sangat Tinggi)')
    elif z_std[i] < 0 and lag_std[i] < 0:
        lisa_types.append('Low-Low (Rendah)')
    elif z_std[i] > 0 and lag_std[i] < 0:
        lisa_types.append('High-Low (Tinggi)')
    else:
        lisa_types.append('Low-High (Sedang)')

df_2026['prioritas'] = lisa_types

# Count priority summaries
priority_counts = df_2026['prioritas'].value_counts()
hh_count = priority_counts.get('High-High (Sangat Tinggi)', 0)
hl_count = priority_counts.get('High-Low (Tinggi)', 0)
lh_count = priority_counts.get('Low-High (Sedang)', 0)
ll_count = priority_counts.get('Low-Low (Rendah)', 0)

# Layout Grid: Left Column (Decision Matrix), Right Column (Dynamic Recommendations)
col_left, col_right = st.columns([1, 1])

with col_left:
    st.markdown("<h4 style='font-size:1.1rem; font-weight:700; margin-bottom:15px;'>Matriks Pengelompokan Wilayah (2026)</h4>", unsafe_allow_html=True)
    
    # 4 Summary stats
    col_s1, col_s2, col_s3, col_s4 = st.columns(4)
    with col_s1:
        st.markdown(f"""
            <div class="spk-urgency-card" style="border-left: 4px solid #ef4444; height: 165px;">
                <div style="color:#ef4444; font-size:0.68rem; font-weight:700; letter-spacing:0.03em;">HIGH-HIGH (HOTSPOT)</div>
                <div style="font-size:1.8rem; font-weight:800; color:var(--text-color); margin:2px 0;">{hh_count}</div>
                <div style="font-size:0.65rem; color:#64748b;">Prioritas 1: Sangat Tinggi</div>
            </div>
        """, unsafe_allow_html=True)
    with col_s2:
        st.markdown(f"""
            <div class="spk-urgency-card" style="border-left: 4px solid #f97316; height: 165px;">
                <div style="color:#f97316; font-size:0.68rem; font-weight:700; letter-spacing:0.03em;">HIGH-LOW (OUTLIER)</div>
                <div style="font-size:1.8rem; font-weight:800; color:var(--text-color); margin:2px 0;">{hl_count}</div>
                <div style="font-size:0.65rem; color:#64748b;">Prioritas 2: Tinggi</div>
            </div>
        """, unsafe_allow_html=True)
    with col_s3:
        st.markdown(f"""
            <div class="spk-urgency-card" style="border-left: 4px solid #3b82f6; height: 165px;">
                <div style="color:#3b82f6; font-size:0.68rem; font-weight:700; letter-spacing:0.03em;">LOW-HIGH (OUTLIER)</div>
                <div style="font-size:1.8rem; font-weight:800; color:var(--text-color); margin:2px 0;">{lh_count}</div>
                <div style="font-size:0.65rem; color:#64748b;">Prioritas 3: Sedang</div>
            </div>
        """, unsafe_allow_html=True)
    with col_s4:
        st.markdown(f"""
            <div class="spk-urgency-card" style="border-left: 4px solid #10b981; height: 165px;">
                <div style="color:#10b981; font-size:0.68rem; font-weight:700; letter-spacing:0.03em;">LOW-LOW (COLDSPOT)</div>
                <div style="font-size:1.8rem; font-weight:800; color:var(--text-color); margin:2px 0;">{ll_count}</div>
                <div style="font-size:0.65rem; color:#64748b;">Prioritas 4: Rendah</div>
            </div>
        """, unsafe_allow_html=True)
        
    st.write("")
    
    # Landasan Metodologi Pembagian Prioritas
    st.markdown("""
        <div style="background-color:rgba(128,128,128,0.05); border-radius:8px; padding:15px; border:1px solid rgba(128,128,128,0.15); font-size:0.8rem; line-height:1.5; margin-bottom:15px;">
            <b>ℹ️ Landasan Statistik Klasifikasi Prioritas:</b><br>
            Pengelompokkan prioritas wilayah tahun 2026 diintegrasikan secara objektif dengan <b>Analisis Spasial LISA (Local Indicators of Spatial Association)</b> berdasarkan proyeksi jumlah penduduk miskin tahun 2026:
            <ul style="margin-top: 5px; margin-bottom: 5px; padding-left: 18px;">
                <li><b>Prioritas 1: Sangat Tinggi (High-High Hotspot)</b>: Wilayah dengan angka kemiskinan tinggi yang dikelilingi oleh wilayah bertetangga yang juga memiliki kemiskinan tinggi. Memerlukan intervensi makro dan program lintas wilayah karena adanya dampak limpahan spasial (*spatial spillover*).</li>
                <li><b>Prioritas 2: Tinggi (High-Low Outlier)</b>: Wilayah dengan angka kemiskinan tinggi tetapi dikelilingi oleh wilayah bertetangga yang memiliki kemiskinan rendah. Merupakan wilayah kantong kemiskinan terisolasi yang memerlukan intervensi lokal terfokus secara spesifik.</li>
                <li><b>Prioritas 3: Sedang (Low-High Outlier)</b>: Wilayah dengan angka kemiskinan rendah tetapi dikelilingi oleh wilayah bertetangga yang memiliki kemiskinan tinggi. Membutuhkan langkah preventif spasial untuk menangkal dampak limpahan negatif dari sekitarnya.</li>
                <li><b>Prioritas 4: Rendah (Low-Low Coldspot)</b>: Wilayah dengan angka kemiskinan rendah dan dikelilingi oleh wilayah bertetangga yang juga memiliki kemiskinan rendah. Menunjukkan kondisi kesejahteraan sosial ekonomi yang stabil secara spasial.</li>
            </ul>
            Metode klasifikasi berbasis 4 kuadran spasial LISA ini merupakan kerangka kerja statistik resmi untuk membantu Bappeda memformulasikan kebijakan pembangunan daerah secara adil, terarah, dan berbasis geospasial.
        </div>
    """, unsafe_allow_html=True)
    
    with st.expander("📚 Dasar Statistik & Perhitungan Klaster LISA (Untuk Ujian/Akademis)"):
        st.markdown(r"""
            ### 1. Landasan Teoretis LISA (Anselin, 1995)
            *Local Indicators of Spatial Association* (LISA) digunakan untuk mengukur seberapa besar kontribusi suatu wilayah secara individual terhadap pembentukan hubungan keruangan (autokorelasi spasial). Ini mendeteksi apakah suatu daerah dikelilingi oleh wilayah bertetangga yang memiliki karakteristik serupa (klaster homogen) atau bertolak belakang (pencilan/outlier).
            
            ### 2. Formulasi Matematika & Perhitungan
            Indeks **Local Moran's $I_i$** untuk masing-masing wilayah $i$ dihitung sebagai berikut:
            $$I_i = \frac{z_i - \bar{z}}{s^2} \sum_{j=1}^{N} w_{ij} (z_j - \bar{z})$$
            Karena data deviasi terhadap rata-rata ($z_i$) sudah dipusatkan ($\bar{z} = 0$), maka rumusnya disederhanakan menjadi:
            $$I_i = \frac{z_i}{s^2} \sum_{j=1}^{N} w_{ij} z_j$$
            Di mana:
            - $N$ = Jumlah kabupaten/kota di Jawa Timur ($38$).
            - $z_i$ = Deviasi nilai indikator wilayah $i$ terhadap rata-rata ($x_i - \bar{x}$).
            - $s^2$ = Varians dari variabel indikator tersebut.
            - $w_{ij}$ = Elemen matriks bobot spasial Queen Contiguity terstandarisasi baris ($\sum_j w_{ij} = 1$).
            - $\sum_{j=1}^{N} w_{ij} z_j$ = **Spatial Lag** dari wilayah $i$ (rata-rata tertimbang dari nilai tetangganya).
            
            ### 3. Dasar Keputusan Pengelompokan Kuadran Moran
            Klasifikasi wilayah didasarkan pada perpaduan tanda positif/negatif koordinat wilayah pada diagram kartesius **Moran Scatterplot**:
            
            *   **High-High (Sangat Tinggi)**
                *   *Syarat*: $z_i > 0$ dan $\text{Lag}_i > 0$.
                *   *Landasan*: Wilayah bernilai tinggi dikelilingi tetangga bernilai tinggi (*hotspot*). Memerlukan koordinasi lintas wilayah karena adanya dampak penularan spasial (*spatial spillover*).
            *   **High-Low (Tinggi)**
                *   *Syarat*: $z_i > 0$ dan $\text{Lag}_i < 0$.
                *   *Landasan*: Wilayah bernilai tinggi dikelilingi tetangga bernilai rendah (*outlier HL*). Merupakan wilayah kantong kemiskinan terisolasi, membutuhkan bantuan lokal terfokus.
            *   **Low-High (Sedang)**
                *   *Syarat*: $z_i < 0$ dan $\text{Lag}_i > 0$.
                *   *Landasan*: Wilayah bernilai rendah dikelilingi tetangga bernilai tinggi (*outlier LH*). Wilayah ini bertindak sebagai penyangga (*buffer*), tetapi rentan terpengaruh dampak buruk wilayah sekitar.
            *   **Low-Low (Rendah)**
                *   *Syarat*: $z_i < 0$ dan $\text{Lag}_i < 0$.
                *   *Landasan*: Wilayah bernilai rendah dikelilingi tetangga bernilai rendah (*coldspot*). Menunjukkan kestabilan wilayah dengan tingkat kemakmuran sosial ekonomi yang baik.
        """)
    
    # Selection of District to show Dynamic Recommendation
    list_districts = sorted(df_2026['nama_wilayah'].unique().tolist())
    selected_district = st.selectbox("Pilih Kabupaten/Kota untuk Analisis Kebijakan:", list_districts, index=0)
    
    # Priority matrix list
    st.markdown("<h5 style='font-size:0.92rem; font-weight:700; margin-bottom:10px;'>Status Prioritas Kabupaten/Kota</h5>", unsafe_allow_html=True)
    
    df_sorted = df_2026.sort_values(by='jumlah_penduduk_miskin_pred', ascending=False).reset_index(drop=True)
    df_sorted['prioritas_label'] = df_sorted['prioritas'].map({
        'High-High (Sangat Tinggi)': 'Sangat Tinggi',
        'High-Low (Tinggi)': 'Tinggi',
        'Low-High (Sedang)': 'Sedang',
        'Low-Low (Rendah)': 'Rendah'
    })
    df_show = df_sorted[['nama_wilayah', 'prioritas_label', 'jumlah_penduduk_miskin_pred']].rename(columns={
        'nama_wilayah': 'Kabupaten/Kota',
        'prioritas_label': 'Kelas Prioritas',
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
    if prio_class == 'High-High (Sangat Tinggi)':
        prio_badge = '<span class="priority-badge priority-high" style="background-color:#ef4444; color:white; padding:3px 8px; border-radius:4px;">Sangat Tinggi (Hotspot)</span>'
        prio_border = "#ef4444"
        prio_details = f'<li><b>Koordinasi Lintas-Wilayah:</b> Melakukan sinkronisasi program penanggulangan kemiskinan dengan wilayah tetangga untuk mengatasi dampak limpahan (*spatial spillover*).</li><li><b>Akselerasi Program Padat Karya:</b> Mengurangi TPT melalui pembangunan infrastruktur desa/kelurahan secara padat karya.</li><li><b>Peningkatan IPM Terintegrasi:</b> Fokus pada peningkatan akses pendidikan dasar dan kesehatan di perbatasan kabupaten.</li>'
    elif prio_class == 'High-Low (Tinggi)':
        prio_badge = '<span class="priority-badge priority-medium" style="background-color:#f97316; color:white; padding:3px 8px; border-radius:4px;">Tinggi (Outlier HL)</span>'
        prio_border = "#f97316"
        prio_details = f'<li><b>Intervensi Kantong Kemiskinan:</b> Fokus program bantuan sosial dan pemberdayaan ekonomi langsung ke kecamatan/desa dengan kerawanan tinggi.</li><li><b>Stimulus UMKM Lokal:</b> Memberikan modal usaha mikro untuk mendorong kemandirian ekonomi keluarga pra-sejahtera.</li><li><b>Optimalisasi Ketenagakerjaan:</b> Mengadakan pelatihan vokasi tematik berbasis potensi lokal guna menyerap angkatan kerja.</li>'
    elif prio_class == 'Low-High (Sedang)':
        prio_badge = '<span class="priority-badge" style="background-color:rgba(59,130,246,0.1); color:#3b82f6; border:1px solid rgba(59,130,246,0.2); padding:3px 8px; border-radius:4px; font-weight:700; text-transform:uppercase; font-size:0.72rem; display:inline-block;">Sedang (Outlier LH)</span>'
        prio_border = "#3b82f6"
        prio_details = f'<li><b>Langkah Preventif Spasial:</b> Memperkuat ketahanan ekonomi wilayah untuk menahan efek limpahan kemiskinan dari wilayah tetangga yang tinggi.</li><li><b>Pengawasan Mobilitas & Sosial:</b> Monitoring sosial ekonomi berkala untuk mendeteksi kerawanan sedini mungkin.</li><li><b>Pengembangan Sentra Ekonomi Perbatasan:</b> Membangun pusat aktivitas ekonomi baru di perbatasan untuk menangkap peluang ekonomi.</li>'
    else: # Low-Low (Rendah)
        prio_badge = '<span class="priority-badge priority-low" style="background-color:#10b981; color:white; padding:3px 8px; border-radius:4px;">Rendah (Coldspot)</span>'
        prio_border = "#10b981"
        prio_details = f'<li><b>Inovasi & Digitalisasi Layanan (Smart City):</b> Mendorong pelayanan publik berbasis digital penuh guna meningkatkan produktivitas daerah.</li><li><b>Investasi Bernilai Tambah Tinggi:</b> Mendorong investasi padat modal and teknologi untuk mendukung pertumbuhan ekonomi berkelanjutan.</li><li><b>Penguatan Jaringan Logistik:</b> Meningkatkan infrastruktur logistik penunjang distribusi barang antar-kabupaten/kota.</li>'
        
    recommendation_html = f'<div class="premium-card" style="border-top: 5px solid {prio_border};"><h5 style="font-size:1.15rem; font-weight:700; margin-top:0; margin-bottom:8px;">{selected_district}</h5><div style="margin-bottom:15px;">Status Prioritas: {prio_badge}</div><div style="font-size:0.88rem; line-height:1.5; margin-bottom:15px; opacity:0.9;">Berdasarkan evaluasi model spasial LISA, jumlah penduduk miskin di {selected_district} pada tahun 2026 diproyeksikan mencapai <b>{pred_val:,.3f} ribu jiwa</b> (dibandingkan tahun 2025 sebesar <b>{act_val:,.3f} ribu jiwa</b>). Tingkat prioritas pembangunan untuk wilayah ini diklasifikasikan sebagai <b>{prio_class}</b>.</div><h6 style="font-size:0.92rem; font-weight:700; margin-bottom:8px;">Usulan Agenda Taktis Bappeda:</h6><ul style="font-size:0.85rem; line-height:1.6; padding-left:18px; margin-bottom:0; opacity:0.85;">{prio_details}</ul></div>'
    
    st.markdown(recommendation_html, unsafe_allow_html=True)
    
    # Extra Bappeda RPJMD target guidelines
    st.markdown("""
        <div style="background-color:rgba(128,128,128,0.05); border-radius:8px; padding:15px; border:1px solid rgba(128,128,128,0.12); font-size:0.82rem; line-height:1.4; opacity:0.85;">
            <b>Panduan Strategis RPJMD Jatim:</b><br>
            Setiap agenda taktis di atas harus diintegrasikan ke dalam Rencana Kerja Pemerintah Daerah (RKPD) tahunan 
            dan diprioritaskan alokasinya melalui skema Anggaran Pendapatan dan Belanja Daerah (APBD) Jawa Timur.
        </div>
    """, unsafe_allow_html=True)

st.write("")
st.markdown("""
    <div style="background-color:rgba(128,128,128,0.05); border-radius:8px; padding:12px 15px; border:1px solid rgba(128,128,128,0.15); font-size:0.8rem; color:#64748b; line-height:1.5; margin-top:10px;">
        <b>ℹ️ Sumber Data Klasifikasi & Kebijakan:</b><br>
        1. <b>Metrik Indikator Penjelas (IPM, TPT, dan Jumlah Penduduk Miskin)</b> bersumber dari <b>Badan Pusat Statistik (BPS) Provinsi Jawa Timur</b> (Periode 2018–2025).<br>
        2. <b>Estimasi Proyeksi & Model Machine Learning</b> dikalkulasi menggunakan algoritma <i>Random Forest Regressor</i> berdasarkan pemodelan data historis Jawa Timur.<br>
        3. <b>Rekomendasi Kebijakan Dinamis</b> diselaraskan dengan prioritas Rencana Pembangunan Jangka Menengah Daerah (RPJMD) <b>Bappeda Provinsi Jawa Timur</b>.
    </div>
""", unsafe_allow_html=True)
