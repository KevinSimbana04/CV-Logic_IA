import streamlit as st
from utils.data import calcular_match

def show_dashboard_empresa():
    """Dashboard para empresas - Con navegación por tarjetas"""
    
    # 🛡️ SEGURIDAD ANTIFALLOS: Asegurar que las variables globales existan
    if 'vacantes' not in st.session_state:
        st.session_state.vacantes = []
    if 'mis_postulaciones' not in st.session_state:
        st.session_state.mis_postulaciones = []
    if 'usuario' not in st.session_state or st.session_state.usuario is None:
        st.session_state.usuario = "Empresa"
    # Estado para controlar qué pantalla ver ('lista' o el ID de la vacante seleccionada)
    if 'vacante_seleccionada' not in st.session_state:
        st.session_state.vacante_seleccionada = None

    # --- ENRUTADOR DE VISTAS ---
    if st.session_state.vacante_seleccionada is not None:
        # Si hay una vacante seleccionada, cargamos la vista detallada en una "nueva página"
        mostrar_detalle_vacante(st.session_state.vacante_seleccionada)
    else:
        # Si no, cargamos la lista principal de tarjetas
        mostrar_lista_principal()


def mostrar_lista_principal():
    """Vista principal: Lista de vacantes y formulario de creación"""
    # Cabecera / Navbar superior
    col1, col2, col3 = st.columns([3, 1, 1])
    with col1:
        st.title("🏢 Panel de Gestión")
        st.markdown(f"👤 **Usuario:** {st.session_state.usuario}")
    with col3:
        if st.button("🚪 Cerrar Sesión", use_container_width=True):
            st.session_state.autenticado = False
            st.session_state.usuario = None
            st.session_state.rol = None
            st.session_state.vacante_seleccionada = None
            st.rerun()
    
    st.markdown("---")
    
    # Formulario para agregar vacante
    if st.button("➕ Agregar Nueva Vacante", use_container_width=True):
        st.session_state.mostrar_form_vacante = True
    
    if st.session_state.get('mostrar_form_vacante', False):
        with st.expander("📝 Crear Nueva Vacante", expanded=True):
            titulo = st.text_input("Título de la oferta", placeholder="Ej: Desarrollador Python Senior")
            tecnologias = st.text_input("Tecnologías requeridas (separadas por coma)", placeholder="Python, FastAPI, SQL, Docker")
            experiencia = st.number_input("Nivel de experiencia esperado (años)", min_value=0, max_value=15, value=3)
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
    st.subheader("📋 Mis Vacantes")
    
    # Filtrar vacantes de la empresa
    mis_vacantes = [v for v in st.session_state.vacantes if v.get('empresa') == st.session_state.usuario]
    st.write(f"**Vacantes encontradas:** {len(mis_vacantes)}")
    
    if not mis_vacantes:
        st.info("📌 Aún no has creado vacantes. ¡Crea tu primera vacante!")
    else:
        # Renderizar cada vacante como tarjeta cliqueable
        for vacante in mis_vacantes:
            tecnologias_lista = vacante.get('tecnologias', [])
            tech_texto = ", ".join(tecnologias_lista) if isinstance(tecnologias_lista, list) else str(tecnologias_lista)
            
            # Caja visual estilizada
            st.markdown(f"""
                <div style='padding: 15px; border-radius: 8px 8px 0 0; background: #f8f9fa; margin-top: 15px; border-top: 1px solid #e9ecef; border-left: 1px solid #e9ecef; border-right: 1px solid #e9ecef;'>
                    <h3 style='margin: 0; color: #1E3A8A;'>💼 {vacante.get('titulo', 'Vacante sin título')}</h3>
                    <p style='margin: 5px 0 0 0; color: #6B7280;'>🛠️ {tech_texto} | 📍 {vacante.get('modalidad')} | 📊 {vacante.get('nivel_experiencia')} años exp.</p>
                </div>
            """, unsafe_allow_html=True)
            
            # Botón nativo de Streamlit pegado a la caja para simular el click de la tarjeta
            if st.button(f"🔍 Ver detalles y postulantes", key=f"btn_vac_{vacante.get('id')}", use_container_width=True):
                st.session_state.vacante_seleccionada = vacante.get('id')
                st.rerun()


def mostrar_detalle_vacante(vacante_id):
    """Vista de detalle: Muestra la información completa y sus postulantes"""
    # Buscar el objeto de la vacante activa
    vacante = next((v for v in st.session_state.vacantes if v.get('id') == vacante_id), None)
    
    if not vacante:
        st.error("❌ No se encontró la vacante seleccionada.")
        if st.button("⬅️ Volver al panel"):
            st.session_state.vacante_seleccionada = None
            st.rerun()
        return

    # Botón superior para regresar de página
    if st.button("⬅️ Volver al listado de vacantes"):
        st.session_state.vacante_seleccionada = None
        st.rerun()
        
    st.title(f"📌 {vacante.get('titulo')}")
    st.markdown("### 📝 Requisitos de la Oferta")
    
    # Ficha técnica de la vacante
    tech_texto = ", ".join(vacante.get('tecnologias', []))
    st.info(f"""
    * **Modalidad:** {vacante.get('modalidad')}
    * **Experiencia Mínima:** {vacante.get('nivel_experiencia')} años
    * **Tecnologías Clave:** {tech_texto}
    """)
    
    st.markdown("---")
    st.subheader("📥 Candidatos Postulados")
    
    # Buscar las postulaciones asociadas a este ID de oferta
    postulaciones = [p for p in st.session_state.mis_postulaciones if p.get('vacante_id') == vacante_id]
    
    if not postulaciones:
        st.info("📭 Aún no se han recibido candidatos para esta posición.")
    else:
        st.write(f"Se han encontrado **{len(postulaciones)}** postulantes interesados:")
        
        for idx, p in enumerate(postulaciones):
            skills_candidato = p.get('skills', {})
            tech_cand = skills_candidato.get('tecnologias', [])
            tech_cand_texto = ", ".join(tech_cand)
            
            # Contenedor del candidato
            with st.container():
                st.markdown(f"#### 👤 Postulante #{idx + 1}")
                
                col_cand_info, col_cand_match = st.columns([2, 1])
                
                with col_cand_info:
                    st.markdown(f"""
                    * **Experiencia del Candidato:** {skills_candidato.get('anios_experiencia', 0)} años
                    * **Preferencia de Trabajo:** {skills_candidato.get('modalidad', 'No especificada')}
                    * **Tecnologías que domina:** {tech_cand_texto}
                    """)
                
                with col_cand_match:
                    st.write("")  # Espaciado estético
                    # Botón de Match solicitado en la intersección del perfil del candidato
                    if st.button(f"🎯 Calcular Match", key=f"calc_match_{vacante_id}_{idx}", use_container_width=True):
                        match_score = calcular_match(vacante, skills_candidato)
                        
                        if match_score >= 70:
                            st.success(f"**¡Match Altamente Recomendado!** \n\n Score: {match_score}%")
                            st.balloons()
                        elif match_score >= 50:
                            st.warning(f"**Perfil Intermedio** \n\n Score: {match_score}%")
                        else:
                            st.error(f"**Match Insuficiente** \n\n Score: {match_score}%")
            st.markdown("<br>", unsafe_allow_html=True)