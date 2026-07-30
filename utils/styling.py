import streamlit as st

def inject_custom_css(theme_mode="Sistem"):
    """
    Menginjeksikan CSS kustom bertema formal instansi pemerintah dengan pilihan
    tiga tema: Sistem, Terang (Light Mode), dan Gelap (Dark Mode).
    Juga menyamakan tinggi seluruh kotak kecil metrik dan statistik secara presisi.
    Serta mendesain top navigation bar (Header) berwarna biru sesuai revisi mentor.
    """
    if theme_mode == "Terang":
        bg_color = "#f8fafc"
        text_color = "#1e293b"
        sidebar_bg = "#ffffff"
        sidebar_text = "#1e293b"
        card_bg = "#ffffff"
        card_border = "#e2e8f0"
        card_hover_border = "#3b82f6"
        card_shadow = "0 1px 3px rgba(0, 0, 0, 0.05)"
        metric_title_color = "#64748b"
        metric_value_color = "#0f172a"
        banner_bg = "linear-gradient(135deg, #1e3a8a 0%, #3b82f6 100%)"
        banner_title_color = "#ffffff"
        banner_desc_color = "#bfdbfe"
        hero_gradient = "linear-gradient(180deg, rgba(255, 255, 255, 0.35) 0%, rgba(248, 250, 252, 0.75) 100%)"
    elif theme_mode == "Gelap":
        bg_color = "#0f172a"
        text_color = "#f8fafc"
        sidebar_bg = "#1e293b"
        sidebar_text = "#f8fafc"
        card_bg = "#1e293b"
        card_border = "#334155"
        card_hover_border = "#3b82f6"
        card_shadow = "0 4px 6px rgba(0, 0, 0, 0.15)"
        metric_title_color = "#94a3b8"
        metric_value_color = "#f8fafc"
        banner_bg = "linear-gradient(135deg, #0b1329 0%, #1e3a8a 100%)"
        banner_title_color = "#ffffff"
        banner_desc_color = "#93c5fd"
        hero_gradient = "linear-gradient(180deg, rgba(15, 23, 42, 0.4) 0%, rgba(30, 41, 59, 0.85) 100%)"
    else:  # Sistem (Menggunakan variabel CSS bawaan Streamlit)
        bg_color = "var(--background-color)"
        text_color = "var(--text-color)"
        sidebar_bg = "var(--secondary-background-color)"
        sidebar_text = "var(--text-color)"
        card_bg = "var(--secondary-background-color)"
        card_border = "rgba(128, 128, 128, 0.2)"
        card_hover_border = "var(--primary-color)"
        card_shadow = "0 1px 2px rgba(0, 0, 0, 0.05)"
        metric_title_color = "var(--text-color)"
        metric_value_color = "var(--text-color)"
        banner_bg = "linear-gradient(135deg, #1e3a8a 0%, #2563eb 100%)"
        banner_title_color = "#ffffff"
        banner_desc_color = "#bfdbfe"
        hero_gradient = "linear-gradient(180deg, rgba(255, 255, 255, 0.35) 0%, rgba(248, 250, 252, 0.75) 100%)"

    st.markdown(f"""
        <style>
        /* Impor font profesional */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');
        
        :root {{
            --hero-gradient: {hero_gradient};
        }}
        
        @media (prefers-color-scheme: dark) {{
            :root {{
                --hero-gradient: {"linear-gradient(180deg, rgba(15, 23, 42, 0.4) 0%, rgba(30, 41, 59, 0.85) 100%)" if theme_mode == "Sistem" else hero_gradient};
            }}
        }}
        
        /* Tema Dasar Aplikasi */
        html, body, [class*="css"], .stApp {{
            font-family: 'Inter', sans-serif;
            background-color: {bg_color} !important;
            color: {text_color} !important;
        }}
        
        /* Tema Sidebar */
        [data-testid="stSidebar"] {{
            background-color: {sidebar_bg} !important;
            border-right: 1px solid {card_border} !important;
        }}
        
        [data-testid="stSidebar"] * {{
            color: {sidebar_text} !important;
        }}
        
        /* DESAIN TOP NAVIGATION BAR (Header Biru Instansi Pemerintah) */
        .stAppHeader, header[data-testid="stHeader"] {{
            background-color: #1e3a8a !important; /* Warna biru resmi */
            border-bottom: 2px solid #152b66 !important;
            height: 60px !important;
            z-index: 999999 !important;
        }}
        
        /* Memaksa semua tulisan dan ikon di navbar atas berwarna putih */
        .stAppHeader *, header[data-testid="stHeader"] * {{
            color: #ffffff !important;
            fill: #ffffff !important;
            border-bottom: none !important; /* Pastikan tidak ada border di child element */
        }}
        
        /* Hover item menu navigasi atas */
        .stAppHeader a:hover *, header[data-testid="stHeader"] a:hover *,
        .stAppHeader button:hover *, header[data-testid="stHeader"] button:hover * {{
            color: #bfdbfe !important; /* Warna biru muda saat hover */
            fill: #bfdbfe !important;
        }}
        
        /* Desain item navigasi atas yang aktif - MENAMPILKAN PILL HIGHLIGHT (TANPA GARIS BAWAH) */
        .stAppHeader a[aria-current="page"], header[data-testid="stHeader"] a[aria-current="page"],
        .stAppHeader button[aria-current="page"], header[data-testid="stHeader"] button[aria-current="page"] {{
            background-color: rgba(255, 255, 255, 0.15) !important; /* Latar belakang semi transparan */
            border-radius: 4px !important;
            border-bottom: none !important; /* Hapus garis bawah sepenuhnya */
            padding: 6px 12px !important;
        }}
        
        .stAppHeader a[aria-current="page"] *, header[data-testid="stHeader"] a[aria-current="page"] *,
        .stAppHeader button[aria-current="page"] *, header[data-testid="stHeader"] button[aria-current="page"] * {{
            color: #ffffff !important;
            font-weight: 700 !important;
            border-bottom: none !important; /* Hapus garis bawah sepenuhnya dari teks/ikon */
        }}
        
        /* Menghilangkan navigasi bawaan di dalam sidebar (karena sudah pindah ke atas) */
        [data-testid="stSidebarNav"] {{
            display: none !important;
        }}
        
        /* Banner Dashboard Resmi */
        .dashboard-banner {{
            background: {banner_bg};
            border-radius: 12px;
            padding: 30px;
            margin-bottom: 25px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            box-shadow: {card_shadow};
        }}
        .banner-title {{
            font-size: 2rem;
            font-weight: 800;
            color: {banner_title_color};
            margin-bottom: 8px;
        }}
        .banner-desc {{
            font-size: 1rem;
            color: {banner_desc_color};
            max-width: 800px;
            line-height: 1.5;
        }}
        
        /* Kartu Informasi Premium */
        .premium-card {{
            background-color: {card_bg};
            border-radius: 12px;
            padding: 24px;
            border: 1px solid {card_border};
            margin-bottom: 20px;
            box-shadow: {card_shadow};
            transition: all 0.25s ease-in-out;
        }}
        .premium-card:hover {{
            border-color: {card_hover_border};
            transform: translateY(-2px);
        }}
        
        /* Kotak Metrik dengan Tinggi yang Sama Presisi */
        .metric-card {{
            background-color: {card_bg};
            border-radius: 12px;
            padding: 18px 20px;
            border: 1px solid {card_border};
            text-align: left;
            position: relative;
            overflow: hidden;
            box-shadow: {card_shadow};
            transition: all 0.25s ease;
            height: 140px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            box-sizing: border-box;
        }}
        .metric-card:hover {{
            transform: translateY(-2px);
            border-color: {card_hover_border};
        }}
        .metric-card::before {{
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            width: 4px;
            height: 100%;
            background-color: #3b82f6;
        }}
        .metric-title {{
            font-size: 0.75rem;
            color: {metric_title_color};
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.05em;
            margin-bottom: 4px;
        }}
        .metric-value {{
            font-size: 1.6rem;
            color: {metric_value_color};
            font-weight: 700;
            margin-bottom: 2px;
            line-height: 1.1;
        }}
        .metric-change {{
            font-size: 0.75rem;
            font-weight: 600;
            display: flex;
            align-items: center;
            gap: 4px;
        }}
        .change-up {{
            color: #10b981;
        }}
        .change-down {{
            color: #ef4444;
        }}
        .change-neutral {{
            color: #64748b;
        }}
        
        /* Kotak Statistik Berukuran Sama Presisi di Landing Page */
        .landing-stat-card {{
            background-color: {card_bg};
            padding: 18px 15px;
            border-radius: 12px;
            border: 1px solid {card_border};
            text-align: center;
            box-shadow: {card_shadow};
            height: 165px;
            display: flex;
            flex-direction: column;
            justify-content: center;
            box-sizing: border-box;
        }}
        
        /* Kotak Fitur Berukuran Sama Presisi di Landing Page */
        .landing-feature-card {{
            background-color: {card_bg};
            border: 1px solid {card_border};
            border-radius: 12px;
            padding: 24px;
            box-shadow: {card_shadow};
            height: 280px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            box-sizing: border-box;
            transition: all 0.25s ease;
        }}
        .landing-feature-card:hover {{
            border-color: {card_hover_border};
            transform: translateY(-2px);
        }}
        
        /* Kotak Urgensi SPK Berukuran Sama Presisi */
        .spk-urgency-card {{
            background-color: {card_bg};
            border-radius: 12px;
            padding: 22px;
            box-shadow: {card_shadow};
            height: 160px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            box-sizing: border-box;
            text-align: center;
        }}
        
        /* Progress Bar Kustom untuk SaaS Command Center */
        .progress-bar-container {{
            width: 100%;
            background-color: rgba(128, 128, 128, 0.15);
            border-radius: 4px;
            height: 6px;
            overflow: hidden;
            margin-top: 4px;
        }}
        .progress-bar-fill {{
            height: 100%;
            border-radius: 4px;
            transition: width 0.4s ease-in-out;
        }}
        
        /* Item Daftar Wilayah (SaaS style) */
        .list-item-card {{
            background-color: {card_bg};
            padding: 10px 14px;
            border-radius: 8px;
            border: 1px solid {card_border};
            margin-bottom: 8px;
            transition: all 0.2s ease-in-out;
        }}
        .list-item-card:hover {{
            border-color: {card_hover_border};
            background-color: rgba(59, 130, 246, 0.05);
        }}
        
        /* Badge Urgensi/Prioritas */
        .priority-badge {{
            padding: 4px 10px;
            border-radius: 9999px;
            font-size: 0.72rem;
            font-weight: 700;
            text-transform: uppercase;
            display: inline-block;
        }}
        .priority-high {{
            background-color: rgba(239, 68, 68, 0.1);
            color: #ef4444;
            border: 1px solid rgba(239, 68, 68, 0.2);
        }}
        .priority-medium {{
            background-color: rgba(245, 158, 11, 0.1);
            color: #d97706;
            border: 1px solid rgba(245, 158, 11, 0.2);
        }}
        .priority-low {{
            background-color: rgba(16, 185, 129, 0.1);
            color: #059669;
            border: 1px solid rgba(16, 185, 129, 0.2);
        }}
        </style>
    """, unsafe_allow_html=True)

