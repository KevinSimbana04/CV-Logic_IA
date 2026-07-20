import os
import pandas as pd
import pickle
import numpy as np
from sklearn.preprocessing import MultiLabelBinarizer, LabelEncoder
from sklearn.neural_network import MLPClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
from sklearn.model_selection import train_test_split
import matplotlib.pyplot as plt
import seaborn as sns
from schemas import TrainingParams

# Rutas
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
MODELS_DIR = os.path.join(BASE_DIR, "ai_model")
TRANSFORMATION_DIR = os.path.join(MODELS_DIR, "tranformation")

DATASET_PATH = os.path.abspath(os.path.join(BASE_DIR, "..", "ia_training", "data", "data_old", "india_job_market_2024_2026.csv"))

def entrenar_modelo_ia(params: TrainingParams):
    if not os.path.exists(DATASET_PATH):
        raise FileNotFoundError(f"No se encontró el dataset en la ruta esperada: {DATASET_PATH}")
        
    print("Cargando y procesando dataset para la Red Neuronal...")
    df = pd.read_csv(DATASET_PATH)
    
    # Asignacion de variables de necesarias para el modelo
    df_clean = df[['Job_Title', 'Skills_Required', 'Experience_Level', 'Job_Type', 'Work_Mode']].copy()
    
    # Asignar a cada skill a una columna con su representacion binaria
    df_clean['Skills_List'] = df_clean['Skills_Required'].apply(lambda x: [skill.strip() for skill in x.split(',')])
    mlb = MultiLabelBinarizer()
    skills_encoded = mlb.fit_transform(df_clean['Skills_List'])
    df_skills = pd.DataFrame(skills_encoded, columns=mlb.classes_)
    
    # Categoriar opciones de acuerdo a las opciones
    df_categorical = pd.get_dummies(df_clean[['Experience_Level', 'Job_Type', 'Work_Mode']], dtype=int)
    columnas_categoricas = list(df_categorical.columns)
    
    # Unficacion de datos skill, datos administrativos
    X = pd.concat([df_skills, df_categorical], axis=1)
    
    # Tranformacion a datos categoricos Job_Title
    le = LabelEncoder()
    y = le.fit_transform(df_clean['Job_Title'])
    
    # Parsear hidden_layers (ej: "128,64" -> (128, 64))
    try:
        layers = tuple(int(x.strip()) for x in params.hidden_layers.split(','))
    except Exception:
        layers = (128, 64)
        
    print(f"Entrenando Perceptrón Multicapa (MLP) con capas {layers}...")
    modelo_nn = MLPClassifier(
        hidden_layer_sizes=layers,
        activation=params.activation,
        solver='adam',
        max_iter=params.max_iter,
        random_state=42
    )
    
    # Separar datos en entrenamiento (80%) y prueba (20%)
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    
    # Entrenar solo con datos de entrenamiento
    modelo_nn.fit(X_train, y_train)
    
    # Evaluar con datos de prueba (datos nunca antes vistos)
    y_pred = modelo_nn.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    precision = precision_score(y_test, y_pred, average='weighted', zero_division=0)
    recall = recall_score(y_test, y_pred, average='weighted', zero_division=0)
    f1 = f1_score(y_test, y_pred, average='weighted', zero_division=0)
    
    print(f"Red entrenada. Precisión interna alcanzada: {accuracy * 100:.2f}%")
    
    # Guardar el modelo de red neuronal
    os.makedirs(MODELS_DIR, exist_ok=True)
    os.makedirs(TRANSFORMATION_DIR, exist_ok=True)
    
    # --- Generar y Guardar Matriz de Confusión ---
    cm = confusion_matrix(y_test, y_pred)
    plt.figure(figsize=(14, 12))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                xticklabels=le.classes_, yticklabels=le.classes_)
    plt.title('Matriz de Confusión del Modelo')
    plt.ylabel('Etiqueta Verdadera')
    plt.xlabel('Predicción de la IA')
    plt.xticks(rotation=90, fontsize=8)
    plt.yticks(rotation=0, fontsize=8)
    
    # Guardar en MODELS_DIR
    cm_path = os.path.join(MODELS_DIR, 'confusion_matrix.png')
    plt.savefig(cm_path, bbox_inches='tight', dpi=100)
    plt.close()
    
    with open(os.path.join(MODELS_DIR, 'modelo_nn.pkl'), 'wb') as file:
        pickle.dump(modelo_nn, file)
        
    # Guardar el lista de categorias
    with open(os.path.join(TRANSFORMATION_DIR, 'lista_categorias.pkl'), 'wb') as file:
        pickle.dump(le, file)
        
    # Guardar la lista de columnas categoricas
    with open(os.path.join(TRANSFORMATION_DIR, 'columnas_datos.pkl'), 'wb') as file:
        pickle.dump(columnas_categoricas, file)
        
        
    from services.ai_service import cargar_modelos
    import services.ai_service as ai_module
    ai_module._modelo_nn = None
    ai_module._label_encoder = None
    ai_module._feature_names = None
    cargar_modelos()
        
    metrics_data = {
        "mensaje": "Modelo entrenado y guardado correctamente.",
        "accuracy": float(accuracy),
        "precision": float(precision),
        "recall": float(recall),
        "f1_score": float(f1),
        "has_confusion_matrix": True
    }
    
    # Guardar métricas del último entrenamiento
    import json
    with open(os.path.join(MODELS_DIR, 'last_metrics.json'), 'w') as file:
        json.dump(metrics_data, file)
        
    return metrics_data
