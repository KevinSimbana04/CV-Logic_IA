import streamlit as st
from utils.data import init_session_state
import time

# Configuración de la página
st.set_page_config(
    page_title="Sistema de Filtrado de CVs",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Inicializar datos
init_session_state()

# CSS personalizado
st.markdown("""
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        
        .css-1d391kg {display: none !important;}
        .css-1aumxhk {display: none !important;}
        .css-12oz5g7 {display: none !important;}
        .stSidebar {display: none !important;}
        
        .splash-container {
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            height: 100vh;
            text-align: center;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }
        .splash-title {
            color: white;
            font-size: 42px;
            font-weight: bold;
            margin-top: 30px;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
            animation: fadeIn 1.5s ease-in;
        }
        .splash-subtitle {
            color: rgba(255,255,255,0.9);
            font-size: 22px;
            margin-top: 15px;
            animation: fadeIn 2s ease-in;
        }
        .loading-bar {
            width: 300px;
            height: 4px;
            background: rgba(255,255,255,0.3);
            border-radius: 2px;
            margin-top: 40px;
            overflow: hidden;
            animation: slideIn 1s ease-out;
        }
        .loading-bar-inner {
            width: 0%;
            height: 100%;
            background: white;
            border-radius: 2px;
            animation: loading 2.5s ease-in-out forwards;
        }
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        @keyframes slideIn {
            from { opacity: 0; transform: scaleX(0); }
            to { opacity: 1; transform: scaleX(1); }
        }
        @keyframes loading {
            0% { width: 0%; }
            100% { width: 100%; }
        }
        
        .card {
            padding: 20px;
            border-radius: 10px;
            background: white;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 20px;
            border-left: 4px solid #667eea;
        }
        .vacancy-card {
            padding: 15px;
            border-radius: 8px;
            background: #f8f9fa;
            margin: 10px 0;
            border: 1px solid #e9ecef;
        }
        .skill-tag {
            display: inline-block;
            padding: 6px 14px;
            margin: 4px;
            background: #667eea;
            color: white;
            border-radius: 20px;
            font-size: 13px;
            font-weight: 500;
            white-space: nowrap;
            box-shadow: 0 1px 3px rgba(0,0,0,0.1);
        }
        .skill-tag:hover {
            background: #5a6fd6;
            transform: scale(1.05);
            transition: all 0.2s ease;
        }
    </style>
""", unsafe_allow_html=True)

# Mostrar splash screen
if not st.session_state.get('splash_shown', False):
    with st.container():
        st.markdown("""
            <div class='splash-container'>
                <h1 style='font-size: 80px; color: white;'>📄</h1>
                <div class='splash-title'>
                    Bienvenido a nuestro modelo de filtrado de Hojas de Vida
                </div>
                <div class='splash-subtitle'>
                    Sistema inteligente de selección de candidatos
                </div>
                <div class='loading-bar'>
                    <div class='loading-bar-inner'></div>
                </div>
                <br>
        """, unsafe_allow_html=True)
        
        if st.button("🚀 Comenzar", key="btn_splash"):
            st.session_state.splash_shown = True
            st.rerun()
        
        st.markdown("</div>", unsafe_allow_html=True)
        
        placeholder = st.empty()
        with placeholder.container():
            for i in range(3, 0, -1):
                st.markdown(f"<p style='text-align: center; color: rgba(255,255,255,0.7);'>Cargando... {i}s</p>", unsafe_allow_html=True)
                time.sleep(1)
        
        if not st.session_state.get('splash_shown', False):
            st.session_state.splash_shown = True
            st.rerun()
    
    st.stop()

# Navegación
if 'pagina_actual' not in st.session_state:
    st.session_state.pagina_actual = 'login'

if not st.session_state.autenticado:
    if st.session_state.pagina_actual == 'login':
        from pages.login import show_login
        show_login()
    else:
        from pages.registro import show_registro
        show_registro()
else:
    if st.session_state.rol == 'candidato':
        from pages.dashboard_candidato import show_dashboard_candidato
        show_dashboard_candidato()
    else:
        from pages.dashboard_empresa import show_dashboard_empresa