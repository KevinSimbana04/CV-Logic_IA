import streamlit as st
from utils.data import calcular_match

def show_dashboard_empresa():
    """Dashboard para empresas"""
    
    # Botón de cerrar sesión en la parte superior
    col1, col2, col3 = st.columns([3, 1, 1])
    with col1:
        st.title("🏢 Panel de Gestión")
        st.markdown(f"👤 **Usuario:** {st.session_state.usuario}")
    with col3:
        if st.button("🚪 Cerrar Sesión", use_container_width=True):
            st.session_state.autenticado = False
            st.session_state.usuario = None
            st.session_state.rol = None
            st.rerun()
    
    st.markdown("---")
    
    # Botón para agregar vacante
    if st.button("➕ Agregar Nueva Vacante", use_container_width=True):
        st.session_state.mostrar_form_vacante = True
    
    # Formulario para nueva vacante
    if st.session_state.get('mostrar_form_vacante', False):
        with st.expander("📝 Crear Nueva Vacante", expanded=True):
            titulo = st.text_input("Título de la oferta", placeholder="Ej: Desarrollador Python Senior")
            tecnologias = st.text_input("Tecnologías requeridas (separadas por coma)", 
                                       placeholder="Python, FastAPI, SQL, Docker")
            experiencia = st.number_input("Nivel de experiencia esperado (años)", 
                                         min_value=0, max_value=15, value=3)
            modalidad = st.selectbox("Modalidad", ["Remoto", "Híbrido", "Presencial"])
            
            col_save1, col_save2 = st.columns(2)
            
            with col_save1:
                if st.button("💾 Guardar Vacante", use_container_width=True):
                    if titulo and tecnologias:
                        tech_list = [t.strip() for t in tecnologias.split(',')]
                        nueva_vacante = {
                            'id': len(st.session_state.vacantes) + 1,
                            'titulo': titulo,
                            'empresa': st.session_state.usuario,
                            'tecnologias': tech_list,
                            'nivel_experiencia': experiencia,
                            'modalidad': modalidad,
                            'postulaciones': []
                        }
                        st.session_state.vacantes.append(nueva_vacante)
                        st.session_state.mostrar_form_vacante = False
                        st.success("✅ Vacante creada exitosamente")
                        st.rerun()
                    else:
                        st.error("❌ Completa todos los campos")
            
            with col_save2:
                if st.button("❌ Cancelar", use_container_width=True):
                    st.session_state.mostrar_form_vacante = False
                    st.rerun()
    
    st.markdown("---")
    
    # Mostrar vacantes creadas
    st.subheader("📋 Mis Vacantes")
    
    # Filtrar vacantes de esta empresa
    mis_vacantes = []
    for v in st.session_state.vacantes:
        if v['empresa'] == st.session_state.usuario:
            mis_vacantes.append(v)
    
    # Depuración - mostrar cuántas vacantes tiene la empresa
    st.write(f"**Vacantes encontradas:** {len(mis_vacantes)}")
    
    if not mis_vacantes:
        st.info("📌 Aún no has creado vacantes. ¡Crea tu primera vacante!")
    else:
        for vacante in mis_vacantes:
            with st.container():
                # Convertimos las tecnologías a texto simple separado por comas
                tech_texto = ", ".join(vacante["tecnologias"])
                
                st.markdown(f"""
                    <div style='padding: 15px; border-radius: 8px; background: #f8f9fa; margin: 10px 0; border: 1px solid #e9ecef;'>
                        <h3>{vacante['titulo']}</h3>
                        <p><strong>📊 Experiencia requerida:</strong> {vacante['nivel_experiencia']} años</p>
                        <p><strong>📍 Modalidad:</strong> {vacante['modalidad']}</p>
                        <p><strong>🛠️ Tecnologías:</strong> {tech_texto}</p>
                    </div>
                """, unsafe_allow_html=True)  # Aquí cerramos correctamente el </div> principal antes de seguir
                
                # Buscar postulaciones para esta vacante
                postulaciones = []
                for p in st.session_state.mis_postulaciones:
                    if p['vacante_id'] == vacante['id']:
                        postulaciones.append(p)
                
                if postulaciones:
                    st.write(f"**📥 Postulaciones recibidas:** {len(postulaciones)}")
                    
                    # Mostrar postulaciones
                    for idx, p in enumerate(postulaciones):
                        with st.expander(f"👤 Postulación {idx + 1}"):
                            st.write("**Skills del candidato:**")
                            st.write(f"- Tecnologías: {', '.join(p['skills']['tecnologias'])}")
                            st.write(f"- Experiencia: {p['skills']['anios_experiencia']} años")
                            st.write(f"- Modalidad: {p['skills']['modalidad']}")
                            
                            # Botón de match
                            if st.button(f"🎯 Calcular Match", key=f"match_emp_{vacante['id']}_{idx}"):
                                match = calcular_match(vacante, p['skills'])
                                if match >= 70:
                                    st.success(f"✅ ¡Excelente candidato! Match: {match}%")
                                    st.balloons()
                                elif match >= 50:
                                    st.warning(f"⚠️ Buen candidato: {match}%")
                                else:
                                    st.error(f"❌ No es el perfil buscado: {match}%")
                else:
                    st.info("📭 Aún no hay postulaciones para esta vacante")
                
                st.markdown("---")