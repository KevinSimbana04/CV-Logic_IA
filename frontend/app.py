import streamlit as st
from utils.data import init_session_state
import time

# Configuración de la página
st.set_page_config(
    page_title="B2B-Plataforma de Reclutamiento",
    page_icon="assets/logo.jpg",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Inicializar datos
init_session_state()

# CSS personalizado para Splash Screen y ocultar menús nativos
st.markdown("""
    <link href="https://fonts.googleapis.com/css2?family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@24,400,0,0" rel="stylesheet" />
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        
        /* Eliminar márgenes blancos superiores nativos de Streamlit, pero mantener espacio al final */
        .block-container {
            padding-top: 0rem !important;
            padding-bottom: 4rem !important;
            margin: 0 !important;
        }
        
        .splash-screen {
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            z-index: 999999;
            text-align: center;
            color: white;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 0;
        }
        
        .splash-title {
            font-size: 3rem;
            font-weight: bold;
            margin: 20px 0 10px 0;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        }
        
        .splash-subtitle {
            font-size: 1.2rem;
            opacity: 0.9;
            margin-bottom: 40px;
        }
        
        /* Barra de carga animada */
        .loading-bar {
            width: 300px;
            height: 6px;
            background: rgba(255,255,255,0.2);
            border-radius: 3px;
            overflow: hidden;
        }
        
        .loading-bar-inner {
            width: 0%;
            height: 100%;
            background: white;
            border-radius: 3px;
            animation: loading 2.5s ease-in-out forwards;
        }
        
        @keyframes loading {
            0% { width: 0%; }
            100% { width: 100%; }
        }
    </style>
""", unsafe_allow_html=True)

import base64
import os

def get_base64_of_bin_file(bin_file):
    if not os.path.exists(bin_file):
        return ""
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

# Mostrar splash screen
if not st.session_state.get('splash_shown', False):
    placeholder = st.empty()
    
    # Preparar tag del logo
    logo_path = "assets/logo.jpg"
    logo_b64 = get_base64_of_bin_file(logo_path)
    if logo_b64:
        logo_html = f"<img src='data:image/jpeg;base64,{logo_b64}' style='width: 150px; border-radius: 15px; margin-bottom: 10px;'>"
    else:
        logo_html = "<h1 style='font-size: 5rem; margin:0;'><span class='material-symbols-outlined' style='font-size: inherit; vertical-align: middle;'>description</span></h1>"

    with placeholder.container():
        st.markdown(f"""
            <div class="splash-screen">
                {logo_html}
                <div class='splash-title'>
                    B2B-Plantaforma de Reclutamiento
                </div>
                <div class='splash-subtitle'>
                    Sistema inteligente de selección de candidatos
                </div>
                <div class='loading-bar'>
                    <div class='loading-bar-inner'></div>
                </div>
            </div>
        """, unsafe_allow_html=True)
        time.sleep(2.6) # Tiempo que dura la animación de carga
    
    placeholder.empty()
    st.session_state.splash_shown = True
    st.rerun()

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
    elif st.session_state.rol == 'empresa':
        from pages.dashboard_empresa import show_dashboard_empresa
        show_dashboard_empresa()