import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np

# ─────────────────────────────────────────────
#  PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="Dashboard Perikanan – UNSOED",
    page_icon=" ",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
#  LOAD & CLEAN DATA — PRODUKSI TANGKAP
# ─────────────────────────────────────────────
@st.cache_data
def load_data():
    df = pd.read_csv(
        "Produksi Perikanan Tangkap di Laut Menurut Komoditas Utama, 2024.csv",
        skiprows=[0, 1, 3],
        header=0,
    )
    df = df.rename(columns={df.columns[0]: "Provinsi"})
    df.columns = ["Provinsi", "Cakalang", "Tongkol", "Tuna", "Udang", "Lainnya", "Jumlah"]
    df = df[~df["Provinsi"].str.strip().str.upper().isin(["INDONESIA", ""])].copy()
    df = df.dropna(subset=["Provinsi"])
    df["Provinsi"] = (
        df["Provinsi"]
        .str.strip()
        .str.replace(r"\s+", " ", regex=True)
        .str.title()
    )
    for col in ["Cakalang", "Tongkol", "Tuna", "Udang", "Lainnya", "Jumlah"]:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)

    region_map = {
        "Aceh": "Sumatera", "Sumatera Utara": "Sumatera", "Sumatera Barat": "Sumatera",
        "Riau": "Sumatera", "Jambi": "Sumatera", "Sumatera Selatan": "Sumatera",
        "Bengkulu": "Sumatera", "Lampung": "Sumatera",
        "Kep. Bangka Belitung": "Sumatera", "Kep. Riau": "Sumatera",
        "Dki Jakarta": "Jawa", "Jawa Barat": "Jawa", "Jawa Tengah": "Jawa",
        "Di Yogyakarta": "Jawa", "Jawa Timur": "Jawa", "Banten": "Jawa",
        "Bali": "Bali & Nusa Tenggara",
        "Nusa Tenggara Barat": "Bali & Nusa Tenggara",
        "Nusa Tenggara Timur": "Bali & Nusa Tenggara",
        "Kalimantan Barat": "Kalimantan", "Kalimantan Tengah": "Kalimantan",
        "Kalimantan Selatan": "Kalimantan", "Kalimantan Timur": "Kalimantan",
        "Kalimantan Utara": "Kalimantan",
        "Sulawesi Utara": "Sulawesi", "Sulawesi Tengah": "Sulawesi",
        "Sulawesi Selatan": "Sulawesi", "Sulawesi Tenggara": "Sulawesi",
        "Gorontalo": "Sulawesi", "Sulawesi Barat": "Sulawesi",
        "Maluku": "Maluku & Papua", "Maluku Utara": "Maluku & Papua",
        "Papua Barat": "Maluku & Papua", "Papua Barat Daya": "Maluku & Papua",
        "Papua": "Maluku & Papua", "Papua Selatan": "Maluku & Papua",
        "Papua Tengah": "Maluku & Papua", "Papua Pegunungan": "Maluku & Papua",
    }
    df["Pulau"] = df["Provinsi"].map(region_map).fillna("Lainnya")
    df["Kategori_Produksi"] = pd.cut(
        df["Jumlah"],
        bins=[0, 100_000, 250_000, 500_000, 9_999_999],
        labels=["Rendah (<100 rb T)", "Sedang (100–250 rb T)",
                "Tinggi (250–500 rb T)", "Sangat Tinggi (>500 rb T)"],
    )
    df_long = df.melt(
        id_vars=["Provinsi", "Pulau", "Jumlah", "Kategori_Produksi"],
        value_vars=["Cakalang", "Tongkol", "Tuna", "Udang", "Lainnya"],
        var_name="Komoditas",
        value_name="Produksi_Ton",
    )
    return df, df_long


# ─────────────────────────────────────────────
#  LOAD & CLEAN DATA — E-COMMERCE TOKOPEDIA
# ─────────────────────────────────────────────
@st.cache_data
def load_ecommerce():
    ec = pd.read_csv("Data ikan baru.csv")

    # Normalize province names to match tangkap dataset (title case, clean)
    ec["Provinsi"] = (
        ec["Provinsi"]
        .str.strip()
        .str.replace(r"\s+", " ", regex=True)
        .str.title()
    )

    # Fix known name differences between the two datasets
    prov_fix = {
        "Dki Jakarta": "DKI Jakarta",
        "Di Yogyakarta": "DI Yogyakarta",
        "Kepulauan Bangka Belitung": "Kep. Bangka Belitung",
        "Kepulauan Riau": "Kep. Riau",
    }
    ec["Provinsi"] = ec["Provinsi"].replace(prov_fix)

    ec["Harga (IDR)"] = pd.to_numeric(ec["Harga (IDR)"], errors="coerce").fillna(0)
    ec["Unit Terjual"] = pd.to_numeric(ec["Unit Terjual"], errors="coerce").fillna(0).astype(int)
    ec["Volume Penjualan (IDR)"] = pd.to_numeric(ec["Volume Penjualan (IDR)"], errors="coerce").fillna(0)
    ec["Rating"] = pd.to_numeric(ec["Rating"], errors="coerce")

    region_map_ec = {
        "Aceh": "Sumatera", "Sumatera Utara": "Sumatera", "Sumatera Barat": "Sumatera",
        "Riau": "Sumatera", "Jambi": "Sumatera", "Sumatera Selatan": "Sumatera",
        "Bengkulu": "Sumatera", "Lampung": "Sumatera",
        "Kep. Bangka Belitung": "Sumatera", "Kep. Riau": "Sumatera",
        "DKI Jakarta": "Jawa", "Jawa Barat": "Jawa", "Jawa Tengah": "Jawa",
        "DI Yogyakarta": "Jawa", "Jawa Timur": "Jawa", "Banten": "Jawa",
        "Bali": "Bali & Nusa Tenggara",
        "Nusa Tenggara Barat": "Bali & Nusa Tenggara",
        "Nusa Tenggara Timur": "Bali & Nusa Tenggara",
        "Kalimantan Barat": "Kalimantan", "Kalimantan Tengah": "Kalimantan",
        "Kalimantan Selatan": "Kalimantan", "Kalimantan Timur": "Kalimantan",
        "Kalimantan Utara": "Kalimantan",
        "Sulawesi Utara": "Sulawesi", "Sulawesi Tengah": "Sulawesi",
        "Sulawesi Selatan": "Sulawesi", "Sulawesi Tenggara": "Sulawesi",
        "Gorontalo": "Sulawesi", "Sulawesi Barat": "Sulawesi",
        "Maluku": "Maluku & Papua", "Maluku Utara": "Maluku & Papua",
        "Papua Barat": "Maluku & Papua", "Papua Barat Daya": "Maluku & Papua",
        "Papua": "Maluku & Papua", "Papua Selatan": "Maluku & Papua",
        "Papua Tengah": "Maluku & Papua", "Papua Pegunungan": "Maluku & Papua",
    }
    ec["Pulau"] = ec["Provinsi"].map(region_map_ec).fillna("Lainnya")

    # Price category
    ec["Kategori_Harga"] = pd.cut(
        ec["Harga (IDR)"],
        bins=[0, 50_000, 100_000, 250_000, 500_000, 99_999_999],
        labels=["< 50 rb", "50–100 rb", "100–250 rb", "250–500 rb", "> 500 rb"],
    )

    return ec


df, df_long = load_data()
ec = load_ecommerce()


# ─────────────────────────────────────────────
#  COLOUR PALETTE
# ─────────────────────────────────────────────
OCEAN_PALETTE = [
    "#001219", "#003049", "#005F73", "#0A9396",
    "#94D2BD", "#48CAE4", "#90E0EF", "#CAF0F8",
    "#14213D", "#1D3557"
]

KOMODITAS_COLORS = {
    "Cakalang": "#003049",
    "Tongkol":  "#005F73",
    "Tuna":     "#0A9396",
    "Udang":    "#48CAE4",
    "Lainnya":  "#90E0EF"
}

EC_PALETTE = ["#0077B6", "#00B4D8", "#48CAE4", "#0A9396", "#005F73",
              "#90E0EF", "#003049", "#94D2BD", "#1D3557", "#CAF0F8"]

# ─────────────────────────────────────────────
#  GLOBAL CSS — PREMIUM UPGRADE
# ─────────────────────────────────────────────
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Cormorant+Garamond:wght@400;500;600;700&family=DM+Sans:wght@300;400;500;600&family=Space+Mono:wght@400;700&display=swap');

