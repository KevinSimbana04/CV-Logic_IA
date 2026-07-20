import streamlit as st

def show_login():
    """Muestra la página de login - VERSIÓN CORREGIDA"""
    
    st.markdown("""
        <div style='text-align: center; padding: 50px 0;'>
            <h1 style='font-size: 48px; color: #667eea;'>💼 Sistema de Filtrado de CVs</h1>
            <p style='font-size: 18px; color: #666;'>Inicia sesión para continuar</p>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        with st.container():
            st.markdown("""
                <div style='background: white; padding: 40px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1);'>
            """, unsafe_allow_html=True)
            
            # Mostrar usuarios disponibles
            st.info("🔑 **Usuarios disponibles:**")
            for email, user_data in st.session_state.usuarios.items():
                st.write(f"- **{email}** ({user_data['rol']}) | Contraseña: {user_data['password']}")
            
            st.markdown("---")
            
            email = st.text_input("📧 Correo Electrónico", placeholder="Ingresa tu email")
            password = st.text_input("🔒 Contraseña", type="password", placeholder="Ingresa tu contraseña")
            rol = st.selectbox("🎯 Tipo de Usuario", ["candidato", "empresa"])
            
            col_btn1, col_btn2 = st.columns(2)
            
            with col_btn1:
                if st.button("🚀 Iniciar Sesión", use_container_width=True):
                    # Verificar que los campos no estén vacíos
                    if not email or not password:
                        st.warning("⚠️ Por favor completa todos los campos")
                    else:
                        # Buscar usuario por email
                        if email in st.session_state.usuarios:
                            user_data = st.session_state.usuarios[email]
                            
                            # Verificar contraseña
                            if user_data['password'] == password:
                                # Verificar rol
                                if user_data['rol'] == rol:
                                    st.session_state.autenticado = True
                                    st.session_state.usuario = user_data['nombre']
                                    st.session_state.rol = rol
                                    st.success(f"✅ ¡Bienvenido {user_data['nombre']}!")
                                    st.rerun()
                                else:
                                    st.error(f"❌ Este usuario es {user_data['rol']}, no {rol}")
                            else:
                                st.error("❌ Contraseña incorrecta")
                        else:
                            st.error("❌ Usuario no encontrado. ¿Quieres registrarte?")
            
            with col_btn2:
                if st.button("📝 Registrarse", use_container_width=True):
                    st.session_state.pagina_actual = 'registro'
                    st.rerun()
            
            st.markdown("</div>", unsafe_allow_html=True)