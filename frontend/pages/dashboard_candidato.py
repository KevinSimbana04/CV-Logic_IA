import streamlit as st
import requests


import os
from dotenv import load_dotenv

load_dotenv()
API_URL = os.getenv("API_URL", "https://b2b-logic-ia.onrender.com")

def show_dashboard_candidato():
    """Dashboard para candidatos"""
    
    col1, col2, col3 = st.columns([3, 1, 1])
    with col1:
        st.title(":material/category: Panel de Candidato")
        st.markdown(f":material/person: **Usuario:** {st.session_state.usuario}")
    with col3:
        if st.button(":material/logout: Cerrar Sesión", use_container_width=True):
            st.session_state.autenticado = False
            st.session_state.token = None
            st.session_state.usuario = None
            st.session_state.rol = None
            st.rerun()
    
    
    headers = {"Authorization": f"Bearer {st.session_state.token}"}

    if "candidato_skills" not in st.session_state or st.session_state.get("_reload_skills", True):
        res = requests.get(f"{API_URL}/candidatos/perfil", headers=headers)
        if res.status_code == 200:
            st.session_state.candidato_skills = res.json()
        else:
            st.session_state.candidato_skills = None
        st.session_state._reload_skills = False
        
    if "vacantes" not in st.session_state or st.session_state.get("_reload_vacantes", True):
        res_v = requests.get(f"{API_URL}/candidatos/vacantes", headers=headers)
        st.session_state.vacantes = res_v.json() if res_v.status_code == 200 else []
        
        res_p = requests.get(f"{API_URL}/candidatos/postulaciones", headers=headers)
        st.session_state.mis_postulaciones = res_p.json() if res_p.status_code == 200 else []
        
        st.session_state._reload_vacantes = False

    tab_vacantes, tab_postulaciones, tab_perfil = st.tabs([":material/work: Vacantes Disponibles", ":material/upload: Mis Postulaciones", ":material/list_alt: Mi Perfil"])
    
    with tab_vacantes:
        st.subheader(":material/work: Vacantes Disponibles")
        
        if not st.session_state.vacantes:
            st.info(":material/push_pin: No hay vacantes disponibles en este momento")
        else:
            # Filtrar vacantes
            vacantes_filtradas = []
            for vacante in st.session_state.vacantes:
                ya_postulo = any(
                    p['vacante_id'] == vacante['id'] 
                    for p in st.session_state.mis_postulaciones
                )
                if not ya_postulo:
                    vacantes_filtradas.append(vacante)
            
            if not vacantes_filtradas:
                st.info(":material/check_circle: Ya has postulado a todas las vacantes disponibles")


            cols = st.columns(2)
            for idx, vacante in enumerate(vacantes_filtradas):
                with cols[idx % 2]:
                    with st.container(border=True):
                        tech_texto = ", ".join(vacante.get('tecnologias_requeridas', []))
                        empresa_nombre = vacante.get('empresa', {}).get('nombre_completo', 'Empresa Anónima') if vacante.get('empresa') else 'Empresa Anónima'
                        
                        st.subheader(f"{vacante['titulo_oferta']}")
                        st.markdown(f"**:material/business: Empresa:** {empresa_nombre}")
                        st.markdown(f"**:material/bar_chart: Experiencia:** {vacante['nivel_experiencia_esperado']} años")
                        st.markdown(f"**:material/location_on: Modalidad:** {vacante['modalidad']}")
                        st.markdown(f"**:material/build: Tecnologías:** {tech_texto}")
                        
                        st.write("")
                        if st.button(f":material/upload: Postular", key=f"postular_{vacante['id']}", use_container_width=True, type="primary"):
                            res_postular = requests.post(
                                f"{API_URL}/candidatos/vacantes/{vacante['id']}/postular",
                                headers=headers
                            )
                            if res_postular.status_code == 201:
                                st.session_state._reload_vacantes = True
                                st.success(":material/check_circle: Te has postulado exitosamente")
                                import time
                                time.sleep(1.2)
                                st.rerun()
                            elif res_postular.status_code == 400:
                                st.error(f":material/cancel: {res_postular.json().get('detail')}")
                            else:
                                st.error(":material/cancel: Ocurrió un error al postular")
                                
    with tab_postulaciones:
        st.subheader(":material/list_alt: Mis Postulaciones")
        if not st.session_state.mis_postulaciones:
             st.info("Aún no tienes postulaciones. Ve a 'Vacantes Disponibles' para aplicar a una.")
        else:
            for postulacion in st.session_state.mis_postulaciones:
                vacante = postulacion.get('vacante', {})
                titulo = vacante.get('titulo_oferta', f"Vacante #{postulacion['vacante_id']}")
                fecha_post = str(postulacion.get('fecha_postulacion', ''))[:10]
                
                with st.container(border=True):
                    st.markdown(f"### :material/push_pin: {titulo}")
                    st.caption(f"Postulado el: {fecha_post}")
                    if vacante:
                        st.write(f"**Empresa:** {vacante.get('empresa', {}).get('nombre_completo', 'Desconocida')}")
                        st.write("**Tecnologías requeridas:**", ', '.join(vacante.get('tecnologias_requeridas', [])))
                        st.write(f"**Experiencia esperada:** {vacante.get('nivel_experiencia_esperado', 0)} años")
                        st.write(f"**Modalidad:** {vacante.get('modalidad', 'N/A')}")
                        
    with tab_perfil:
        st.subheader(":material/list_alt: Mi Perfil")
        if not st.session_state.get('mostrar_form_skills', False):
            if st.session_state.candidato_skills:
                skills = st.session_state.candidato_skills
                with st.container(border=True):
                    st.info("Tus habilidades actuales registradas en el sistema.")
                    st.markdown(f"**:material/build: Tecnologías:** {', '.join(skills['tecnologias'])}")
                    st.markdown(f"**:material/bar_chart: Años de experiencia:** {skills['anios_experiencia']}")
                    st.markdown(f"**:material/location_on: Modalidad:** {skills['modalidad']}")
                    
                    st.write("")
                    if st.button(":material/edit_document: Actualizar Skills"):
                        st.session_state.mostrar_form_skills = True
                        st.rerun()
            else:
                st.warning(":material/warning: Aún no has registrado tus skills")
                if st.button(":material/edit_document: Registrar Skills"):
                    st.session_state.mostrar_form_skills = True
                    st.rerun()
        else:
            # Formulario para actualizar skills
            st.subheader(":material/edit_document: Registrar / Actualizar mis skills")
            tecnologias = st.text_input("Tecnologías (separadas por coma)", placeholder="Python, AWS, Docker, SQL")
            
            col_exp, col_mod = st.columns(2)
            with col_exp:
                anios = st.number_input("Años de experiencia", min_value=0, max_value=30, value=2)
            with col_mod:
                modalidad = st.selectbox("Modalidad preferida", ["Remoto", "Híbrido", "Presencial"])
                
            st.write("")
            st.write("")
            col_save1, col_save2 = st.columns(2)
            with col_save1:
                if st.button(":material/save: Guardar Skills", use_container_width=True, type="primary"):
                    if tecnologias:
                        skills_list = [t.strip() for t in tecnologias.split(',')]
                        payload = {
                            "tecnologias": skills_list,
                            "anios_experiencia": anios,
                            "modalidad": modalidad,
                            "tipo_empleo": "Full-Time"
                        }
                        res = requests.post(f"{API_URL}/candidatos/perfil", json=payload, headers=headers)
                        if res.status_code == 201:
                            st.session_state._reload_skills = True
                            st.session_state.mostrar_form_skills = False
                            st.success(":material/check_circle: Skills guardadas correctamente")
                            st.rerun()
                        else:
                            st.error(f":material/cancel: Error al guardar: {res.text}")
                    else:
                        st.error(":material/cancel: Ingresa al menos una tecnología")
            
            with col_save2:
                if st.button(":material/cancel: Cancelar", use_container_width=True):
                    st.session_state.mostrar_form_skills = False
                    st.rerun()