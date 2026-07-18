import streamlit as st

def show_registro():
    """Muestra la página de registro - VERSIÓN CORREGIDA"""
    
    st.markdown("""
        <div style='text-align: center; padding: 30px 0;'>
            <h1 style='font-size: 36px; color: #667eea;'>📝 Registro de Usuario</h1>
            <p style='font-size: 16px; color: #666;'>Crea tu cuenta para comenzar</p>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        with st.container():
            st.markdown("""
                <div style='background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);'>
            """, unsafe_allow_html=True)
            
            nombre = st.text_input("👤 Nombre Completo", placeholder="Tu nombre completo")
            email = st.text_input("📧 Correo Electrónico", placeholder="ejemplo@correo.com")
            password = st.text_input("🔒 Contraseña", type="password", placeholder="Mínimo 6 caracteres")
            confirm_password = st.text_input("🔒 Confirmar Contraseña", type="password", placeholder="Repite tu contraseña")
            rol = st.selectbox("🎯 Tipo de Usuario", ["candidato", "empresa"])
            
            col_btn1, col_btn2 = st.columns(2)
            
            with col_btn1:
                if st.button("✅ Registrarse", use_container_width=True):
                    if nombre and email and password and confirm_password:
                        if password != confirm_password:
                            st.error("❌ Las contraseñas no coinciden")
                        elif len(password) < 6:
                            st.error("❌ La contraseña debe tener al menos 6 caracteres")
                        elif email in st.session_state.usuarios:
                            st.error("❌ Este correo ya está registrado")
                        else:
                            # Registrar nuevo usuario
                            st.session_state.usuarios[email] = {
                                'password': password,
                                'rol': rol,
                                'nombre': nombre
                            }
                            st.success("✅ Registro exitoso! Ahora inicia sesión")
                            st.session_state.pagina_actual = 'login'
                            st.rerun()
                    else:
                        st.warning("⚠️ Por favor completa todos los campos")
            
            with col_btn2:
                if st.button("🔙 Volver al Login", use_container_width=True):
                    st.session_state.pagina_actual = 'login'
                    st.rerun()
            
            st.markdown("</div>", unsafe_allow_html=True)