/* ── Reset & Base ── */
html, body, [class*="css"] {
    font-family: 'DM Sans', sans-serif;
    background-color: #030d1a !important;
}
.main .block-container {
    background: linear-gradient(160deg, #030d1a 0%, #041525 40%, #062040 100%);
    min-height: 100vh;
    padding-top: 0 !important;
}

/* ══════════════════════════════════
   HERO BANNER
══════════════════════════════════ */
.hero-banner {
    position: relative;
    width: calc(100% + 8rem);
    margin-left: -4rem;
    margin-bottom: 2.5rem;
    overflow: hidden;
    border-bottom: 1px solid rgba(0,180,216,0.25);
}
.hero-banner img.bg {
    width: 100%;
    height: 360px;
    object-fit: cover;
    object-position: center 40%;
    display: block;
    filter: brightness(0.35) saturate(1.4) contrast(1.1);
}
.hero-overlay {
    position: absolute;
    inset: 0;
    background:
        linear-gradient(180deg,
            rgba(3,13,26,0.1) 0%,
            rgba(3,13,26,0.3) 40%,
            rgba(3,13,26,0.85) 100%),
        linear-gradient(90deg,
            rgba(0,60,120,0.6) 0%,
            rgba(0,30,80,0.2) 50%,
            transparent 100%);
    display: flex;
    align-items: flex-end;
    padding: 2rem 3rem 2.5rem;
    gap: 2rem;
}
.hero-text h1 {
    font-family: 'Cormorant Garamond', Georgia, serif;
    font-size: 2.6rem;
    font-weight: 700;
    color: #ffffff;
    margin: 0 0 .5rem;
    letter-spacing: -.01em;
    line-height: 1.15;
    text-shadow: 0 2px 30px rgba(0,100,200,0.5);
}
.hero-text p {
    color: #7ec8e3;
    font-size: .9rem;
    margin: 0;
    font-weight: 400;
    font-family: 'Space Mono', monospace;
    letter-spacing: .04em;
    opacity: .85;
}
.hero-text .hero-badge {
    display: inline-block;
    background: rgba(0,180,216,0.15);
    border: 1px solid rgba(0,180,216,0.4);
    color: #48CAE4;
    font-size: .72rem;
    font-family: 'Space Mono', monospace;
    letter-spacing: .12em;
    text-transform: uppercase;
    padding: .3rem .9rem;
    border-radius: 2rem;
    margin-bottom: .75rem;
}
.hero-logo img {
    height: 90px;
    filter: drop-shadow(0 0 20px rgba(0,180,216,0.4)) brightness(1.1);
    border-radius: 10px;
}
.hero-wave {
    position: absolute;
    bottom: -1px; left: 0; right: 0;
    height: 40px;
    background: linear-gradient(180deg, transparent 0%, #030d1a 100%);
}

/* ══════════════════════════════════
   SIDEBAR
══════════════════════════════════ */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg,
        #020b16 0%,
        #031525 50%,
        #041e34 100%) !important;
    border-right: 1px solid rgba(0,180,216,0.12) !important;
}
[data-testid="stSidebar"] * { color: #b8dff0 !important; }
[data-testid="stSidebar"] .sidebar-title {
    font-family: 'Space Mono', monospace;
    font-size: .72rem;
    font-weight: 700;
    color: #48CAE4 !important;
    letter-spacing: .15em;
    text-transform: uppercase;
    padding: .5rem 0 .4rem;
    border-bottom: 1px solid rgba(72,202,228,0.2);
    margin-bottom: .75rem;
}
[data-testid="stSidebar"] hr { border-color: rgba(72,202,228,0.1) !important; }

/* ══════════════════════════════════
   METRIC CARDS
══════════════════════════════════ */
[data-testid="stMetric"] {
    background:
        linear-gradient(135deg,
            rgba(0,50,100,0.6) 0%,
            rgba(0,80,140,0.4) 50%,
            rgba(0,40,80,0.6) 100%) !important;
    backdrop-filter: blur(20px);
    -webkit-backdrop-filter: blur(20px);
    border-radius: 16px !important;
    padding: 1.4rem 1.6rem !important;
    border: 1px solid rgba(72,202,228,0.2) !important;
    box-shadow:
        0 8px 32px rgba(0,0,0,0.4),
        0 0 0 1px rgba(0,180,216,0.05),
        inset 0 1px 0 rgba(255,255,255,0.05) !important;
    transition: transform .25s ease, box-shadow .25s ease !important;
    position: relative;
    overflow: hidden;
}
[data-testid="stMetric"]::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, transparent, #00B4D8, transparent);
}
[data-testid="stMetric"]:hover {
    transform: translateY(-4px) !important;
    box-shadow: 0 16px 48px rgba(0,100,200,0.35), 0 0 20px rgba(0,180,216,0.15) !important;
}
[data-testid="stMetricLabel"] {
    color: #7ec8e3 !important;
    font-size: .72rem !important;
    font-weight: 600 !important;
    font-family: 'Space Mono', monospace !important;
    text-transform: uppercase !important;
    letter-spacing: .1em !important;
}
[data-testid="stMetricValue"] {
    color: #ffffff !important;
    font-family: 'Cormorant Garamond', Georgia, serif !important;
    font-size: 1.9rem !important;
    font-weight: 700 !important;
    line-height: 1.1 !important;
}
[data-testid="stMetricDelta"] > div { color: #48CAE4 !important; }

/* ══════════════════════════════════
   SECTION HEADERS
══════════════════════════════════ */
.section-header {
    display: flex;
    align-items: center;
    gap: .7rem;
    margin: 2rem 0 1rem;
    padding-bottom: .6rem;
    border-bottom: 1px solid rgba(0,180,216,0.15);
}
.section-header .icon { font-size: 1.3rem; }
.section-header h2 {
    font-family: 'Cormorant Garamond', Georgia, serif;
    font-size: 1.3rem;
    font-weight: 600;
    color: #e0f4ff;
    margin: 0;
    letter-spacing: .02em;
}
.section-header::after {
    content: '';
    flex: 1;
    height: 1px;
    background: linear-gradient(90deg, rgba(0,180,216,0.3), transparent);
    margin-left: .5rem;
}

/* ══════════════════════════════════
   CHART CONTAINERS
══════════════════════════════════ */
.chart-card {
    background: linear-gradient(135deg,
        rgba(0,30,60,0.7) 0%,
        rgba(0,50,90,0.5) 100%);
    backdrop-filter: blur(10px);
    border-radius: 20px;
    padding: 1.5rem;
    box-shadow: 0 8px 40px rgba(0,0,0,0.4), inset 0 1px 0 rgba(255,255,255,0.04);
    border: 1px solid rgba(72,202,228,0.12);
    margin-bottom: 1rem;
}
.chart-card h3 {
    font-family: 'Cormorant Garamond', Georgia, serif;
    font-size: 1.05rem;
    font-weight: 600;
    color: #cce8f4;
    margin: 0 0 .75rem;
}

/* ══════════════════════════════════
   E-COMMERCE PRODUCT CARD
══════════════════════════════════ */
.ec-card {
    background: linear-gradient(135deg, rgba(0,40,80,0.7) 0%, rgba(0,60,100,0.5) 100%);
    border: 1px solid rgba(72,202,228,0.18);
    border-radius: 14px;
    padding: 1rem 1.2rem;
    margin-bottom: .7rem;
    position: relative;
    overflow: hidden;
    transition: transform .2s ease, box-shadow .2s ease;
}
.ec-card::before {
    content: '';
    position: absolute;
    left: 0; top: 0; bottom: 0;
    width: 3px;
    background: linear-gradient(180deg, #00B4D8, #0077B6);
    border-radius: 3px 0 0 3px;
}
.ec-card:hover {
    transform: translateX(4px);
    box-shadow: 0 8px 24px rgba(0,100,200,0.25);
}
.ec-card .ec-title {
    font-family: 'DM Sans', sans-serif;
    font-size: .85rem;
    font-weight: 600;
    color: #cce8f4;
    margin-bottom: .4rem;
    line-height: 1.3;
}
.ec-card .ec-meta {
    display: flex;
    gap: .6rem;
    flex-wrap: wrap;
    align-items: center;
}
.ec-badge {
    display: inline-block;
    background: rgba(0,100,180,0.25);
    border: 1px solid rgba(0,180,216,0.25);
    border-radius: 6px;
    padding: .15rem .55rem;
    font-size: .7rem;
    color: #7ec8e3;
    font-family: 'Space Mono', monospace;
    font-weight: 600;
}
.ec-badge.green {
    background: rgba(10,147,150,0.2);
    border-color: rgba(10,147,150,0.35);
    color: #94D2BD;
}
.ec-badge.gold {
    background: rgba(200,150,0,0.2);
    border-color: rgba(200,150,0,0.35);
    color: #f0c060;
}

/* ══════════════════════════════════
   INFO / BADGE
══════════════════════════════════ */
.info-badge {
    display: inline-block;
    background: rgba(0,180,216,0.1);
    border: 1px solid rgba(0,180,216,0.3);
    border-radius: 6px;
    padding: .3rem .85rem;
    font-size: .78rem;
    color: #48CAE4;
    font-family: 'Space Mono', monospace;
    font-weight: 600;
    letter-spacing: .04em;
}

/* ══════════════════════════════════
   DIVIDER
══════════════════════════════════ */
.ocean-divider {
    height: 1px;
    background: linear-gradient(90deg,
        transparent,
        rgba(0,180,216,0.5),
        rgba(72,202,228,0.8),
        rgba(144,224,239,0.4),
        transparent);
    border: none;
    border-radius: 3px;
    margin: 2rem 0;
}

/* ══════════════════════════════════
   DATA TABLE
══════════════════════════════════ */
[data-testid="stDataFrame"] {
    border-radius: 14px !important;
    overflow: hidden !important;
    border: 1px solid rgba(72,202,228,0.15) !important;
    background: rgba(0,20,45,0.6) !important;
}

/* ══════════════════════════════════
   TAB STYLING
══════════════════════════════════ */
[data-baseweb="tab-list"] {
    background: rgba(0,20,50,0.8) !important;
    border-radius: 12px !important;
    padding: 4px !important;
    border: 1px solid rgba(72,202,228,0.12) !important;
}
[data-baseweb="tab"] {
    border-radius: 8px !important;
    font-weight: 500 !important;
    font-size: .88rem !important;
    color: #7ec8e3 !important;
    font-family: 'DM Sans', sans-serif !important;
}
[data-baseweb="tab"]:hover {
    background: rgba(0,119,182,0.25) !important;
    color: #ffffff !important;
}
[aria-selected="true"][data-baseweb="tab"] {
    background: linear-gradient(135deg, #005F73, #0077B6) !important;
    color: #ffffff !important;
    box-shadow: 0 4px 12px rgba(0,100,180,0.4) !important;
}
[data-baseweb="tab"] p { color: inherit !important; }

/* ══════════════════════════════════
   BUTTONS
══════════════════════════════════ */
[data-testid="baseButton-secondary"] {
    background: linear-gradient(135deg, #005F73, #0077B6) !important;
    color: #fff !important;
    border: 1px solid rgba(0,180,216,0.3) !important;
    border-radius: 10px !important;
    font-weight: 600 !important;
    font-family: 'DM Sans', sans-serif !important;
    box-shadow: 0 4px 16px rgba(0,100,180,0.3) !important;
    transition: all .2s !important;
}
[data-testid="baseButton-secondary"]:hover {
    box-shadow: 0 6px 24px rgba(0,100,180,0.5) !important;
    transform: translateY(-1px) !important;
}

/* ══════════════════════════════════
   EXPANDER
══════════════════════════════════ */
[data-testid="stExpander"] {
    background: rgba(0,25,55,0.6) !important;
    border: 1px solid rgba(72,202,228,0.12) !important;
    border-radius: 14px !important;
}

/* ══════════════════════════════════
   SELECTBOX & INPUTS
══════════════════════════════════ */
[data-testid="stSelectbox"] > div > div {
    background: rgba(0,20,50,0.8) !important;
    border: 1px solid rgba(72,202,228,0.2) !important;
    border-radius: 8px !important;
    color: #b8dff0 !important;
}

/* ══════════════════════════════════
   FOOTER
══════════════════════════════════ */
.footer {
    text-align: center;
    padding: 2rem;
    color: #4a7a96;
    font-size: .78rem;
    border-top: 1px solid rgba(72,202,228,0.1);
    margin-top: 2rem;
    font-family: 'Space Mono', monospace;
    letter-spacing: .03em;
}

.stApp {
    background: linear-gradient(160deg, #030d1a 0%, #041525 60%, #062040 100%) !important;
}

[data-testid="stRadio"] label { color: #b8dff0 !important; }
[data-testid="stRadio"] label:hover { color: #ffffff !important; }

[data-testid="stAlert"] {
    background: rgba(0,95,115,0.2) !important;
    border: 1px solid rgba(0,180,216,0.3) !important;
    border-radius: 10px !important;
    color: #7ec8e3 !important;
}
</style>
""",
    unsafe_allow_html=True,
)

# ─────────────────────────────────────────────
#  ASSETS
# ─────────────────────────────────────────────
UNSOED_LOGO_URL = "https://dinaspajak.com/wp-content/uploads/2023/07/Logo-UNSOED-e1691736987438.png"
FISH_BG         = "https://i.pinimg.com/736x/77/b0/08/77b008cd14d68e62855c2c9b1a0ce370.jpg"

# ─────────────────────────────────────────────
#  SIDEBAR NAVIGATION
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        f"""
        <div style="text-align:center; padding: 1.25rem 0 .75rem;">
            <img src="{UNSOED_LOGO_URL}" style="height:76px; border-radius:10px;
                margin-bottom:.75rem;
                box-shadow: 0 0 24px rgba(0,180,216,0.35), 0 8px 20px rgba(0,0,0,0.5);">
            <div style="font-family:'Space Mono',monospace; font-size:.68rem;
                        color:#48CAE4; font-weight:700; letter-spacing:.12em;
                        text-transform:uppercase; line-height:1.6;">
                UNIVERSITAS JENDERAL SOEDIRMAN
            </div>
            <div style="font-size:.72rem; color:#5fa8c8; margin-top:.35rem;
                        font-family:'DM Sans',sans-serif;">
                Praktikum Pengolahan Data Kelautan
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown('<div class="sidebar-title"> &nbsp;Navigasi</div>', unsafe_allow_html=True)

    menu = st.radio(
        label="",
        options=[
            " Beranda",
            " Analisis Komoditas",
            " Analisis Provinsi",
            " Perbandingan Regional",
            " Data E-Commerce",
            " Analisis Korelasi Pasar",
            " Pencarian Data",
            " Data Lengkap",
        ],
        label_visibility="collapsed",
    )

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown('<div class="sidebar-title"> &nbsp;Filter Global</div>', unsafe_allow_html=True)

    all_pulau  = ["Semua"] + sorted(df["Pulau"].unique().tolist())
    sel_pulau  = st.selectbox("Wilayah/Pulau", all_pulau)

    all_prov   = ["Semua"] + sorted(df["Provinsi"].unique().tolist())
    sel_prov   = st.selectbox("Provinsi", all_prov)

    all_kom    = ["Semua", "Cakalang", "Tongkol", "Tuna", "Udang", "Lainnya"]
    sel_kom    = st.selectbox("Komoditas", all_kom)

    jml_min, jml_max = int(df["Jumlah"].min()), int(df["Jumlah"].max())
    sel_range  = st.slider(
        "Rentang Total Produksi (Ton)", jml_min, jml_max, (jml_min, jml_max), 1000,
    )

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown('<div class="sidebar-title">Kelompok 15</div>', unsafe_allow_html=True)
    st.markdown(
        """
        <div style="font-family:'DM Sans',sans-serif; font-size:.72rem; color:#b8dff0;
                    line-height:2; padding-bottom:.5rem;">
            <div style="display:flex; justify-content:space-between; padding:.2rem 0;
                        border-bottom:1px solid rgba(72,202,228,0.08);">
                <span>Kiki Rahmadhani</span>
                <span style="color:#48CAE4; font-family:'Space Mono',monospace;
                             font-size:.65rem;">L1C024097</span>
            </div>
            <div style="display:flex; justify-content:space-between; padding:.2rem 0;
                        border-bottom:1px solid rgba(72,202,228,0.08);">
                <span>Syifa Hana Putriani</span>
                <span style="color:#48CAE4; font-family:'Space Mono',monospace;
                             font-size:.65rem;">L1C024102</span>
            </div>
            <div style="display:flex; justify-content:space-between; padding:.2rem 0;
                        border-bottom:1px solid rgba(72,202,228,0.08);">
                <span>M. Nabil Dwi Andika</span>
                <span style="color:#48CAE4; font-family:'Space Mono',monospace;
                             font-size:.65rem;">L1C024111</span>
            </div>
            <div style="display:flex; justify-content:space-between; padding:.2rem 0;
                        border-bottom:1px solid rgba(72,202,228,0.08);">
                <span>Nathania Elfaretta R.</span>
                <span style="color:#48CAE4; font-family:'Space Mono',monospace;
                             font-size:.65rem;">L1C024113</span>
            </div>
            <div style="display:flex; justify-content:space-between; padding:.2rem 0;
                        border-bottom:1px solid rgba(72,202,228,0.08);">
                <span>Istamar Sholeh F.</span>
                <span style="color:#48CAE4; font-family:'Space Mono',monospace;
                             font-size:.65rem;">L1C024119</span>
            </div>
            <div style="display:flex; justify-content:space-between; padding:.2rem 0;
                        border-bottom:1px solid rgba(72,202,228,0.08);">
                <span>Rizki Syakir P.</span>
                <span style="color:#48CAE4; font-family:'Space Mono',monospace;
                             font-size:.65rem;">L1C024121</span>
            </div>
            <div style="display:flex; justify-content:space-between; padding:.2rem 0;">
                <span>M. Fahrian Dharis</span>
                <span style="color:#48CAE4; font-family:'Space Mono',monospace;
                             font-size:.65rem;">L1C024141</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown("<hr>", unsafe_allow_html=True)
    st.markdown(
        '<div style="font-size:.68rem; color:#345f76; text-align:center; padding-top:.5rem;'
        'font-family:\'Space Mono\',monospace; letter-spacing:.04em;">'
        "v4.0 · 2024<br>38 Provinsi Indonesia"
        "</div>",
        unsafe_allow_html=True,
    )

# ─────────────────────────────────────────────
#  APPLY FILTERS — PRODUKSI TANGKAP
# ─────────────────────────────────────────────
fdf = df.copy()
if sel_pulau != "Semua": fdf = fdf[fdf["Pulau"] == sel_pulau]
if sel_prov  != "Semua": fdf = fdf[fdf["Provinsi"] == sel_prov]
fdf = fdf[(fdf["Jumlah"] >= sel_range[0]) & (fdf["Jumlah"] <= sel_range[1])]

fdf_long = df_long[df_long["Provinsi"].isin(fdf["Provinsi"])]
if sel_kom != "Semua": fdf_long = fdf_long[fdf_long["Komoditas"] == sel_kom]

# Apply filters for e-commerce (use same provinsi/pulau filter)
fec = ec.copy()
if sel_pulau != "Semua": fec = fec[fec["Pulau"] == sel_pulau]
if sel_prov  != "Semua": fec = fec[fec["Provinsi"] == sel_prov]

# ─────────────────────────────────────────────
#  HERO BANNER
# ─────────────────────────────────────────────
st.markdown(
    f"""
    <div class="hero-banner">
        <img class="bg" src="{FISH_BG}" alt="fishing background">
        <div class="hero-overlay">
            <div style="flex:1;">
                <div class="hero-badge"> &nbsp; Produksi & Pasar Perikanan Nasional</div>
                <h1 class="hero-text" style="font-family:'Cormorant Garamond',Georgia,serif;
                    font-size:2.6rem; font-weight:700; color:#ffffff; margin:0 0 .5rem;
                    line-height:1.2; text-shadow:0 2px 30px rgba(0,100,200,0.5);">
                    Dashboard Perikanan Tangkap<br>& Pasar Digital Ikan 2024
                </h1>
                <p style="color:#7ec8e3; font-size:.85rem; margin:0;
                    font-family:'Space Mono',monospace; letter-spacing:.04em; opacity:.85;">
                    &nbsp;&nbsp;&nbsp;&nbsp;Praktikum Pengolahan Data Kelautan 
                </p>
            </div>
            <div>
                <img src="{UNSOED_LOGO_URL}" alt="Logo UNSOED"
                    style="height:100px; filter:drop-shadow(0 0 20px rgba(0,180,216,0.5))
                           brightness(1.1); border-radius:12px;">
            </div>
        </div>
        <div class="hero-wave"></div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ─────────────────────────────────────────────
#  METRIC CARDS — TOP ROW (combined)
# ─────────────────────────────────────────────
total_filter     = fdf["Jumlah"].sum()
top_prov         = fdf.loc[fdf["Jumlah"].idxmax(), "Provinsi"] if len(fdf) > 0 else "-"
kom_totals       = {k: fdf[k].sum() for k in ["Cakalang","Tongkol","Tuna","Udang","Lainnya"]}
top_komoditas    = max(kom_totals, key=kom_totals.get) if len(fdf) > 0 else "-"
rata_prov        = fdf["Jumlah"].mean() if len(fdf) > 0 else 0
total_ec_volume  = fec["Volume Penjualan (IDR)"].sum()
avg_rating_ec    = fec["Rating"].mean() if fec["Rating"].notna().any() else 0

m1, m2, m3, m4, m5, m6 = st.columns(6)
with m1: st.metric("Total Produksi (Ton)", f"{total_filter:,.0f}")
with m2: st.metric("Jumlah Provinsi", len(fdf))
with m3: st.metric("Provinsi Teratas", top_prov)
with m4: st.metric("Komoditas Dominan", top_komoditas)
with m5: st.metric("Total Produk (Tokopedia)", f"{len(fec):,}")
with m6: st.metric("Volume Penjualan Digital", f"Rp {total_ec_volume/1_000_000:.1f} Jt")

st.markdown('<hr class="ocean-divider">', unsafe_allow_html=True)

# ─────────────────────────────────────────────
#  HELPERS
# ─────────────────────────────────────────────
def section(icon, title):
    st.markdown(
        f'<div class="section-header"><span class="icon">{icon}</span>'
        f"<h2>{title}</h2></div>",
        unsafe_allow_html=True,
    )

def plotly_cfg(fig, h=380):
    fig.update_layout(
        height=h,
        margin=dict(l=10, r=10, t=45, b=10),
        font=dict(family="DM Sans, sans-serif", size=12, color="#b8dff0"),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        legend=dict(
            bgcolor="rgba(0,15,35,0.7)",
            bordercolor="rgba(72,202,228,0.2)",
            borderwidth=1,
            font=dict(size=11, color="#b8dff0"),
        ),
        title_font=dict(
            family="Cormorant Garamond, Georgia, serif",
            size=15,
            color="#cce8f4",
        ),
    )
    fig.update_xaxes(
        gridcolor="rgba(72,202,228,0.08)",
        showgrid=True,
        linecolor="rgba(72,202,228,0.15)",
        tickfont=dict(color="#7ec8e3"),
        title_font=dict(color="#7ec8e3"),
    )
    fig.update_yaxes(
        gridcolor="rgba(72,202,228,0.08)",
        showgrid=True,
        linecolor="rgba(72,202,228,0.15)",
        tickfont=dict(color="#7ec8e3"),
        title_font=dict(color="#7ec8e3"),
    )
    return fig


# ═══════════════════════════════════════════════════
#  PAGE: BERANDA
# ═══════════════════════════════════════════════════
if menu == " Beranda":
    section("", "Ringkasan Produksi Perikanan Tangkap 2024")

    col_l, col_r = st.columns(2)

    with col_l:
        top_prov_df = fdf.sort_values("Jumlah", ascending=True).tail(15)
        fig = px.bar(
            top_prov_df, x="Jumlah", y="Provinsi", orientation="h",
            color="Jumlah",
            color_continuous_scale=["#0A4F6E", "#0077B6", "#00B4D8", "#90E0EF"],
            text="Jumlah",
            labels={"Jumlah": "Produksi (Ton)", "Provinsi": ""},
            title=" Top Provinsi Berdasarkan Total Produksi",
        )
        fig.update_traces(texttemplate="%{text:,.0f}", textposition="outside",
                          textfont=dict(color="#cce8f4"))
        fig.update_coloraxes(showscale=False)
        st.plotly_chart(plotly_cfg(fig, 480), use_container_width=True)

    with col_r:
        kom_data = pd.DataFrame({
            "Komoditas": list(kom_totals.keys()),
            "Produksi": list(kom_totals.values()),
        })
        fig = px.pie(
            kom_data, values="Produksi", names="Komoditas", hole=0.48,
            color="Komoditas",
            color_discrete_map=KOMODITAS_COLORS,
            title=" Distribusi Produksi per Komoditas",
        )
        fig.update_traces(
            textposition="outside", textinfo="percent+label",
            textfont=dict(color="#b8dff0"),
            marker=dict(line=dict(color="#030d1a", width=2)),
        )
        st.plotly_chart(plotly_cfg(fig, 480), use_container_width=True)

    section("", "Produksi per Wilayah/Pulau")
    pulau_df = fdf.groupby("Pulau")[["Cakalang","Tongkol","Tuna","Udang","Lainnya"]].sum().reset_index()
    pulau_long = pulau_df.melt(id_vars="Pulau", var_name="Komoditas", value_name="Produksi_Ton")
    fig = px.bar(
        pulau_long, x="Pulau", y="Produksi_Ton", color="Komoditas",
        barmode="stack", color_discrete_map=KOMODITAS_COLORS,
        labels={"Produksi_Ton": "Produksi (Ton)", "Pulau": "Wilayah"},
        title="Komposisi Komoditas per Wilayah",
    )
    fig.update_traces(marker=dict(line=dict(color="rgba(0,0,0,0.3)", width=.5)))
    st.plotly_chart(plotly_cfg(fig, 350), use_container_width=True)

    col_a, col_b = st.columns(2)
    with col_a:
        section("", "Top 5 Provinsi Produksi Tertinggi")
        top5 = fdf.nlargest(5, "Jumlah")[["Provinsi","Cakalang","Tongkol","Tuna","Udang","Lainnya","Jumlah"]]
        st.dataframe(top5, use_container_width=True, hide_index=True)

    with col_b:
        section("", "Distribusi Kategori Produksi")
        kat = fdf["Kategori_Produksi"].value_counts().reset_index()
        kat.columns = ["Kategori", "Jumlah Provinsi"]
        fig = px.bar(
            kat, x="Kategori", y="Jumlah Provinsi",
            color="Kategori",
            color_discrete_sequence=["#005F73","#0077B6","#00B4D8","#48CAE4"],
            text="Jumlah Provinsi",
            title="Sebaran Kategori Produksi per Provinsi",
        )
        fig.update_traces(textposition="outside", textfont=dict(color="#cce8f4"),
                          marker=dict(line=dict(color="#030d1a", width=1)))
        fig.update_layout(showlegend=False)
        st.plotly_chart(plotly_cfg(fig, 320), use_container_width=True)

    # Mini E-Commerce Snapshot on Beranda
    st.markdown('<hr class="ocean-divider">', unsafe_allow_html=True)
    section("", "Snapshot Pasar Digital (Tokopedia 2024)")
    ec_prov_agg = fec.groupby("Provinsi").agg(
        Total_Produk=("Nama Produk","count"),
        Total_Unit=("Unit Terjual","sum"),
        Total_Volume=("Volume Penjualan (IDR)","sum"),
        Avg_Harga=("Harga (IDR)","mean"),
    ).reset_index().sort_values("Total_Volume", ascending=False)

    snap_c1, snap_c2, snap_c3 = st.columns(3)
    with snap_c1:
        fig = px.bar(
            ec_prov_agg.head(10).sort_values("Total_Volume"),
            x="Total_Volume", y="Provinsi", orientation="h",
            color="Total_Volume",
            color_continuous_scale=["#003F6B","#0077B6","#48CAE4"],
            text="Total_Volume", title=" Top 10 Provinsi – Volume Penjualan (Rp)",
        )
        fig.update_traces(texttemplate="Rp %{text:,.0f}", textposition="outside",
                          textfont=dict(color="#cce8f4", size=10))
        fig.update_coloraxes(showscale=False)
        st.plotly_chart(plotly_cfg(fig, 380), use_container_width=True)

    with snap_c2:
        fig = px.bar(
            ec_prov_agg.head(10).sort_values("Total_Unit"),
            x="Total_Unit", y="Provinsi", orientation="h",
            color="Total_Unit",
            color_continuous_scale=["#005F73","#0A9396","#94D2BD"],
            text="Total_Unit", title=" Top 10 Provinsi – Unit Terjual",
        )
        fig.update_traces(texttemplate="%{text}", textposition="outside",
                          textfont=dict(color="#cce8f4", size=10))
        fig.update_coloraxes(showscale=False)
        st.plotly_chart(plotly_cfg(fig, 380), use_container_width=True)

    with snap_c3:
        fig = px.scatter(
            ec_prov_agg, x="Total_Unit", y="Total_Volume",
            size="Total_Produk", color="Total_Volume",
            color_continuous_scale=["#003F6B","#0077B6","#48CAE4"],
            hover_name="Provinsi", size_max=40,
            title=" Unit vs Volume Penjualan per Provinsi",
            labels={"Total_Unit":"Unit Terjual","Total_Volume":"Volume (Rp)"},
        )
        fig.update_coloraxes(showscale=False)
        st.plotly_chart(plotly_cfg(fig, 380), use_container_width=True)


# ═══════════════════════════════════════════════════
#  PAGE: ANALISIS KOMODITAS
# ═══════════════════════════════════════════════════
elif menu == " Analisis Komoditas":
    section("", "Analisis Per Komoditas")

    tab1, tab2, tab3 = st.tabs([" Produksi Komoditas", " Perbandingan", " Distribusi"])

    with tab1:
        col1, col2 = st.columns(2)
        with col1:
            kom_sum = fdf[["Cakalang","Tongkol","Tuna","Udang","Lainnya"]].sum().reset_index()
            kom_sum.columns = ["Komoditas", "Total Produksi (Ton)"]
            kom_sum = kom_sum.sort_values("Total Produksi (Ton)", ascending=False)
            fig = px.bar(
                kom_sum, x="Komoditas", y="Total Produksi (Ton)",
                color="Komoditas", color_discrete_map=KOMODITAS_COLORS,
                text="Total Produksi (Ton)", title="Total Produksi per Komoditas",
            )
            fig.update_traces(texttemplate="%{text:,.0f}", textposition="outside",
                              textfont=dict(color="#cce8f4"),
                              marker=dict(line=dict(color="#030d1a", width=1)))
            fig.update_layout(showlegend=False)
            st.plotly_chart(plotly_cfg(fig, 400), use_container_width=True)

        with col2:
            fig = px.scatter(
                fdf, x="Tuna", y="Cakalang", size="Jumlah",
                color="Pulau", color_discrete_sequence=OCEAN_PALETTE,
                hover_name="Provinsi", size_max=60,
                title="Bubble: Tuna vs Cakalang (ukuran = Total Produksi)",
                labels={"Tuna": "Tuna (Ton)", "Cakalang": "Cakalang (Ton)"},
            )
            st.plotly_chart(plotly_cfg(fig, 400), use_container_width=True)

        st.dataframe(
            kom_sum.assign(**{"% Nasional": lambda d: (d["Total Produksi (Ton)"] / d["Total Produksi (Ton)"].sum() * 100).round(2)}),
            use_container_width=True, hide_index=True,
        )

    with tab2:
        top10 = fdf.nlargest(10, "Jumlah")
        top10_long = top10.melt(
            id_vars="Provinsi", value_vars=["Cakalang","Tongkol","Tuna","Udang","Lainnya"],
            var_name="Komoditas", value_name="Ton",
        )
        fig = px.bar(
            top10_long, x="Provinsi", y="Ton", color="Komoditas",
            barmode="group", color_discrete_map=KOMODITAS_COLORS,
            title=" Perbandingan Komoditas – Top 10 Provinsi",
        )
        fig.update_xaxes(tickangle=-30)
        fig.update_traces(marker=dict(line=dict(color="#030d1a", width=.5)))
        st.plotly_chart(plotly_cfg(fig, 450), use_container_width=True)

        section("", "Radar Produksi Komoditas per Wilayah")
        pulau_rad = fdf.groupby("Pulau")[["Cakalang","Tongkol","Tuna","Udang","Lainnya"]].sum().reset_index()
        fig = go.Figure()
        categories = ["Cakalang","Tongkol","Tuna","Udang","Lainnya"]
        radar_colors = ["#0077B6","#00B4D8","#48CAE4","#90E0EF","#005F73","#0A9396"]
        for i, (_, row) in enumerate(pulau_rad.iterrows()):
            c = radar_colors[i % len(radar_colors)]
            fig.add_trace(go.Scatterpolar(
                r=[row[k] for k in categories] + [row["Cakalang"]],
                theta=categories + [categories[0]],
                fill="toself", name=row["Pulau"],
                line=dict(color=c, width=2),
                fillcolor=f"rgba({int(c[1:3],16)},{int(c[3:5],16)},{int(c[5:7],16)},0.15)",
            ))
        fig.update_layout(
            polar=dict(
                radialaxis=dict(visible=True, gridcolor="rgba(72,202,228,0.2)", tickfont=dict(color="#7ec8e3")),
                angularaxis=dict(gridcolor="rgba(72,202,228,0.15)", tickfont=dict(color="#cce8f4")),
                bgcolor="rgba(0,10,25,0.5)",
            ),
            title=dict(text=" Radar Produksi Komoditas per Wilayah", font=dict(color="#cce8f4", size=15,
                       family="Cormorant Garamond, Georgia, serif")),
            height=420, paper_bgcolor="rgba(0,0,0,0)",
            font=dict(family="DM Sans, sans-serif", color="#b8dff0"),
            legend=dict(bgcolor="rgba(0,15,35,0.7)", bordercolor="rgba(72,202,228,0.2)", borderwidth=1),
        )
        st.plotly_chart(fig, use_container_width=True)

    with tab3:
        c1, c2 = st.columns(2)
        with c1:
            fig = px.box(
                fdf_long, x="Komoditas", y="Produksi_Ton",
                color="Komoditas", color_discrete_map=KOMODITAS_COLORS,
                title="Box Plot Distribusi Produksi per Komoditas",
            )
            fig.update_layout(showlegend=False)
            fig.update_traces(marker=dict(color="#48CAE4", opacity=0.7))
            st.plotly_chart(plotly_cfg(fig, 400), use_container_width=True)

        with c2:
            fig = px.violin(
                fdf_long, x="Komoditas", y="Produksi_Ton",
                color="Komoditas", color_discrete_map=KOMODITAS_COLORS,
                box=True, title="Violin Plot Distribusi Komoditas",
            )
            fig.update_layout(showlegend=False)
            st.plotly_chart(plotly_cfg(fig, 400), use_container_width=True)


# ═══════════════════════════════════════════════════
#  PAGE: ANALISIS PROVINSI
# ═══════════════════════════════════════════════════
elif menu == " Analisis Provinsi":
    section("", "Analisis Per Provinsi")

    st.info(
        "Data mencakup 38 Provinsi Indonesia. Wilayah yang ditampilkan: "
        + ", ".join(sorted(fdf["Pulau"].unique())),
        icon="",
    )

    col1, col2 = st.columns(2)
    with col1:
        prov_sorted = fdf.sort_values("Jumlah", ascending=False)
        fig = px.funnel(
            prov_sorted.head(15), x="Jumlah", y="Provinsi",
            color="Pulau", color_discrete_sequence=OCEAN_PALETTE,
            title=" Top 15 Provinsi – Funnel Produksi (Ton)",
            labels={"Jumlah": "Produksi (Ton)"},
        )
        st.plotly_chart(plotly_cfg(fig, 500), use_container_width=True)

    with col2:
        prov_long = fdf.melt(
            id_vars="Provinsi", value_vars=["Cakalang","Tongkol","Tuna","Udang","Lainnya"],
            var_name="Komoditas", value_name="Ton",
        )
        top15_names = fdf.nlargest(15, "Jumlah")["Provinsi"].tolist()
        fig = px.bar(
            prov_long[prov_long["Provinsi"].isin(top15_names)],
            x="Provinsi", y="Ton", color="Komoditas",
            barmode="stack", color_discrete_map=KOMODITAS_COLORS,
            title=" Komposisi Komoditas – Top 15 Provinsi",
        )
        fig.update_xaxes(tickangle=-35)
        fig.update_traces(marker=dict(line=dict(color="#030d1a", width=.5)))
        st.plotly_chart(plotly_cfg(fig, 500), use_container_width=True)

    section("", "Treemap Wilayah → Provinsi")
    fig = px.treemap(
        fdf, path=["Pulau", "Provinsi"], values="Jumlah",
        color="Jumlah",
        color_continuous_scale=["#002B45","#005F73","#0077B6","#00B4D8","#90E0EF"],
        title="Hierarki Produksi: Wilayah → Provinsi",
    )
    fig.update_traces(
        textfont=dict(color="#ffffff", family="DM Sans, sans-serif"),
        marker=dict(line=dict(color="#030d1a", width=2)),
    )
    st.plotly_chart(plotly_cfg(fig, 500), use_container_width=True)

    section("", "Hubungan Antar Komoditas")
    c1, c2 = st.columns(2)
    with c1:
        fig = px.scatter(
            fdf, x="Tongkol", y="Tuna", size="Jumlah",
            color="Pulau", color_discrete_sequence=OCEAN_PALETTE,
            hover_name="Provinsi", size_max=55,
            title="Tongkol vs Tuna per Provinsi",
        )
        st.plotly_chart(plotly_cfg(fig, 380), use_container_width=True)

    with c2:
        fig = px.scatter(
            fdf, x="Udang", y="Cakalang", size="Jumlah",
            color="Pulau", color_discrete_sequence=OCEAN_PALETTE,
            hover_name="Provinsi", size_max=55,
            title="Udang vs Cakalang per Provinsi",
        )
        st.plotly_chart(plotly_cfg(fig, 380), use_container_width=True)

    section("", "Statistik per Provinsi")
    display_stat = fdf[["Provinsi","Pulau","Cakalang","Tongkol","Tuna","Udang","Lainnya","Jumlah","Kategori_Produksi"]].copy()
    display_stat.columns = ["Provinsi","Wilayah","Cakalang","Tongkol","Tuna","Udang","Lainnya","Total (Ton)","Kategori"]
    st.dataframe(display_stat, use_container_width=True, hide_index=True)


# ═══════════════════════════════════════════════════
#  PAGE: PERBANDINGAN REGIONAL
# ═══════════════════════════════════════════════════
elif menu == " Perbandingan Regional":
    section("", "Perbandingan Produksi Antar Wilayah")

    pulau_agg = fdf.groupby("Pulau")[["Cakalang","Tongkol","Tuna","Udang","Lainnya","Jumlah"]].sum().reset_index()

    col1, col2 = st.columns(2)
    with col1:
        fig = px.bar(
            pulau_agg.sort_values("Jumlah", ascending=True),
            x="Jumlah", y="Pulau", orientation="h",
            color="Jumlah",
            color_continuous_scale=["#003F6B","#0077B6","#00B4D8","#90E0EF"],
            text="Jumlah", title=" Total Produksi per Wilayah",
        )
        fig.update_traces(texttemplate="%{text:,.0f}", textposition="outside",
                          textfont=dict(color="#cce8f4"))
        fig.update_coloraxes(showscale=False)
        st.plotly_chart(plotly_cfg(fig, 400), use_container_width=True)

    with col2:
        fig = px.pie(
            pulau_agg, values="Jumlah", names="Pulau", hole=0.44,
            color_discrete_sequence=["#005F73","#0077B6","#0A9396","#48CAE4","#90E0EF","#003049"],
            title=" Proporsi Produksi per Wilayah",
        )
        fig.update_traces(
            textposition="outside", textinfo="percent+label",
            textfont=dict(color="#b8dff0"),
            marker=dict(line=dict(color="#030d1a", width=2)),
        )
        st.plotly_chart(plotly_cfg(fig, 400), use_container_width=True)

    section("", "Komposisi Komoditas per Wilayah")
    pulau_long2 = pulau_agg.melt(
        id_vars="Pulau", value_vars=["Cakalang","Tongkol","Tuna","Udang","Lainnya"],
        var_name="Komoditas", value_name="Ton",
    )
    fig = px.bar(
        pulau_long2, x="Pulau", y="Ton", color="Komoditas",
        barmode="stack", color_discrete_map=KOMODITAS_COLORS,
        title="Komposisi Komoditas per Wilayah",
    )
    fig.update_traces(marker=dict(line=dict(color="#030d1a", width=.5)))
    st.plotly_chart(plotly_cfg(fig, 380), use_container_width=True)

    section("", "Sunburst: Wilayah → Provinsi → Komoditas")
    sun = fdf_long.groupby(["Pulau","Provinsi","Komoditas"])["Produksi_Ton"].sum().reset_index()
    fig = px.sunburst(
        sun, path=["Pulau","Provinsi","Komoditas"],
        values="Produksi_Ton", color="Produksi_Ton",
        color_continuous_scale=["#002B45","#005F73","#0077B6","#00B4D8","#90E0EF"],
        title="Hierarki: Wilayah → Provinsi → Komoditas",
    )
    fig.update_traces(
        textfont=dict(color="#ffffff"),
        marker=dict(line=dict(color="#030d1a", width=1.5)),
    )
    st.plotly_chart(plotly_cfg(fig, 560), use_container_width=True)

    section("", "Radar Komoditas per Wilayah")
    fig = go.Figure()
    cats = ["Cakalang","Tongkol","Tuna","Udang","Lainnya"]
    radar_colors = ["#0077B6","#00B4D8","#48CAE4","#90E0EF","#005F73","#0A9396"]
    for i, (_, row) in enumerate(pulau_agg.iterrows()):
        c = radar_colors[i % len(radar_colors)]
        r, g, b = int(c[1:3],16), int(c[3:5],16), int(c[5:7],16)
        vals = [row[k] for k in cats] + [row["Cakalang"]]
        fig.add_trace(go.Scatterpolar(
            r=vals, theta=cats + [cats[0]],
            fill="toself", name=row["Pulau"],
            line=dict(color=c, width=2),
            fillcolor=f"rgba({r},{g},{b},0.12)",
        ))
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, gridcolor="rgba(72,202,228,0.2)", tickfont=dict(color="#7ec8e3")),
            angularaxis=dict(gridcolor="rgba(72,202,228,0.15)", tickfont=dict(color="#cce8f4")),
            bgcolor="rgba(0,10,25,0.5)",
        ),
        title=dict(text=" Radar Komoditas per Wilayah",
                   font=dict(color="#cce8f4", size=15, family="Cormorant Garamond, Georgia, serif")),
        height=420, paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="DM Sans, sans-serif", color="#b8dff0"),
        legend=dict(bgcolor="rgba(0,15,35,0.7)", bordercolor="rgba(72,202,228,0.2)", borderwidth=1),
    )
    st.plotly_chart(fig, use_container_width=True)

    section("", "Tabel Statistik per Wilayah")
    st.dataframe(pulau_agg, use_container_width=True, hide_index=True)


# ═══════════════════════════════════════════════════
#  PAGE: DATA E-COMMERCE   NEW 
# ═══════════════════════════════════════════════════
elif menu == " Data E-Commerce":
    section("", "Analisis Pasar Digital Produk Ikan – Tokopedia 2024")

    st.info(
        f"Data mencakup **{len(ec):,} produk ikan laut** dari **38 Provinsi** Indonesia "
        f"yang dipasarkan melalui Tokopedia. Filter sidebar berlaku pada halaman ini.",
        icon="",
    )

    # ── Metric strip ──
    ec_total_unit   = fec["Unit Terjual"].sum()
    ec_total_vol    = fec["Volume Penjualan (IDR)"].sum()
    ec_avg_harga    = fec["Harga (IDR)"].mean()
    ec_avg_rating   = fec["Rating"].mean()
    ec_n_prov       = fec["Provinsi"].nunique()

    e1, e2, e3, e4, e5 = st.columns(5)
    with e1: st.metric("Total Produk", f"{len(fec):,}")
    with e2: st.metric("Total Unit Terjual", f"{ec_total_unit:,}")
    with e3: st.metric("Volume Penjualan", f"Rp {ec_total_vol/1_000_000:.1f} Jt")
    with e4: st.metric("Rata-rata Harga", f"Rp {ec_avg_harga:,.0f}")
    with e5: st.metric("Avg Rating", f" {ec_avg_rating:.2f}" if not np.isnan(ec_avg_rating) else "–")

    st.markdown('<hr class="ocean-divider">', unsafe_allow_html=True)

    tab_ov, tab_prov, tab_harga, tab_produk, tab_raw = st.tabs([
        " Overview", " Per Provinsi", " Analisis Harga", " Produk Unggulan", " Data Lengkap"
    ])

    # ── TAB 1: OVERVIEW ──
    with tab_ov:
        c1, c2 = st.columns(2)
        with c1:
            vol_pulau = fec.groupby("Pulau")["Volume Penjualan (IDR)"].sum().reset_index().sort_values("Volume Penjualan (IDR)", ascending=False)
            fig = px.pie(
                vol_pulau, values="Volume Penjualan (IDR)", names="Pulau", hole=0.45,
                color_discrete_sequence=EC_PALETTE,
                title=" Proporsi Volume Penjualan per Wilayah",
            )
            fig.update_traces(
                textposition="outside", textinfo="percent+label",
                textfont=dict(color="#b8dff0"),
                marker=dict(line=dict(color="#030d1a", width=2)),
            )
            st.plotly_chart(plotly_cfg(fig, 400), use_container_width=True)

        with c2:
            unit_pulau = fec.groupby("Pulau")["Unit Terjual"].sum().reset_index().sort_values("Unit Terjual", ascending=True)
            fig = px.bar(
                unit_pulau, x="Unit Terjual", y="Pulau", orientation="h",
                color="Unit Terjual",
                color_continuous_scale=["#003F6B","#0077B6","#48CAE4"],
                text="Unit Terjual", title=" Total Unit Terjual per Wilayah",
            )
            fig.update_traces(texttemplate="%{text:,}", textposition="outside",
                              textfont=dict(color="#cce8f4"))
            fig.update_coloraxes(showscale=False)
            st.plotly_chart(plotly_cfg(fig, 400), use_container_width=True)

        # Kategori harga distribusi
        c3, c4 = st.columns(2)
        with c3:
            kat_h = fec["Kategori_Harga"].value_counts().reset_index()
            kat_h.columns = ["Kategori Harga", "Jumlah Produk"]
            fig = px.bar(
                kat_h, x="Kategori Harga", y="Jumlah Produk",
                color="Jumlah Produk",
                color_continuous_scale=["#003F6B","#0077B6","#48CAE4"],
                text="Jumlah Produk", title=" Distribusi Kategori Harga Produk",
            )
            fig.update_traces(textposition="outside", textfont=dict(color="#cce8f4"),
                              marker=dict(line=dict(color="#030d1a", width=1)))
            fig.update_coloraxes(showscale=False)
            fig.update_layout(showlegend=False)
            st.plotly_chart(plotly_cfg(fig, 360), use_container_width=True)

        with c4:
            rating_df = fec.dropna(subset=["Rating"])
            fig = px.histogram(
                rating_df, x="Rating", nbins=20,
                color_discrete_sequence=["#0077B6"],
                title=" Distribusi Rating Produk Ikan",
                labels={"Rating":"Rating","count":"Frekuensi"},
            )
            fig.update_traces(marker_line_color="#00B4D8", marker_line_width=1, opacity=0.85)
            st.plotly_chart(plotly_cfg(fig, 360), use_container_width=True)

        # Scatter: Harga vs Unit Terjual
        section("", "Harga vs Performa Penjualan")
        fig = px.scatter(
            fec[fec["Unit Terjual"] > 0], x="Harga (IDR)", y="Unit Terjual",
            size="Volume Penjualan (IDR)", color="Pulau",
            color_discrete_sequence=EC_PALETTE,
            hover_name="Nama Produk", size_max=40,
            log_x=True,
            title="Harga (log) vs Unit Terjual — ukuran = Volume Penjualan",
            labels={"Harga (IDR)": "Harga (IDR) — skala log", "Unit Terjual": "Unit Terjual"},
        )
        fig.update_traces(marker=dict(opacity=0.8, line=dict(color="#030d1a", width=0.5)))
        st.plotly_chart(plotly_cfg(fig, 420), use_container_width=True)

    # ── TAB 2: PER PROVINSI ──
    with tab_prov:
        ec_prov = fec.groupby("Provinsi").agg(
            Jumlah_Produk=("Nama Produk","count"),
            Total_Unit=("Unit Terjual","sum"),
            Total_Volume=("Volume Penjualan (IDR)","sum"),
            Avg_Harga=("Harga (IDR)","mean"),
            Avg_Rating=("Rating","mean"),
        ).reset_index().sort_values("Total_Volume", ascending=False)

        c1, c2 = st.columns(2)
        with c1:
            fig = px.bar(
                ec_prov.sort_values("Total_Volume", ascending=True).tail(15),
                x="Total_Volume", y="Provinsi", orientation="h",
                color="Total_Volume",
                color_continuous_scale=["#003F6B","#0077B6","#48CAE4"],
                text="Total_Volume",
                title=" Top 15 Provinsi – Volume Penjualan (Rp)",
            )
            fig.update_traces(texttemplate="Rp %{text:,.0f}", textposition="outside",
                              textfont=dict(color="#cce8f4", size=10))
            fig.update_coloraxes(showscale=False)
            st.plotly_chart(plotly_cfg(fig, 520), use_container_width=True)

        with c2:
            fig = px.bar(
                ec_prov.sort_values("Total_Unit", ascending=True).tail(15),
                x="Total_Unit", y="Provinsi", orientation="h",
                color="Total_Unit",
                color_continuous_scale=["#005F73","#0A9396","#94D2BD"],
                text="Total_Unit",
                title=" Top 15 Provinsi – Total Unit Terjual",
            )
            fig.update_traces(texttemplate="%{text:,}", textposition="outside",
                              textfont=dict(color="#cce8f4", size=10))
            fig.update_coloraxes(showscale=False)
            st.plotly_chart(plotly_cfg(fig, 520), use_container_width=True)

        section("", "Treemap – Provinsi → Volume Penjualan")
        ec_prov_pulau = fec.groupby(["Pulau","Provinsi"])["Volume Penjualan (IDR)"].sum().reset_index()
        ec_prov_pulau = ec_prov_pulau[ec_prov_pulau["Volume Penjualan (IDR)"] > 0]
        fig = px.treemap(
            ec_prov_pulau, path=["Pulau","Provinsi"],
            values="Volume Penjualan (IDR)",
            color="Volume Penjualan (IDR)",
            color_continuous_scale=["#002B45","#005F73","#0077B6","#00B4D8","#90E0EF"],
            title="Peta Volume Penjualan Digital per Provinsi",
        )
        fig.update_traces(
            textfont=dict(color="#ffffff", family="DM Sans, sans-serif"),
            marker=dict(line=dict(color="#030d1a", width=2)),
        )
        st.plotly_chart(plotly_cfg(fig, 500), use_container_width=True)

        section("", "Statistik Lengkap per Provinsi")
        ec_prov_disp = ec_prov.copy()
        ec_prov_disp["Avg_Harga"] = ec_prov_disp["Avg_Harga"].round(0).astype(int)
        ec_prov_disp["Avg_Rating"] = ec_prov_disp["Avg_Rating"].round(3)
        ec_prov_disp.columns = ["Provinsi","Jml Produk","Total Unit","Volume (Rp)","Avg Harga (Rp)","Avg Rating"]
        st.dataframe(ec_prov_disp, use_container_width=True, hide_index=True)

    # ── TAB 3: ANALISIS HARGA ──
    with tab_harga:
        c1, c2 = st.columns(2)
        with c1:
            avg_harga_prov = fec.groupby("Provinsi")["Harga (IDR)"].mean().reset_index().sort_values("Harga (IDR)", ascending=True)
            fig = px.bar(
                avg_harga_prov.tail(15),
                x="Harga (IDR)", y="Provinsi", orientation="h",
                color="Harga (IDR)",
                color_continuous_scale=["#003F6B","#0077B6","#48CAE4"],
                text="Harga (IDR)",
                title=" Rata-rata Harga Produk Ikan per Provinsi (Top 15)",
            )
            fig.update_traces(texttemplate="Rp %{text:,.0f}", textposition="outside",
                              textfont=dict(color="#cce8f4", size=10))
            fig.update_coloraxes(showscale=False)
            st.plotly_chart(plotly_cfg(fig, 500), use_container_width=True)

        with c2:
            fig = px.box(
                fec[fec["Harga (IDR)"] < 500_000],  # exclude extreme outliers for clarity
                x="Pulau", y="Harga (IDR)",
                color="Pulau", color_discrete_sequence=EC_PALETTE,
                title=" Distribusi Harga per Wilayah (< Rp 500.000)",
                labels={"Harga (IDR)":"Harga (IDR)","Pulau":"Wilayah"},
            )
            fig.update_layout(showlegend=False)
            fig.update_xaxes(tickangle=-20)
            st.plotly_chart(plotly_cfg(fig, 500), use_container_width=True)

        section("", "Volume Penjualan vs Harga per Provinsi")
        ec_hv = fec.groupby("Provinsi").agg(
            Avg_Harga=("Harga (IDR)","mean"),
            Total_Volume=("Volume Penjualan (IDR)","sum"),
            Total_Unit=("Unit Terjual","sum"),
        ).reset_index()
        fig = px.scatter(
            ec_hv, x="Avg_Harga", y="Total_Volume",
            size="Total_Unit", color="Total_Volume",
            color_continuous_scale=["#003F6B","#0077B6","#48CAE4"],
            hover_name="Provinsi", size_max=45,
            title="Rata-rata Harga vs Volume Penjualan per Provinsi",
            labels={"Avg_Harga":"Rata-rata Harga (IDR)","Total_Volume":"Total Volume (Rp)"},
        )
        fig.update_traces(marker=dict(opacity=0.85, line=dict(color="#030d1a", width=0.5)))
        fig.update_coloraxes(showscale=False)
        st.plotly_chart(plotly_cfg(fig, 400), use_container_width=True)

        section("", "Hubungan Harga & Rating")
        rated = fec.dropna(subset=["Rating"])
        c3, c4 = st.columns(2)
        with c3:
            fig = px.scatter(
                rated[rated["Harga (IDR)"] < 1_000_000],
                x="Harga (IDR)", y="Rating",
                color="Pulau", color_discrete_sequence=EC_PALETTE,
                hover_name="Nama Produk",
                title="Harga vs Rating Produk",
                opacity=0.7,
            )
            fig.update_traces(marker=dict(size=7))
            st.plotly_chart(plotly_cfg(fig, 380), use_container_width=True)

        with c4:
            avg_rating_prov = rated.groupby("Provinsi")["Rating"].mean().reset_index().sort_values("Rating", ascending=True)
            fig = px.bar(
                avg_rating_prov,
                x="Rating", y="Provinsi", orientation="h",
                color="Rating",
                color_continuous_scale=["#003F6B","#0077B6","#48CAE4"],
                text="Rating",
                title=" Rata-rata Rating per Provinsi",
            )
            fig.update_traces(texttemplate="%{text:.3f}", textposition="outside",
                              textfont=dict(color="#cce8f4", size=9))
            fig.update_coloraxes(showscale=False)
            st.plotly_chart(plotly_cfg(fig, 380), use_container_width=True)

    # ── TAB 4: PRODUK UNGGULAN ──
    with tab_produk:
        section("", "Produk dengan Volume Penjualan Tertinggi")

        top_prod = (
            fec[fec["Volume Penjualan (IDR)"] > 0]
            .sort_values("Volume Penjualan (IDR)", ascending=False)
            .head(20)
            .reset_index(drop=True)
        )

        for i, row in top_prod.iterrows():
            nama   = str(row["Nama Produk"])[:80] + ("…" if len(str(row["Nama Produk"])) > 80 else "")
            rating = f" {row['Rating']:.1f}" if not np.isnan(row["Rating"]) else "–"
            st.markdown(
                f"""
                <div class="ec-card">
                    <div class="ec-title">#{i+1} &nbsp; {nama}</div>
                    <div class="ec-meta">
                        <span class="ec-badge"> {row['Provinsi']}</span>
                        <span class="ec-badge"> Rp {row['Harga (IDR)']:,.0f}</span>
                        <span class="ec-badge green"> {row['Unit Terjual']} unit</span>
                        <span class="ec-badge green"> Rp {row['Volume Penjualan (IDR)']:,.0f}</span>
                        <span class="ec-badge gold">{rating}</span>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        section("", "Top 20 Produk – Visualisasi")
        fig = px.bar(
            top_prod.sort_values("Volume Penjualan (IDR)", ascending=True),
            x="Volume Penjualan (IDR)",
            y=top_prod.sort_values("Volume Penjualan (IDR)", ascending=True)["Nama Produk"].str[:40],
            orientation="h",
            color="Volume Penjualan (IDR)",
            color_continuous_scale=["#003F6B","#0077B6","#48CAE4"],
            text="Volume Penjualan (IDR)",
            title=" Top 20 Produk – Volume Penjualan (Rp)",
        )
        fig.update_traces(texttemplate="Rp %{text:,.0f}", textposition="outside",
                          textfont=dict(color="#cce8f4", size=9))
        fig.update_coloraxes(showscale=False)
        fig.update_yaxes(tickfont=dict(size=9))
        st.plotly_chart(plotly_cfg(fig, 620), use_container_width=True)

    # ── TAB 5: RAW DATA ──
    with tab_raw:
        section("", "Data Mentah E-Commerce")

        col_f1, col_f2, col_f3 = st.columns(3)
        with col_f1:
            q_prov_ec = st.text_input(" Cari Provinsi", placeholder="Jawa Timur", key="ec_prov")
        with col_f2:
            q_nama_ec = st.text_input(" Cari Nama Produk", placeholder="Ikan Tuna", key="ec_nama")
        with col_f3:
            min_vol_ec = st.number_input("Min Volume Penjualan (Rp)", min_value=0, value=0, step=100_000, key="ec_vol")

        sdf_ec = fec.copy()
        if q_prov_ec: sdf_ec = sdf_ec[sdf_ec["Provinsi"].str.contains(q_prov_ec, case=False, na=False)]
        if q_nama_ec: sdf_ec = sdf_ec[sdf_ec["Nama Produk"].str.contains(q_nama_ec, case=False, na=False)]
        if min_vol_ec > 0: sdf_ec = sdf_ec[sdf_ec["Volume Penjualan (IDR)"] >= min_vol_ec]

        st.markdown(
            f'<span class="info-badge"> {len(sdf_ec):,} produk ditemukan</span>',
            unsafe_allow_html=True,
        )
        st.markdown("")

        disp_cols = ["Provinsi","Pulau","Nama Produk","Lokasi Toko",
                     "Harga (IDR)","Unit Terjual","Volume Penjualan (IDR)","Rating"]
        st.dataframe(
            sdf_ec[disp_cols].sort_values("Volume Penjualan (IDR)", ascending=False),
            use_container_width=True, hide_index=True, height=480,
        )

        c_dl1, c_dl2 = st.columns(2)
        with c_dl1:
            st.download_button(
                " Download Data Terfilter (CSV)",
                data=sdf_ec.to_csv(index=False),
                file_name="ecommerce_terfilter.csv",
                mime="text/csv",
            )
        with c_dl2:
            st.download_button(
                " Download Semua Data E-Commerce (CSV)",
                data=ec.to_csv(index=False),
                file_name="ecommerce_lengkap.csv",
                mime="text/csv",
            )


# ═══════════════════════════════════════════════════
#  PAGE: ANALISIS KORELASI PASAR   NEW 
# ═══════════════════════════════════════════════════
elif menu == " Analisis Korelasi Pasar":
    section("", "Korelasi Produksi Tangkap vs Pasar Digital")

    st.info(
        "Halaman ini menggabungkan data **produksi perikanan tangkap** (BPS 2024) "
        "dengan data **penjualan digital** (Tokopedia 2024) untuk melihat korelasi antar keduanya.",
        icon="",
    )

    # ── Merge datasets per provinsi ──
    tangkap_prov = fdf[["Provinsi","Jumlah","Cakalang","Tongkol","Tuna","Udang","Lainnya","Pulau"]].copy()
    ec_prov_merge = fec.groupby("Provinsi").agg(
        EC_Produk=("Nama Produk","count"),
        EC_Unit=("Unit Terjual","sum"),
        EC_Volume=("Volume Penjualan (IDR)","sum"),
        EC_Avg_Harga=("Harga (IDR)","mean"),
        EC_Avg_Rating=("Rating","mean"),
    ).reset_index()

    merged = tangkap_prov.merge(ec_prov_merge, on="Provinsi", how="inner")

    if len(merged) == 0:
        st.warning("Tidak ada data yang dapat digabungkan dengan filter saat ini. Coba atur ulang filter.")
    else:
        m1, m2, m3, m4 = st.columns(4)
        with m1: st.metric("Provinsi Tergabung", len(merged))
        with m2: st.metric("Total Produksi (Ton)", f"{merged['Jumlah'].sum():,.0f}")
        with m3: st.metric("Total Unit EC", f"{merged['EC_Unit'].sum():,}")
        with m4: st.metric("Total Volume EC", f"Rp {merged['EC_Volume'].sum()/1_000_000:.1f} Jt")

        st.markdown('<hr class="ocean-divider">', unsafe_allow_html=True)

        # ── Scatter: Produksi Tangkap vs Volume Digital ──
        section("", "Produksi Tangkap vs Volume Penjualan Digital")
        c1, c2 = st.columns(2)
        with c1:
            fig = px.scatter(
                merged, x="Jumlah", y="EC_Volume",
                size="EC_Unit", color="Pulau",
                color_discrete_sequence=EC_PALETTE,
                hover_name="Provinsi", size_max=45,
                trendline="ols",
                title="Produksi Tangkap (Ton) vs Volume Penjualan Digital (Rp)",
                labels={"Jumlah":"Produksi Tangkap (Ton)","EC_Volume":"Volume Penjualan Digital (Rp)"},
            )
            fig.update_traces(marker=dict(opacity=0.85))
            st.plotly_chart(plotly_cfg(fig, 440), use_container_width=True)

        with c2:
            fig = px.scatter(
                merged, x="Jumlah", y="EC_Unit",
                size="EC_Volume", color="Pulau",
                color_discrete_sequence=EC_PALETTE,
                hover_name="Provinsi", size_max=45,
                trendline="ols",
                title="Produksi Tangkap (Ton) vs Unit Terjual Digital",
                labels={"Jumlah":"Produksi Tangkap (Ton)","EC_Unit":"Unit Terjual"},
            )
            fig.update_traces(marker=dict(opacity=0.85))
            st.plotly_chart(plotly_cfg(fig, 440), use_container_width=True)

        # ── Bar perbandingan: Produksi & Volume per Wilayah ──
        section("", "Perbandingan Produksi Tangkap & Aktivitas Digital per Wilayah")
        pulau_merged = merged.groupby("Pulau").agg(
            Produksi_Ton=("Jumlah","sum"),
            EC_Volume=("EC_Volume","sum"),
            EC_Unit=("EC_Unit","sum"),
        ).reset_index()

        # Dual-axis chart
        fig = make_subplots(specs=[[{"secondary_y": True}]])
        fig.add_trace(
            go.Bar(
                x=pulau_merged["Pulau"], y=pulau_merged["Produksi_Ton"],
                name="Produksi Tangkap (Ton)", marker_color="#0077B6",
                text=pulau_merged["Produksi_Ton"].map(lambda v: f"{v:,.0f}"),
                textposition="auto", textfont=dict(color="#ffffff", size=10),
            ),
            secondary_y=False,
        )
        fig.add_trace(
            go.Scatter(
                x=pulau_merged["Pulau"], y=pulau_merged["EC_Volume"],
                name="Volume Penjualan Digital (Rp)", mode="lines+markers",
                line=dict(color="#48CAE4", width=2.5),
                marker=dict(size=9, color="#48CAE4"),
            ),
            secondary_y=True,
        )
        fig.update_layout(
            height=420,
            margin=dict(l=10, r=10, t=50, b=10),
            font=dict(family="DM Sans, sans-serif", size=12, color="#b8dff0"),
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(0,0,0,0)",
            title=dict(text=" Produksi Tangkap vs Volume Digital per Wilayah",
                       font=dict(family="Cormorant Garamond, Georgia, serif", size=15, color="#cce8f4")),
            legend=dict(bgcolor="rgba(0,15,35,0.7)", bordercolor="rgba(72,202,228,0.2)", borderwidth=1,
                        font=dict(color="#b8dff0")),
            xaxis=dict(gridcolor="rgba(72,202,228,0.08)", linecolor="rgba(72,202,228,0.15)",
                       tickfont=dict(color="#7ec8e3")),
        )
        fig.update_yaxes(title_text="Produksi Tangkap (Ton)", gridcolor="rgba(72,202,228,0.08)",
                         linecolor="rgba(72,202,228,0.15)", tickfont=dict(color="#7ec8e3"),
                         title_font=dict(color="#0077B6"), secondary_y=False)
        fig.update_yaxes(title_text="Volume Penjualan Digital (Rp)", gridcolor="rgba(72,202,228,0.05)",
                         tickfont=dict(color="#48CAE4"), title_font=dict(color="#48CAE4"), secondary_y=True)
        st.plotly_chart(fig, use_container_width=True)

        # ── Correlation matrix ──
        section("", "Matriks Korelasi – Variabel Gabungan")
        num_cols = ["Jumlah","Cakalang","Tongkol","Tuna","Udang","Lainnya",
                    "EC_Unit","EC_Volume","EC_Avg_Harga","EC_Avg_Rating"]
        rename_map = {
            "Jumlah":"Total Produksi","Cakalang":"Cakalang","Tongkol":"Tongkol",
            "Tuna":"Tuna","Udang":"Udang","Lainnya":"Lainnya",
            "EC_Unit":"Unit EC","EC_Volume":"Vol EC","EC_Avg_Harga":"Harga Avg",
            "EC_Avg_Rating":"Rating Avg",
        }
        corr_df = merged[num_cols].rename(columns=rename_map).corr().round(3)
        fig = px.imshow(
            corr_df, text_auto=True,
            color_continuous_scale=["#001525","#003F6B","#0077B6","#00B4D8","#90E0EF"],
            title=" Matriks Korelasi: Produksi Tangkap ↔ Pasar Digital",
            aspect="auto",
        )
        fig.update_traces(textfont=dict(color="#ffffff", size=11))
        st.plotly_chart(plotly_cfg(fig, 480), use_container_width=True)

        # ── Tabel gabungan ──
        section("", "Tabel Data Gabungan per Provinsi")
        disp_merged = merged[["Provinsi","Pulau","Jumlah","EC_Unit","EC_Volume","EC_Avg_Harga","EC_Avg_Rating"]].copy()
        disp_merged.columns = ["Provinsi","Wilayah","Produksi (Ton)","Unit EC","Volume EC (Rp)","Avg Harga EC","Avg Rating EC"]
        disp_merged["Avg Harga EC"] = disp_merged["Avg Harga EC"].round(0).astype(int)
        disp_merged["Avg Rating EC"] = disp_merged["Avg Rating EC"].round(3)
        st.dataframe(disp_merged.sort_values("Produksi (Ton)", ascending=False),
                     use_container_width=True, hide_index=True)

        st.download_button(
            " Download Data Gabungan (CSV)",
            data=merged.to_csv(index=False),
            file_name="data_gabungan_tangkap_ecommerce.csv",
            mime="text/csv",
        )


# ═══════════════════════════════════════════════════
#  PAGE: PENCARIAN DATA
# ═══════════════════════════════════════════════════
elif menu == " Pencarian Data":
    section("", "Pencarian & Filter Data")

    with st.expander(" Pencarian Lanjutan", expanded=True):
        sc1, sc2, sc3 = st.columns(3)
        with sc1:
            q_prov = st.text_input(" Cari Provinsi", placeholder="Jawa Timur")
        with sc2:
            q_pulau = st.text_input(" Cari Wilayah", placeholder="Sulawesi")
        with sc3:
            sort_col = st.selectbox(
                "Urutkan berdasarkan",
                ["Jumlah","Cakalang","Tongkol","Tuna","Udang","Lainnya"],
            )

        sc4, sc5 = st.columns(2)
        with sc4:
            sort_dir = st.radio("Urutan", ["Descending ↓","Ascending ↑"], horizontal=True)
        with sc5:
            min_jumlah = st.number_input("Minimum Total Produksi (Ton)", min_value=0, value=0, step=1000)

    sdf = fdf.copy()
    if q_prov:  sdf = sdf[sdf["Provinsi"].str.contains(q_prov, case=False, na=False)]
    if q_pulau: sdf = sdf[sdf["Pulau"].str.contains(q_pulau, case=False, na=False)]
    if min_jumlah > 0: sdf = sdf[sdf["Jumlah"] >= min_jumlah]
    asc = sort_dir.startswith("Ascending")
    sdf = sdf.sort_values(sort_col, ascending=asc)

    st.markdown(
        f'<span class="info-badge"> {len(sdf)} provinsi ditemukan dari {len(fdf)} data terfilter</span>',
        unsafe_allow_html=True,
    )
    st.markdown("")

    col_res, col_sum = st.columns([3, 1])
    with col_res:
        display_cols = ["Provinsi","Pulau","Cakalang","Tongkol","Tuna","Udang","Lainnya","Jumlah","Kategori_Produksi"]
        st.dataframe(
            sdf[display_cols].rename(columns={"Jumlah":"Total (Ton)","Kategori_Produksi":"Kategori"}),
            use_container_width=True, hide_index=True, height=420,
        )

    with col_sum:
        st.markdown("** Statistik Hasil Pencarian**")
        if len(sdf) > 0:
            st.metric("Total Produksi", f"{sdf['Jumlah'].sum():,.0f} Ton")
            st.metric("Rata-rata", f"{sdf['Jumlah'].mean():,.0f} Ton")
            st.metric("Tertinggi", f"{sdf['Jumlah'].max():,.0f} Ton")
            st.metric("Terendah", f"{sdf['Jumlah'].min():,.0f} Ton")
        else:
            st.warning("Tidak ada data")

    st.download_button(
        " Download Hasil Pencarian (CSV)",
        data=sdf.to_csv(index=False),
        file_name="hasil_pencarian.csv",
        mime="text/csv",
    )


# ═══════════════════════════════════════════════════
#  PAGE: DATA LENGKAP
# ═══════════════════════════════════════════════════
elif menu == " Data Lengkap":
    section("", "Data Lengkap Produksi Perikanan Tangkap 2024")

    tab_raw, tab_stat, tab_corr = st.tabs([" Tabel Data"," Statistik Deskriptif"," Korelasi"])

    with tab_raw:
        st.markdown(
            f'<span class="info-badge"> Menampilkan {len(fdf)} dari {len(df)} total provinsi</span>',
            unsafe_allow_html=True,
        )
        st.markdown("")
        display = fdf[["Provinsi","Pulau","Cakalang","Tongkol","Tuna","Udang","Lainnya","Jumlah","Kategori_Produksi"]].copy()
        display.columns = ["Provinsi","Wilayah","Cakalang","Tongkol","Tuna","Udang","Lainnya","Total (Ton)","Kategori"]
        st.dataframe(display, use_container_width=True, hide_index=True, height=500)

        c1, c2 = st.columns(2)
        with c1:
            st.download_button(
                " Download Data Terfilter (CSV)",
                data=fdf.to_csv(index=False), file_name="data_terfilter.csv", mime="text/csv",
            )
        with c2:
            st.download_button(
                " Download Semua Data (CSV)",
                data=df.to_csv(index=False), file_name="data_lengkap.csv", mime="text/csv",
            )

    with tab_stat:
        stat_cols = ["Cakalang","Tongkol","Tuna","Udang","Lainnya","Jumlah"]
        stat = fdf[stat_cols].agg(["sum","mean","std","min","max"]).round(0).T
        stat.columns = ["Total","Rata-rata","Std Dev","Min","Max"]
        stat.index.name = "Komoditas"
        st.dataframe(stat.reset_index(), use_container_width=True, hide_index=True)

        fig = px.histogram(
            fdf, x="Jumlah", nbins=15,
            color_discrete_sequence=["#0077B6"],
            title=" Distribusi Total Produksi per Provinsi",
            labels={"Jumlah":"Total Produksi (Ton)","count":"Frekuensi"},
        )
        fig.update_traces(marker_line_color="#00B4D8", marker_line_width=1,
                          marker_color="#0077B6", opacity=0.85)
        st.plotly_chart(plotly_cfg(fig, 320), use_container_width=True)

        prov_long_all = fdf.sort_values("Jumlah", ascending=False).melt(
            id_vars="Provinsi", value_vars=["Cakalang","Tongkol","Tuna","Udang","Lainnya"],
            var_name="Komoditas", value_name="Ton",
        )
        fig = px.area(
            prov_long_all, x="Provinsi", y="Ton", color="Komoditas",
            color_discrete_map=KOMODITAS_COLORS,
            title="Area Chart Komposisi Komoditas per Provinsi",
        )
        fig.update_xaxes(tickangle=-40)
        fig.update_traces(opacity=0.8)
        st.plotly_chart(plotly_cfg(fig, 360), use_container_width=True)

    with tab_corr:
        st.markdown(
            '<span style="color:#7ec8e3;font-family:\'DM Sans\',sans-serif;">'
            "Korelasi antar variabel numerik (produksi per komoditas)</span>",
            unsafe_allow_html=True,
        )
        num_df = fdf[["Cakalang","Tongkol","Tuna","Udang","Lainnya","Jumlah"]]
        corr = num_df.corr().round(3)
        fig = px.imshow(
            corr, text_auto=True,
            color_continuous_scale=["#001525","#003F6B","#0077B6","#00B4D8","#90E0EF"],
            title=" Matriks Korelasi Antar Komoditas", aspect="auto",
        )
        fig.update_traces(textfont=dict(color="#ffffff", size=13))
        st.plotly_chart(plotly_cfg(fig, 420), use_container_width=True)

        fig = px.scatter_matrix(
            fdf, dimensions=["Cakalang","Tongkol","Tuna","Udang","Lainnya"],
            color="Pulau", color_discrete_sequence=OCEAN_PALETTE,
            title="Scatter Matrix Komoditas",
        )
        fig.update_traces(marker=dict(size=5, opacity=0.7,
                                      line=dict(color="#030d1a", width=0.5)))
        st.plotly_chart(plotly_cfg(fig, 500), use_container_width=True)


# ─────────────────────────────────────────────
#  FOOTER
# ─────────────────────────────────────────────
st.markdown('<hr class="ocean-divider">', unsafe_allow_html=True)
st.markdown(
    f"""
    <div class="footer">
        <img src="{UNSOED_LOGO_URL}"
            style="height:30px; vertical-align:middle; margin-right:.6rem;
                   border-radius:5px; opacity:.8;">
        <strong style="color:#4a7a96;">Dashboard Praktikum Pengolahan Data Kelautan</strong>
        &nbsp;·&nbsp; Universitas Jenderal Soedirman &nbsp;·&nbsp; 2026<br>
        <span style="opacity:.6;">
            Sumber Data: BPS — Produksi Perikanan Tangkap 2024 &nbsp;|&nbsp;
            Tokopedia — Data Produk Ikan Laut 2024 &nbsp;·&nbsp; 38 Provinsi Indonesia
        </span>
    </div>
    """,
    unsafe_allow_html=True,
)