def render_metric_card(title, value, change_val=None, is_positive_good=True, border_color="#3b82f6"):
    """
    Merender kartu metrik formal dengan struktur HTML kustom yang disematkan kelas tinggi seragam.
    """
    change_html = ""
    if change_val is not None:
        is_up = change_val > 0
        sign = "+" if is_up else ""
        
        if change_val == 0:
            change_html = f'<div class="metric-change change-neutral">0.00% vs tahun sebelumnya</div>'
        else:
            is_good = is_up if is_positive_good else not is_up
            class_name = "change-up" if is_good else "change-down"
            direction_str = "Kenaikan" if is_up else "Penurunan"
            change_html = f'<div class="metric-change {class_name}">{direction_str} {sign}{change_val:.2f}% vs tahun sebelumnya</div>'
            
    st.markdown(f"""
        <div class="metric-card" style="border-left: 4px solid {border_color};">
            <div class="metric-title">{title}</div>
            <div class="metric-value">{value}</div>
            {change_html}
        </div>
    """, unsafe_allow_html=True)

def render_theme_selector():
    """
    Hanya merender pemilih tema di sidebar karena navigasi halaman
    sekarang ditangani secara terpusat oleh top navigation bar Streamlit.
    """
    theme_mode = st.session_state.get("theme_mode", "Sistem")
    st.sidebar.markdown("<br><br><div style='font-size: 0.72rem; font-weight: 600; color: #64748b; margin-bottom: 6px;'>PENGATURAN TEMA</div>", unsafe_allow_html=True)
    t_index = ["Sistem", "Terang", "Gelap"].index(theme_mode)
    new_theme = st.sidebar.selectbox(
        "Pilih Tema:",
        ["Sistem", "Terang", "Gelap"],
        index=t_index,
        key="theme_mode_selector_sidebar",
        label_visibility="collapsed"
    )
    if new_theme != theme_mode:
        st.session_state["theme_mode"] = new_theme
        st.rerun()

def render_custom_sidebar(active_page="Home"):
    """
    Fallback untuk kompatibilitas ke belakang. Hanya memanggil render_theme_selector
    karena menu navigasi utama sudah berpindah ke top navbar.
    """
    render_theme_selector()
