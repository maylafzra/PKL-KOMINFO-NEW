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
        card_hover_border = "#4069AF"
        card_shadow = "0 1px 3px rgba(0, 0, 0, 0.05)"
        metric_title_color = "#64748b"
        metric_value_color = "#0f172a"
        banner_bg = "linear-gradient(135deg, #354599 0%, #4069AF 100%)"
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
        card_hover_border = "#4069AF"
        card_shadow = "0 4px 6px rgba(0, 0, 0, 0.15)"
        metric_title_color = "#94a3b8"
        metric_value_color = "#f8fafc"
        banner_bg = "linear-gradient(135deg, #0b1329 0%, #354599 100%)"
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
        banner_bg = "linear-gradient(135deg, #354599 0%, #4069AF 100%)"
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
        
        /* ===== Navbar Atas Kominfo ===== */
        html body [data-testid="stHeader"] {{
            background: linear-gradient(90deg, #1a2a63 0%, #354599 55%, #4069AF 100%) !important;
            border-bottom: 3px solid #43C4F0 !important;
            box-shadow: 0 2px 12px rgba(0, 0, 0, 0.18) !important;
            height: 64px !important;
        }}

        /* Link-link menu navbar atas: teks putih terang, dipaksa juga ke semua elemen anak */
        html body [data-testid="stTopNavLink"],
        html body [data-testid="stTopNavLink"] *,
        html body [data-testid="stTopNavLink"] span,
        html body [data-testid="stTopNavLink"] p {{
            color: #eef1fb !important;
            fill: #eef1fb !important;
            opacity: 1 !important;
            font-weight: 500 !important;
            border-radius: 8px !important;
            transition: all 0.2s ease-in-out !important;
        }}

        html body [data-testid="stTopNavLink"]:hover {{
            background-color: rgba(255, 255, 255, 0.12) !important;
            color: #ffffff !important;
        }}

        /* Halaman aktif: latar putih transparan + garis bawah aksen cyan */
        html body [data-testid="stTopNavLink"][aria-current="page"] {{
            background-color: rgba(255, 255, 255, 0.18) !important;
            font-weight: 700 !important;
            box-shadow: inset 0 -3px 0 0 #43C4F0 !important;
        }}
        html body [data-testid="stTopNavLink"][aria-current="page"],
        html body [data-testid="stTopNavLink"][aria-current="page"] *,
        html body [data-testid="stTopNavLink"][aria-current="page"] span,
        html body [data-testid="stTopNavLink"][aria-current="page"] p {{
            color: #ffffff !important;
            fill: #ffffff !important;
        }}

        /* Baris yang membungkus semua link navbar: kumpulan menu digeser ke tengah,
           jarak antar-menu dibikin sama rata pakai gap (bukan mepet ke kiri lagi) */
        html body *:has(> [data-testid="stTopNavLinkContainer"]) {{
            display: flex !important;
            flex: 1 1 auto !important;
            width: 100% !important;
            justify-content: center !important;
            align-items: center !important;
            gap: 36px !important;
        }}

        /* Ikon menu (toolbar, deploy button, dsb) di header ikut putih agar kontras */
        html body [data-testid="stHeader"] svg {{
            fill: #ffffff !important;
        }}

        /* ===== Konten halaman dibuat memenuhi lebar layar (tidak mepet ke tengah) ===== */
        html body [data-testid="stMainBlockContainer"],
        html body .block-container {{
            max-width: 100% !important;
            padding-left: 3rem !important;
            padding-right: 3rem !important;
            padding-top: 5.5rem !important;
        }}

        /* ===== Sidebar kiri kini hanya berisi panel kecil "Pengaturan Tema" ===== */
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
            background-color: #4069AF;
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
            background-color: {link_hover_bg if 'link_hover_bg' in locals() else 'rgba(59, 130, 246, 0.05)'};
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

def render_metric_card(title, value, change_val=None, is_positive_good=True, border_color="#4069AF"):
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
    Menghias sidebar bawaan Streamlit agar terlihat premium dan menambahkan ikon vektor SVG
    secara dinamis di samping teks link navigasi menggunakan CSS (Tanpa HTML kustom / Tanpa Emoji).
    Memperbaiki tulisan hilang saat diklik (active) dan merapatkan jarak antar link (tidak lebar).
    """
    theme_mode = st.session_state.get("theme_mode", "Sistem")
    
    # Menentukan warna teks dan latar belakang tautan aktif/hover
    if theme_mode == "Terang":
        icon_color = "%23475569"         # Slate-600
        icon_active = "%232563eb"        # Blue-600 (Ikon biru di latar belakang soft blue)
        link_hover_bg = "rgba(59, 130, 246, 0.08)"
        link_active_bg = "rgba(59, 130, 246, 0.12)" # Soft blue background
        link_color = "#475569"
        link_active_color = "#2563eb"    # Teks biru (tidak hilang/terbaca jelas)
    elif theme_mode == "Gelap":
        icon_color = "%2394a3b8"         # Slate-400
        icon_active = "%2360a5fa"        # Blue-400
        link_hover_bg = "rgba(59, 130, 246, 0.12)"
        link_active_bg = "rgba(59, 130, 246, 0.2)"
        link_color = "#94a3b8"
        link_active_color = "#60a5fa"
    else:  # Sistem
        icon_color = "%23475569"
        icon_active = "var(--primary-color)"
        link_hover_bg = "rgba(128, 128, 128, 0.1)"
        link_active_bg = "rgba(59, 130, 246, 0.12)"
        link_color = "var(--text-color)"
        link_active_color = "var(--primary-color)"

    # SVG Icon Definitions (URL Encoded)
    svg_home = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="{icon_color}" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>'
    svg_home_active = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="{icon_active}" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>'
    
    svg_mon = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="{icon_color}" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/></svg>'
    svg_mon_active = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="{icon_active}" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/></svg>'
    
    svg_spa = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="{icon_color}" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><polygon points="1 6 1 22 8 18 16 22 23 18 23 2 16 6 8 2 1 6"/><line x1="8" y1="2" x2="8" y2="18"/><line x1="16" y1="6" x2="16" y2="22"/></svg>'
    svg_spa_active = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="{icon_active}" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><polygon points="1 6 1 22 8 18 16 22 23 18 23 2 16 6 8 2 1 6"/><line x1="8" y1="2" x2="8" y2="18"/><line x1="16" y1="6" x2="16" y2="22"/></svg>'
    
    svg_pred = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="{icon_color}" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><rect x="4" y="4" width="16" height="16" rx="2" ry="2"/><rect x="9" y="9" width="6" height="6"/><line x1="9" y1="1" x2="9" y2="4"/><line x1="15" y1="1" x2="15" y2="4"/><line x1="9" y1="20" x2="9" y2="23"/><line x1="15" y1="20" x2="15" y2="23"/><line x1="20" y1="9" x2="23" y2="9"/><line x1="20" y1="15" x2="23" y2="15"/><line x1="1" y1="9" x2="4" y2="9"/><line x1="1" y1="15" x2="4" y2="15"/></svg>'
    svg_pred_active = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="{icon_active}" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><rect x="4" y="4" width="16" height="16" rx="2" ry="2"/><rect x="9" y="9" width="6" height="6"/><line x1="9" y1="1" x2="9" y2="4"/><line x1="15" y1="1" x2="15" y2="4"/><line x1="9" y1="20" x2="9" y2="23"/><line x1="15" y1="20" x2="15" y2="23"/><line x1="20" y1="9" x2="23" y2="9"/><line x1="20" y1="15" x2="23" y2="15"/><line x1="1" y1="9" x2="4" y2="9"/><line x1="1" y1="15" x2="4" y2="15"/></svg>'
    
    svg_spk = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="{icon_color}" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/></svg>'
    svg_spk_active = f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="{icon_active}" stroke-width="2.2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><circle cx="12" cy="12" r="6"/><circle cx="12" cy="12" r="2"/></svg>'

    # URL Encode SVGs manually for CSS safety
    import urllib.parse
    enc_home = urllib.parse.quote(svg_home)
    enc_home_act = urllib.parse.quote(svg_home_active)
    enc_mon = urllib.parse.quote(svg_mon)
    enc_mon_act = urllib.parse.quote(svg_mon_active)
    enc_spa = urllib.parse.quote(svg_spa)
    enc_spa_act = urllib.parse.quote(svg_spa_active)
    enc_pred = urllib.parse.quote(svg_pred)
    enc_pred_act = urllib.parse.quote(svg_pred_active)
    enc_spk = urllib.parse.quote(svg_spk)
    enc_spk_act = urllib.parse.quote(svg_spk_active)

    # Menginjeksikan CSS kustom untuk memperindah dan merapatkan sidebar bawaan Streamlit
    st.markdown(f"""
        <style>
        /* Tampilkan navigasi bawaan Streamlit */
        [data-testid="stSidebarNav"] {{
            display: block !important;
            padding-top: 10px !important;
        }}
        
        /* Hilangkan header 'Pages' bawaan Streamlit */
        [data-testid="stSidebarNav"] > div {{
            display: none !important;
        }}
        
        /* Merapatkan daftar menu */
        [data-testid="stSidebarNav"] ul {{
            display: flex !important;
            flex-direction: column !important;
            gap: 2px !important; /* Dirapatkan agar jarak antar menu tidak lebar */
            padding: 0 !important;
            margin: 0 !important;
            list-style: none !important;
        }}
        
        /* Hilangkan margin/padding bawaan list item */
        [data-testid="stSidebarNav"] ul li {{
            padding: 0 !important;
            margin: 0 !important;
        }}
        
        /* Mengatur link navigasi */
        [data-testid="stSidebarNav"] ul li a {{
            display: flex !important;
            align-items: center !important;
            padding: 8px 12px 8px 38px !important; /* Padding dirapatkan secara vertikal */
            border-radius: 6px !important;
            text-decoration: none !important;
            font-size: 0.88rem !important;
            font-weight: 500 !important;
            position: relative !important;
            transition: all 0.2s ease-in-out !important;
            background-color: transparent !important;
            color: {link_color} !important;
        }}
        
        /* Selesaikan masalah teks menghilang: paksa warna text span & div */
        [data-testid="stSidebarNav"] ul li a span,
        [data-testid="stSidebarNav"] ul li a div {{
            color: inherit !important;
            font-weight: inherit !important;
        }}
        
        [data-testid="stSidebarNav"] ul li a:hover {{
            background-color: {link_hover_bg} !important;
            color: {icon_active.replace('%23', '#')} !important;
        }}
        
        /* Status Link Aktif (aria-current="page") */
        [data-testid="stSidebarNav"] ul li a[aria-current="page"] {{
            background-color: {link_active_bg} !important;
            color: {link_active_color} !important;
            font-weight: 600 !important;
        }}
        
        /* Menambahkan Ikon SVG menggunakan CSS ::before */
        [data-testid="stSidebarNav"] ul li a::before {{
            content: '';
            position: absolute;
            left: 12px;
            top: 50%;
            transform: translateY(-50%);
            width: 16px;
            height: 16px;
            background-size: contain;
            background-repeat: no-repeat;
            transition: all 0.2s ease;
        }}
        
        /* Menautkan ikon ke masing-masing posisi urutan link di sidebar */
        /* Link 1: Home / Beranda */
        [data-testid="stSidebarNav"] ul li:nth-child(1) a::before {{
            background-image: url('data:image/svg+xml;utf8,{enc_home}');
        }}
        [data-testid="stSidebarNav"] ul li:nth-child(1) a[aria-current="page"]::before {{
            background-image: url('data:image/svg+xml;utf8,{enc_home_act}');
        }}
        
        /* Link 2: Monitoring Pembangunan */
        [data-testid="stSidebarNav"] ul li:nth-child(2) a::before {{
            background-image: url('data:image/svg+xml;utf8,{enc_mon}');
        }}
        [data-testid="stSidebarNav"] ul li:nth-child(2) a[aria-current="page"]::before {{
            background-image: url('data:image/svg+xml;utf8,{enc_mon_act}');
        }}
        
        /* Link 3: Analisis Spasial */
        [data-testid="stSidebarNav"] ul li:nth-child(3) a::before {{
            background-image: url('data:image/svg+xml;utf8,{enc_spa}');
        }}
        [data-testid="stSidebarNav"] ul li:nth-child(3) a[aria-current="page"]::before {{
            background-image: url('data:image/svg+xml;utf8,{enc_spa_act}');
        }}
        
        /* Link 4: Prediksi Kemiskinan */
        [data-testid="stSidebarNav"] ul li:nth-child(4) a::before {{
            background-image: url('data:image/svg+xml;utf8,{enc_pred}');
        }}
        [data-testid="stSidebarNav"] ul li:nth-child(4) a[aria-current="page"]::before {{
            background-image: url('data:image/svg+xml;utf8,{enc_pred_act}');
        }}
        
        /* Link 5: Sistem Pendukung Keputusan */
        [data-testid="stSidebarNav"] ul li:nth-child(5) a::before {{
            background-image: url('data:image/svg+xml;utf8,{enc_spk}');
        }}
        [data-testid="stSidebarNav"] ul li:nth-child(5) a[aria-current="page"]::before {{
            background-image: url('data:image/svg+xml;utf8,{enc_spk_act}');
        }}
        </style>
    """, unsafe_allow_html=True)
    
    # Menempatkan pengaturan tema secara native di paling bawah sidebar
    st.sidebar.markdown("<br><br><br><br><br><br><br><br><br><br><hr style='margin: 15px 0;'>", unsafe_allow_html=True)
    st.sidebar.markdown("<div style='font-size: 0.72rem; font-weight: 600; color: #64748b; margin-bottom: 6px;'>PENGATURAN TEMA</div>", unsafe_allow_html=True)
    
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
