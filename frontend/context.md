# 📋 DOCUMENTACIÓN DEL PROYECTO - SISTEMA DE FILTRADO DE CVs

## 🎯 VISIÓN GENERAL

Este proyecto es un **Sistema de Filtrado de Hojas de Vida (CVs)** desarrollado con **Streamlit**. Permite a dos tipos de usuarios (candidatos y empresas) interactuar en un entorno de reclutamiento:

- **Candidatos**: Pueden registrar sus habilidades, buscar vacantes y postularse.
- **Empresas**: Pueden crear vacantes, visualizar postulantes y calcular el match de habilidades.

---

## 📁 ESTRUCTURA DEL CÓDIGO

```
📂 Proyecto
├── 📄 app.py                    # Punto de entrada principal
├── 📄 splash.py                 # Pantalla de bienvenida animada
├── 📄 requirements.txt          # Dependencias del proyecto
├── 📂 pages/
│   ├── 📄 login.py              # Autenticación de usuarios
│   ├── 📄 registro.py           # Registro de nuevos usuarios
│   ├── 📄 dashboard_candidato.py # Panel del candidato
│   └── 📄 dashboard_empresa.py  # Panel de la empresa
├── 📂 utils/
│   └── 📄 data.py               # Manejo de datos y estado global
└── 📂 .streamlit/
    └── 📄 config.toml           # Configuración de Streamlit
```

---

## 📄 app.py - PUNTO DE ENTRADA PRINCIPAL

**FUNCIONALIDAD:** Orquesta toda la aplicación, manejando el flujo de navegación y la interfaz.

### 🔧 Configuración Inicial
```python
st.set_page_config(
    page_title="Sistema de Filtrado de CVs",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="collapsed"
)
```
- Configura el título, ícono y diseño de la página.
- Oculta la barra lateral por defecto para una experiencia más limpia.

### 🚀 Gestión de Estado
```python
init_session_state()
```
- Inicializa todas las variables de sesión necesarias para el funcionamiento de la app.

### 🎨 Estilos CSS Personalizados
- Oculta elementos nativos de Streamlit (menú, footer, header, sidebar).
- Define estilos para:
  - **Splash screen**: Animaciones de fade-in, loading bar, gradientes.
  - **Tarjetas de vacantes**: Bordes, sombras, efectos hover.
  - **Etiquetas de habilidades**: Badges con colores y animaciones.

### 🖥️ Lógica de Navegación
```python
if not st.session_state.get('splash_shown', False):
    # Mostrar splash screen con animación
    # ... código del splash ...
else:
    # Navegación según autenticación y rol
```

**Flujo:**
1. **Splash Screen** → Se muestra al cargar la app.
2. **Login/Registro** → Si el usuario no está autenticado.
3. **Dashboard** → Según el rol del usuario (candidato o empresa).

---

## 📄 splash.py - PANTALLA DE BIENVENIDA

**FUNCIONALIDAD:** Muestra una pantalla de bienvenida atractiva con animaciones antes de que el usuario acceda a la aplicación.

### 🎭 Componentes Principales

#### `show_splash()` - Función principal
```python
def show_splash():
    """Muestra la pantalla de inicio con animación"""
```

**Características:**
- **Fondo gradiente**: Degradado de azul a morado.
- **Logo/Emoji**: Muestra un logo si existe en `assets/logo.png`, o un emoji 📄 por defecto.
- **Animaciones CSS**: 
  - `fadeIn`: Texto aparece con desvanecimiento.
  - `slideIn`: Barra de carga aparece deslizándose.
  - `loading`: Barra de progreso animada.
- **Botón "Comenzar"**: Permite al usuario avanzar manualmente.
- **Auto-redirección**: Después de 3 segundos, redirige automáticamente.

**Uso de `st.rerun()`:** Refresca la página para actualizar el estado.

---

## 📄 utils/data.py - GESTIÓN DE DATOS Y ESTADO

**FUNCIONALIDAD:** Maneja el estado global de la aplicación y proporciona utilidades para cálculos de match.

### 🔄 `init_session_state()` - Inicialización de Estado

```python
def init_session_state():
    """Inicializa las variables de sesión"""
```

**Variables de sesión:**

| Variable | Tipo | Propósito |
|----------|------|-----------|
| `autenticado` | bool | Indica si el usuario ha iniciado sesión |
| `usuario` | str | Nombre del usuario autenticado |
| `rol` | str | Rol del usuario ('candidato' o 'empresa') |
| `pagina_actual` | str | Página actual ('login' o 'registro') |
| `splash_shown` | bool | Controla si se ha mostrado el splash screen |
| `usuarios` | dict | Base de datos de usuarios (pre-definidos) |
| `vacantes` | list | Lista de ofertas de trabajo |
| `mis_postulaciones` | list | Postulaciones del candidato |
| `candidato_skills` | dict | Habilidades registradas por el candidato |
| `mostrar_form_*` | bool | Controla visibilidad de formularios |

### 👥 Usuarios Pre-definidos
```python
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
```

### 📊 `calcular_match()` - Algoritmo de Coincidencia

