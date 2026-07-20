import streamlit as st

def calcular_match_interno(vacante, skills_candidato):
    """Calcula un porcentaje de match interno basado en tecnologías y experiencia"""
    tech_vacante = set([t.lower().strip() for t in vacante.get('tecnologias', [])])
    tech_candidato = set([t.lower().strip() for t in skills_candidato.get('tecnologias', [])])
    
    if not tech_vacante:
        score_tech = 100
    else:
        coincidencias = tech_vacante.intersection(tech_candidato)
        score_tech = (len(coincidencias) / len(tech_vacante)) * 100
        
    exp_requerida = vacante.get('nivel_experiencia', 0)
    exp_candidato = skills_candidato.get('anios_experiencia', 0)
    
    score_exp = 100 if exp_candidato >= exp_requerida else (exp_candidato / exp_requerida) * 100 if exp_requerida > 0 else 100
    
    # 70% peso a tecnologías, 30% a experiencia
    return round((score_tech * 0.7) + (score_exp * 0.3))

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
                # Limpiar estados de herramientas anteriores al cambiar de vista
                st.session_state.ver_top_5 = False
                st.session_state.ver_metricas = False
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
    
    # Buscar las postulaciones asociadas a este ID de oferta específico
    postulaciones = [p for p in st.session_state.mis_postulaciones if p.get('vacante_id') == vacante_id]
    
    if not postulaciones:
        st.info("📭 Aún no se han recibido candidatos para esta posición.")
    else:
        st.write(f"Se han encontrado **{len(postulaciones)}** postulantes interesados:")
        
        # --- SECCIÓN DE HERRAMIENTAS MIGRADA AQUÍ (Dentro de Ver Detalles) ---
        col_tools1, col_tools2 = st.columns(2)
        
        with col_tools1:
            if st.button("🏆 Comparar Postulaciones (Top 5)", key=f"btn_top5_{vacante_id}", use_container_width=True, type="primary"):
                st.session_state.ver_top_5 = not st.session_state.get('ver_top_5', False)
                st.session_state.ver_metricas = False
                st.rerun()
                
        with col_tools2:
            if st.button("📊 Métricas de la Vacante", key=f"btn_metrics_{vacante_id}", use_container_width=True):
                st.session_state.ver_metricas = not st.session_state.get('ver_metricas', False)
                st.session_state.ver_top_5 = False
                st.rerun()

        # Desplegar Top 5 mejores coincidencias para esta vacante específica
        if st.session_state.get('ver_top_5', False):
            with st.expander("⭐ Top 5 Candidatos con Mejor Coincidencia", expanded=True):
                matches_vacante = []
                
                for idx, p in enumerate(postulaciones):
                    skills_candidato = p.get('skills', {})
                    score = calcular_match_interno(vacante, skills_candidato)
                    matches_vacante.append({
                        'idx_original': idx + 1,
                        'skills': skills_candidato,
                        'score': score
                    })
                
                # Ordenar de mayor a menor score y tomar los primeros 5
                top_5 = sorted(matches_vacante, key=lambda x: x['score'], reverse=True)[:5]
                for pos, item in enumerate(top_5):
                    tech_cand = ", ".join(item['skills'].get('tecnologias', []))
                    st.markdown(f"**#{pos+1}** - **Postulante #{item['idx_original']}**")
                    st.write(f"🔹 **Match: {item['score']}%** | Exp: {item['skills'].get('anios_experiencia', 0)} años | Techs: {tech_cand}")
                    st.markdown("---")

        # Desplegar Métricas Específicas de la Vacante
        if st.session_state.get('ver_metricas', False):
            with st.expander("📈 Resumen de Métricas de la Vacante", expanded=True):
                total_postulantes_v = len(postulaciones)
                
                # Calcular el promedio de match de todos los inscritos
                scores = [calcular_match_interno(vacante, p.get('skills', {})) for p in postulaciones]
                promedio_match = round(sum(scores) / total_postulantes_v) if total_postulantes_v > 0 else 0
                
                m_col1, m_col2 = st.columns(2)
                m_col1.metric("Postulantes Totales", total_postulantes_v)
                m_col2.metric("Promedio Coincidencia (Match)", f"{promedio_match}%")
        
        st.markdown("<br>", unsafe_allow_html=True)

        # --- LISTADO TRADICIONAL DE CANDIDATOS ---
        for idx, p in enumerate(postulaciones):
            skills_candidato = p.get('skills', {})
            tech_cand = skills_candidato.get('tecnologias', [])
            tech_cand_texto = ", ".join(tech_cand)
            
            # Contenedor del candidato
            with st.container():
                st.markdown(f"#### 👤 Postulante #{idx + 1}")
                
                # Cálculo asíncrono y automático sin botón manual
                match_score = calcular_match_interno(vacante, skills_candidato)
                
                col_cand_info, col_cand_match = st.columns([2, 1])
                
                with col_cand_info:
                    st.markdown(f"""
                    * **Experiencia del Candidato:** {skills_candidato.get('anios_experiencia', 0)} años
                    * **Preferencia de Trabajo:** {skills_candidato.get('modalidad', 'No especificada')}
                    * **Tecnologías que domina:** {tech_cand_texto}
                    """)
                
                with col_cand_match:
                    st.write("")  # Espaciado estético
                    if match_score >= 70:
                        st.success(f"**¡Match Recomendado!** \n\n Score: {match_score}%")
                    elif match_score >= 50:
                        st.warning(f"**Perfil Intermedio** \n\n Score: {match_score}%")
                    else:
                        st.error(f"**Match Insuficiente** \n\n Score: {match_score}%")
            st.markdown("<br>", unsafe_allow_html=True)