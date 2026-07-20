import joblib
import pandas as pd
import numpy as np
import os

# Rutas a los modelos
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MODELS_DIR = os.path.join(BASE_DIR, "ai_model")
TRANSFORMATION_DIR = os.path.join(MODELS_DIR, "tranformation")

# Variables globales para cachear los modelos en memoria
_modelo_nn = None
_label_encoder = None
_feature_names = None

def cargar_modelos():
    global _modelo_nn, _label_encoder, _feature_names
    if _modelo_nn is None:
        try:
            _modelo_nn = joblib.load(os.path.join(MODELS_DIR, "modelo_nn.pkl"))
            _label_encoder = joblib.load(os.path.join(TRANSFORMATION_DIR, "lista_categorias.pkl"))
            _feature_names = _modelo_nn.feature_names_in_
            print("Modelos de IA cargados correctamente.")
        except Exception as e:
            print(f"Error al cargar modelos de IA: {e}")

def mapear_experiencia(anios: int) -> str:
    if anios <= 1:
        return 'Experience_Level_Fresher (0-1 yr)'
    elif anios <= 3:
        return 'Experience_Level_Junior (1-3 yrs)'
    elif anios <= 6:
        return 'Experience_Level_Mid (3-6 yrs)'
    elif anios <= 10:
        return 'Experience_Level_Senior (6-10 yrs)'
    else:
        return 'Experience_Level_Lead (10+ yrs)'

def mapear_modalidad(modalidad: str) -> str:
    mod = modalidad.lower()
    if mod == "remoto":
        return 'Work_Mode_Remote'
    elif mod == "presencial":
        return 'Work_Mode_On-site'
    else:
        return 'Work_Mode_Hybrid'

def mapear_tipo_empleo(tipo: str) -> str:
    tipo_lower = tipo.lower()
    if tipo_lower == "medio tiempo":
        return 'Job_Type_Part-Time'
    elif tipo_lower == "contrato":
        return 'Job_Type_Contract'
    else:
        return 'Job_Type_Full-Time'

def evaluar_candidatos_para_vacante(candidatos, titulo_vacante: str):
    cargar_modelos()
    
    if _modelo_nn is None:
        raise RuntimeError("Los modelos de IA no están disponibles.")

    if not candidatos:
        return []

    # Verificar si el titulo de la vacante existe en las clases del modelo
    try:
       
        clases = list(_label_encoder.classes_)
        titulo_lower = titulo_vacante.lower().strip()
        clase_idx = -1
        for i, c in enumerate(clases):
            if c.lower().strip() == titulo_lower:
                clase_idx = i
                break
        
        if clase_idx == -1:
            print(f"Advertencia: El rol '{titulo_vacante}' no está en las clases de la IA.")
    except Exception as e:
        print(f"Error buscando clase: {e}")
        clase_idx = -1

    # Preparar el DataFrame para todos los candidatos
    data_rows = []
    
    for candidato in candidatos:
        perfil = candidato.perfil
        if not perfil:
            continue
            
        input_data = {col: 0 for col in _feature_names}

        if isinstance(perfil.tecnologias, list):
            for tech in perfil.tecnologias:
                if tech in input_data:
                    input_data[tech] = 1
                
        # Mapear Categorías
        exp_col = mapear_experiencia(perfil.anios_experiencia)
        if exp_col in input_data:
            input_data[exp_col] = 1
            
        mod_col = mapear_modalidad(perfil.modalidad)
        if mod_col in input_data:
            input_data[mod_col] = 1
            
        tipo_col = mapear_tipo_empleo(perfil.tipo_empleo)
        if tipo_col in input_data:
            input_data[tipo_col] = 1
            
        data_rows.append((candidato, input_data))

    if not data_rows:
        return []

    df = pd.DataFrame([row[1] for row in data_rows])
    
    probabilidades_matriz = _modelo_nn.predict_proba(df)
    
    resultados = []
    for i, (candidato, _) in enumerate(data_rows):
        probs = probabilidades_matriz[i]
        
        if clase_idx != -1:
            confianza_vacante = float(probs[clase_idx])
        else:
            confianza_vacante = float(np.max(probs))
            
        # Determinar qué rol cree la IA que realmente es este candidato
        indice_max = np.argmax(probs)
        confianza_sugerida = float(probs[indice_max])
        rol_sugerido = _label_encoder.inverse_transform([indice_max])[0]
            
        resultados.append({
            "candidato": candidato,
            "confianza_vacante": confianza_vacante,
            "rol_sugerido": rol_sugerido,
            "confianza_sugerida": confianza_sugerida
        })
        
    # Ordenar por el match de la vacante, para que los relevantes salgan primero
    resultados.sort(key=lambda x: x["confianza_vacante"], reverse=True)
    
    # Asignar Top 3 y limpiar rol sugerido para ellos
    for idx, res in enumerate(resultados):
        if idx < 3:
            res["es_top_3"] = True
            res["rol_sugerido"] = None
            res["confianza_sugerida"] = None
        else:
            res["es_top_3"] = False
            
    return resultados
