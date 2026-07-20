import streamlit as st
import time
from PIL import Image
import os

def show_splash():
    
    hide_streamlit_style = """
        <style>
            #MainMenu {visibility: hidden;}
            footer {visibility: hidden;}
            header {visibility: hidden;}
            .stApp {
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            }
            .splash-container {
                display: flex;
                flex-direction: column;
                align-items: center;
                justify-content: center;
                height: 100vh;
                text-align: center;
                padding: 20px;
            }
            .splash-title {
                color: white;
                font-size: 48px;
                font-weight: bold;
                margin-top: 30px;
                text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
                animation: fadeIn 1.5s ease-in;
            }
            .splash-subtitle {
                color: rgba(255,255,255,0.9);
                font-size: 24px;
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
        </style>
    """
    st.markdown(hide_streamlit_style, unsafe_allow_html=True)
    
    # Contenedor principal
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        # Mostrar imagen si existe
        img_path = "assets/logo.png"
        if os.path.exists(img_path):
            try:
                img = Image.open(img_path)
                st.image(img, width=200)
            except:
                # Si no se puede cargar la imagen, mostrar emoji
                st.markdown("<h1 style='text-align: center; font-size: 80px;'><span class="material-symbols-outlined" style="font-size: inherit; vertical-align: middle;">description</span></h1>", unsafe_allow_html=True)
        else:
            # Si no hay imagen, mostrar emoji
            st.markdown("<h1 style='text-align: center; font-size: 80px;'><span class="material-symbols-outlined" style="font-size: inherit; vertical-align: middle;">description</span></h1>", unsafe_allow_html=True)
        
        # Título principal
        st.markdown("""
            <div class='splash-title'>
                Bienvenido a nuestro modelo de filtrado de Hojas de Vida
            </div>
        """, unsafe_allow_html=True)
        
        # Subtítulo
        st.markdown("""
            <div class='splash-subtitle'>
                Sistema inteligente de selección de candidatos
            </div>
        """, unsafe_allow_html=True)
        
        # Barra de carga
        st.markdown("""
            <div class='loading-bar'>
                <div class='loading-bar-inner'></div>
            </div>
        """, unsafe_allow_html=True)
        
        # Espacio para el botón
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Botón para continuar (después de la animación)
        if st.button(":material/rocket_launch: Comenzar", use_container_width=True):
            st.session_state.splash_shown = True
            st.rerun()
        
        # Auto-redirección después de 3 segundos
        placeholder = st.empty()
        with placeholder.container():
            st.markdown("<p style='text-align: center; color: rgba(255,255,255,0.7);'>Cargando... 3s</p>", unsafe_allow_html=True)
            time.sleep(1)
            st.markdown("<p style='text-align: center; color: rgba(255,255,255,0.7);'>Cargando... 2s</p>", unsafe_allow_html=True)
            time.sleep(1)
            st.markdown("<p style='text-align: center; color: rgba(255,255,255,0.7);'>Cargando... 1s</p>", unsafe_allow_html=True)
            time.sleep(1)
        
        # Auto-redirección
        if not st.session_state.splash_shown:
            st.session_state.splash_shown = True
            st.rerun()