```python
def calcular_match(vacante, skills_candidato):
    """Calcula el porcentaje de match entre una vacante y las skills del candidato"""
```

**Fórmula de cálculo:**

1. **Match Tecnológico (60% peso):**
   ```python
   tecnologias_match = set(vacante['tecnologias']) & set(skills_candidato['tecnologias'])
   porcentaje_tecnologias = len(tecnologias_match) / len(vacante['tecnologias']) * 100
   ```

2. **Match Experiencia (30% peso):**
   - Si experiencia candidato >= requerida → 100%
   - Si no → `(exp_candidato / exp_requerida) * 100`

3. **Match Modalidad (10% peso):**
   - Si coincide → 100%
   - Si no → 50%

```python
match_total = (porcentaje_tecnologias * 0.6) + (match_experiencia * 0.3) + (match_modalidad * 0.1)
return round(match_total, 1)
```

---

## 📄 pages/login.py - AUTENTICACIÓN

**FUNCIONALIDAD:** Permite a los usuarios iniciar sesión en el sistema.

### 🖥️ `show_login()` - Página de Login

**Interfaz:**
- Muestra los usuarios disponibles con sus credenciales.
- Campos para email, contraseña y selección de rol.
- Botones de "Iniciar Sesión" y "Registrarse".

**Lógica de Autenticación:**
1. Verifica que los campos no estén vacíos.
2. Busca el email en `st.session_state.usuarios`.
3. Valida la contraseña.
4. Verifica que el rol seleccionado coincida con el rol del usuario.
5. Si todo es correcto:
   ```python
   st.session_state.autenticado = True
   st.session_state.usuario = user_data['nombre']
   st.session_state.rol = rol
   st.rerun()
   ```

---

## 📄 pages/registro.py - REGISTRO DE USUARIOS

**FUNCIONALIDAD:** Permite crear nuevas cuentas de usuario.

### 🖥️ `show_registro()` - Página de Registro

**Campos del formulario:**
- Nombre completo
- Correo electrónico
- Contraseña (mínimo 6 caracteres)
- Confirmación de contraseña
- Tipo de usuario (candidato/empresa)

**Validaciones:**
```python
if password != confirm_password:
    st.error("❌ Las contraseñas no coinciden")
elif len(password) < 6:
    st.error("❌ La contraseña debe tener al menos 6 caracteres")
elif email in st.session_state.usuarios:
    st.error("❌ Este correo ya está registrado")
```

**Registro exitoso:**
```python
st.session_state.usuarios[email] = {
    'password': password,
    'rol': rol,
    'nombre': nombre
}
st.session_state.pagina_actual = 'login'
st.rerun()
```

---

## 📄 pages/dashboard_candidato.py - PANEL DEL CANDIDATO

**FUNCIONALIDAD:** Interfaz para que los candidatos gestionen su perfil y postulaciones.

### 🖥️ `show_dashboard_candidato()` - Dashboard del Candidato

#### 🔧 Sección: "Mi Perfil"
- Muestra las habilidades registradas del candidato.
- Botón "Buscar Match" para calcular coincidencias.
- Formulario para registrar/actualizar skills:
  ```python
  skills = {
      'tecnologias': ['Python', 'AWS', 'Docker'],
      'anios_experiencia': 2,
      'modalidad': 'Remoto'
  }
  ```

#### 💼 Sección: "Vacantes Disponibles"
- Muestra todas las vacantes a las que el candidato NO ha postulado.
- **Filtrado de vacantes:**
  ```python
  ya_postulo = any(p['vacante_id'] == vacante['id'] 
                   for p in st.session_state.mis_postulaciones)
  if not ya_postulo:
      vacantes_filtradas.append(vacante)
  ```
- Tarjetas de vacantes con información:
  - Título, empresa, experiencia requerida, modalidad.
  - Tecnologías requeridas (formateadas como texto).
  - Botón "Postular".

#### 📝 Formulario de Postulación
- El candidato ingresa sus skills específicas para la vacante.
- La postulación se guarda en `st.session_state.mis_postulaciones`.

#### 📋 Sección: "Mis Postulaciones"
- Lista todas las postulaciones realizadas.
- Muestra detalles: fecha, tecnologías, experiencia, modalidad.

---

## 📄 pages/dashboard_empresa.py - PANEL DE LA EMPRESA

**FUNCIONALIDAD:** Interfaz para que las empresas gestionen vacantes y postulantes.

### 🖥️ `show_dashboard_empresa()` - Dashboard de la Empresa

**Estructura de navegación:**
- Vista principal: Lista de vacantes.
- Vista detalle: Información de una vacante específica con sus postulantes.

### 🔍 `mostrar_lista_principal()` - Lista de Vacantes

**Formulario de creación:**
```python
nueva_vacante = {
    'id': len(st.session_state.vacantes) + 1,
    'titulo': titulo,
    'empresa': st.session_state.usuario,
    'tecnologias': tech_list,
    'nivel_experiencia': experiencia,
    'modalidad': modalidad,
    'postulaciones': []
}
```

**Tarjetas de vacantes:**
- Cada vacante se muestra como una tarjeta cliqueable.
- Al hacer clic, se navega a la vista detalle.

