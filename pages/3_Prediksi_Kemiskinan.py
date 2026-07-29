import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from utils.load_data import load_master
from utils.styling import inject_custom_css, render_metric_card, render_custom_sidebar

# Check if xgboost is available
try:
    import xgboost as xgb
    use_xgb = True
except ImportError:
    use_xgb = False

# Page Configuration
st.set_page_config(
    page_title="Prediksi Kemiskinan - Jawa Timur",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize theme mode in session state if not present
if "theme_mode" not in st.session_state:
    st.session_state["theme_mode"] = "Sistem"

# Inject dynamic theme CSS
inject_custom_css(st.session_state["theme_mode"])
chart_theme = "plotly_dark" if st.session_state["theme_mode"] == "Gelap" else "plotly_white"

# Render custom sidebar
render_custom_sidebar("Prediksi")

# Load master data
df = load_master()

# Header Banner
st.markdown("""
    <div class="dashboard-banner">
        <div class="banner-title">Machine Learning Simulator</div>
        <div class="banner-desc">
            Pusat simulasi estimasi kemiskinan daerah. Latih ulang model secara real-time, 
            analisis kontribusi faktor (Feature Importance), serta simulasikan proyeksi wilayah hingga 2028.
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
    st.markdown("<h4 style='font-size:1.1rem; font-weight:700; margin-bottom:15px;'>Kontrol Simulator & Model</h4>", unsafe_allow_html=True)
    
    # 1. Model Configuration
    model_choices = ["Random Forest Regressor"]
    if use_xgb:
        model_choices.insert(0, "XGBoost Regressor")
    
    selected_model_name = st.selectbox(
        "Pilih Algoritma Model:",
        model_choices
    )
    
    # Train selected model dynamically
    @st.cache_resource
    def train_dynamic_model(model_name):
        if model_name == "XGBoost Regressor":
            model_obj = xgb.XGBRegressor(n_estimators=100, max_depth=4, learning_rate=0.08, random_state=42)
        else:
            model_obj = RandomForestRegressor(n_estimators=100, random_state=42)
        model_obj.fit(X_train, y_train)
        return model_obj
        
    model = train_dynamic_model(selected_model_name)
    
    # Predict Test set for evaluation
    y_pred = model.predict(X_test)

    # Calculate metrics
    mae = mean_absolute_error(y_test, y_pred)
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    mape = np.mean(np.abs((y_test - y_pred) / y_test)) * 100
    r2 = r2_score(y_test, y_pred)
    
    st.write("")
    
    # 2. Display Model Performance (Vertical stack in 1/3 column)
    st.markdown("<h5 style='font-size:0.92rem; font-weight:700; margin-bottom:10px;'>Akurasi Uji Validasi (Tahun 2025)</h5>", unsafe_allow_html=True)
    
    render_metric_card("R-Squared Score (R²)", f"{r2:.4f}", border_color="#2563eb")
    render_metric_card("Mean Absolute Pct Error", f"{mape:.2f} %", border_color="#0d9488")
    render_metric_card("Root Mean Squared Error", f"{rmse:.3f} Ribu", border_color="#d97706")

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
    def get_projections(model_name):
        # We pass model_name to invalidate cache when model is switched
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

    df_forecast = get_projections(selected_model_name)
    
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

# Predictions table for 2026 (SaaS style Table)
st.subheader("Hasil Estimasi Angka Kemiskinan Kabupaten/Kota (Tahun 2026)")
df_2026 = df_forecast[df_forecast['tahun'] == 2026][['kode_wilayah', 'nama_wilayah', 'tipe_wilayah', 'jumlah_penduduk_miskin_pred']].copy()
df_2026 = df_2026.rename(columns={
    'kode_wilayah': 'Kode Wilayah',
    'nama_wilayah': 'Kabupaten/Kota',
    'tipe_wilayah': 'Tipe Wilayah',
    'jumlah_penduduk_miskin_pred': 'Prediksi Kemiskinan 2026 (Ribu Jiwa)'
}).reset_index(drop=True)

df_2026['Prediksi Kemiskinan 2026 (Ribu Jiwa)'] = df_2026['Prediksi Kemiskinan 2026 (Ribu Jiwa)'].round(3)
df_2026['Prediksi Jiwa Miskin (Jiwa)'] = (df_2026['Prediksi Kemiskinan 2026 (Ribu Jiwa)'] * 1000).round(0)

# Search
search_tbl = st.text_input("Saring Tabel Hasil Prediksi:", "", key="tbl_search_q", placeholder="Cari kabupaten/kota...")
if search_tbl:
    df_2026 = df_2026[df_2026['Kabupaten/Kota'].str.contains(search_tbl, case=False)]
    
st.dataframe(df_2026, use_container_width=True, hide_index=True)
