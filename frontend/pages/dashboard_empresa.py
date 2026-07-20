import streamlit as st
import requests

import os
from dotenv import load_dotenv

load_dotenv()
API_URL = os.getenv("API_URL", "https://b2b-logic-ia.onrender.com")

def get_headers():
    token = st.session_state.get('token')
    if token:
        return {"Authorization": f"Bearer {token}"}
    return {}

def show_dashboard_empresa():
    
    # 🛡️ SEGURIDAD ANTIFALLOS: Asegurar que las variables globales existan
    if 'usuario' not in st.session_state or st.session_state.usuario is None:
        st.session_state.usuario = "Empresa"
    if 'vacante_seleccionada' not in st.session_state:
        st.session_state.vacante_seleccionada = None
    if 'vacante_seleccionada_info' not in st.session_state:
        st.session_state.vacante_seleccionada_info = None

    # --- ENRUTADOR DE VISTAS ---
    if st.session_state.vacante_seleccionada is not None:
        mostrar_detalle_vacante(st.session_state.vacante_seleccionada, st.session_state.vacante_seleccionada_info)
    else:
        mostrar_lista_principal()


def mostrar_lista_principal():

    col1, col2, col3 = st.columns([3, 1, 1])
    with col1:
        st.title(":material/business: Panel de Gestión")
        st.markdown(f":material/person: **Usuario:** {st.session_state.usuario}")
    with col3:
        if st.button(":material/logout: Cerrar Sesión", use_container_width=True):
            st.session_state.autenticado = False
            st.session_state.usuario = None
            st.session_state.rol = None
            st.session_state.token = None
            st.session_state.vacante_seleccionada = None
            st.session_state.vacante_seleccionada_info = None
            st.rerun()
    
    
    tab_vacantes, tab_crear, tab_ia = st.tabs([":material/list_alt: Mis Vacantes", ":material/add: Nueva Vacante", ":material/psychology: Entrenamiento IA"])
    
    with tab_vacantes:
        try:
            res = requests.get(f"{API_URL}/empresas/vacantes", headers=get_headers())
            mis_vacantes = res.json() if res.status_code == 200 else []
        except Exception:
            mis_vacantes = []
            st.error(":material/cancel: Error de conexión al cargar vacantes")
            
        if not mis_vacantes:
            st.info(":material/push_pin: Aún no has creado vacantes. ¡Ve a la pestaña 'Nueva Vacante' para crear la primera!")
        else:
            st.write(f"**Total de vacantes activas:** {len(mis_vacantes)}")
            
            # Usar columnas para organizar las tarjetas de vacantes
            cols = st.columns(2)
            for idx, vacante in enumerate(mis_vacantes):
                with cols[idx % 2]:
                    with st.container(border=True):
                        tecnologias_lista = vacante.get('tecnologias_requeridas', [])
                        tech_texto = ", ".join(tecnologias_lista) if isinstance(tecnologias_lista, list) else str(tecnologias_lista)
                        
                        st.subheader(f":material/work: {vacante.get('titulo_oferta', 'Vacante')}")
                        st.markdown(f"**:material/location_on: Modalidad:** {vacante.get('modalidad')}")
                        st.markdown(f"**:material/bar_chart: Experiencia:** {vacante.get('nivel_experiencia_esperado')} años")
                        st.markdown(f"**:material/build: Tecnologías:** {tech_texto}")
                        
                        st.write("") # Espaciador
                        if st.button(f":material/search: Ver detalles y postulantes", key=f"btn_vac_{vacante.get('id')}", use_container_width=True):
                            st.session_state.vacante_seleccionada = vacante.get('id')
                            st.session_state.vacante_seleccionada_info = vacante
                            st.session_state.ver_top_5 = False
                            st.session_state.ver_metricas = False
                            st.rerun()

    with tab_crear:
        st.subheader(":material/edit_document: Detalles de la Vacante")
        titulo = st.text_input("Título de la oferta", placeholder="Ej: Desarrollador Python Senior")
        tecnologias = st.text_input("Tecnologías requeridas (separadas por coma)", placeholder="Python, FastAPI, SQL, Docker")
        
        col_exp, col_mod = st.columns(2)
        with col_exp:
            experiencia = st.number_input("Nivel de experiencia esperado (años)", min_value=0, max_value=15, value=3)
        with col_mod:
            modalidad = st.selectbox("Modalidad", ["Remoto", "Híbrido", "Presencial"])
        
        st.write("")
        if st.button(":material/save: Guardar Vacante", use_container_width=True, type="primary"):
            if titulo and tecnologias:
                tech_list = [t.strip() for t in tecnologias.split(',') if t.strip()]
                payload = {
                    "titulo_oferta": titulo,
                    "tecnologias_requeridas": tech_list,
                    "nivel_experiencia_esperado": experiencia,
                    "modalidad": modalidad
                }
                try:
                    res = requests.post(f"{API_URL}/empresas/vacantes", json=payload, headers=get_headers())
                    if res.status_code == 201:
                        st.success(":material/check_circle: Vacante creada exitosamente. Actualizando lista...")
                        import time
                        time.sleep(1.2)
                        st.rerun()
                    else:
                        st.error(f":material/cancel: Error al crear vacante: {res.text}")
                except Exception as e:
                    st.error(f"Error de conexión: {str(e)}")
            else:
                st.error(":material/cancel: Completa todos los campos obligatorios")

    with tab_ia:
        st.subheader(":material/settings: Configuración del Modelo de Asignación")
        st.markdown("Ajusta los parámetros para re-entrenar el modelo IA utilizado para predecir matches.")
        
        col_ia1, col_ia2 = st.columns(2)
        with col_ia1:
            hidden_layers = st.text_input("Capas Ocultas (separadas por coma)", value="128,64", help="Ejemplo: 128,64 para dos capas de 128 y 64 neuronas")
            activation = st.selectbox("Función de Activación", ["relu", "identity", "logistic", "tanh"], index=0)
        with col_ia2:
            max_iter = st.number_input("Iteraciones Máximas (Épocas)", min_value=10, max_value=2000, value=300, step=50)
            
        st.write("")
        if st.button(":material/rocket_launch: Iniciar Entrenamiento", use_container_width=True, type="primary"):
            with st.spinner("Entrenando modelo de IA, esto puede tomar unos segundos..."):
                payload_ia = {
                    "hidden_layers": hidden_layers,
                    "max_iter": max_iter,
                    "activation": activation
                }
                try:
                    res_ia = requests.post(f"{API_URL}/ia/entrenar", json=payload_ia, headers=get_headers())
                    if res_ia.status_code == 200:
                        st.success(f":material/check_circle: {res_ia.json().get('mensaje', 'Entrenamiento completado')}")
                        import time
                        time.sleep(1.2)
                        st.rerun()
                    else:
                        st.error(f":material/cancel: Error durante el entrenamiento: {res_ia.text}")
                except Exception as e:
                    st.error(f":material/cancel: Error de conexión al servidor de IA: {str(e)}")

        st.markdown("---")
        st.subheader(":material/monitoring: Resultados del Último Entrenamiento")
        
        import os
        import json
        
        # Rutas de los archivos generados en el backend
        api_ai_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'api', 'ai_model'))
        metrics_path = os.path.join(api_ai_dir, 'last_metrics.json')
        cm_path = os.path.join(api_ai_dir, 'confusion_matrix.png')
        
        if os.path.exists(metrics_path):
            with open(metrics_path, 'r') as f:
                last_metrics = json.load(f)
                
            col_matrix, spacer, col_metrics = st.columns([1.8, 0.2, 1])
            
            with col_matrix:
                if last_metrics.get('has_confusion_matrix') and os.path.exists(cm_path):
                    st.markdown("#### :material/grid_on: Matriz de Confusión (Datos de Prueba)")
                    st.image(cm_path, use_container_width=True)
                else:
                    st.info("La matriz de confusión no está disponible.")
                    
            with col_metrics:
                st.markdown("#### :material/analytics: Métricas de Evaluación")
                st.write("")
                st.metric(":material/my_location: Accuracy (Exactitud)", f"{last_metrics.get('accuracy', 0)*100:.2f}%")
                st.metric(":material/ads_click: Precision (Precisión)", f"{last_metrics.get('precision', 0)*100:.2f}%")
                st.metric(":material/replay: Recall (Sensibilidad)", f"{last_metrics.get('recall', 0)*100:.2f}%")
                st.metric(":material/stars: F1-Score (Puntaje F1)", f"{last_metrics.get('f1_score', 0)*100:.2f}%")
        else:
            st.info("No hay datos de entrenamientos previos. Ejecuta un entrenamiento para ver las métricas y la matriz de confusión.")
