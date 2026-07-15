import streamlit as st

def show_home():
    """Muestra la página principal después del splash"""
    
    # Configurar sidebar
    st.sidebar.title("📋 Navegación")
    st.sidebar.markdown("---")
    
    # Opciones
    option = st.sidebar.radio(
        "Selecciona una opción:",
        ["🏠 Inicio", "📊 Subir CV", "📈 Resultados", "⚙️ Configuración"]
    )
    
    # Contenido principal según la opción seleccionada
    if option == "🏠 Inicio":
        st.title("🏠 Panel Principal")
        st.markdown("---")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("📄 CVs Procesados", "0", "0")
        with col2:
            st.metric("🎯 Candidatos Filtrados", "0", "0")
        with col3:
            st.metric("⏱️ Tiempo Promedio", "0s", "0")
        
        st.markdown("---")
        st.subheader("📝 Instrucciones")
        st.info("""
        1. Ve a la sección **Subir CV** para cargar documentos
        2. El sistema analizará automáticamente las hojas de vida
        3. Revisa los resultados en **Resultados**
        4. Ajusta parámetros en **Configuración**
        """)
        
            
    elif option == "📊 Subir CV":
        st.title("📊 Subir Hojas de Vida")
        st.markdown("---")
        
        uploaded_files = st.file_uploader(
            "Selecciona los archivos PDF de las hojas de vida",
            type=['pdf'],
            accept_multiple_files=True
        )
        
        if uploaded_files:
            st.success(f"✅ {len(uploaded_files)} archivo(s) cargado(s) correctamente")
            for file in uploaded_files:
                st.write(f"📎 {file.name}")
            
            if st.button("🔍 Analizar CVs"):
                with st.spinner("Procesando documentos..."):
                    # Aquí iría la lógica de filtrado
                    st.success("¡Análisis completado!")
                    st.balloons()
        else:
            st.info("📌 Arrastra o selecciona archivos PDF para comenzar")
            
    elif option == "📈 Resultados":
        st.title("📈 Resultados del Filtrado")
        st.markdown("---")
        st.info("📊 Aquí se mostrarán los resultados del análisis")
        
        # Tabla de resultados de ejemplo
        data = {
            "Nombre": ["Juan Pérez", "María García", "Carlos López"],
            "Puntuación": [85, 92, 78],
            "Estado": ["Preseleccionado", "Preseleccionado", "Descartado"]
        }
        st.table(data)
        
    else:  # Configuración
        st.title("⚙️ Configuración")
        st.markdown("---")
        
        st.subheader("Parámetros del Modelo")
        col1, col2 = st.columns(2)
        
        with col1:
            threshold = st.slider("Umbral de filtrado", 0.0, 1.0, 0.7, 0.05)
            st.write(f"Umbral actual: **{threshold}**")
        
        with col2:
            max_candidates = st.number_input("Máximo de candidatos", 1, 100, 20)
            st.write(f"Máximo: **{max_candidates}**")
        
        if st.button("💾 Guardar Configuración"):
            st.success("✅ Configuración guardada correctamente")
    
    # Footer
    st.markdown("---")
    st.markdown("*© 2026 - Sistema de Filtrado de Hojas de Vida con IA*")