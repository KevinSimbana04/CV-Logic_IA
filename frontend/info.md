
## Características Principales

* **Autenticación Basada en Roles**: Vistas y permisos adaptados para *Candidatos* y *Empresas*.
* **Panel de Candidatos**: Registro de *skills*, visualización de ofertas, postulación con un clic y seguimiento.
* **Panel de Reclutadores**: Creación de vacantes, gestión de candidatos y un Top 5 automático de postulantes con mayor compatibilidad.
* **UI/UX Interactiva**: Tarjetas estilizadas con CSS, barras de carga animadas y etiquetas (*pills*) interactivas.

---

## Arquitectura del Sistema

```
┌─────────────────────────────────────────────────────┐
│                      FRONTEND                       │
│  ┌─────────────┐  ┌─────────────┐  ┌───────────┐    │
│  │   Splash    │  │   Login/    │  │ Dashboards│    │
│  │   Screen    │  │  Registro   │  │ (2 roles) │    │
│  └─────────────┘  └─────────────┘  └───────────┘    │
└─────────────────────────────────────────────────────┘
                           │
┌─────────────────────────────────────────────────────┐
│                 ESTADO DE SESIÓN                    │
│  ┌──────────────────────────────────────────────┐   │
│  │           Session State de Streamlit         │   │
│  │ (Usuarios, Vacantes, Postulaciones, Skills)  │   │
│  └──────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────┘

```

---

## Stack Tecnológico

| Componente | Tecnología | Descripción |
| --- | --- | --- |
| **Lenguaje** | Python 3.8+ | Lenguaje base |
| **Frontend / UI** | Streamlit 1.28.1 | Framework web interactivo |
| **Procesamiento de Datos** | Pandas & NumPy | Análisis de datos y operaciones matriciales |
| **Imágenes** | Pillow 10.1.0 | Manejo de assets gráficos |
| **Estilos** | CSS3 / HTML5 | Inyección de estilos custom para potenciar la UI |

---

## Estructura del Proyecto

```bash

frontend/
│
├── app.py                          # Punto de entrada
├── splash.py                       # Pantalla de bienvenida
├── requirements.txt                # Dependencias
│
├── .streamlit/                     # Configuración
│   └── config.toml
│
├── assets/                         # Recursos estáticos
│   └── logo.png
│
├── pages/                          # Módulos de páginas
│   ├── __init__.py
│   ├── login.py                    # Autenticación
│   ├── registro.py                 # Registro
│   ├── dashboard_candidato.py      # Panel candidato
│   └── dashboard_empresa.py        # Panel empresa
│
└── utils/                          # Utilidades
    ├── __init__.py
    └── data.py                     # Gestión de datos

```

---


## Modelo de Datos

Las estructuras primarias utilizadas dentro de la sesión son:

```python
# Usuario
{
    'email': 'candidato@test.com',
    'password': 'hash_password',
    'rol': 'candidato', # 'candidato' | 'empresa'
    'nombre': 'John Doe'
}

# Vacante
{
    'id': 101,
    'titulo': 'Senior Backend Developer',
    'empresa': 'TechCorp',
    'tecnologias': ['Python', 'SQL', 'Docker'],
    'nivel_experiencia': 3,
    'modalidad': 'Remoto',
    'postulaciones': [...]
}

```

---

## Instalación y Configuración

Sigue estos pasos para clonar y ejecutar el proyecto de forma local:

### 1. Clonar el repositorio

```bash
git clone https://github.com/KevinSimbana04/CV-Logic_IA.git
cd CV-Logic_IA

```

### 2. Instalar dependencias

```bash
pip install -r requirements.txt

```

### 3. Iniciar la aplicación

```bash
streamlit run app.py

```

La aplicación se abrirá automáticamente en tu navegador predeterminado en `http://localhost:8501`.

---

## Uso y Credenciales Demo

Para probar rápidamente la plataforma sin registrarte, puedes utilizar las siguientes credenciales de prueba:

| Rol | Correo Electrónico | Contraseña |
| --- | --- | --- |
| **Candidato** | `candidato@test.com` | `123456` |
| **Empresa** | `empresa@test.com` | `123456` |

