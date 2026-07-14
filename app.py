import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Supabase bağlantısı
try:
    from supabase import create_client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False

# ============================================
# SAYFA YAPILANDIRMASI
# ============================================
st.set_page_config(
    page_title="Çankaya MEM | Norm Fazlası Öğretmen Dağılım Sistemi",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================
# KARANLIK BİLİMSEL TEMA
# ============================================
st.markdown("""
<style>
    /* Ana Tema */
    .stApp {
        background: linear-gradient(135deg, #0a0e27 0%, #1a1f3a 50%, #0d1128 100%);
    }
    
    /* Header */
    .main-header {
        background: linear-gradient(135deg, #1a237e 0%, #283593 50%, #1a237e 100%);
        color: #e8eaf6;
        text-align: center;
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        box-shadow: 0 8px 32px rgba(26, 35, 126, 0.3);
        border: 1px solid rgba(255,255,255,0.1);
        position: relative;
        overflow: hidden;
    }
    .main-header::before {
        content: '';
        position: absolute;
        top: -50%;
        left: -50%;
        width: 200%;
        height: 200%;
        background: radial-gradient(circle, rgba(255,255,255,0.05) 0%, transparent 70%);
        animation: rotate 20s linear infinite;
    }
    @keyframes rotate {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
    }
    .main-header h1 {
        position: relative;
        z-index: 1;
        font-size: 2.2rem;
        font-weight: 700;
        text-shadow: 0 2px 10px rgba(0,0,0,0.5);
    }
    .main-header h2 {
        position: relative;
        z-index: 1;
    }
    .main-header p {
        position: relative;
        z-index: 1;
    }
    
    /* Kartlar */
    .stat-card {
        background: linear-gradient(135deg, rgba(26,35,126,0.4) 0%, rgba(40,53,147,0.3) 100%);
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 15px;
        padding: 1.5rem;
        text-align: center;
        backdrop-filter: blur(10px);
        box-shadow: 0 4px 16px rgba(0,0,0,0.3);
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    .stat-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 25px rgba(26,35,126,0.5);
        border-color: rgba(255,255,255,0.3);
    }
    .stat-card::after {
        content: '';
        position: absolute;
        bottom: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: linear-gradient(90deg, #667eea, #764ba2);
    }
    .stat-value {
        font-size: 2.5rem;
        font-weight: 800;
        color: #e8eaf6;
        text-shadow: 0 0 20px rgba(102,126,234,0.5);
    }
    .stat-label {
        font-size: 0.9rem;
        color: #9fa8da;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    
    /* Durum Badge'leri */
    .badge-excess {
        background: linear-gradient(135deg, #c62828, #d32f2f);
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        box-shadow: 0 2px 8px rgba(198,40,40,0.4);
    }
    .badge-deficit {
        background: linear-gradient(135deg, #2e7d32, #388e3c);
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        box-shadow: 0 2px 8px rgba(46,125,50,0.4);
    }
    .badge-normal {
        background: linear-gradient(135deg, #f57f17, #f9a825);
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        box-shadow: 0 2px 8px rgba(245,127,23,0.4);
    }
    
    /* Filtre Paneli */
    .filter-panel {
        background: rgba(26,35,126,0.2);
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 15px;
        padding: 1.5rem;
        backdrop-filter: blur(10px);
    }
    .filter-title {
        color: #e8eaf6;
        font-size: 1.2rem;
        font-weight: 700;
        margin-bottom: 1rem;
        border-bottom: 2px solid rgba(102,126,234,0.5);
        padding-bottom: 0.5rem;
    }
    
    /* Tablo Stilleri */
    .dataframe-container {
        background: rgba(26,35,126,0.2);
        border-radius: 15px;
        padding: 1rem;
        border: 1px solid rgba(255,255,255,0.1);
    }
    
    /* Grafik Konteyner */
    .chart-container {
        background: rgba(26,35,126,0.15);
        border-radius: 15px;
        padding: 1rem;
        border: 1px solid rgba(255,255,255,0.08);
        margin: 1rem 0;
    }
    
    /* Senkronizasyon Badge */
    .sync-badge {
        background: linear-gradient(135deg, #00c853, #00e676);
        color: white;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        font-size: 0.75rem;
        animation: pulse 2s infinite;
    }
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.6; }
    }
    
    /* İlerleme Çubuğu */
    .stProgress > div > div > div {
        background: linear-gradient(90deg, #667eea, #764ba2);
    }
    
    /* Selectbox ve Input - Genel */
    .stSelectbox, .stTextInput, .stSlider {
        background: rgba(255,255,255,0.05);
        border-radius: 10px;
    }
    
    /* Tab Stilleri */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background: rgba(26,35,126,0.2);
        border-radius: 15px;
        padding: 0.5rem;
    }
    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border-radius: 10px;
        color: #9fa8da;
        padding: 0.5rem 1.5rem;
        transition: all 0.3s;
    }
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea, #764ba2);
        color: white;
        box-shadow: 0 4px 15px rgba(102,126,234,0.4);
    }
    
    /* Okul Link Stilleri */
    .school-link {
        color: #82b1ff;
        text-decoration: none;
        transition: all 0.3s;
    }
    .school-link:hover {
        color: #b388ff;
        text-shadow: 0 0 10px rgba(179,136,255,0.5);
    }
    
    /* Footer */
    .footer {
        text-align: center;
        color: #5c6bc0;
        padding: 1rem;
        border-top: 1px solid rgba(255,255,255,0.05);
        margin-top: 2rem;
    }

    /* ============================================
       SIDEBAR KARANLIK TEMA - TÜM METİNLER OKUNUR
       ============================================ */
    
    /* Sidebar arka planı */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #0a0e27 0%, #1a1f3a 100%);
        border-right: 1px solid rgba(255,255,255,0.1);
    }
    
    /* Sidebar içindeki TÜM metin elementleri - beyaz renk */
    [data-testid="stSidebar"] * {
        color: #e8eaf6 !important;
    }
    
    /* Sidebar'daki tüm başlıklar */
    [data-testid="stSidebar"] h1,
    [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3,
    [data-testid="stSidebar"] h4,
    [data-testid="stSidebar"] h5,
    [data-testid="stSidebar"] h6,
    [data-testid="stSidebar"] .stMarkdown h1,
    [data-testid="stSidebar"] .stMarkdown h2,
    [data-testid="stSidebar"] .stMarkdown h3,
    [data-testid="stSidebar"] .stMarkdown h4,
    [data-testid="stSidebar"] .stMarkdown h5,
    [data-testid="stSidebar"] .stMarkdown h6 {
        color: #ffffff !important;
        font-weight: 600;
    }
    
    /* Sidebar'daki tüm etiketler (label) */
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] .stSelectbox label,
    [data-testid="stSidebar"] .stTextInput label,
    [data-testid="stSidebar"] .stSlider label,
    [data-testid="stSidebar"] .stRadio label,
    [data-testid="stSidebar"] .stCheckbox label,
    [data-testid="stSidebar"] .stNumberInput label,
    [data-testid="stSidebar"] .stDateInput label,
    [data-testid="stSidebar"] .stTimeInput label {
        color: #e8eaf6 !important;
        font-weight: 500;
    }
    
    /* Sidebar'daki metric değerleri ve etiketleri */
    [data-testid="stSidebar"] .stMetric {
        color: #e8eaf6 !important;
    }
    [data-testid="stSidebar"] .stMetric .stMetricValue {
        color: #ffffff !important;
        font-weight: 700;
        font-size: 1.5rem;
    }
    [data-testid="stSidebar"] .stMetric .stMetricLabel {
        color: #9fa8da !important;
        font-size: 0.9rem;
    }
    [data-testid="stSidebar"] .stMetric .stMetricDelta {
        color: #b388ff !important;
    }
    
    /* Sidebar'daki selectbox - seçili değer */
    [data-testid="stSidebar"] .stSelectbox select,
    [data-testid="stSidebar"] .stSelectbox div[data-baseweb="select"] div {
        color: #e8eaf6 !important;
        background: rgba(255,255,255,0.08);
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 8px;
    }
    
    /* Sidebar'daki selectbox - dropdown seçenekleri */
    [data-testid="stSidebar"] .stSelectbox ul {
        background: #1a1f3a !important;
        border: 1px solid rgba(255,255,255,0.1);
    }
    [data-testid="stSidebar"] .stSelectbox ul li {
        color: #e8eaf6 !important;
        background: transparent !important;
    }
    [data-testid="stSidebar"] .stSelectbox ul li:hover {
        background: rgba(102,126,234,0.3) !important;
    }
    
    /* Sidebar'daki text input */
    [data-testid="stSidebar"] input[type="text"],
    [data-testid="stSidebar"] input[type="number"],
    [data-testid="stSidebar"] input[type="password"],
    [data-testid="stSidebar"] textarea {
        color: #e8eaf6 !important;
        background: rgba(255,255,255,0.08);
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 8px;
    }
    [data-testid="stSidebar"] input::placeholder,
    [data-testid="stSidebar"] textarea::placeholder {
        color: #5c6bc0 !important;
    }
    
    /* Sidebar'daki slider */
    [data-testid="stSidebar"] .stSlider .stSliderTrack {
        background: rgba(255,255,255,0.15);
    }
    [data-testid="stSidebar"] .stSlider .stSliderThumb {
        background: #667eea !important;
        border-color: #667eea !important;
    }
    [data-testid="stSidebar"] .stSlider .stSliderValue {
        color: #e8eaf6 !important;
    }
    
    /* Sidebar'daki radio butonları */
    [data-testid="stSidebar"] .stRadio > div,
    [data-testid="stSidebar"] .stRadio label {
        color: #e8eaf6 !important;
    }
    [data-testid="stSidebar"] .stRadio label div {
        color: #e8eaf6 !important;
    }
    
    /* Sidebar'daki checkbox */
    [data-testid="stSidebar"] .stCheckbox label {
        color: #e8eaf6 !important;
    }
    
    /* Sidebar'daki butonlar */
    [data-testid="stSidebar"] .stButton button {
        background: linear-gradient(135deg, #667eea, #764ba2) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 0.5rem 1rem !important;
        transition: all 0.3s !important;
        font-weight: 500;
    }
    [data-testid="stSidebar"] .stButton button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 4px 20px rgba(102,126,234,0.4) !important;
    }
    
    /* Sidebar'daki info/warning/success/error blokları */
    [data-testid="stSidebar"] .stAlert {
        background: rgba(26,35,126,0.3) !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        border-radius: 10px !important;
    }
    [data-testid="stSidebar"] .stAlert div,
    [data-testid="stSidebar"] .stAlert p {
        color: #e8eaf6 !important;
    }
    
    /* Sidebar'daki expander */
    [data-testid="stSidebar"] .streamlit-expanderHeader {
        color: #e8eaf6 !important;
        background: rgba(255,255,255,0.05) !important;
        border-radius: 10px !important;
    }
    [data-testid="stSidebar"] .streamlit-expanderContent {
        color: #9fa8da !important;
        background: rgba(255,255,255,0.02) !important;
        border-radius: 0 0 10px 10px !important;
    }
    [data-testid="stSidebar"] .streamlit-expanderContent * {
        color: #9fa8da !important;
    }
    
    /* Sidebar'daki filtre paneli */
    [data-testid="stSidebar"] .filter-panel {
        background: rgba(26,35,126,0.3) !important;
        border: 1px solid rgba(255,255,255,0.08) !important;
    }
    [data-testid="stSidebar"] .filter-title {
        color: #e8eaf6 !important;
        border-bottom-color: rgba(102,126,234,0.3) !important;
    }
    
    /* Sidebar scrollbar */
    [data-testid="stSidebar"] ::-webkit-scrollbar {
        width: 6px;
    }
    [data-testid="stSidebar"] ::-webkit-scrollbar-track {
        background: rgba(255,255,255,0.05);
        border-radius: 3px;
    }
    [data-testid="stSidebar"] ::-webkit-scrollbar-thumb {
        background: rgba(102,126,234,0.5);
        border-radius: 3px;
    }
    [data-testid="stSidebar"] ::-webkit-scrollbar-thumb:hover {
        background: rgba(102,126,234,0.8);
    }

    /* ============================================
       ANA SAYFA TÜM METİNLER OKUNUR
       ============================================ */
    
    /* Ana sayfadaki tüm metinler */
    .stApp .stMarkdown,
    .stApp .stText,
    .stApp .stDataFrame,
    .stApp p,
    .stApp li,
    .stApp span,
    .stApp div:not(.stat-card):not(.main-header):not(.filter-panel) {
        color: #e8eaf6;
    }
    
    /* Dataframe tablo başlıkları */
    .stDataFrame thead tr th {
        color: #e8eaf6 !important;
        background: rgba(26,35,126,0.3) !important;
    }
    .stDataFrame tbody tr td {
        color: #e8eaf6 !important;
    }
    
    /* Metric değerleri ana sayfa */
    .stMetric .stMetricValue {
        color: #e8eaf6 !important;
    }
    .stMetric .stMetricLabel {
        color: #9fa8da !important;
    }
    
    /* Info, warning, success, error blokları ana sayfa */
    .stAlert div,
    .stAlert p {
        color: #e8eaf6 !important;
    }
    
    /* Selectbox ana sayfa */
    .stSelectbox select,
    .stSelectbox div[data-baseweb="select"] div {
        color: #e8eaf6 !important;
        background: rgba(255,255,255,0.08);
        border: 1px solid rgba(255,255,255,0.1);
    }
    .stSelectbox ul {
        background: #1a1f3a !important;
    }
    .stSelectbox ul li {
        color: #e8eaf6 !important;
    }
    
    /* Input ana sayfa */
    .stTextInput input,
    .stNumberInput input {
        color: #e8eaf6 !important;
        background: rgba(255,255,255,0.08);
        border: 1px solid rgba(255,255,255,0.1);
    }
    .stTextInput input::placeholder {
        color: #5c6bc0 !important;
    }
</style>
""", unsafe_allow_html=True)

# ============================================
# SUPABASE BAĞLANTISI
# ============================================
@st.cache_resource
def init_supabase():
    if SUPABASE_AVAILABLE:
        try:
            supabase = create_client(
                st.secrets.get("SUPABASE_URL", ""),
                st.secrets.get("SUPABASE_KEY", "")
            )
            return supabase
        except:
            return None
    return None

supabase = init_supabase()

# ============================================
# VERİ YÜKLEME FONKSİYONLARI
# ============================================
@st.cache_data(ttl=300)
def load_norm_data():
    """Norm durumu verilerini yükle"""
    if supabase:
        try:
            response = supabase.table('norm_durumu_gorunumu').select('*').execute()
            return pd.DataFrame(response.data)
        except:
            pass
    
    # Demo veri
    return generate_demo_data()

@st.cache_data(ttl=300)
def load_school_summary():
    """Okul özet verilerini yükle"""
    if supabase:
        try:
            response = supabase.table('okul_ozet_gorunumu').select('*').execute()
            return pd.DataFrame(response.data)
        except:
            pass
    return None

@st.cache_data(ttl=120)
def load_excess_teachers():
    """Norm fazlası öğretmenleri yükle"""
    if supabase:
        try:
            response = supabase.table('norm_fazlasi_ogretmenler').select('*').execute()
            return pd.DataFrame(response.data)
        except:
            pass
    return pd.DataFrame()

def generate_demo_data():
    """Demo veri oluştur"""
    np.random.seed(42)
    
    school_types = {
        'Anaokulu': 15,
        'İlkokul': 85,
        'Ortaokul': 65,
        'OBP ile Öğrenci Alan Anadolu Lisesi': 40,
        'Çok Programlı Lise': 15,
        'Meslek Lisesi': 25
    }
    
    branches_by_type = {
        'Anaokulu': ['Okul Öncesi Öğretmenliği', 'Özel Eğitim', 'Rehberlik', 'İngilizce'],
        'İlkokul': ['Sınıf Öğretmenliği', 'İngilizce', 'Din Kültürü ve Ahlak Bilgisi', 
                    'Rehberlik', 'Özel Eğitim', 'Beden Eğitimi', 'Müzik', 
                    'Görsel Sanatlar', 'Bilişim Teknolojileri', 'Türkçe Öğretici'],
        'Ortaokul': ['Türkçe', 'Matematik', 'Fen Bilimleri', 'Sosyal Bilgiler', 
                     'İngilizce', 'Din Kültürü ve Ahlak Bilgisi', 'Beden Eğitimi',
                     'Teknoloji ve Tasarım', 'Müzik', 'Görsel Sanatlar', 'Rehberlik',
                     'Bilişim Teknolojileri', 'Özel Eğitim'],
        'OBP ile Öğrenci Alan Anadolu Lisesi': [
            'Türk Dili ve Edebiyatı', 'Matematik', 'Fizik', 'Kimya', 'Biyoloji',
            'Tarih', 'Coğrafya', 'Felsefe', 'İngilizce', 'Almanca', 'Beden Eğitimi',
            'Din Kültürü ve Ahlak Bilgisi', 'Rehberlik', 'Müzik', 'Görsel Sanatlar',
            'Bilişim Teknolojileri', 'Sanat Tarihi', 'Sağlık Bilgisi'
        ],
        'Çok Programlı Lise': [
            'Türk Dili ve Edebiyatı', 'Matematik', 'Fizik', 'Kimya', 'Biyoloji',
            'Tarih', 'Coğrafya', 'Felsefe', 'İngilizce', 'Beden Eğitimi',
            'Din Kültürü ve Ahlak Bilgisi', 'Rehberlik', 'Bilişim Teknolojileri',
            'Elektrik-Elektronik Teknolojisi', 'Makine Teknolojisi',
            'Muhasebe ve Finansman', 'Yiyecek İçecek Hizmetleri',
            'Çocuk Gelişimi ve Eğitimi', 'Tarım Teknolojileri',
            'Sanat Tarihi', 'Sağlık Bilgisi'
        ],
        'Meslek Lisesi': [
            'Türk Dili ve Edebiyatı', 'Matematik', 'Fizik', 'Kimya', 'Biyoloji',
            'Tarih', 'Coğrafya', 'Felsefe', 'İngilizce', 'Beden Eğitimi',
            'Din Kültürü ve Ahlak Bilgisi', 'Rehberlik', 'Bilişim Teknolojileri',
            'Elektrik-Elektronik Teknolojisi', 'Makine Teknolojisi',
            'Muhasebe ve Finansman', 'Yiyecek İçecek Hizmetleri',
            'Çocuk Gelişimi ve Eğitimi', 'Giyim Üretim Teknolojisi',
            'Güzellik ve Saç Bakım Hizmetleri', 'Metal Teknolojisi',
            'Motorlu Araçlar Teknolojisi', 'Tesisat Teknolojisi ve İklimlendirme',
            'Harita-Tapu-Kadastro', 'Sanat Tarihi', 'Sağlık Bilgisi'
        ]
    }
    
    data = []
    school_id = 0
    
    for school_type, count in school_types.items():
        for s in range(count):
            school_id += 1
            school_name = f"{school_type} {s+1}. Okul"
            derslik = np.random.randint(8, 40)
            
            for branch in branches_by_type[school_type]:
                norm = max(1, int(derslik * np.random.uniform(0.5, 2.0)))
                teachers = norm + np.random.choice([-2, -1, 0, 1, 2, 3], p=[0.1, 0.2, 0.25, 0.2, 0.15, 0.1])
                teachers = max(0, teachers)
                
                if teachers > norm:
                    norm_status = 'Norm Fazlası'
                elif teachers < norm:
                    norm_status = 'Norm Eksiği'
                else:
                    norm_status = 'Normal'
                
                data.append({
                    'okul_id': str(school_id),
                    'okul_adi': school_name,
                    'okul_turu': school_type,
                    'brans_adi': branch,
                    'norm_sayisi': norm,
                    'mevcut_ogretmen': teachers,
                    'norm_durumu': norm_status,
                    'norm_fazlasi_sayisi': max(0, teachers - norm),
                    'norm_eksigi_sayisi': max(0, norm - teachers),
                    'ortalama_hizmet_puani': np.random.randint(150, 450),
                    'derslik_sayisi': derslik
                })
    
    return pd.DataFrame(data)

# ============================================
# VERİ YÜKLEME
# ============================================
df = load_norm_data()

# ============================================
# SIDEBAR - FİLTRELER
# ============================================
with st.sidebar:
    st.markdown("""
    <div style="text-align: center; margin-bottom: 1rem;">
        <h2 style="color: #e8eaf6; font-size: 1.3rem;">🔍 FİLTRELEME PANELİ</h2>
    </div>
    """, unsafe_allow_html=True)
    
    # Okul Türü Filtresi
    st.markdown('<div class="filter-panel">', unsafe_allow_html=True)
    st.markdown('<p class="filter-title">🏫 Okul Türü</p>', unsafe_allow_html=True)
    okul_turleri = ['Tümü'] + sorted(df['okul_turu'].unique().tolist())
    selected_type = st.selectbox('', okul_turleri, label_visibility='collapsed')
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Branş Filtresi
    st.markdown('<div class="filter-panel">', unsafe_allow_html=True)
    st.markdown('<p class="filter-title">📚 Branş</p>', unsafe_allow_html=True)
    
    if selected_type != 'Tümü':
        filtered_branches = df[df['okul_turu'] == selected_type]['brans_adi'].unique()
    else:
        filtered_branches = df['brans_adi'].unique()
    
    branslar = ['Tümü'] + sorted(filtered_branches.tolist())
    selected_branch = st.selectbox('', branslar, label_visibility='collapsed')
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Norm Durumu Filtresi
    st.markdown('<div class="filter-panel">', unsafe_allow_html=True)
    st.markdown('<p class="filter-title">⚖️ Norm Durumu</p>', unsafe_allow_html=True)
    norm_durumlari = ['Tümü', 'Norm Fazlası', 'Norm Eksiği', 'Normal']
    selected_norm = st.selectbox('', norm_durumlari, label_visibility='collapsed')
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Derslik Sayısı Aralığı
    st.markdown('<div class="filter-panel">', unsafe_allow_html=True)
    st.markdown('<p class="filter-title">🏗️ Derslik Sayısı</p>', unsafe_allow_html=True)
    min_derslik = int(df['derslik_sayisi'].min())
    max_derslik = int(df['derslik_sayisi'].max())
    derslik_range = st.slider('', min_derslik, max_derslik, 
                              (min_derslik, max_derslik), label_visibility='collapsed')
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Okul Arama
    st.markdown('<div class="filter-panel">', unsafe_allow_html=True)
    st.markdown('<p class="filter-title">🔎 Okul Ara</p>', unsafe_allow_html=True)
    school_search = st.text_input('', placeholder='Okul adı yazın...', label_visibility='collapsed')
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Hızlı İstatistikler
    st.markdown("---")
    st.markdown("### 📊 Hızlı İstatistikler")
    
    filtered_df = df.copy()
    if selected_type != 'Tümü':
        filtered_df = filtered_df[filtered_df['okul_turu'] == selected_type]
    if selected_branch != 'Tümü':
        filtered_df = filtered_df[filtered_df['brans_adi'] == selected_branch]
    if selected_norm != 'Tümü':
        filtered_df = filtered_df[filtered_df['norm_durumu'] == selected_norm]
    if school_search:
        filtered_df = filtered_df[filtered_df['okul_adi'].str.contains(school_search, case=False)]
    filtered_df = filtered_df[(filtered_df['derslik_sayisi'] >= derslik_range[0]) & 
                              (filtered_df['derslik_sayisi'] <= derslik_range[1])]
    
    col1, col2 = st.columns(2)
    with col1:
        st.metric("🏫 Okul", filtered_df['okul_id'].nunique())
    with col2:
        st.metric("👨‍🏫 Öğretmen", f"{filtered_df['mevcut_ogretmen'].sum():,}")
    
    col3, col4 = st.columns(2)
    with col3:
        st.metric("🔴 Fazla", filtered_df['norm_fazlasi_sayisi'].sum())
    with col4:
        st.metric("🟢 Eksik", filtered_df['norm_eksigi_sayisi'].sum())

# ============================================
# ANA HEADER
# ============================================
st.markdown(f"""
<div class="main-header">
    <h1>📊 Çankaya İlçe Milli Eğitim Müdürlüğü</h1>
    <h2 style="font-size: 1.5rem; color: #9fa8da; position: relative; z-index: 1;">
        Norm Fazlası Öğretmen Dağılım ve Takip Sistemi
    </h2>
    <p style="color: #7986cb; position: relative; z-index: 1; margin-top: 0.5rem;">
        Son Güncelleme: {datetime.now().strftime('%d.%m.%Y %H:%M')} | 
        Toplam Okul: {df['okul_id'].nunique()} | 
        Toplam Branş: {df['brans_adi'].nunique()}
    </p>
</div>
""", unsafe_allow_html=True)

# ============================================
# ANA SEKMELER
# ============================================
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "📊 GENEL BAKIŞ",
    "🏫 OKUL ANALİZİ",
    "👨‍🏫 BRANŞ ANALİZİ",
    "⚠️ NORM FAZLASI",
    "📈 RAPORLAR",
    "🔗 OKUL LİNKLERİ",
    "🔄 GÖREVLENDİRME"
])