### 📊 `mostrar_detalle_vacante()` - Detalle de Vacante

**Muestra:**
1. **Información de la oferta**: Modalidad, experiencia, tecnologías.
2. **Candidatos postulados**: Lista de todos los postulantes.
3. **Herramientas de análisis:**
   - "Comparar Postulaciones (Top 5)": Muestra los mejores candidatos.
   - "Métricas de la Vacante": Postulantes totales y promedio de match.

#### 🏆 Función: `calcular_match_interno()`
```python
def calcular_match_interno(vacante, skills_candidato):
    """Calcula match basado en tecnologías (70%) y experiencia (30%)"""
    # 70% peso a tecnologías
    # 30% peso a experiencia
    return round((score_tech * 0.7) + (score_exp * 0.3))
```

**Visualización de postulantes:**
- Para cada candidato muestra:
  - Experiencia, modalidad, tecnologías.
  - **Score de match** con color indicativo:
    - 🟢 ≥ 70%: Match Recomendado
    - 🟡 ≥ 50%: Perfil Intermedio
    - 🔴 < 50%: Match Insuficiente

---

## 📄 .streamlit/config.toml - CONFIGURACIÓN

**FUNCIONALIDAD:** Configuraciones globales de Streamlit.

```toml
[theme]
primaryColor = "#667eea"        # Color principal (morado)
backgroundColor = "#f8f9fa"     # Fondo claro
secondaryBackgroundColor = "#ffffff"
textColor = "#333333"
font = "sans serif"

[server]
maxUploadSize = 10              # Límite de carga: 10MB
enableXsrfProtection = true
enableCORS = false

[browser]
gatherUsageStats = false        # Desactiva estadísticas de uso
```

---

## 🔄 FLUJO DE TRABAJO COMPLETO

### 🚶 Candidato:
1. **Registro/Login** → Accede al sistema.
2. **Registrar Skills** → Define sus habilidades.
3. **Ver Vacantes** → Explora ofertas disponibles.
4. **Postular** → Aplica a vacantes de interés.
5. **Ver Postulaciones** → Monitorea sus aplicaciones.

### 🏢 Empresa:
1. **Registro/Login** → Accede al sistema.
2. **Crear Vacante** → Publica nuevas ofertas.
3. **Ver Postulantes** → Visualiza candidatos aplicados.
4. **Analizar Match** → Calcula compatibilidad automáticamente.
5. **Top 5** → Identifica mejores candidatos.
6. **Métricas** → Estadísticas de la vacante.

---

## 📊 VARIABLES DE ESTADO IMPORTANTES

| Variable | Propósito |
|----------|-----------|
| `st.session_state.autenticado` | Control de autenticación |
| `st.session_state.usuario` | Nombre del usuario actual |
| `st.session_state.rol` | Rol actual ('candidato'/'empresa') |
| `st.session_state.vacantes` | Lista global de vacantes |
| `st.session_state.mis_postulaciones` | Postulaciones del candidato |
| `st.session_state.candidato_skills` | Skills del candidato |
| `st.session_state.mostrar_form_*` | Control de visibilidad de formularios |
| `st.session_state.vacante_seleccionada` | ID de vacante en vista detalle |

---

## 🛠️ FUNCIONES CLAVE

### `calcular_match(vacante, skills_candidato)`
- **Ubicación:** `utils/data.py`
- **Propósito:** Calcula match global (candidato vs vacante).
- **Pesos:** Tecnologías 60%, Experiencia 30%, Modalidad 10%.

### `calcular_match_interno(vacante, skills_candidato)`
- **Ubicación:** `dashboard_empresa.py`
- **Propósito:** Cálculo simplificado para empresas.
- **Pesos:** Tecnologías 70%, Experiencia 30%.

### `init_session_state()`
- **Ubicación:** `utils/data.py`
- **Propósito:** Inicializa todas las variables de sesión.

---

## 🎨 ESTILOS Y UI

- **Tarjetas con borde lateral** (morado) para vacantes.
- **Badges de skills** con efecto hover.
- **Gradientes** en splash screen.
- **Animaciones CSS** para mejorar experiencia de usuario.
- **Diseño responsive** con columnas de Streamlit.

---

## 📦 DEPENDENCIAS (requirements.txt)

```txt
streamlit==1.28.1    # Framework principal
Pillow==10.1.0       # Manejo de imágenes
pandas==2.1.1        # Manipulación de datos
numpy==1.24.3        # Cálculos numéricos
```

---

## ✅ CONCLUSIÓN

El sistema implementa un **flujo completo de reclutamiento** con:

- **Autenticación** de usuarios (dos roles).
- **Gestión de perfiles** (skills, experiencia, modalidad).
- **Publicación de vacantes** por empresas.
- **Postulación** por candidatos.
- **Cálculo automático de match** con diferentes ponderaciones.
- **Análisis de postulantes** (Top 5, métricas).
- **Interfaz intuitiva** con animaciones y diseño moderno.

El código está estructurado de forma modular, con separación clara entre lógica de datos, autenticación y dashboards específicos por rol.