def mostrar_detalle_vacante(vacante_id, vacante_info):
    """Vista de detalle: Muestra la información completa y consulta el match de la IA"""
    if not vacante_info:
        st.error(":material/cancel: No se encontró la vacante seleccionada.")
        if st.button(":material/arrow_back: Volver al panel"):
            st.session_state.vacante_seleccionada = None
            st.rerun()
        return

    if st.button(":material/arrow_back: Volver al listado de vacantes"):
        st.session_state.vacante_seleccionada = None
        st.session_state.vacante_seleccionada_info = None
        st.rerun()
        
    st.title(f":material/push_pin: {vacante_info.get('titulo_oferta')}")
    st.markdown("### :material/edit_document: Requisitos de la Oferta")
    
    tech_texto = ", ".join(vacante_info.get('tecnologias_requeridas', []))
    st.info(f"""
    * **Modalidad:** {vacante_info.get('modalidad')}
    * **Experiencia Mínima:** {vacante_info.get('nivel_experiencia_esperado')} años
    * **Tecnologías Clave:** {tech_texto}
    """)
    
    st.markdown("---")
    st.subheader(":material/analytics: Análisis de Postulantes (IA)")
    
    # Consultar endpoint de match
    with st.spinner("Consultando análisis de IA de postulantes..."):
        try:
            res = requests.get(f"{API_URL}/empresas/vacantes/{vacante_id}/match", headers=get_headers())
            if res.status_code == 200:
                matches_data = res.json().get('resultados', [])
                mostrar_resultados_ia(matches_data, vacante_id)
            elif res.status_code == 400:
                error_detail = res.json().get("detail", "")
                st.warning(f"⏳ **IA en proceso:** {error_detail}")
                st.info("La recolección de candidatos y evaluación inicial requiere 3 minutos después de creada la vacante.")
            else:
                st.error(f":material/cancel: Error al obtener matches: {res.text}")
        except Exception as e:
            st.error(":material/cancel: Error de conexión al consultar matches.")

