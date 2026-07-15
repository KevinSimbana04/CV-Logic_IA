import streamlit as st
from splash import show_splash
from home import show_home

# Configuración de la página
st.set_page_config(
    page_title="Filtro de Hojas de Vida",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Inicializar estado de sesión
if 'splash_shown' not in st.session_state:
    st.session_state.splash_shown = False

# Mostrar splash o home
if not st.session_state.splash_shown:
    show_splash()
else:
    show_home()