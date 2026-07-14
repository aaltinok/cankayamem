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


        backdrop-filter: blur(10px);
        ;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 600;
        box-shadow: 0 2px 8px rgba(245, 127, 23, 0.4);
    }
    
    /* Filtre Paneli */
    .filter-panel {
        background: rgba(26, 35, 126, 0.2);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 15px;
        padding: 1.5rem;
        backdrop-filter: blur(10px);
    }
    .filter-title {
        color: #e8eaf6;
        font-size: 1.2rem;
        font-weight: 700;
        margin-bottom: 1rem;
        border-bottom: 2px solid rgba(102, 126, 234, 0.5);
        padding-bottom: 0.5rem;
    }
    
    /* Tablo Stilleri */
    .dataframe-container {
        background: rgba(26, 35, 126, 0.2);
        border-radius: 15px;
        padding: 1rem;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    /* Grafik Konteyner */
    .chart-container {
        background: rgba(26, 35, 126, 0.15);
        border-radius: 15px;
        padding: 1rem;
        border: 1px solid rgba(255, 255, 255, 0.08);
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
    
    /* Selectbox ve Input */
    .stSelectbox, .stTextInput, .stSlider {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 10px;
    }
    
    /* Tab Stilleri */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background: rgba(26, 35, 126, 0.2);
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
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    }
    
    /* Okul Link Stilleri */
    .school-link {
# ============================================
# KARANLIK BİLİMSEL TEMA (DÜZELTİLMİŞ)
# ============================================
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #0a0e27 0%, #1a1f3a 50%, #0d1128 100%);
    }
    .main-header {
        background: linear-gradient(135deg, #1a237e 0%, #283593 50%, #1a237e 100%);
        color: #e8eaf6; text-align: center; padding: 2rem; border-radius: 15px;
        margin-bottom: 2rem; box-shadow: 0 8px 32px rgba(26, 35, 126, 0.3);
        border: 1px solid rgba(255, 255, 255, 0.1); position: relative; overflow: hidden;
    }
    .main-header::before {
        content: ''; position: absolute; top: -50%; left: -50%;
        width: 200%; height: 200%;
        background: radial-gradient(circle, rgba(255, 255, 255, 0.05) 0%, transparent 70%);
        animation: rotate 20s linear infinite;
    }
    @keyframes rotate {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
    }
    .main-header h1 { position: relative; z-index: 1; font-size: 2.2rem; font-weight: 700; text-shadow: 0 2px 10px rgba(0, 0, 0, 0.5); }
    
    .stat-card {
        background: linear-gradient(135deg, rgba(26, 35, 126, 0.4) 0%, rgba(40, 53, 147, 0.3) 100%);
        border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 15px; padding: 1.5rem;
        text-align: center; backdrop-filter: blur(10px); box-shadow: 0 4px 16px rgba(0, 0, 0, 0.3);
        transition: all 0.3s ease; position: relative; overflow: hidden;
    }
    .stat-card:hover { transform: translateY(-5px); box-shadow: 0 8px 25px rgba(26, 35, 126, 0.5); border-color: rgba(255, 255, 255, 0.3); }
    .stat-card::after { content: ''; position: absolute; bottom: 0; left: 0; right: 0; height: 3px; background: linear-gradient(90deg, #667eea, #764ba2); }
    .stat-value { font-size: 2.5rem; font-weight: 800; color: #e8eaf6; text-shadow: 0 0 20px rgba(102, 126, 234, 0.5); }
    .stat-label { font-size: 0.9rem; color: #9fa8da; text-transform: uppercase; letter-spacing: 1px; }
    
    .badge-excess { background: linear-gradient(135deg, #c62828, #d32f2f); color: white; padding: 0.3rem 0.8rem; border-radius: 20px; font-size: 0.8rem; font-weight: 600; box-shadow: 0 2px 8px rgba(198, 40, 40, 0.4); }
    .badge-deficit { background: linear-gradient(135deg, #2e7d32, #388e3c); color: white; padding: 0.3rem 0.8rem; border-radius: 20px; font-size: 0.8rem; font-weight: 600; box-shadow: 0 2px 8px rgba(46, 125, 50, 0.4); }
    .badge-normal { background: linear-gradient(135deg, #f57f17, #f9a825); color: white; padding: 0.3rem 0.8rem; border-radius: 20px; font-size: 0.8rem; font-weight: 600; box-shadow: 0 2px 8px rgba(245, 127, 23, 0.4); }
    
    .filter-panel { background: rgba(26, 35, 126, 0.2); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 15px; padding: 1.5rem; backdrop-filter: blur(10px); }
    .filter-title { color: #e8eaf6; font-size: 1.2rem; font-weight: 700; margin-bottom: 1rem; border-bottom: 2px solid rgba(102, 126, 234, 0.5); padding-bottom: 0.5rem; }
    
    .dataframe-container { background: rgba(26, 35, 126, 0.2); border-radius: 15px; padding: 1rem; border: 1px solid rgba(255, 255, 255, 0.1); }
    .chart-container { background: rgba(26, 35, 126, 0.15); border-radius: 15px; padding: 1rem; border: 1px solid rgba(255, 255, 255, 0.08); margin: 1rem 0; }
    
    .sync-badge { background: linear-gradient(135deg, #00c853, #00e676); color: white; padding: 0.3rem 0.8rem; border-radius: 20px; font-size: 0.75rem; animation: pulse 2s infinite; }
    @keyframes pulse { 0%, 100% { opacity: 1; } 50% { opacity: 0.6; } }
    
    .stProgress > div > div > div { background: linear-gradient(90deg, #667eea, #764ba2); }
    .stSelectbox, .stTextInput, .stSlider { background: rgba(255, 255, 255, 0.05); border-radius: 10px; }
    
    .stTabs [data-baseweb="tab-list"] { gap: 10px; background: rgba(26, 35, 126, 0.2); border-radius: 15px; padding: 0.5rem; }
    .stTabs [data-baseweb="tab"] { background: transparent; border-radius: 10px; color: #9fa8da; padding: 0.5rem 1.5rem; transition: all 0.3s; }
    .stTabs [aria-selected="true"] { background: linear-gradient(135deg, #667eea, #764ba2); color: white; box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4); }
    
    .school-link { color: #82b1ff; text-decoration: none; transition: all 0.3s; }
    .school-link:hover { color: #b388ff; text-shadow: 0 0 10px rgba(179, 136, 255, 0.5); }
    
    .footer { text-align: center; color: #5c6bc0; padding: 1rem; border-top: 1px solid rgba(255, 255, 255, 0.05); margin-top: 2rem; }
    
    [data-testid="stSidebar"] { background: linear-gradient(180deg, #0a0e27 0%, #1a1f3a 100%); border-right: 1px solid rgba(255, 255, 255, 0.1); }
    [data-testid="stSidebar"] * { color: #e8eaf6 !important; }
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 { color: #ffffff !important; }
    [data-testid="stSidebar"] .stSelectbox select, [data-testid="stSidebar"] input { background: rgba(255, 255, 255, 0.08); color: #e8eaf6 !important; border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 8px; }
    [data-testid="stSidebar"] .stButton button { background: linear-gradient(135deg, #667eea, #764ba2) !important; color: white !important; border: none !important; border-radius: 10px !important; }
    [data-testid="stSidebar"] .stMetric .stMetricValue { color: #ffffff !important; font-weight: 700; }
    [data-testid="stSidebar"] .stMetric .stMetricLabel { color: #9fa8da !important; }
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
    
    # Demo veri (Supabase yoksa)
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
    <h2>Norm Fazlası Öğretmen Dağılım ve Takip Sistemi</h2>
    <p>Son Güncelleme: {datetime.now().strftime('%d.%m.%Y %H:%M')} | 
    Toplam Okul: {df['okul_id'].nunique()} | 
    Toplam Branş: {df['brans_adi'].nunique()}</p>
</div>
""", unsafe_allow_html=True)

# ============================================
# ANA SEKMELER (7 SEKME)
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
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        type_dist = filtered_df.groupby('okul_turu')['okul_id'].nunique().reset_index()
        type_dist.columns = ['Okul Türü', 'Okul Sayısı']
        fig = px.pie(type_dist, values='Okul Sayısı', names='Okul Türü',
                     title='Okul Türlerine Göre Dağılım',
                     color_discrete_sequence=px.colors.sequential.Plasma_r, hole=0.4)
        fig.update_traces(textposition='inside', textinfo='percent+label', textfont=dict(color='white', size=11))
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                         font=dict(color='#e8eaf6'), title_font=dict(color='#e8eaf6', size=16),
                         legend=dict(font=dict(color='#9fa8da')), height=450)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        norm_dist = filtered_df['norm_durumu'].value_counts().reset_index()
        norm_dist.columns = ['Norm Durumu', 'Sayı']
        fig = px.bar(norm_dist, x='Norm Durumu', y='Sayı', title='Norm Durumu Dağılımı',
                     color='Norm Durumu', color_discrete_map={'Norm Fazlası': '#ff5252', 'Normal': '#ffab40', 'Norm Eksiği': '#69f0ae'},
                     text='Sayı')
        fig.update_traces(textposition='outside', textfont=dict(color='white', size=14))
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                         font=dict(color='#e8eaf6'), title_font=dict(color='#e8eaf6', size=16),
                         showlegend=False, height=450)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("### Okul Türüne Göre Norm Kadro Karşılaştırması")
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    type_analysis = filtered_df.groupby('okul_turu').agg({
        'norm_sayisi': 'sum', 'mevcut_ogretmen': 'sum',
        'norm_fazlasi_sayisi': 'sum', 'norm_eksigi_sayisi': 'sum'
    }).reset_index()
    fig = go.Figure()
    fig.add_trace(go.Bar(name='Norm Kadro', x=type_analysis['okul_turu'], y=type_analysis['norm_sayisi'],
                         marker_color='#82b1ff', marker_line_color='#448aff', marker_line_width=1.5))
    fig.add_trace(go.Bar(name='Mevcut Öğretmen', x=type_analysis['okul_turu'], y=type_analysis['mevcut_ogretmen'],
                         marker_color='#b388ff', marker_line_color='#7c4dff', marker_line_width=1.5))
    fig.add_trace(go.Bar(name='Norm Fazlası', x=type_analysis['okul_turu'], y=type_analysis['norm_fazlasi_sayisi'],
                         marker_color='#ff5252', marker_line_color='#d32f2f', marker_line_width=1.5))
    fig.add_trace(go.Bar(name='Norm Eksiği', x=type_analysis['okul_turu'], y=type_analysis['norm_eksigi_sayisi'],
                         marker_color='#69f0ae', marker_line_color='#00c853', marker_line_width=1.5))
    fig.update_layout(barmode='group', title='Okul Türüne Göre Norm ve Mevcut Öğretmen Karşılaştırması',
                      paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                      font=dict(color='#e8eaf6'), title_font=dict(color='#e8eaf6', size=16),
                      legend=dict(font=dict(color='#9fa8da')), xaxis=dict(tickangle=-45, gridcolor='rgba(255,255,255,0.05)'),
                      yaxis=dict(gridcolor='rgba(255,255,255,0.05)'), height=500)
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ============================================
# TAB 2: OKUL ANALİZİ
# ============================================
with tab2:
    st.markdown("## 🏫 Okul Bazında Detaylı Norm Analizi")
    schools_list = sorted(filtered_df['okul_adi'].unique())
    if schools_list:
        selected_school = st.selectbox('🔍 İncelemek istediğiniz okulu seçin:', schools_list)
        if selected_school:
            school_data = filtered_df[filtered_df['okul_adi'] == selected_school]
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
            st.dataframe(display_df.style.map(highlight_status, subset=['Durum']), use_container_width=True, hide_index=True, height=400)
            
            st.markdown("### 📊 Branş Bazında Norm/Mevcut Karşılaştırması")
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            fig = go.Figure()
            fig.add_trace(go.Bar(name='Norm Kadro', x=school_data['brans_adi'], y=school_data['norm_sayisi'],
                                 marker_color='#82b1ff', marker_line_color='#448aff', marker_line_width=1.5,
                                 text=school_data['norm_sayisi'], textposition='outside', textfont=dict(color='#82b1ff', size=11)))
            fig.add_trace(go.Bar(name='Mevcut Öğretmen', x=school_data['brans_adi'], y=school_data['mevcut_ogretmen'],
                                 marker_color='#b388ff', marker_line_color='#7c4dff', marker_line_width=1.5,
                                 text=school_data['mevcut_ogretmen'], textposition='outside', textfont=dict(color='#b388ff', size=11)))
            fig.update_layout(title=f'{selected_school} - Branş Bazında Karşılaştırma', barmode='group',
                              paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                 margin-bottom: 2rem; box-shadow: 0 8px 32px rgba(26,35,126,0.3);
        border: 1px solid rgba(255,255,255,0.1); position: relative; overflow: hidden;
    }
    .main-header::before {
        content: ''; position: absolute; top: -50%; left: -50%;
        width: 200%; height: 200%;
        background: radial-gradient(circle, rgba(255,255,255,0.05) 0%, transparent 70%);
        animation: rotate 20s linear infinite;
    }
    @keyframes rotate { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
    .main-header h1 { position: relative; z-index: 1; font-size: 2.2rem; font-weight: 700; text-shadow: 0 2px 10px rgba(0,0,0,0.5); }
    .stat-card {
        background: linear-gradient(135deg, rgba(26,35,126,0.4) 0%, rgba(40,53,147,0.3) 100%);
        border: 1px solid rgba(255,255,255,0.1); border-radius: 15px; padding: 1.5rem;
        text-align: center; backdrop-filter: blur(10px); box-shadow: 0 4px 16px rgba(0,0,0,0.3);
        transition: all 0.3s ease; position: relative; overflow: hidden;
    }
    .stat-card:hover { transform: translateY(-5px); box-shadow: 0 8px 25px rgba(26,35,126,0.5); border-color: rgba(255,255,255,0.3); }
    .stat-card::after {
        content: ''; position: absolute; bottom: 0; left: 0; right: 0; height: 3px;
        background: linear-gradient(90deg, #667eea, #764ba2);
    }
    .stat-value { font-size: 2.5rem; font-weight: 800; color: #e8eaf6; text-shadow: 0 0 20px rgba(102,126,234,0.5); }
    .stat-label { font-size: 0.9rem; color: #9fa8da; text-transform: uppercase; letter-spacing: 1px; }
    .filter-panel { background: rgba(26,35,126,0.2); border: 1px solid rgba(255,255,255,0.1); border-radius: 15px; padding: 1.5rem; backdrop-filter: blur(10px); }
    .filter-title { color: #e8eaf6; font-size: 1.2rem; font-weight: 700; margin-bottom: 1rem; border-bottom: 2px solid rgba(102,126,234,0.5); padding-bottom: 0.5rem; }
    .chart-container { background: rgba(26,35,126,0.15); border-radius: 15px; padding: 1rem; border: 1px solid rgba(255,255,255,0.08); margin: 1rem 0; }
    .footer { text-align: center; color: #5c6bc0; padding: 1rem; border-top: 1px solid rgba(255,255,255,0.05); margin-top: 2rem; }
    
    /* Sidebar Karanlık Tema */
    [data-testid="stSidebar"] { background: linear-gradient(180deg, #0a0e27 0%, #1a1f3a 100%); border-right: 1px solid rgba(255,255,255,0.1); }
    [data-testid="stSidebar"] * { color: #e8eaf6 !important; }
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 { color: #ffffff !important; }
    [data-testid="stSidebar"] .stSelectbox select, [data-testid="stSidebar"] input {
        background: rgba(255,255,255,0.08); color: #e8eaf6 !important;
        border: 1px solid rgba(255,255,255,0.1); border-radius: 8px;
    }
    [data-testid="stSidebar"] .stButton button {
        background: linear-gradient(135deg, #667eea, #764ba2) !important;
        color: white !important; border: none !important; border-radius: 10px !important;
    }
    [data-testid="stSidebar"] .stMetric .stMetricValue { color: #ffffff !important; font-weight: 700; }
    [data-testid="stSidebar"] .stMetric .stMetricLabel { color: #9fa8da !important; }
    
    .stTabs [data-baseweb="tab-list"] { gap: 10px; background: rgba(26,35,126,0.2); border-radius: 15px; padding: 0.5rem; }
    .stTabs [data-baseweb="tab"] { background: transparent; border-radius: 10px; color: #9fa8da; padding: 0.5rem 1.5rem; transition: all 0.3s; }
    .stTabs [aria-selected="true"] { background: linear-gradient(135deg, #667eea, #764ba2); color: white; box-shadow: 0 4px 15px rgba(102,126,234,0.4); }
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
# VERİ YÜKLEME
# ============================================
@st.cache_data(ttl=300)
def load_norm_data():
    if supabase:
        try:
            response = supabase.table('norm_durumu_gorunumu').select('*').execute()
            return pd.DataFrame(response.data)
        except:
            pass
    return pd.DataFrame()

df = load_norm_data()

# Eğer veri yoksa uyarı göster
if df.empty:
    st.error("⚠️ Veri bulunamadı! Lütfen Supabase bağlantısını kontrol edin veya veri ekleyin.")
    st.stop()

# ============================================
# SIDEBAR - FİLTRELER
# ============================================
with st.sidebar:
    st.markdown("""
    <div style="text-align: center; margin-bottom: 1rem;">
        <h2 style="color: #e8eaf6; font-size: 1.3rem;">🔍 FİLTRELEME PANELİ</h2>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="filter-panel">', unsafe_allow_html=True)
    st.markdown('<p class="filter-title">🏫 Okul Türü</p>', unsafe_allow_html=True)
    okul_turleri = ['Tümü'] + sorted(df['okul_turu'].unique().tolist())
    selected_type = st.selectbox('', okul_turleri, label_visibility='collapsed')
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="filter-panel">', unsafe_allow_html=True)
    st.markdown('<p class="filter-title">📚 Branş</p>', unsafe_allow_html=True)
    if selected_type != 'Tümü':
        filtered_branches = df[df['okul_turu'] == selected_type]['brans_adi'].unique()
    else:
        filtered_branches = df['brans_adi'].unique()
    branslar = ['Tümü'] + sorted(filtered_branches.tolist())
    selected_branch = st.selectbox('', branslar, label_visibility='collapsed')
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="filter-panel">', unsafe_allow_html=True)
    st.markdown('<p class="filter-title">⚖️ Norm Durumu</p>', unsafe_allow_html=True)
    norm_durumlari = ['Tümü', 'Norm Fazlası', 'Norm Eksiği', 'Normal']
    selected_norm = st.selectbox('', norm_durumlari, label_visibility='collapsed')
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="filter-panel">', unsafe_allow_html=True)
    st.markdown('<p class="filter-title">🏗️ Derslik Sayısı</p>', unsafe_allow_html=True)
    min_derslik = int(df['derslik_sayisi'].min())
    max_derslik = int(df['derslik_sayisi'].max())
    derslik_range = st.slider('', min_derslik, max_derslik, (min_derslik, max_derslik), label_visibility='collapsed')
    st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="filter-panel">', unsafe_allow_html=True)
    st.markdown('<p class="filter-title">🔎 Okul Ara</p>', unsafe_allow_html=True)
    school_search = st.text_input('', placeholder='Okul adı yazın...', label_visibility='collapsed')
    st.markdown('</div>', unsafe_allow_html=True)
    
    # Filtrele
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
    
    st.markdown("---")
    st.markdown("### 📊 Hızlı İstatistikler")
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
# ANA SEKMELER (7 SEKME)
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
    
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1:
        st.markdown(f"""
        <div class="stat-card"><div class="stat-value">{filtered_df['okul_id'].nunique()}</div>
        <div class="stat-label">🏫 Toplam Okul</div></div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown(f"""
        <div class="stat-card"><div class="stat-value">{filtered_df['mevcut_ogretmen'].sum():,}</div>
        <div class="stat-label">👨‍🏫 Toplam Öğretmen</div></div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown(f"""
        <div class="stat-card"><div class="stat-value">{filtered_df['norm_sayisi'].sum():,}</div>
        <div class="stat-label">📋 Toplam Norm Kadro</div></div>
        """, unsafe_allow_html=True)
    with col4:
        st.markdown(f"""
        <div class="stat-card"><div class="stat-value" style="color: #ff5252;">{filtered_df['norm_fazlasi_sayisi'].sum()}</div>
        <div class="stat-label">🔴 Norm Fazlası</div></div>
        """, unsafe_allow_html=True)
    with col5:
        st.markdown(f"""
        <div class="stat-card"><div class="stat-value" style="color: #69f0ae;">{filtered_df['norm_eksigi_sayisi'].sum()}</div>
        <div class="stat-label">🟢 Norm Eksiği</div></div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        type_dist = filtered_df.groupby('okul_turu')['okul_id'].nunique().reset_index()
        type_dist.columns = ['Okul Türü', 'Okul Sayısı']
        fig = px.pie(type_dist, values='Okul Sayısı', names='Okul Türü', title='Okul Türlerine Göre Dağılım',
                     color_discrete_sequence=px.colors.sequential.Plasma_r, hole=0.4)
        fig.update_traces(textposition='inside', textinfo='percent+label', textfont=dict(color='white', size=11))
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                         font=dict(color='#e8eaf6'), title_font=dict(color='#e8eaf6', size=16),
                         legend=dict(font=dict(color='#9fa8da')), height=450)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="chart-container">', unsafe_allow_html=True)
        norm_dist = filtered_df['norm_durumu'].value_counts().reset_index()
        norm_dist.columns = ['Norm Durumu', 'Sayı']
        fig = px.bar(norm_dist, x='Norm Durumu', y='Sayı', title='Norm Durumu Dağılımı',
                     color='Norm Durumu', color_discrete_map={'Norm Fazlası': '#ff5252', 'Normal': '#ffab40', 'Norm Eksiği': '#69f0ae'},
                     text='Sayı')
        fig.update_traces(textposition='outside', textfont=dict(color='white', size=14))
        fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                         font=dict(color='#e8eaf6'), title_font=dict(color='#e8eaf6', size=16),
                         showlegend=False, height=450)
        st.plotly_chart(fig, use_container_width=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.markdown("### Okul Türüne Göre Norm Kadro Karşılaştırması")
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    type_analysis = filtered_df.groupby('okul_turu').agg({
        'norm_sayisi': 'sum', 'mevcut_ogretmen': 'sum',
        'norm_fazlasi_sayisi': 'sum', 'norm_eksigi_sayisi': 'sum'
    }).reset_index()
    fig = go.Figure()
    fig.add_trace(go.Bar(name='Norm Kadro', x=type_analysis['okul_turu'], y=type_analysis['norm_sayisi'],
                         marker_color='#82b1ff', marker_line_color='#448aff', marker_line_width=1.5))
    fig.add_trace(go.Bar(name='Mevcut Öğretmen', x=type_analysis['okul_turu'], y=type_analysis['mevcut_ogretmen'],
                         marker_color='#b388ff', marker_line_color='#7c4dff', marker_line_width=1.5))
    fig.add_trace(go.Bar(name='Norm Fazlası', x=type_analysis['okul_turu'], y=type_analysis['norm_fazlasi_sayisi'],
                         marker_color='#ff5252', marker_line_color='#d32f2f', marker_line_width=1.5))
    fig.add_trace(go.Bar(name='Norm Eksiği', x=type_analysis['okul_turu'], y=type_analysis['norm_eksigi_sayisi'],
                         marker_color='#69f0ae', marker_line_color='#00c853', marker_line_width=1.5))
    fig.update_layout(barmode='group', title='Okul Türüne Göre Norm ve Mevcut Öğretmen Karşılaştırması',
                      paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                      font=dict(color='#e8eaf6'), title_font=dict(color='#e8eaf6', size=16),
                      legend=dict(font=dict(color='#9fa8da')), xaxis=dict(tickangle=-45, gridcolor='rgba(255,255,255,0.05)'),
                      yaxis=dict(gridcolor='rgba(255,255,255,0.05)'), height=500)
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ============================================
# TAB 2: OKUL ANALİZİ
# ============================================
with tab2:
    st.markdown("## 🏫 Okul Bazında Detaylı Norm Analizi")
    schools_list = sorted(filtered_df['okul_adi'].unique())
    if schools_list:
        selected_school = st.selectbox('🔍 İncelemek istediğiniz okulu seçin:', schools_list)
        if selected_school:
            school_data = filtered_df[filtered_df['okul_adi'] == selected_school]
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
            st.dataframe(display_df.style.map(highlight_status, subset=['Durum']), use_container_width=True, hide_index=True, height=400)
            
            st.markdown("### 📊 Branş Bazında Norm/Mevcut Karşılaştırması")
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            fig = go.Figure()
            fig.add_trace(go.Bar(name='Norm Kadro', x=school_data['brans_adi'], y=school_data['norm_sayisi'],
                                 marker_color='#82b1ff', marker_line_color='#448aff', marker_line_width=1.5,
                                 text=school_data['norm_sayisi'], textposition='outside', textfont=dict(color='#82b1ff', size=11)))
            fig.add_trace(go.Bar(name='Mevcut Öğretmen', x=school_data['brans_adi'], y=school_data['mevcut_ogretmen'],
                                 marker_color='#b388ff', marker_line_color='#7c4dff', marker_line_width=1.5,
                                 text=school_data['mevcut_ogretmen'], textposition='outside', textfont=dict(color='#b388ff', size=11)))
            fig.update_layout(title=f'{selected_school} - Branş Bazında Karşılaştırma', barmode='group',
                              paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                              font=dict(color='#e8eaf6'), title_font=dict(color='#e8eaf6', size=16),
                              legend=dict(font=dict(color='#9fa8da')), xaxis=dict(tickangle=-45, gridcolor='rgba(255,255,255,0.05)'),
                              yaxis=dict(gridcolor='rgba(255,255,255,0.05)'), height=450)
            st.plotly_chart(fig, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)
    else:
        st.warning("⚠️ Seçili filtrelerde okul bulunamadı.")

# ============================================
# TAB 3: BRANŞ ANALİZİ
# ============================================
with tab3:
    st.markdown("## 👨‍🏫 Branş Bazında Norm Fazlası Analizi")
    branch_summary = filtered_df.groupby('brans_adi').agg({
        'norm_sayisi': 'sum', 'mevcut_ogretmen': 'sum',
        'norm_fazlasi_sayisi': 'sum', 'norm_eksigi_sayisi': 'sum',
        'okul_id': 'nunique'
    }).reset_index()
    branch_summary.columns = ['Branş', 'Toplam Norm', 'Toplam Öğretmen', 'Norm Fazlası', 'Norm Eksiği', 'Okul Sayısı']
    
    st.markdown("### 🔴 En Fazla Norm Fazlası Olan Branşlar")
    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    top_excess = branch_summary.nlargest(15, 'Norm Fazlası')
    fig = px.bar(top_excess, x='Branş', y='Norm Fazlası', title='Norm Fazlası Öğretmen Sayısı (İlk 15 Branş)',
                 color='Norm Fazlası', color_continuous_scale='Reds', text='Norm Fazlası')
    fig.update_traces(textposition='outside', textfont=dict(color='#ff5252', size=11))
    fig.update_layout(paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)',
                      font=dict(color='#e8eaf6'), title_font=dict(color='#e8eaf6', size=16),
                      xaxis=dict(tickangle=-45, gridcolor='rgba(255,255,255,0.05)'),
                      yaxis=dict(gridcolor='rgba(255,255,255,0.05)'), coloraxis_showscale=False, height=500)
    st.plotly_chart(fig, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

# ============================================
# TAB 4: NORM FAZLASI
# ============================================
with tab4:
    st.markdown("## ⚠️ Norm Fazlası Öğretmenler ve Hizmet Puanları")
    excess_data = filtered_df[filtered_df['norm_durumu'] == 'Norm Fazlası']
    if not excess_data.empty:
        st.markdown("### 📋 Norm Fazlası Öğretmen Listesi")
        display_excess = excess_data[['okul_adi', 'okul_turu', 'brans_adi', 
                                      'norm_fazlasi_sayisi', 'ortalama_hizmet_puani', 'derslik_sayisi']].copy()
        display_excess.columns = ['Okul Adı', 'Okul Türü', 'Branş', 'Fazla Sayısı', 'Ort. Hizmet Puanı', 'Derslik']
        display_excess = display_excess.sort_values('Ort. Hizmet Puanı', ascending=False)
        st.dataframe(display_excess, use_container_width=True, hide_index=True, height=400)
    else:
        st.info("ℹ️ Seçili filtrelerde norm fazlası öğretmen bulunmamaktadır.")

# ============================================
# TAB 5: RAPORLAR
# ============================================
with tab5:
    st.markdown("## 📈 Detaylı Raporlar ve İstatistiksel Analizler")
    type_report = filtered_df.groupby('okul_turu').agg({
        'okul_id': 'nunique', 'norm_sayisi': 'sum', 'mevcut_ogretmen': 'sum',
        'norm_fazlasi_sayisi': 'sum', 'norm_eksigi_sayisi': 'sum',
        'ortalama_hizmet_puani': 'mean'
    }).round(1)
    type_report.columns = ['Okul Sayısı', 'Toplam Norm', 'Toplam Öğretmen', 'Norm Fazlası', 'Norm Eksiği', 'Ort. Hizmet Puanı']
    type_report['Doluluk Oranı (%)'] = (type_report['Toplam Öğretmen'] / type_report['Toplam Norm'] * 100).round(1)
    st.dataframe(type_report, use_container_width=True)

# ============================================
# TAB 6: OKUL LİNKLERİ
# ============================================
with tab6:
    st.markdown("## 🔗 Okul Web Siteleri ve Teşkilat Sayfaları")
    school_list = filtered_df[['okul_adi', 'okul_turu']].drop_duplicates()
    school_list = school_list.sort_values(['okul_turu', 'okul_adi'])
    selected_link_type = st.selectbox('Okul Türüne Göre Filtrele:', ['Tümü'] + sorted(school_list['okul_turu'].unique().tolist()))
    if selected_link_type != 'Tümü':
        school_list = school_list[school_list['okul_turu'] == selected_link_type]
    for idx, row in school_list.iterrows():
        school_name = row['okul_adi']
        school_type = row['okul_turu']
        slug = school_name.lower().replace(' ', '').replace('ı', 'i').replace('ğ', 'g').replace('ü', 'u').replace('ş', 's').replace('ö', 'o').replace('ç', 'c')
        website_url = f"https://{slug}.meb.k12.tr"
        teskilat_url = f"https://{slug}.meb.k12.tr/tema/teskilat.php"
        st.markdown(f"""
        <div style="background: rgba(26,35,126,0.2); border: 1px solid rgba(255,255,255,0.1); 
                    border-radius: 10px; padding: 1rem; margin: 0.5rem 0;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div><strong style="color: #e8eaf6; font-size: 1.1rem;">{school_name}</strong>
                <span style="color: #9fa8da; margin-left: 1rem;">({school_type})</span></div>
                <div>
                    <a href="{website_url}" target="_blank" style="color: #82b1ff; text-decoration: none; margin-right: 1rem;
                       padding: 0.3rem 0.8rem; border: 1px solid #82b1ff; border-radius: 15px; font-size: 0.85rem;">🌐 Web Sitesi</a>
                    <a href="{teskilat_url}" target="_blank" style="color: #b388ff; text-decoration: none;
                       padding: 0.3rem 0.8rem; border: 1px solid #b388ff; border-radius: 15px; font-size: 0.85rem;">👨‍🏫 Teşkilat</a>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

# ============================================
# TAB 7: GÖREVLENDİRME (ÖZET)
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
    
    excess_teachers = filtered_df[filtered_df['norm_durumu'] == 'Norm Fazlası']
    if not excess_teachers.empty:
        st.markdown("### 📋 Norm Fazlası Öğretmenler (Hizmet Puanı Düşükten Yükseğe)")
        display_df = excess_teachers[['okul_adi', 'okul_turu', 'brans_adi', 
                                      'norm_fazlasi_sayisi', 'ortalama_hizmet_puani']].copy()
        display_df.columns = ['Okul Adı', 'Okul Türü', 'Branş', 'Fazla Sayısı', 'Hizmet Puanı']
        display_df = display_df.sort_values('Hizmet Puanı', ascending=True)
        st.dataframe(display_df, use_container_width=True, hide_index=True, height=400)
        st.info(f"📊 Toplam {len(display_df)} norm fazlası öğretmen tespit edildi.")
    else:
        st.success("✅ Norm fazlası öğretmen bulunmamaktadır!")

# ============================================
# FOOTER
# ============================================
st.markdown("---")
st.markdown(f"""
<div class="footer">
    <p><strong>Çankaya İlçe Milli Eğitim Müdürlüğü</strong></p>
    <p>Norm Fazlası Öğretmen Dağılım ve Takip Sistemi | Versiyon 2.0</p>
    <p>© {datetime.now().year} | Tüm hakları saklıdır.</p>
</div>
""", unsafe_allow_html=True)

# ============================================
# BAŞLANGIÇ BİLDİRİMİ
# ============================================
if 'initialized' not in st.session_state:
    st.session_state.initialized = True
    st.toast('✅ Sistem başarıyla başlatıldı!', icon='🚀')
    st.toast(f'📊 {df["okul_id"].nunique()} okul ve {df["brans_adi"].nunique()} branş yüklendi.', icon='📚')
