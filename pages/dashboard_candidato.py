import streamlit as st
from utils.data import calcular_match

def show_dashboard_candidato():
    """Dashboard para candidatos"""
    
    # Botón de cerrar sesión en la parte superior
    col1, col2, col3 = st.columns([3, 1, 1])
    with col1:
        st.title("🎯 Panel de Vacantes")
        st.markdown(f"👤 **Usuario:** {st.session_state.usuario}")
    with col3:
        if st.button("🚪 Cerrar Sesión", use_container_width=True):
            st.session_state.autenticado = False
            st.session_state.usuario = None
            st.session_state.rol = None
            st.rerun()
    
    st.markdown("---")
    
    # Sección: Mis Skills
    st.subheader("📋 Mi Perfil")
    col1, col2 = st.columns([2, 1])
    
    with col1:
        if st.session_state.candidato_skills:
            skills = st.session_state.candidato_skills
            st.info(f"""
                **Tecnologías:** {', '.join(skills['tecnologias'])}
                **Años de experiencia:** {skills['anios_experiencia']}
                **Modalidad:** {skills['modalidad']}
            """)
        else:
            st.warning("⚠️ Aún no has registrado tus skills")
    
    with col2:
        if st.button("🔍 Buscar Match", use_container_width=True):
            st.session_state.mostrar_match = True
    
    # Mostrar resultados del match
    if st.session_state.get('mostrar_match', False):
        with st.expander("🎯 Resultados del Match", expanded=True):
            if st.session_state.candidato_skills:
                st.write("**Buscando vacantes que coincidan con tus skills...**")
                for vacante in st.session_state.vacantes:
                    match = calcular_match(vacante, st.session_state.candidato_skills)
                    if match >= 70:
                        st.success(f"✅ {vacante['titulo']} - Match: {match}%")
                    elif match >= 50:
                        st.warning(f"⚠️ {vacante['titulo']} - Match: {match}%")
                    else:
                        st.error(f"❌ {vacante['titulo']} - Match: {match}%")
                
                if st.button("❌ Cerrar resultados"):
                    st.session_state.mostrar_match = False
                    st.rerun()
            else:
                st.error("❌ Primero registra tus skills en la sección 'Mi Perfil'")
                if st.button("📝 Registrar Skills"):
                    st.session_state.mostrar_form_skills = True
                    st.session_state.mostrar_match = False
                    st.rerun()
    
    # Formulario para actualizar skills
    if st.session_state.get('mostrar_form_skills', False):
        with st.expander("📝 Registrar mis skills", expanded=True):
            tecnologias = st.text_input("Tecnologías (separadas por coma)", 
                                       placeholder="Python, AWS, Docker, SQL")
            anios = st.number_input("Años de experiencia", min_value=0, max_value=30, value=2)
            modalidad = st.selectbox("Modalidad preferida", ["Remoto", "Híbrido", "Presencial"])
            
            col_save1, col_save2 = st.columns(2)
            with col_save1:
                if st.button("💾 Guardar Skills", use_container_width=True):
                    if tecnologias:
                        skills_list = [t.strip() for t in tecnologias.split(',')]
                        st.session_state.candidato_skills = {
                            'tecnologias': skills_list,
                            'anios_experiencia': anios,
                            'modalidad': modalidad
                        }
                        st.session_state.mostrar_form_skills = False
                        st.success("✅ Skills guardadas correctamente")
                        st.rerun()
                    else:
                        st.error("❌ Ingresa al menos una tecnología")
            
            with col_save2:
                if st.button("❌ Cancelar", use_container_width=True):
                    st.session_state.mostrar_form_skills = False
                    st.rerun()
    
    st.markdown("---")
    
    # Mostrar vacantes
    st.subheader("💼 Vacantes Disponibles")
    
    if not st.session_state.vacantes:
        st.info("📌 No hay vacantes disponibles en este momento")
    else:
        # Filtrar vacantes
        vacantes_filtradas = []
        for vacante in st.session_state.vacantes:
            # Verificar si ya postuló
            ya_postulo = any(
                p['vacante_id'] == vacante['id'] 
                for p in st.session_state.mis_postulaciones
            )
            if not ya_postulo:
                vacantes_filtradas.append(vacante)
        
        if not vacantes_filtradas:
            st.info("✅ Ya has postulado a todas las vacantes disponibles")
        
        # Mostrar tarjetas de vacantes
        cols = st.columns(2)
        
        for idx, vacante in enumerate(vacantes_filtradas[:2]):  # Mostrar máximo 2
            with cols[idx % 2]:
                with st.container():
                    # Unimos la lista de tecnologías en un solo string separado por comas
                    tech_texto = ", ".join(vacante['tecnologias'])
                    
                    st.markdown(f"""
                        <div style='padding: 20px; border-radius: 10px; background: white; box-shadow: 0 2px 4px rgba(0,0,0,0.1); margin-bottom: 20px; border-left: 4px solid #667eea;'>
                            <h3>{vacante['titulo']}</h3>
                            <p><strong>🏢 Empresa:</strong> {vacante['empresa']}</p>
                            <p><strong>📊 Experiencia:</strong> {vacante['nivel_experiencia']} años</p>
                            <p><strong>📍 Modalidad:</strong> {vacante['modalidad']}</p>
                            <p><strong>🛠️ Tecnologías requeridas:</strong> {tech_texto}</p>
                    """, unsafe_allow_html=True)
                    
                    # Botón de postular
                    if st.button(f"📤 Postular", key=f"postular_{vacante['id']}", use_container_width=True):
                        st.session_state.vacante_postular = vacante
                        st.session_state.mostrar_form_postulacion = True
                        st.rerun()
                    
                    st.markdown("</div>", unsafe_allow_html=True)
    
    # Formulario de postulación
    if st.session_state.get('mostrar_form_postulacion', False):
        with st.expander("📝 Postular a vacante", expanded=True):
            vacante = st.session_state.vacante_postular
            st.write(f"**Postulando a:** {vacante['titulo']}")
            st.write(f"**Empresa:** {vacante['empresa']}")
            
            # Mostrar tecnologías requeridas (también simplificado aquí si lo deseas)
            st.write(f"**Tecnologías requeridas:** {', '.join(vacante['tecnologias'])}")
            
            st.write("---")
            st.write("**Ingresa tus skills para postular:**")
            
            # Campos para postulación
            tecnologias_post = st.text_input("Tus tecnologías (separadas por coma)", 
                                             placeholder="Python, AWS, Docker, SQL")
            anios_post = st.number_input("Años de experiencia", min_value=0, max_value=30, value=2)
            modalidad_post = st.selectbox("Modalidad preferida", ["Remoto", "Híbrido", "Presencial"])
            
            col_post1, col_post2 = st.columns(2)
            
            with col_post1:
                if st.button("📤 Enviar Postulación", use_container_width=True):
                    if tecnologias_post:
                        # Guardar postulación
                        skills_post = {
                            'tecnologias': [t.strip() for t in tecnologias_post.split(',')],
                            'anios_experiencia': anios_post,
                            'modalidad': modalidad_post
                        }
                        st.session_state.mis_postulaciones.append({
                            'vacante_id': vacante['id'],
                            'vacante_titulo': vacante['titulo'],
                            'skills': skills_post,
                            'fecha': '2024-01-15'
                        })
                        st.session_state.mostrar_form_postulacion = False
                        st.success("✅ Postulación enviada correctamente")
                        st.rerun()
                    else:
                        st.error("❌ Ingresa al menos una tecnología")
            
            with col_post2:
                if st.button("❌ Cancelar", use_container_width=True):
                    st.session_state.mostrar_form_postulacion = False
                    st.rerun()
    
    # Sección de mis postulaciones
    if st.session_state.mis_postulaciones:
        st.markdown("---")
        st.subheader("📋 Mis Postulaciones")
        
        for postulacion in st.session_state.mis_postulaciones:
            with st.expander(f"📌 {postulacion['vacante_titulo']}"):
                st.write(f"**Fecha:** {postulacion['fecha']}")
                st.write("**Tecnologías:**", ', '.join(postulacion['skills']['tecnologias']))
                st.write(f"**Experiencia:** {postulacion['skills']['anios_experiencia']} años")
                st.write(f"**Modalidad:** {postulacion['skills']['modalidad']}")