def mostrar_resultados_ia(matches, vacante_id):
    if not matches:
        st.info(":material/inbox: Aún no se han recibido candidatos para esta posición, o la IA no encontró perfiles compatibles.")
        return
        
    st.write(f"Se han evaluado **{len(matches)}** postulantes para esta vacante.")
    
    # 1. Ordenar todos los postulantes por score (confianza_vacante) de mayor a menor
    matches_sorted = sorted(matches, key=lambda x: float(x.get('confianza_vacante', 0)), reverse=True)
    
    mejor_candidato = matches_sorted[0]
    
    st.markdown("### :material/star: Mejor Candidato Recomendado")
    
    perfil = mejor_candidato.get('perfil', {})
    tech_cand = ", ".join(perfil.get('tecnologias', []))
    match_score_str = mejor_candidato.get('porcentaje_match_vacante', '0%')
    
    with st.container(border=True):
        st.markdown(f"#### :material/person: {mejor_candidato.get('nombre_completo')}")
        
        col_cand_info, col_cand_match = st.columns([2, 1])
        
        with col_cand_info:
            st.markdown(f"""
            * **Contacto:** {mejor_candidato.get('email')}
            * **Experiencia:** {perfil.get('anios_experiencia', 0)} años
            * **Preferencia:** {perfil.get('modalidad', 'No especificada')}
            * **Tecnologías:** {tech_cand}
            """)
            if mejor_candidato.get('rol_sugerido_por_ia'):
                st.info(f":material/psychology: La IA sugiere que su perfil encaja más con: **{mejor_candidato.get('rol_sugerido_por_ia')}** ({mejor_candidato.get('porcentaje_rol_sugerido')})")
        
        with col_cand_match:
            st.write("") 
            st.success(f"**:material/verified: Match Destacado!** \n\n Score: {match_score_str}")
            
    st.write("")

    if len(matches_sorted) > 1:
        with st.expander(":material/emoji_events: Ver Otros Candidatos Destacados (Top 2-5)"):
            otros_top = matches_sorted[1:5]
            for pos, item in enumerate(otros_top):
                perfil = item.get('perfil', {})
                tech_cand = ", ".join(perfil.get('tecnologias', []))
                
                st.markdown(f"**#{pos+2}** - **{item.get('nombre_completo')}** ({item.get('email')})")
                st.write(f":material/done_all: **Match: {item.get('porcentaje_match_vacante')}** | Exp: {perfil.get('anios_experiencia', 0)} años | Techs: {tech_cand}")
                if item.get('rol_sugerido_por_ia'):
                    st.write(f":material/psychology: *IA sugiere rol:* {item.get('rol_sugerido_por_ia')} ({item.get('porcentaje_rol_sugerido')})")
                st.markdown("---")

    with st.expander(":material/bar_chart: Ver Resumen de Métricas de la Vacante"):
        total_postulantes_v = len(matches_sorted)
        scores = [float(p.get('confianza_vacante', 0)) * 100 for p in matches_sorted]
        promedio_match = round(sum(scores) / total_postulantes_v) if total_postulantes_v > 0 else 0
        
        m_col1, m_col2 = st.columns(2)
        m_col1.metric("Postulantes Evaluados", total_postulantes_v)
        m_col2.metric("Promedio Coincidencia (Match)", f"{promedio_match}%")
        st.markdown("<br>", unsafe_allow_html=True)