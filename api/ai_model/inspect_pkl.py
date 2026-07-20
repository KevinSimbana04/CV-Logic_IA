import joblib
import pandas as pd
import sklearn
import os

def inspect_models():
    print("scikit-learn version:", sklearn.__version__)
    
    try:
        lista_categorias = joblib.load(os.path.join("tranformation", "lista_categorias.pkl"))
        print("\n=== Lista Categorias ===")
        if hasattr(lista_categorias, "classes_"):
            print("Classes:", lista_categorias.classes_)
        else:
            print("Type:", type(lista_categorias))
    except Exception as e:
        print("Error loading lista_categorias:", e)
        
    try:
        columnas_categoricas = joblib.load(os.path.join("tranformation", "columnas_categoricas.pkl"))
        print("\n=== Columnas Categoricas ===")
        print("Type:", type(columnas_categoricas))
        if isinstance(columnas_categoricas, list) or isinstance(columnas_categoricas, tuple):
            print("Length:", len(columnas_categoricas))
            print("First 10 items:", columnas_categoricas[:10])
        else:
            print("Value:", columnas_categoricas)
    except Exception as e:
        print("Error loading columnas_categoricas:", e)
        
    try:
        columnas_datos = joblib.load(os.path.join("tranformation", "columnas_datos.pkl"))
        print("\n=== Columnas Datos ===")
        print("Type:", type(columnas_datos))
        if isinstance(columnas_datos, list) or isinstance(columnas_datos, tuple):
            print("Length:", len(columnas_datos))
            print("First 10 items:", columnas_datos[:10])
        else:
            print("Value:", columnas_datos)
    except Exception as e:
        print("Error loading columnas_datos:", e)
        
    try:
        modelo_nn = joblib.load("modelo_nn.pkl")
        print("\n=== Modelo NN ===")
        print("Model Type:", type(modelo_nn))
        if hasattr(modelo_nn, "n_features_in_"):
            print("n_features_in_:", modelo_nn.n_features_in_)
        if hasattr(modelo_nn, "feature_names_in_"):
            print("feature_names_in_ (first 10):", modelo_nn.feature_names_in_[:10])
    except Exception as e:
        print("Error loading modelo_nn:", e)

if __name__ == "__main__":
    inspect_models()
