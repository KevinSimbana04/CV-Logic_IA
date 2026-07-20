import streamlit as st
import requests

import os
from dotenv import load_dotenv

load_dotenv()
API_URL = os.getenv("API_URL", "https://b2b-logic-ia.onrender.com")

def show_registro():
    
    st.write("")
    st.write("")
    
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
                <h1 style='color: #667eea; margin-bottom: 0px;'>{logo_html}Registro de Usuario</h1>
                <p style='color: gray; margin-top: 5px; font-size: 1.1rem;'>Crea tu cuenta para comenzar</p>
            </div>
        """, unsafe_allow_html=True)
        
        with st.form("registro_form", border=False):
            nombre = st.text_input(":material/person: Nombre Completo", placeholder="Tu nombre completo")
            email = st.text_input(":material/mail: Correo Electrónico", placeholder="ejemplo@correo.com")
            password = st.text_input(":material/lock: Contraseña", type="password", placeholder="Mínimo 6 caracteres")
            confirm_password = st.text_input(":material/lock: Confirmar Contraseña", type="password", placeholder="Repite tu contraseña")
            rol = st.selectbox(":material/person_search: Tipo de Usuario", ["candidato", "empresa"])
            
            st.write("")
            col_btn1, col_btn2 = st.columns(2)
            
            with col_btn1:
                submit_btn = st.form_submit_button(":material/check_circle: Registrarse", use_container_width=True, type="primary")
            with col_btn2:
                back_btn = st.form_submit_button(":material/arrow_back: Volver al Login", use_container_width=True)
                
            if submit_btn:
                if nombre and email and password and confirm_password:
                    if password != confirm_password:
                        st.error(":material/cancel: Las contraseñas no coinciden")
                    elif len(password) < 6:
                        st.error(":material/cancel: La contraseña debe tener al menos 6 caracteres")
                    else:
                        payload = {
                            "email": email,
                            "password": password,
                            "rol": rol,
                            "nombre_completo": nombre
                        }
                        try:
                            res = requests.post(f"{API_URL}/auth/registro", json=payload)
                            if res.status_code == 201:
                                st.success(":material/check_circle: Registro exitoso! Ahora inicia sesión")
                                import time
                                time.sleep(1.2)
                                st.session_state.pagina_actual = 'login'
                                st.rerun()
                            elif res.status_code == 400:
                                st.error(f":material/cancel: {res.json().get('detail', 'Error en el registro')}")
                            else:
                                st.error(f":material/cancel: Error en el servidor: {res.text}")
                        except requests.exceptions.ConnectionError:
                            st.error(":material/cancel: No se pudo conectar al backend.")
                else:
                    st.warning(":material/warning: Por favor completa todos los campos")
                    
            if back_btn:
                st.session_state.pagina_actual = 'login'
                st.rerun()