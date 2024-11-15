import streamlit as st
from PIL import Image

# Encabezado en dos columnas con foto y descripción
header_col1, header_col2 = st.columns([1, 3], gap="medium")

with header_col1:
    st.image("assets/profile2.png", width=150)

with header_col2:
    # Título y presentación
    st.title("Gabriel Barrientos")
    st.write("""
        ¡Hola! Soy un **Data Scientist** en formación con experiencia en desarrollo de modelos de Machine Learning, 
        ciencia de datos y desarrollo web en Django. Me apasiona el aprendizaje continuo y la aplicación de modelos 
        avanzados para resolver problemas complejos.
    """)

    # Información académica
    st.subheader("Formación Académica")
    st.write("""
        - **Universidad Nacional de Ingeniería**  
          Ciencias de la Computación (8º ciclo)
        - **Especialización en Ciencia de Datos**  
          Cibertec
    """)

    # Información de contacto
    st.subheader("Contacto")
    st.write("📫 Puedes contactarme a través de mi perfil de LinkedIn o por correo: gabriel.barrientos.c@uni.pe.")
    
    # Botón de LinkedIn con logo
    linkedin_url = "https://www.linkedin.com/in/gabrielbarrientoscardenas/"
    if st.button("Visita mi LinkedIn"):
        st.markdown(f"[LinkedIn]({linkedin_url})", unsafe_allow_html=True)


# Separador elegante
st.markdown("---")

