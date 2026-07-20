import streamlit as st

def init_session_state():
    """Inicializa las variables de sesión"""
    if 'autenticado' not in st.session_state:
        st.session_state.autenticado = False
    if 'usuario' not in st.session_state:
        st.session_state.usuario = None
    if 'rol' not in st.session_state:
        st.session_state.rol = None
    if 'pagina_actual' not in st.session_state:
        st.session_state.pagina_actual = 'login'
    if 'splash_shown' not in st.session_state:
        st.session_state.splash_shown = False
    
    # USUARIOS PRE-DEFINIDOS
    if 'usuarios' not in st.session_state:
        st.session_state.usuarios = {
            'candidato@test.com': {
                'password': '123456',
                'rol': 'candidato',
                'nombre': 'Juan Pérez'
            },
            'empresa@test.com': {
                'password': '123456',
                'rol': 'empresa',
                'nombre': 'Tech Solutions S.A.'
            }
        }
    
    # Datos de vacantes
    if 'vacantes' not in st.session_state:
        st.session_state.vacantes = [
            {
                'id': 1,
                'titulo': 'Desarrollador Python Senior',
                'empresa': 'Tech Solutions S.A.',
                'tecnologias': ['Python', 'FastAPI', 'SQL', 'Streamlit', 'Docker', 'React', 'AWS'],
                'nivel_experiencia': 4,
                'modalidad': 'Remoto'
            },
            {
                'id': 2,
                'titulo': 'Arquitecto Cloud',
                'empresa': 'Cloud Innovations',
                'tecnologias': ['AWS', 'Docker', 'Kubernetes', 'Python', 'Terraform', 'Azure'],
                'nivel_experiencia': 5,
                'modalidad': 'Híbrido'
            }
        ]
    
    # Postulaciones del candidato
    if 'mis_postulaciones' not in st.session_state:
        st.session_state.mis_postulaciones = []
    
    # Skills del candidato
    if 'candidato_skills' not in st.session_state:
        st.session_state.candidato_skills = None
    
    # Variables para formularios
    if 'mostrar_form_skills' not in st.session_state:
        st.session_state.mostrar_form_skills = False
    if 'mostrar_match' not in st.session_state:
        st.session_state.mostrar_match = False
    if 'mostrar_form_postulacion' not in st.session_state:
        st.session_state.mostrar_form_postulacion = False
    if 'mostrar_form_vacante' not in st.session_state:
        st.session_state.mostrar_form_vacante = False
    if 'vacante_postular' not in st.session_state:
        st.session_state.vacante_postular = None

def calcular_match(vacante, skills_candidato):
    """Calcula el porcentaje de match entre una vacante y las skills del candidato"""
    if not skills_candidato:
        return 0
    
    tecnologias_match = set(vacante['tecnologias']) & set(skills_candidato['tecnologias'])
    porcentaje_tecnologias = len(tecnologias_match) / len(vacante['tecnologias']) * 100
    
    experiencia_candidato = skills_candidato['anios_experiencia']
    experiencia_requerida = vacante['nivel_experiencia']
    
    if experiencia_candidato >= experiencia_requerida:
        match_experiencia = 100
    else:
        match_experiencia = (experiencia_candidato / experiencia_requerida) * 100
    
    match_modalidad = 100 if skills_candidato['modalidad'] == vacante['modalidad'] else 50
    
    match_total = (porcentaje_tecnologias * 0.6) + (match_experiencia * 0.3) + (match_modalidad * 0.1)
    
    return round(match_total, 1)