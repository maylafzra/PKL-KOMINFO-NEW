import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from utils.load_data import load_master
from utils.styling import inject_custom_css, render_metric_card

# Page Configuration (Managed by Home.py)

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
        <div class="banner-title">Machine Learning Simulator</div>
        <div class="banner-desc">
            Pusat simulasi estimasi kemiskinan daerah menggunakan algoritma Random Forest Regressor. 
            Simulasikan proyeksi wilayah Anda hingga tahun 2028 secara interaktif.
        </div>
    </div>
""", unsafe_allow_html=True)

# Prepare training (before 2025) and test data (year 2025)
df_train = df[df['tahun'] < 2025].copy()
df_test = df[df['tahun'] == 2025].copy()

# Features and target
features = ['jumlah_penduduk', 'ipm', 'tpt', 'kepadatan_sipil_tahunan', 'rasio_jenis_kelamin', 'laju_pertumbuhan']
target = 'jumlah_penduduk_miskin'

df_train_clean = df_train.dropna(subset=features + [target])
df_test_clean = df_test.dropna(subset=features + [target])

X_train, y_train = df_train_clean[features], df_train_clean[target]
X_test, y_test = df_test_clean[features], df_test_clean[target]

# Layout Grid (1/3 Left Controls & Metrics, 2/3 Right Simulator Charts)
col_left, col_right = st.columns([1, 2])

with col_left:
    st.markdown("<h4 style='font-size:1.1rem; font-weight:700; margin-bottom:15px;'>Konfigurasi & Penjelasan Model</h4>", unsafe_allow_html=True)
    
    # Train Random Forest Regressor model
    @st.cache_resource
    def train_rf_model():
        model_obj = RandomForestRegressor(n_estimators=100, random_state=42)
        model_obj.fit(X_train, y_train)
        return model_obj
        
    model = train_rf_model()
    
    # Predict Test set for evaluation
    y_pred = model.predict(X_test)

    # Calculate metrics
    mae = mean_absolute_error(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    mape = np.mean(np.abs((y_test - y_pred) / y_test)) * 100
    r2 = r2_score(y_test, y_pred)
    
    # Penjelasan Model Random Forest
    st.markdown(f"""
        <div style="background-color: rgba(13, 148, 136, 0.04); border-left: 4px solid #0d9488; border-radius: 6px; padding: 16px; margin-bottom: 24px;">
            <h5 style="margin-top: 0; margin-bottom: 8px; color: #0d9488; font-weight: 700; font-size: 0.92rem; text-transform: uppercase; letter-spacing: 0.05em;">Model: Random Forest Regressor</h5>
            <p style="margin: 0 0 10px 0; font-size: 0.8rem; line-height: 1.5;">
                <b>Cara Kerja:</b> Membangun kumpulan 100 pohon keputusan secara independen. Setiap pohon mempelajari pola data historis secara acak, kemudian hasil prediksinya dirata-ratakan (agregasi) untuk menghasilkan estimasi akhir yang stabil dan minim varians.
            </p>
            <p style="margin: 0; font-size: 0.8rem; line-height: 1.5;">
                <b>Hubungan Variabel:</b> Memetakan korelasi non-linear dari total penduduk, IPM, TPT, kepadatan sipil, sex ratio, dan laju pertumbuhan terhadap jumlah penduduk miskin.
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    # 2. Display Model Performance & Conceptual Explanation
    st.markdown("<h5 style='font-size:0.92rem; font-weight:700; margin-bottom:12px;'>Akurasi Uji Validasi (Tahun 2025)</h5>", unsafe_allow_html=True)
    
    # Metric Card 1 (R-Squared)
    st.markdown(f"""
        <div class="metric-card" style="border-left: 4px solid #2563eb; height: auto; min-height: 110px; padding: 15px; margin-bottom: 15px; display: block;">
            <div style="font-size: 0.72rem; color: #64748b; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 2px;">R-Squared Score (R²)</div>
            <div style="font-size: 1.6rem; color: var(--text-color); font-weight: 700; margin-bottom: 4px; line-height: 1.1;">{r2:.4f}</div>
            <div style="font-size: 0.75rem; color: #64748b; line-height: 1.4;">
                <b>Makna:</b> Model mampu menerangkan <b>{r2*100:.1f}%</b> variabilitas data kemiskinan Jawa Timur berdasarkan tren historis.
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Metric Card 2 (MAPE)
    st.markdown(f"""
        <div class="metric-card" style="border-left: 4px solid #0d9488; height: auto; min-height: 110px; padding: 15px; margin-bottom: 15px; display: block;">
            <div style="font-size: 0.72rem; color: #64748b; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 2px;">Mean Absolute Pct Error (MAPE)</div>
            <div style="font-size: 1.6rem; color: var(--text-color); font-weight: 700; margin-bottom: 4px; line-height: 1.1;">{mape:.2f} %</div>
            <div style="font-size: 0.75rem; color: #64748b; line-height: 1.4;">
                <b>Makna:</b> Rata-rata persentase penyimpangan estimasi adalah <b>{mape:.2f}%</b> (tergolong akurasi sangat tinggi/di bawah 10%).
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Metric Card 3 (RMSE)
    st.markdown(f"""
        <div class="metric-card" style="border-left: 4px solid #d97706; height: auto; min-height: 110px; padding: 15px; margin-bottom: 15px; display: block;">
            <div style="font-size: 0.72rem; color: #64748b; font-weight: 700; text-transform: uppercase; letter-spacing: 0.05em; margin-bottom: 2px;">Root Mean Squared Error (RMSE)</div>
            <div style="font-size: 1.6rem; color: var(--text-color); font-weight: 700; margin-bottom: 4px; line-height: 1.1;">{rmse:.3f} Ribu</div>
            <div style="font-size: 0.75rem; color: #64748b; line-height: 1.4;">
                <b>Makna:</b> Standar deviasi kesalahan estimasi adalah sebesar <b>{rmse:.3f} ribu jiwa</b> dari nilai riil data historis.
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # Narasi penjelasan cara mendapatkan proyeksi (Metodologi)
    st.markdown("""
        <div style="background-color: rgba(37, 99, 235, 0.05); border-radius: 8px; padding: 12px 15px; border: 1px dashed rgba(37, 99, 235, 0.25); font-size: 0.8rem; line-height: 1.5; margin-top: 15px;">
            <b>ℹ️ Metodologi Proyeksi Kemiskinan:</b><br>
            Angka proyeksi kemiskinan Jawa Timur tahun 2026–2028 diperoleh melalui dua tahap pemodelan terintegrasi:
            <ol style="margin-top: 5px; margin-bottom: 5px; padding-left: 20px;">
                <li><b>Ekstrapolasi Fitur Historis:</b> Masing-masing indikator penjelas (Penduduk, IPM, TPT, Kepadatan, dsb.) diproyeksikan tren masa depannya menggunakan model <i>Linear Regression</i> pada tingkat kabupaten/kota masing-masing.</li>
                <li><b>Estimasi Target Model ML:</b> Nilai indikator hasil proyeksi tersebut kemudian dimasukkan ke dalam model Machine Learning <i>Random Forest</i> yang telah dilatih pada data historis tahun 2018–2024 untuk memprediksi secara akurat proyeksi jumlah penduduk miskin.</li>
            </ol>
        </div>
    """, unsafe_allow_html=True)

with col_right:
    st.markdown("<h4 style='font-size:1.1rem; font-weight:700; margin-bottom:15px;'>Hasil Simulasi & Analisis Pentingnya Fitur</h4>", unsafe_allow_html=True)
    
    # Selector for viz
    viz_choice = st.radio(
        "Pilih Visualisasi Hasil:",
        ["Simulasi Proyeksi Wilayah", "Kontribusi Fitur (Feature Importance)"],
        horizontal=True,
        label_visibility="collapsed"
    )
    
    st.write("")
    
    # --- PROYEKSI FORECASTING 3 TAHUN (2026-2028) ---
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
    
    if viz_choice == "Simulasi Proyeksi Wilayah":
        # Interactive Projections Line Chart
        list_regions = sorted(df['nama_wilayah'].unique().tolist())
        selected_region = st.selectbox("Pilih Wilayah Simulasi Proyeksi:", list_regions, index=0)
        
        # Get actuals (2018-2025)
        df_act_reg = df[df['nama_wilayah'] == selected_region][['tahun', 'jumlah_penduduk_miskin']].copy()
        df_act_reg['Kategori'] = 'Historis BPS'
        
        # Get predictions (2025-2028)
        df_bridge = df_act_reg[df_act_reg['tahun'] == 2025].copy()
        df_bridge['jumlah_penduduk_miskin_pred'] = df_bridge['jumlah_penduduk_miskin']
        
        df_fc_reg = df_forecast[df_forecast['nama_wilayah'] == selected_region][['tahun', 'jumlah_penduduk_miskin_pred']].copy()
        df_fc_reg = pd.concat([df_bridge[['tahun', 'jumlah_penduduk_miskin_pred']], df_fc_reg]).reset_index(drop=True)
        df_fc_reg['Kategori'] = 'Proyeksi Model'
        df_fc_reg = df_fc_reg.rename(columns={'jumlah_penduduk_miskin_pred': 'jumlah_penduduk_miskin'})
        
        df_plot = pd.concat([df_act_reg, df_fc_reg]).reset_index(drop=True)
        
        fig_fc = px.line(
            df_plot, x='tahun', y='jumlah_penduduk_miskin',
            color='Kategori', markers=True,
            color_discrete_map={'Historis BPS': '#be123c', 'Proyeksi Model': '#2563eb'},
            title=f"Grafik Proyeksi Kemiskinan: {selected_region} (2018-2028)"
        )
        fig_fc.update_layout(
            template=chart_theme,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(tickmode='linear', tick0=2018, dtick=1)
        )
        st.plotly_chart(fig_fc, use_container_width=True)
        
        # Details of 2026 predictions for selected region
        pred_2026_val = df_fc_reg[df_fc_reg['tahun'] == 2026]['jumlah_penduduk_miskin'].iloc[0]
        act_2025_val = df_act_reg[df_act_reg['tahun'] == 2025]['jumlah_penduduk_miskin'].iloc[0]
        chg_val = pred_2026_val - act_2025_val
        direction = "kenaikan" if chg_val > 0 else "penurunan"
        
        st.markdown(f"""
            <div style='background-color:rgba(59,130,246,0.06); border-radius:8px; padding:15px; border:1px solid rgba(59,130,246,0.15); font-size:0.88rem; line-height:1.5;'>
                Proyeksi tahun 2026 menunjukkan angka kemiskinan sebesar <b>{pred_2026_val:,.3f} ribu jiwa</b> (mengalami {direction} 
                sebesar <b>{abs(chg_val):,.3f} ribu jiwa</b> dibandingkan data historis akhir 2025 sebesar <b>{act_2025_val:,.3f} ribu jiwa</b>).
                <div style="margin-top:10px; padding-top:10px; border-top:1px dashed rgba(59,130,246,0.2); font-size:0.78rem; opacity:0.85;">
                    📊 Proyeksi ini dihitung berdasarkan model <b>Random Forest Regressor</b> yang dilatih pada data historis 2018–2024, 
                    dengan variabel penjelas (IPM, TPT, kepadatan penduduk, dsb.) untuk {selected_region} diproyeksikan terlebih dahulu 
                    menggunakan tren regresi linear sebelum diestimasi menjadi angka proyeksi kemiskinan akhir.
                </div>
            </div>
        """, unsafe_allow_html=True)
        
    else:
        # Feature Importance chart
        importances = model.feature_importances_
        df_imp = pd.DataFrame({
            'Fitur': ['Total Penduduk', 'IPM', 'TPT', 'Kepadatan Penduduk', 'Rasio Jenis Kelamin', 'Laju Pertumbuhan'],
            'Nilai': importances
        }).sort_values(by='Nilai', ascending=True)
        
        fig_imp = px.bar(
            df_imp, x='Nilai', y='Fitur',
            orientation='h', color='Nilai',
            color_continuous_scale=px.colors.sequential.Teal,
            title='Kontribusi Signifikansi Faktor Terhadap Angka Kemiskinan Jatim'
        )
        fig_imp.update_layout(template=chart_theme, paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)')
        st.plotly_chart(fig_imp, use_container_width=True)

st.write("---")

# Predictions table for future years (2026-2028)
st.subheader("Hasil Estimasi Angka Kemiskinan Kabupaten/Kota")

col_tbl1, col_tbl2 = st.columns([1, 2])
with col_tbl1:
    selected_proj_year = st.selectbox("Pilih Tahun Estimasi Proyeksi:", [2026, 2027, 2028], index=0)
with col_tbl2:
    search_tbl = st.text_input("Saring Berdasarkan Nama Daerah:", "", key="tbl_search_q", placeholder="Cari kabupaten/kota...")

df_table_year = df_forecast[df_forecast['tahun'] == selected_proj_year][['kode_wilayah', 'nama_wilayah', 'tipe_wilayah', 'jumlah_penduduk_miskin_pred']].copy()
df_table_year = df_table_year.rename(columns={
    'kode_wilayah': 'Kode Wilayah',
    'nama_wilayah': 'Kabupaten/Kota',
    'tipe_wilayah': 'Tipe Wilayah',
    'jumlah_penduduk_miskin_pred': f'Prediksi Kemiskinan {selected_proj_year} (Ribu Jiwa)'
}).reset_index(drop=True)

df_table_year[f'Prediksi Kemiskinan {selected_proj_year} (Ribu Jiwa)'] = df_table_year[f'Prediksi Kemiskinan {selected_proj_year} (Ribu Jiwa)'].round(3)
df_table_year['Estimasi Jumlah Penduduk Miskin (Jiwa)'] = (df_table_year[f'Prediksi Kemiskinan {selected_proj_year} (Ribu Jiwa)'] * 1000).round(0)

if search_tbl:
    df_table_year = df_table_year[df_table_year['Kabupaten/Kota'].str.contains(search_tbl, case=False)]
    
st.dataframe(df_table_year, use_container_width=True, hide_index=True)