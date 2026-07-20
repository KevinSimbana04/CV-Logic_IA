import streamlit as st
import requests

import os
from dotenv import load_dotenv

load_dotenv()
API_URL = os.getenv("API_URL", "http://localhost:8000")

def show_login():

    # Espaciado superior
    st.write("")
    st.write("")
    
    # Columnas para centrar el contenido
    col1, col2, col3 = st.columns([1, 1.5, 1])
    
    import base64
    import os
    
    def get_base64_of_bin_file(bin_file):
        if not os.path.exists(bin_file):
            return ""
        with open(bin_file, 'rb') as f:
            data = f.read()
        return base64.b64encode(data).decode()
        
    logo_path = "assets/logo.jpg"
    logo_b64 = get_base64_of_bin_file(logo_path)
    logo_html = f"<img src='data:image/jpeg;base64,{logo_b64}' style='width: 50px; height: 50px; border-radius: 10px; vertical-align: middle; margin-right: 12px; margin-bottom: 5px;'>" if logo_b64 else ""

    with col2:
        st.markdown(f"""
            <div style='text-align: center; padding-bottom: 20px;'>
                <h1 style='color: #667eea; margin-bottom: 0px;'>{logo_html}B2B-Logic</h1>
                <p style='color: gray;font-size: 1.1rem;'>Inicia sesión para continuar</p>
            </div>
        """, unsafe_allow_html=True)

        st.write("")


        with st.form("login_form", border=False):
            email = st.text_input(":material/mail: Correo Electrónico", placeholder="Ingresa tu email")
            password = st.text_input(":material/lock: Contraseña", type="password", placeholder="Ingresa tu contraseña")
            rol = st.selectbox(":material/person_search: Tipo de Usuario", ["candidato", "empresa"])
            
            st.write("") # Espaciador
            
            col_btn1, col_btn2 = st.columns(2)
            
            with col_btn1:
                submit_btn = st.form_submit_button(":material/login: Iniciar Sesión", use_container_width=True, type="primary")
            with col_btn2:
                register_btn = st.form_submit_button(":material/app_registration: Registrarse", use_container_width=True)
                
            if submit_btn:
                if not email or not password:
                    st.warning(":material/warning: Por favor completa todos los campos")
                else:
                    try:
                        res = requests.post(
                            f"{API_URL}/auth/login",
                            data={"username": email, "password": password}
                        )
                        
                        if res.status_code == 200:
                            token = res.json().get("access_token")
                            headers = {"Authorization": f"Bearer {token}"}
                            me_res = requests.get(f"{API_URL}/auth/me", headers=headers)
                            
                            if me_res.status_code == 200:
                                user_data = me_res.json()
                                if user_data.get("rol") == rol:
                                    st.session_state.autenticado = True
                                    st.session_state.token = token
                                    st.session_state.usuario = user_data.get("nombre_completo")
                                    st.session_state.rol = rol
                                    st.success(f":material/check_circle: ¡Bienvenido {st.session_state.usuario}!")
                                    import time
                                    time.sleep(1.2)
                                    st.rerun()
                                else:
                                    st.error(f":material/cancel: Este usuario es {user_data.get('rol')}, no {rol}")
                            else:
                                st.error(":material/cancel: No se pudo obtener la información del usuario")
                        elif res.status_code == 401:
                            st.error(":material/cancel: Credenciales incorrectas")
                        else:
                            st.error(f":material/cancel: Error en el servidor: {res.text}")
                    except requests.exceptions.ConnectionError:
                        st.error(":material/cancel: No se pudo conectar al backend.")
                        
            if register_btn:
                st.session_state.pagina_actual = 'registro'
                st.rerun()