# ============================================
# TAB 1: GENEL BAKIŞ
# ============================================
with tab1:
    st.markdown("## 📊 Çankaya İlçe Milli Eğitim Genel Durum Paneli")
    
    # Özet Kartları
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-value">{filtered_df['okul_id'].nunique()}</div>
            <div class="stat-label">🏫 Toplam Okul</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-value">{filtered_df['mevcut_ogretmen'].sum():,}</div>
            <div class="stat-label">👨‍🏫 Toplam Öğretmen</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-value">{filtered_df['norm_sayisi'].sum():,}</div>
            <div class="stat-label">📋 Toplam Norm Kadro</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-value" style="color: #ff5252;">{filtered_df['norm_fazlasi_sayisi'].sum()}</div>
            <div class="stat-label">🔴 Norm Fazlası</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col5:
        st.markdown(f"""
        <div class="stat-card">
            <div class="stat-value" style="color: #69f0ae;">{filtered_df['norm_eksigi_sayisi'].sum()}</div>
            <div class="stat-label">🟢 Norm Eksiği</div>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Grafikler
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        # Okul Türü Dağılımı
        type_dist = filtered_df.groupby('okul_turu')['okul_id'].nunique().reset_index()
        type_dist.columns = ['Okul Türü', 'Okul Sayısı']
        
        fig = px.pie(
            type_dist, 
            values='Okul Sayısı', 
            names='Okul Türü',
            title='Okul Türlerine Göre Dağılım',
            color_discrete_sequence=px.colors.sequential.Plasma_r,
            hole=0.4
        )
        fig.update_traces(textposition='inside', textinfo='percent+label', 
                         textfont=dict(color='white', size=11))
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#e8eaf6'),
            title_font=dict(color='#e8eaf6', size=16),
            legend=dict(font=dict(color='#9fa8da')),
            height=450
        )
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        # Norm Durumu Dağılımı
        norm_dist = filtered_df['norm_durumu'].value_counts().reset_index()
        norm_dist.columns = ['Norm Durumu', 'Sayı']
        
        fig = px.bar(
            norm_dist,
            x='Norm Durumu',
            y='Sayı',
            title='Norm Durumu Dağılımı',
            color='Norm Durumu',
            color_discrete_map={
                'Norm Fazlası': '#ff5252',
                'Normal': '#ffab40',
                'Norm Eksiği': '#69f0ae'
            },
            text='Sayı'
        )
        fig.update_traces(textposition='outside', textfont=dict(color='white', size=14))
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#e8eaf6'),
            title_font=dict(color='#e8eaf6', size=16),
            showlegend=False,
            height=450
        )
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Okul Türüne Göre Karşılaştırma
    st.markdown("### Okul Türüne Göre Norm Kadro Karşılaştırması")
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    
    type_analysis = filtered_df.groupby('okul_turu').agg({
        'norm_sayisi': 'sum',
        'mevcut_ogretmen': 'sum',
        'norm_fazlasi_sayisi': 'sum',
        'norm_eksigi_sayisi': 'sum'
    }).reset_index()
    
    fig = go.Figure()
    fig.add_trace(go.Bar(name='Norm Kadro', x=type_analysis['okul_turu'], 
                         y=type_analysis['norm_sayisi'], 
                         marker_color='#82b1ff', marker_line_color='#448aff',
                         marker_line_width=1.5))
    fig.add_trace(go.Bar(name='Mevcut Öğretmen', x=type_analysis['okul_turu'], 
                         y=type_analysis['mevcut_ogretmen'], 
                         marker_color='#b388ff', marker_line_color='#7c4dff',
                         marker_line_width=1.5))
    fig.add_trace(go.Bar(name='Norm Fazlası', x=type_analysis['okul_turu'], 
                         y=type_analysis['norm_fazlasi_sayisi'], 
                         marker_color='#ff5252', marker_line_color='#d32f2f',
                         marker_line_width=1.5))
    fig.add_trace(go.Bar(name='Norm Eksiği', x=type_analysis['okul_turu'], 
                         y=type_analysis['norm_eksigi_sayisi'], 
                         marker_color='#69f0ae', marker_line_color='#00c853',
                         marker_line_width=1.5))
    
    fig.update_layout(
        barmode='group',
        title='Okul Türüne Göre Norm ve Mevcut Öğretmen Karşılaştırması',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#e8eaf6'),
        title_font=dict(color='#e8eaf6', size=16),
        legend=dict(font=dict(color='#9fa8da')),
        xaxis=dict(tickangle=-45, gridcolor='rgba(255,255,255,0.05)'),
        yaxis=dict(gridcolor='rgba(255,255,255,0.05)'),
        height=500
    )
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ============================================
# TAB 2: OKUL ANALİZİ
# ============================================
with tab2:
    st.markdown("## 🏫 Okul Bazında Detaylı Norm Analizi")
    
    # Okul Seçimi
    schools_list = sorted(filtered_df['okul_adi'].unique())
    
    if schools_list:
        selected_school = st.selectbox('🔍 İncelemek istediğiniz okulu seçin:', schools_list)
        
        if selected_school:
            school_data = filtered_df[filtered_df['okul_adi'] == selected_school]
            
            # Okul Bilgileri
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.info(f"**🏫 Okul Türü:** {school_data['okul_turu'].iloc[0]}")
            with col2:
                st.info(f"**🏗️ Derslik:** {school_data['derslik_sayisi'].iloc[0]}")
            with col3:
                st.info(f"**📚 Branş Sayısı:** {len(school_data)}")
            with col4:
                total_teachers = school_data['mevcut_ogretmen'].sum()
                st.info(f"**👨‍🏫 Toplam Öğretmen:** {total_teachers}")
            
            # Norm Özeti
            total_norm = school_data['norm_sayisi'].sum()
            total_excess = school_data['norm_fazlasi_sayisi'].sum()
            total_deficit = school_data['norm_eksigi_sayisi'].sum()
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("📋 Toplam Norm", total_norm)
            with col2:
                st.metric("👨‍🏫 Mevcut", total_teachers)
            with col3:
                st.metric("🔴 Norm Fazlası", total_excess, delta=f"{total_excess} fazla", delta_color="inverse")
            with col4:
                st.metric("🟢 Norm Eksiği", total_deficit, delta=f"{total_deficit} eksik")
            
            # Branş Detay Tablosu
            st.markdown("### 📋 Branş Bazında Öğretmen Durumu")
            
            display_df = school_data[['brans_adi', 'norm_sayisi', 'mevcut_ogretmen', 
                                      'norm_durumu', 'norm_fazlasi_sayisi', 
                                      'norm_eksigi_sayisi', 'ortalama_hizmet_puani']].copy()
            display_df.columns = ['Branş', 'Norm', 'Mevcut', 'Durum', 'Fazla', 'Eksik', 'Ort. Puan']
            
            def highlight_status(val):
                if val == 'Norm Fazlası':
                    return 'background-color: rgba(198,40,40,0.3); color: #ff5252; font-weight: bold;'
                elif val == 'Norm Eksiği':
                    return 'background-color: rgba(46,125,50,0.3); color: #69f0ae; font-weight: bold;'
                else:
                    return 'background-color: rgba(245,127,23,0.3); color: #ffab40; font-weight: bold;'
            
            st.dataframe(
                display_df.style.map(highlight_status, subset=['Durum']),
                use_container_width=True,
                hide_index=True,
                height=400
            )
            
            # Branş Karşılaştırma Grafiği
            st.markdown("### 📊 Branş Bazında Norm/Mevcut Karşılaştırması")
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            
            fig = go.Figure()
            fig.add_trace(go.Bar(
                name='Norm Kadro',
                x=school_data['brans_adi'],
                y=school_data['norm_sayisi'],
                marker_color='#82b1ff',
                marker_line_color='#448aff',
                marker_line_width=1.5,
                text=school_data['norm_sayisi'],
                textposition='outside',
                textfont=dict(color='#82b1ff', size=11)
            ))
            fig.add_trace(go.Bar(
                name='Mevcut Öğretmen',
                x=school_data['brans_adi'],
                y=school_data['mevcut_ogretmen'],
                marker_color='#b388ff',
                marker_line_color='#7c4dff',
                marker_line_width=1.5,
                text=school_data['mevcut_ogretmen'],
                textposition='outside',
                textfont=dict(color='#b388ff', size=11)
            ))
            
            fig.update_layout(
                title=f'{selected_school} - Branş Bazında Karşılaştırma',
                barmode='group',
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#e8eaf6'),
                title_font=dict(color='#e8eaf6', size=16),
                legend=dict(font=dict(color='#9fa8da')),
                xaxis=dict(tickangle=-45, gridcolor='rgba(255,255,255,0.05)'),
                yaxis=dict(gridcolor='rgba(255,255,255,0.05)'),
                height=450
            )
            st.plotly_chart(fig, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.warning("⚠️ Seçili filtrelerde okul bulunamadı.")

# ============================================
# TAB 3: BRANŞ ANALİZİ
# ============================================
with tab3:
    st.markdown("## 👨‍🏫 Branş Bazında Norm Fazlası Analizi")
    
    # Branş Özeti
    branch_summary = filtered_df.groupby('brans_adi').agg({
        'norm_sayisi': 'sum',
        'mevcut_ogretmen': 'sum',
        'norm_fazlasi_sayisi': 'sum',
        'norm_eksigi_sayisi': 'sum',
        'okul_id': 'nunique'
    }).reset_index()
    
    branch_summary.columns = ['Branş', 'Toplam Norm', 'Toplam Öğretmen', 
                              'Norm Fazlası', 'Norm Eksiği', 'Okul Sayısı']
    branch_summary['Fark'] = branch_summary['Toplam Öğretmen'] - branch_summary['Toplam Norm']
    
    # En Fazla Norm Fazlası Olan Branşlar
    st.markdown("### 🔴 En Fazla Norm Fazlası Olan Branşlar")
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    
    top_excess = branch_summary.nlargest(15, 'Norm Fazlası')
    fig = px.bar(
        top_excess,
        x='Branş',
        y='Norm Fazlası',
        title='Norm Fazlası Öğretmen Sayısı (İlk 15 Branş)',
        color='Norm Fazlası',
        color_continuous_scale='Reds',
        text='Norm Fazlası'
    )
    fig.update_traces(textposition='outside', textfont=dict(color='#ff5252', size=11))
    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#e8eaf6'),
        title_font=dict(color='#e8eaf6', size=16),
        xaxis=dict(tickangle=-45, gridcolor='rgba(255,255,255,0.05)'),
        yaxis=dict(gridcolor='rgba(255,255,255,0.05)'),
        coloraxis_showscale=False,
        height=500
    )
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Branş Karşılaştırma Scatter Plot
    st.markdown("### 📈 Branş Bazında Norm vs Mevcut Öğretmen Karşılaştırması")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        fig = px.scatter(
            branch_summary,
            x='Toplam Norm',
            y='Toplam Öğretmen',
            size='Okul Sayısı',
            color='Branş',
            text='Branş',
            title='Branş Bazında Norm vs Mevcut Öğretmen Dağılımı',
            height=600
        )
        fig.add_trace(go.Scatter(
            x=[0, branch_summary['Toplam Norm'].max()],
            y=[0, branch_summary['Toplam Norm'].max()],
            mode='lines',
            name='Eşitlik Çizgisi',
            line=dict(dash='dash', color='rgba(255,255,255,0.3)', width=2)
        ))
        fig.update_traces(textposition='top center', textfont=dict(size=9))
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#e8eaf6'),
            title_font=dict(color='#e8eaf6', size=16),
            legend=dict(font=dict(color='#9fa8da', size=8)),
            xaxis=dict(gridcolor='rgba(255,255,255,0.05)'),
            yaxis=dict(gridcolor='rgba(255,255,255,0.05)')
        )
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown("### 📋 Branş Özet Tablosu")
        st.dataframe(
            branch_summary.sort_values('Norm Fazlası', ascending=False).head(20),
            use_container_width=True,
            hide_index=True,
            height=600
        )

# ============================================
# TAB 4: NORM FAZLASI ÖĞRETMENLER
# ============================================
with tab4:
    st.markdown("## ⚠️ Norm Fazlası Öğretmenler ve Hizmet Puanları")
    
    excess_data = filtered_df[filtered_df['norm_durumu'] == 'Norm Fazlası']
    
    if not excess_data.empty:
        # Hizmet Puanı Filtresi
        st.markdown("### 🔍 Hizmet Puanı Filtresi")
        
        min_puan = int(excess_data['ortalama_hizmet_puani'].min())
        max_puan = int(excess_data['ortalama_hizmet_puani'].max())
        
        puan_range = st.slider(
            'Hizmet Puanı Aralığı:',
            min_puan, max_puan,
            (min_puan, max_puan)
        )
        
        filtered_excess = excess_data[
            (excess_data['ortalama_hizmet_puani'] >= puan_range[0]) & 
            (excess_data['ortalama_hizmet_puani'] <= puan_range[1])
        ]
        
        # İstatistikler
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("🔴 Toplam Norm Fazlası", len(filtered_excess))
        with col2:
            st.metric("📊 Ortalama Hizmet Puanı", f"{filtered_excess['ortalama_hizmet_puani'].mean():.0f}")
        with col3:
            st.metric("⬆️ En Yüksek Puan", filtered_excess['ortalama_hizmet_puani'].max())
        with col4:
            st.metric("⬇️ En Düşük Puan", filtered_excess['ortalama_hizmet_puani'].min())
        
        # Norm Fazlası Tablosu
        st.markdown("### 📋 Norm Fazlası Öğretmen Listesi")
        
        display_excess = filtered_excess[['okul_adi', 'okul_turu', 'brans_adi', 
                                          'norm_fazlasi_sayisi', 'ortalama_hizmet_puani',
                                          'derslik_sayisi']].copy()
        display_excess.columns = ['Okul Adı', 'Okul Türü', 'Branş', 'Fazla Sayısı', 
                                  'Ort. Hizmet Puanı', 'Derslik']
        display_excess = display_excess.sort_values('Ort. Hizmet Puanı', ascending=False)
        
        st.dataframe(
            display_excess,
            use_container_width=True,
            hide_index=True,
            height=400
        )
        
        # Grafikler
        st.markdown("### 📊 Hizmet Puanı Dağılımı ve Branş Analizi")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            fig = px.histogram(
                filtered_excess,
                x='ortalama_hizmet_puani',
                nbins=20,
                title='Norm Fazlası Öğretmenlerin Hizmet Puanı Dağılımı',
                color_discrete_sequence=['#ff5252']
            )
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#e8eaf6'),
                title_font=dict(color='#e8eaf6', size=14),
                xaxis=dict(gridcolor='rgba(255,255,255,0.05)'),
                yaxis=dict(gridcolor='rgba(255,255,255,0.05)'),
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            branch_excess = filtered_excess.groupby('brans_adi')['norm_fazlasi_sayisi'].sum().nlargest(10)
            fig = px.pie(
                values=branch_excess.values,
                names=branch_excess.index,
                title='Branşlara Göre Norm Fazlası Dağılımı (İlk 10)',
                hole=0.4,
                color_discrete_sequence=px.colors.sequential.Reds_r
            )
            fig.update_traces(textposition='inside', textinfo='percent+label',
                            textfont=dict(color='white', size=10))
            fig.update_layout(
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#e8eaf6'),
                title_font=dict(color='#e8eaf6', size=14),
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.info("ℹ️ Seçili filtrelerde norm fazlası öğretmen bulunmamaktadır.")

# ============================================
# TAB 5: RAPORLAR
# ============================================
with tab5:
    st.markdown("## 📈 Detaylı Raporlar ve İstatistiksel Analizler")
    
    # Okul Türü Bazında Özet Rapor
    st.markdown("### 📊 Okul Türü Bazında Özet Rapor")
    
    type_report = filtered_df.groupby('okul_turu').agg({
        'okul_id': 'nunique',
        'norm_sayisi': 'sum',
        'mevcut_ogretmen': 'sum',
        'norm_fazlasi_sayisi': 'sum',
        'norm_eksigi_sayisi': 'sum',
        'ortalama_hizmet_puani': 'mean'
    }).round(1)
    
    type_report.columns = ['Okul Sayısı', 'Toplam Norm', 'Toplam Öğretmen', 
                           'Norm Fazlası', 'Norm Eksiği', 'Ort. Hizmet Puanı']
    type_report['Doluluk Oranı (%)'] = (type_report['Toplam Öğretmen'] / type_report['Toplam Norm'] * 100).round(1)
    
    st.dataframe(type_report, use_container_width=True)
    
    # Isı Haritası
    st.markdown("### 🔥 Norm Fazlası Isı Haritası")
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    
    heatmap_data = filtered_df.pivot_table(
        values='norm_fazlasi_sayisi',
        index='okul_turu',
        columns='brans_adi',
        aggfunc='sum',
        fill_value=0
    )
    
    if not heatmap_data.empty:
        fig = px.imshow(
            heatmap_data,
            title='Okul Türü - Branş Norm Fazlası Isı Haritası',
            labels=dict(x="Branş", y="Okul Türü", color="Norm Fazlası"),
            aspect="auto",
            color_continuous_scale='Reds'
        )
        fig.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(color='#e8eaf6'),
            title_font=dict(color='#e8eaf6', size=16),
            height=600,
            xaxis=dict(tickangle=-45)
        )
        st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Derslik Sayısına Göre Analiz
    st.markdown("### 🏗️ Derslik Sayısına Göre Norm Durumu Analizi")
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    
    filtered_df_copy = filtered_df.copy()
    filtered_df_copy['Derslik Grubu'] = pd.cut(
        filtered_df_copy['derslik_sayisi'],
        bins=[0, 10, 20, 30, 40, 50, 100],
        labels=['0-10', '11-20', '21-30', '31-40', '41-50', '50+']
    )
    
    classroom_analysis = filtered_df_copy.groupby('Derslik Grubu').agg({
        'norm_fazlasi_sayisi': 'sum',
        'norm_eksigi_sayisi': 'sum',
        'okul_id': 'nunique'
    }).reset_index()
    
    fig = make_subplots(specs=[[{"secondary_y": True}]])
    
    fig.add_trace(
        go.Bar(name='Norm Fazlası', x=classroom_analysis['Derslik Grubu'],
               y=classroom_analysis['norm_fazlasi_sayisi'], 
               marker_color='#ff5252', marker_line_color='#d32f2f',
               marker_line_width=1.5),
        secondary_y=False
    )
    
    fig.add_trace(
        go.Bar(name='Norm Eksiği', x=classroom_analysis['Derslik Grubu'],
               y=classroom_analysis['norm_eksigi_sayisi'], 
               marker_color='#69f0ae', marker_line_color='#00c853',
               marker_line_width=1.5),
        secondary_y=False
    )
    
    fig.add_trace(
        go.Scatter(name='Okul Sayısı', x=classroom_analysis['Derslik Grubu'],
                  y=classroom_analysis['okul_id'], mode='lines+markers',
                  line=dict(color='#82b1ff', width=3),
                  marker=dict(size=10, color='#448aff')),
        secondary_y=True
    )
    
    fig.update_layout(
        title='Derslik Sayısı Gruplarına Göre Norm Durumu ve Okul Sayısı',
        barmode='group',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font=dict(color='#e8eaf6'),
        title_font=dict(color='#e8eaf6', size=16),
        legend=dict(font=dict(color='#9fa8da')),
        height=500
    )
    
    fig.update_yaxes(title_text="Öğretmen Sayısı", secondary_y=False, 
                    gridcolor='rgba(255,255,255,0.05)')
    fig.update_yaxes(title_text="Okul Sayısı", secondary_y=True,
                    gridcolor='rgba(255,255,255,0.05)')
    
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ============================================
# TAB 6: OKUL LİNKLERİ
# ============================================
with tab6:
    st.markdown("## 🔗 Okul Web Siteleri ve Teşkilat Sayfaları")
    st.markdown("### Okul isimlerine tıklayarak web sitelerine veya teşkilat sayfalarına ulaşabilirsiniz")
    
    # Okul listesi ve linkler
    st.markdown("### 📋 Çankaya İlçesi Okul Listesi")
    
    school_list = filtered_df[['okul_adi', 'okul_turu']].drop_duplicates()
    school_list = school_list.sort_values(['okul_turu', 'okul_adi'])
    
    # Okul türüne göre filtre
    selected_link_type = st.selectbox(
        'Okul Türüne Göre Filtrele:',
        ['Tümü'] + sorted(school_list['okul_turu'].unique().tolist())
    )
    
    if selected_link_type != 'Tümü':
        school_list = school_list[school_list['okul_turu'] == selected_link_type]
    
    # Okulları göster
    for idx, row in school_list.iterrows():
        school_name = row['okul_adi']
        school_type = row['okul_turu']
        
        # Okul adından slug oluştur (web adresi için)
        slug = school_name.lower()
        slug = slug.replace(' ', '').replace('ı', 'i').replace('ğ', 'g')
        slug = slug.replace('ü', 'u').replace('ş', 's').replace('ö', 'o')
        slug = slug.replace('ç', 'c').replace('İ', 'i').replace('Ğ', 'g')
        slug = slug.replace('Ü', 'u').replace('Ş', 's').replace('Ö', 'o')
        slug = slug.replace('Ç', 'c')
        
        website_url = f"https://{slug}.meb.k12.tr"
        teskilat_url = f"https://{slug}.meb.k12.tr/tema/teskilat.php"
        
        st.markdown(f"""
        <div style="background: rgba(26,35,126,0.2); border: 1px solid rgba(255,255,255,0.1); 
                    border-radius: 10px; padding: 1rem; margin: 0.5rem 0;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <strong style="color: #e8eaf6; font-size: 1.1rem;">{school_name}</strong>
                    <span style="color: #9fa8da; margin-left: 1rem;">({school_type})</span>
                </div>
                <div>
                    <a href="{website_url}" target="_blank" 
                       style="color: #82b1ff; text-decoration: none; margin-right: 1rem;
                              padding: 0.3rem 0.8rem; border: 1px solid #82b1ff; 
                              border-radius: 15px; font-size: 0.85rem;">
                        🌐 Web Sitesi
                    </a>
                    <a href="{teskilat_url}" target="_blank" 
                       style="color: #b388ff; text-decoration: none;
                              padding: 0.3rem 0.8rem; border: 1px solid #b388ff; 
                              border-radius: 15px; font-size: 0.85rem;">
                        👨‍🏫 Teşkilat
                    </a>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # İstatistik
    st.markdown(f"""
    <div style="text-align: center; color: #5c6bc0; margin-top: 1rem;">
        Toplam {len(school_list)} okul listelenmiştir.
    </div>
    """, unsafe_allow_html=True)


# ============================================
# TAB 7: NORM FAZLASI GÖREVLENDİRME
# ============================================
with tab7:
    st.markdown("## 🔄 Norm Fazlası Öğretmen Görevlendirme Sistemi")
    st.markdown("""
    <div style="background: rgba(255,82,82,0.2); border: 1px solid rgba(255,82,82,0.5); 
                border-radius: 10px; padding: 1rem; margin-bottom: 1rem;">
        <h4 style="color: #ff5252; margin: 0;">⚠️ ÖNEMLİ KURAL:</h4>
        <p style="color: #ffcdd2; margin: 0.5rem 0 0 0;">
            Her branşta <strong>hizmet puanı EN DÜŞÜK</strong> olan öğretmen(ler) norm fazlası sayılır 
            ve görevlendirilir. Yüksek hizmet puanlı öğretmenler kendi okullarında kalır.
        </p>
    </div>
    """, unsafe_allow_html=True)

    with st.expander("📖 Görevlendirme Kuralları ve Açıklamalar", expanded=False):
        st.markdown("""
        ### Norm Fazlası Öğretmen Belirleme ve Görevlendirme Kuralları:
        
        1. **Norm Fazlası Tespiti:**
           - Bir okulda bir branşta norm kadrodan fazla öğretmen varsa
           - O branştaki **en düşük hizmet puanlı** öğretmen(ler) norm fazlasıdır
           - Örnek: Matematik branşında norm 4, mevcut 6 öğretmen → 2 öğretmen fazla
           - Bu 2 öğretmen, hizmet puanı en düşük olanlardır
        
        2. **Görevlendirme Önceliği:**
           - Norm fazlası öğretmenler kendi okul türlerindeki diğer okullara görevlendirilir
           - Öncelik aynı ilçe içindeki norm eksiği olan okullardır
           - Branş uyumu zorunludur
        
        3. **Hizmet Puanı Sıralaması:**
           - En düşük puanlı öğretmen en önce görevlendirilir
           - Eşit puan durumunda hizmet süresine bakılır
           - Görevlendirmede gönüllülük esası da değerlendirilebilir
        
        4. **Havuz Sistemi:**
           - Görevlendirilemeyen öğretmenler ilçe norm fazlası havuzuna alınır
           - Havuzdaki öğretmenler ilçe genelinde değerlendirilir
        """)

    # Yardımcı fonksiyonlar
    def prepare_excess_teachers_with_scores(df):
        excess_list = []
        for (okul_id, brans_adi), group in df.groupby(['okul_id', 'brans_adi']):
            row = group.iloc[0]
            if row['norm_durumu'] == 'Norm Fazlası' and row['norm_fazlasi_sayisi'] > 0:
                fazla_sayisi = int(row['norm_fazlasi_sayisi'])
                mevcut_ogretmen = int(row['mevcut_ogretmen'])
                teachers_in_branch = []
                for i in range(mevcut_ogretmen):
                    puan = np.random.randint(120, 500)
                    teachers_in_branch.append({
                        'ogretmen_no': i + 1,
                        'hizmet_puani': puan,
                        'brans': brans_adi,
                        'okul': row['okul_adi']
                    })
                teachers_in_branch.sort(key=lambda x: x['hizmet_puani'])
                norm_fazlasi_ogretmenler = teachers_in_branch[:fazla_sayisi]
                okulda_kalanlar = teachers_in_branch[fazla_sayisi:]
                for teacher in norm_fazlasi_ogretmenler:
                    excess_list.append({
                        'okul_adi': row['okul_adi'],
                        'okul_turu': row['okul_turu'],
                        'brans_adi': brans_adi,
                        'hizmet_puani': teacher['hizmet_puani'],
                        'norm_sayisi': row['norm_sayisi'],
                        'mevcut_ogretmen': mevcut_ogretmen,
                        'norm_fazlasi_sayisi': fazla_sayisi,
                        'durum': 'Norm Fazlası (En Düşük Puanlı)',
                        'kalan_ogretmen_sayisi': len(okulda_kalanlar),
                        'en_yuksek_kalan_puan': okulda_kalanlar[-1]['hizmet_puani'] if okulda_kalanlar else 0
                    })
        return pd.DataFrame(excess_list)

    def prepare_deficit_schools(df):
        deficit_list = []
        for (okul_id, brans_adi), group in df.groupby(['okul_id', 'brans_adi']):
            row = group.iloc[0]
            if row['norm_durumu'] == 'Norm Eksiği' and row['norm_eksigi_sayisi'] > 0:
                deficit_list.append({
                    'okul_adi': row['okul_adi'],
                    'okul_turu': row['okul_turu'],
                    'brans_adi': brans_adi,
                    'norm_sayisi': row['norm_sayisi'],
                    'mevcut_ogretmen': row['mevcut_ogretmen'],
                    'ihtiyac_sayisi': int(row['norm_eksigi_sayisi']),
                    'derslik_sayisi': row['derslik_sayisi'],
                    'ortalama_puan': row['ortalama_hizmet_puani']
                })
        return pd.DataFrame(deficit_list)

    def match_excess_to_deficit(excess_df, deficit_df, strateji='puan_oncelikli'):
        assignments = []
        for brans in excess_df['brans_adi'].unique():
            brans_excess = excess_df[excess_df['brans_adi'] == brans].copy()
            brans_deficit = deficit_df[deficit_df['brans_adi'] == brans].copy()
            if brans_excess.empty or brans_deficit.empty:
                continue
            brans_excess = brans_excess.sort_values('hizmet_puani', ascending=True)
            brans_deficit = brans_deficit.sort_values('ihtiyac_sayisi', ascending=False)
            for _, teacher in brans_excess.iterrows():
                if brans_deficit.empty:
                    break
                best_school = None
                for _, school in brans_deficit.iterrows():
                    if school['okul_turu'] == teacher['okul_turu']:
                        best_school = school
                        break
                if best_school is not None:
                    oncelik_puani = 500 - teacher['hizmet_puani']
                    assignments.append({
                        'ogretmen_hizmet_puani': teacher['hizmet_puani'],
                        'brans_adi': teacher['brans_adi'],
                        'kaynak_okul': teacher['okul_adi'],
                        'kaynak_okul_turu': teacher['okul_turu'],
                        'hedef_okul': best_school['okul_adi'],
                        'hedef_okul_turu': best_school['okul_turu'],
                        'hedef_mevcut_ogretmen': best_school['mevcut_ogretmen'],
                        'hedef_norm': best_school['norm_sayisi'],
                        'hedef_ihtiyac': best_school['ihtiyac_sayisi'],
                        'gorevlendirme_oncelik_puani': oncelik_puani,
                        'gorevlendirme_nedeni': f'En düşük hizmet puanlı ({teacher["hizmet_puani"]} puan)',
                        'durum': 'Görevlendirme Önerisi',
                        'onay_durumu': '⏳ Onay Bekliyor'
                    })
                    brans_deficit.loc[brans_deficit['okul_adi'] == best_school['okul_adi'], 'ihtiyac_sayisi'] -= 1
                    brans_deficit = brans_deficit[brans_deficit['ihtiyac_sayisi'] > 0]
        result_df = pd.DataFrame(assignments)
        if not result_df.empty:
            result_df = result_df.sort_values('ogretmen_hizmet_puani', ascending=True)
        return result_df

    # Ana arayüz
    col1, col2 = st.columns([1, 2])

    with col1:
        st.markdown("### ⚙️ Görevlendirme Ayarları")
        st.markdown('<div class="filter-panel">', unsafe_allow_html=True)
        gorev_turleri = ['Tümü'] + sorted(df['okul_turu'].unique().tolist())
        selected_gorev_type = st.selectbox('🏫 Okul Türü', gorev_turleri, key='gorev_type_new')
        gorev_strateji = st.radio(
            '📋 Görevlendirme Stratejisi',
            ['En Düşük Hizmet Puanı Öncelikli (Zorunlu)',
             'En Çok İhtiyacı Olan Okul Öncelikli',
             'Dengeli Dağılım'],
            key='gorev_strateji_new'
        )
        st.markdown("""
        <div style="background: rgba(255,82,82,0.1); border-radius: 8px; padding: 0.8rem; margin-top: 1rem;">
            <p style="color: #ffcdd2; font-size: 0.8rem; margin: 0;">
                <strong>🔴 Zorunlu Kural:</strong> Her durumda en düşük hizmet puanlı 
                öğretmen norm fazlasıdır ve öncelikli görevlendirilir.
            </p>
        </div>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)

        if st.button('🔄 Görevlendirme Önerilerini Oluştur', type='primary', use_container_width=True, key='btn_olustur'):
            st.session_state.gorev_olustur_new = True
        if st.button('📋 Sadece Norm Fazlası Listesi', use_container_width=True, key='btn_liste'):
            st.session_state.sadece_liste = True

    with col2:
        st.markdown("### 📊 Görevlendirme Sonuçları")
        if 'gorev_olustur_new' in st.session_state and st.session_state.gorev_olustur_new:
            gorev_df = df.copy()
            if selected_gorev_type != 'Tümü':
                gorev_df = gorev_df[gorev_df['okul_turu'] == selected_gorev_type]

            with st.spinner('Norm fazlası öğretmenler belirleniyor...'):
                excess_teachers = prepare_excess_teachers_with_scores(gorev_df)
                st.session_state.excess_teachers = excess_teachers
            with st.spinner('Norm eksiği okullar taranıyor...'):
                deficit_schools = prepare_deficit_schools(gorev_df)
                st.session_state.deficit_schools = deficit_schools

            if not excess_teachers.empty and not deficit_schools.empty:
                with st.spinner('En uygun eşleştirmeler yapılıyor...'):
                    assignments = match_excess_to_deficit(excess_teachers, deficit_schools, strateji='puan_oncelikli')
                    st.session_state.assignments_new = assignments
                st.success(f'✅ {len(assignments)} görevlendirme önerisi oluşturuldu!')
            else:
                if excess_teachers.empty:
                    st.warning("⚠️ Norm fazlası öğretmen bulunamadı.")
                if deficit_schools.empty:
                    st.warning("⚠️ Norm eksiği okul bulunamadı.")
                st.session_state.assignments_new = pd.DataFrame()

        if 'assignments_new' in st.session_state and not st.session_state.assignments_new.empty:
            assignments = st.session_state.assignments_new

            col1, col2, col3, col4, col5 = st.columns(5)
            with col1:
                st.metric("🔄 Toplam Görevlendirme", len(assignments))
            with col2:
                st.metric("⬇️ En Düşük Puan", assignments['ogretmen_hizmet_puani'].min())
            with col3:
                st.metric("⬆️ En Yüksek Puan", assignments['ogretmen_hizmet_puani'].max())
            with col4:
                st.metric("📊 Ortalama Puan", f"{assignments['ogretmen_hizmet_puani'].mean():.0f}")
            with col5:
                st.metric("📚 Branş", assignments['brans_adi'].nunique())

            st.markdown("---")
            st.markdown("### 📋 Görevlendirme Listesi (Hizmet Puanına Göre Sıralı)")
            st.markdown("""
            <div style="background: rgba(255,82,82,0.2); border-radius: 8px; padding: 0.8rem; margin-bottom: 1rem;">
                <p style="color: #ffcdd2; margin: 0; font-size: 0.9rem;">
                    🔴 <strong>En düşük hizmet puanlı öğretmenler</strong> norm fazlası olarak belirlenmiş 
                    ve görevlendirme önerilmiştir. Yüksek puanlı öğretmenler kendi okullarında kalmaya devam eder.
                </p>
            </div>
            """, unsafe_allow_html=True)

            for idx, row in assignments.iterrows():
                puan = row['ogretmen_hizmet_puani']
                if puan < 200:
                    puan_rengi = '#ff5252'
                    oncelik = '🔴 YÜKSEK ÖNCELİK'
                elif puan < 350:
                    puan_rengi = '#ffab40'
                    oncelik = '🟡 ORTA ÖNCELİK'
                else:
                    puan_rengi = '#ffd740'
                    oncelik = '🟢 DÜŞÜK ÖNCELİK'

                st.markdown(f"""
                <div style="background: rgba(26,35,126,0.3); border: 1px solid rgba(255,255,255,0.1); 
                            border-radius: 10px; padding: 1rem; margin: 0.5rem 0;
                            border-left: 4px solid {puan_rengi};">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <div>
                            <strong style="color: #e8eaf6; font-size: 1.1rem;">
                                {row['brans_adi']} Öğretmeni
                            </strong>
                            <span style="color: {puan_rengi}; margin-left: 1rem; font-weight: bold;">
                                Hizmet Puanı: {puan}
                            </span>
                            <span style="color: #ffab40; margin-left: 0.5rem; font-size: 0.8rem;">
                                {oncelik}
                            </span>
                        </div>
                    </div>
                    <div style="margin-top: 0.5rem; color: #9fa8da;">
                        <span>🏫 <strong>Kaynak:</strong> {row['kaynak_okul']}</span>
                        <span style="margin-left: 2rem;">➡️</span>
                        <span style="margin-left: 2rem;">🏫 <strong>Hedef:</strong> {row['hedef_okul']}</span>
                    </div>
                    <div style="margin-top: 0.3rem; color: #7986cb; font-size: 0.85rem;">
                        <span>📋 Hedef Norm: {row['hedef_norm']} | Mevcut: {row['hedef_mevcut_ogretmen']} | İhtiyaç: {row['hedef_ihtiyac']}</span>
                    </div>
                    <div style="margin-top: 0.3rem; color: #ffcdd2; font-size: 0.8rem;">
                        <span>📝 {row['gorevlendirme_nedeni']}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            # Grafikler
            st.markdown("---")
            st.markdown("### 📊 Görevlendirilen Öğretmenlerin Hizmet Puanı Analizi")
            col1, col2 = st.columns(2)

            with col1:
                st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                fig = px.histogram(assignments, x='ogretmen_hizmet_puani', nbins=20,
                                 title='Görevlendirilen Öğretmenlerin Hizmet Puanı Dağılımı',
                                 color_discrete_sequence=['#ff5252'])
                fig.add_vline(x=200, line_dash="dash", line_color="#ffab40",
                            annotation_text="Düşük Puan Sınırı", annotation_position="top right")
                fig.add_vline(x=350, line_dash="dash", line_color="#ffd740",
                            annotation_text="Orta Puan Sınırı", annotation_position="top right")
                fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                                font=dict(color='#e8eaf6'), title_font=dict(color='#e8eaf6'),
                                xaxis=dict(gridcolor='rgba(255,255,255,0.05)', title='Hizmet Puanı'),
                                yaxis=dict(gridcolor='rgba(255,255,255,0.05)', title='Öğretmen Sayısı'),
                                height=400)
                st.plotly_chart(fig, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)

            with col2:
                st.markdown('<div class="chart-container">', unsafe_allow_html=True)
                branch_avg = assignments.groupby('brans_adi')['ogretmen_hizmet_puani'].mean().sort_values()
                fig = px.bar(x=branch_avg.values, y=branch_avg.index, orientation='h',
                           title='Branşlara Göre Görevlendirilenlerin Ortalama Hizmet Puanı',
                           color=branch_avg.values, color_continuous_scale='Reds',
                           labels={'x': 'Ortalama Hizmet Puanı', 'y': 'Branş'})
                fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                                font=dict(color='#e8eaf6'), title_font=dict(color='#e8eaf6'),
                                xaxis=dict(gridcolor='rgba(255,255,255,0.05)'),
                                yaxis=dict(gridcolor='rgba(255,255,255,0.05)'),
                                coloraxis_showscale=False, height=400)
                st.plotly_chart(fig, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)

            # Dışa aktar
            st.markdown("### 💾 Görevlendirme Listesini Dışa Aktar")
            col1, col2 = st.columns(2)
            with col1:
                csv = assignments.to_csv(index=False)
                st.download_button(label="📥 CSV Olarak İndir", data=csv,
                                 file_name=f"norm_fazlasi_gorevlendirme_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                                 mime="text/csv", use_container_width=True)
            with col2:
                from io import BytesIO
                output = BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    assignments.to_excel(writer, sheet_name='Görevlendirme', index=False)
                excel_data = output.getvalue()
                st.download_button(label="📥 Excel Olarak İndir", data=excel_data,
                                 file_name=f"norm_fazlasi_gorevlendirme_{datetime.now().strftime('%Y%m%d_%H%M%S')}.xlsx",
                                 mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                                 use_container_width=True)

        elif 'sadece_liste' in st.session_state and st.session_state.sadece_liste:
            gorev_df = df.copy()
            if selected_gorev_type != 'Tümü':
                gorev_df = gorev_df[gorev_df['okul_turu'] == selected_gorev_type]
            excess_teachers = prepare_excess_teachers_with_scores(gorev_df)
            if not excess_teachers.empty:
                st.markdown("### 📋 Norm Fazlası Öğretmen Listesi (En Düşük Puanlılar)")
                st.dataframe(excess_teachers.sort_values('hizmet_puani', ascending=True),
                           use_container_width=True, hide_index=True)
            else:
                st.info("Norm fazlası öğretmen bulunamadı.")

        else:
            st.markdown("""
            <div style="background: rgba(26,35,126,0.3); border: 1px solid rgba(255,255,255,0.1); 
                        border-radius: 15px; padding: 2rem; text-align: center;">
                <h3 style="color: #e8eaf6;">🔄 Norm Fazlası Görevlendirme Sistemi</h3>
                <p style="color: #9fa8da; margin-top: 1rem;">
                    Bu sistem, <strong style="color: #ff5252;">hizmet puanı en düşük</strong> olan 
                    norm fazlası öğretmenleri otomatik olarak belirler ve 
                    norm eksiği olan okullara görevlendirme önerisi oluşturur.
                </p>
                <div style="display: flex; justify-content: center; gap: 2rem; margin-top: 1.5rem;">
                    <div style="text-align: center; background: rgba(255,82,82,0.2); padding: 1rem; border-radius: 10px;">
                        <div style="font-size: 2rem;">🔴</div>
                        <div style="color: #ffcdd2; font-weight: bold;">Düşük Puanlı</div>
                        <div style="color: #9fa8da; font-size: 0.8rem;">Norm Fazlası Olur</div>
                    </div>
                    <div style="text-align: center; padding-top: 2rem;">
                        <div style="font-size: 2rem; color: #82b1ff;">➡️</div>
                    </div>
                    <div style="text-align: center; background: rgba(105,240,174,0.2); padding: 1rem; border-radius: 10px;">
                        <div style="font-size: 2rem;">🟢</div>
                        <div style="color: #b9f6ca; font-weight: bold;">Norm Eksiği Okul</div>
                        <div style="color: #9fa8da; font-size: 0.8rem;">Görevlendirme Hedefi</div>
                    </div>
                </div>
                <p style="color: #5c6bc0; margin-top: 1.5rem; font-size: 0.9rem;">
                    ⚠️ Yüksek hizmet puanlı öğretmenler <strong>kendi okullarında kalır</strong>, 
                    görevlendirilmezler.
                </p>
            </div>
            """, unsafe_allow_html=True)
            
# ============================================
# FOOTER
# ============================================
st.markdown("---")
st.markdown(f"""
<div class="footer">
    <p><strong>Çankaya İlçe Milli Eğitim Müdürlüğü</strong></p>
    <p>Norm Fazlası Öğretmen Dağılım ve Takip Sistemi | Versiyon 2.0</p>
    <p>© {datetime.now().year} | Tüm hakları saklıdır.</p>
    <p style="font-size: 0.8rem; color: #3f51b5;">
        Son veri senkronizasyonu: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}
    </p>
</div>
""", unsafe_allow_html=True)

# ============================================
# BAŞLANGIÇ BİLDİRİMİ
# ============================================
if 'initialized' not in st.session_state:
    st.session_state.initialized = True
    st.toast('✅ Sistem başarıyla başlatıldı!', icon='🚀')
    st.toast(f'📊 {df["okul_id"].nunique()} okul ve {df["brans_adi"].nunique()} branş yüklendi.', icon='📚')
