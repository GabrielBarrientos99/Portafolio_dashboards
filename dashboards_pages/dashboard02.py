import streamlit as st
import pandas as pd
import plotly.express as px
import os
from PIL import Image


# Cargar el dataset
@st.cache_data
def load_port_data():
    data = pd.read_csv("./dashboards_pages/data/Port_Data_pre.csv")
    data['Vessels in Port'] = data['Vessels in Port'].fillna(0).astype(int)
    data['Departures(Last 24 Hours)'] = data['Departures(Last 24 Hours)'].fillna(0).astype(int)
    data['Arrivals(Last 24 Hours)'] = data['Arrivals(Last 24 Hours)'].fillna(0).astype(int)
    data['Expected Arrivals'] = data['Expected Arrivals'].fillna(0).astype(int)
    return data

# Funciones de estilo
def apply_country_style(row, top_countries):
    style = [""] * len(row)
    if row['Country'] in top_countries:
        index = top_countries.index(row['Country'])
        colors = ["#6a0dad", "#9b59b6", "#d2b4de"]  # Tonos de morado desde oscuro a claro
        style = [f"background-color: {colors[index]}; color: white; font-weight: bold;"] * len(row)
    return style

def apply_port_type_style(row, top_types):
    style = [""] * len(row)
    if row['Type'] in top_types:
        index = top_types.index(row['Type'])
        colors = ["#ff5733", "#ffa474", "#ffd2a0"]  # Tonos cálidos en degradado de naranja
        style = [f"background-color: {colors[index]}; color: white; font-weight: bold;"] * len(row)
    return style

def apply_total_expected_arrivals_style(row, top_ports):
    """Estilo para los puertos con mayor total de llegadas potenciales (arribos actuales + llegadas esperadas)."""
    style = [""] * len(row)
    if row['Port Name'] in top_ports:
        style = ["background-color: #4caf50; color: white; font-weight: bold;"] * len(row)  # Verde intenso
    return style



# Cargar datos de puertos
port_data = load_port_data()

# Título
st.markdown("<h1 style='text-align: center; color: #003366;'>Dashboard de Análisis de Puertos</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>Explora el rendimiento y las características de los puertos de todo el mundo.</p>", unsafe_allow_html=True)

# --- Filtros en la barra lateral ---
st.sidebar.header("Filtros")

# Filtro por tipo de puerto (independiente)
type_options = sorted(port_data['Type'].unique())
selected_types = st.sidebar.multiselect("Seleccione Tipo(s) de Puerto", options=type_options, default=type_options)

# Filtro de selección múltiple por país
selected_countries = st.sidebar.multiselect("Seleccione País(es)", sorted(port_data['Country'].unique()), default=[])

# Filtrar datos en base a selección de países
if selected_countries:
    filtered_data_country = port_data[port_data['Country'].isin(selected_countries) & port_data['Type'].isin(selected_types)]
else:
    filtered_data_country = port_data

# Opciones de Área Global basadas en la selección de países
area_global_options = sorted(filtered_data_country['Area Global'].unique())
selected_global_areas = st.sidebar.multiselect("Seleccione Área Global", options=area_global_options, default=[])

# Filtrar datos en base a selección de área global
if selected_global_areas:
    filtered_data_area_global = filtered_data_country[filtered_data_country['Area Global'].isin(selected_global_areas)]
else:
    filtered_data_area_global = filtered_data_country

# Opciones de Área Local basadas en la selección de área global
area_local_options = sorted(filtered_data_area_global['Area Local'].unique())
selected_local_areas = st.sidebar.multiselect("Seleccione Área Local", options=area_local_options, default=[])

# Filtrar datos en base a selección de área local
if selected_local_areas:
    filtered_data_area_local = filtered_data_area_global[filtered_data_area_global['Area Local'].isin(selected_local_areas)]
else:
    filtered_data_area_local = filtered_data_area_global



# Aplicar todos los filtros
filtered_data = filtered_data_area_local[filtered_data_area_local['Type'].isin(selected_types)]

# --- Métricas Generales ---
st.subheader("Métricas Generales")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Puertos Totales", len(filtered_data['Port Name'].unique()))
col2.metric("Total de Buques en Puerto", filtered_data['Vessels in Port'].sum())
col3.metric("Salidas en las Últ. 24 Hrs", filtered_data['Departures(Last 24 Hours)'].sum())
col4.metric("Llegadas en las Últ. 24 Hrs", filtered_data['Arrivals(Last 24 Hours)'].sum())

# --- Análisis de Distribución ---
st.markdown("""
    <div style="text-align: center; margin-top: 10px; padding: 10px; background-color: #f0f8ff; border-radius: 8px;">
        <h2 style="color: #003366; font-size: 2em;">Análisis de Distribución de Puertos</h2>
        <p style="color: #555; font-size: 1em;">
            Este análisis explora la distribución de puertos por país, tipos de puertos, y otros factores clave. 
            Utilice los filtros para ajustar la visualización de cada gráfico y obtener una vista detallada de los datos relevantes.
        </p>
    </div>
""", unsafe_allow_html=True)

# --- Expander para Análisis de Distribuciones ---
with st.expander("Ver Análisis de Distribuciones"):
    
    # --- Gráfico de Puertos por País ---
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("""
            <div style="text-align: center; margin-top: 10px;">
                <h4 style="color: #003366;">Distribución de Puertos por País</h4>
                <p style="font-size: 0.9em; color: #555;">
                    Este gráfico muestra la cantidad total de puertos distribuidos en cada país. 
                    Puede seleccionar tipos específicos de puertos para analizar su distribución en los países.
                </p>
            </div>
        """, unsafe_allow_html=True)

        # Filtro interno para tipos de puertos
        selected_types_country = st.checkbox("Mostrar solo tipos de puertos específicos", value=False)

        if selected_types_country:
            type_options_country = sorted(filtered_data['Type'].unique())
            selected_types_country_filter = st.multiselect("Filtrar por Tipo de Puerto", options=type_options_country, default=type_options_country, key="types_country_filter")
            filtered_data_country = filtered_data[filtered_data['Type'].isin(selected_types_country_filter)].copy()
        else:
            filtered_data_country = filtered_data.copy()

        # Gráfico de barras para cantidad de puertos por país
        port_count_by_country = filtered_data_country['Country'].value_counts().reset_index()
        port_count_by_country.columns = ['Country', 'Port Count']
        fig_country = px.bar(port_count_by_country, x='Country', y='Port Count', title="Cantidad de Puertos por País")
        fig_country.update_layout(xaxis_title="País", yaxis_title="Cantidad de Puertos", height=350)
        st.plotly_chart(fig_country, use_container_width=True)

    # --- Gráfico de Tipos de Puertos ---
    with col2:
        st.markdown("""
            <div style="text-align: center; margin-top: 10px;">
                <h4 style="color: #003366;">Distribución de Tipos de Puertos</h4>
                <p style="font-size: 0.9em; color: #555;">
                    Analice la distribución de puertos según su tipo. Utilice el filtro para visualizar los tipos de puertos seleccionados.
                </p>
            </div>
        """, unsafe_allow_html=True)

        # Filtro interno para tipos de puertos en general
        selected_types_general = st.checkbox("Mostrar solo ciertos tipos de puertos en el gráfico", key="general_type_checkbox")

        if selected_types_general:
            type_options_general = sorted(filtered_data['Type'].unique())
            selected_types_general_filter = st.multiselect("Filtrar por Tipo de Puerto", options=type_options_general, default=type_options_general, key="types_general_filter")
            filtered_data_type = filtered_data[filtered_data['Type'].isin(selected_types_general_filter)].copy()
        else:
            filtered_data_type = filtered_data.copy()

        # Gráfico de barras por tipos de puerto
        port_count_by_type = filtered_data_type['Type'].value_counts().reset_index()
        port_count_by_type.columns = ['Type', 'Port Count']
        fig_type = px.bar(port_count_by_type, x='Type', y='Port Count', title="Cantidad de Puertos por Tipo")
        fig_type.update_layout(xaxis_title="Tipo de Puerto", yaxis_title="Cantidad", height=350)
        st.plotly_chart(fig_type, use_container_width=True)

    
# --- Análisis Multivariado ---
with st.expander("Ver Análisis Multivariado"):

    # Columnas para el diseño de gráficos y métricas
    col1, col2 = st.columns(2)

    # --- Gráfico de Distribución de Puertos por Área Global ---
    with col1:
        st.markdown("""
            <div style="text-align: center; margin-top: 10px;">
                <h4 style="color: #003366;"> Distribución de Puertos por Área Global</h4>
                <p style="font-size: 0.9em; color: #555;">
                    Este gráfico representa cómo están distribuidos los puertos en diferentes áreas globales, 
                    proporcionando una visión general de la cobertura geográfica.
                </p>
            </div>
        """, unsafe_allow_html=True)

        area_global_counts = filtered_data['Area Global'].value_counts().reset_index()
        area_global_counts.columns = ['Area Global', 'Count']
        fig_area_global = px.pie(
            area_global_counts, values='Count', names='Area Global', title="Distribución por Área Global",
            color_discrete_sequence=px.colors.sequential.Blues
        )
        fig_area_global.update_traces(textinfo="percent+label")
        st.plotly_chart(fig_area_global, use_container_width=True)

    # --- Relación entre Tipo de Puerto y País ---
    with col2:
        st.markdown("""
            <div style="text-align: center; margin-top: 10px;">
                <h4 style="color: #003366;"> Relación entre Tipo de Puerto y País</h4>
                <p style="font-size: 0.9em; color: #555;">
                    Este gráfico muestra la distribución de tipos de puertos en los países seleccionados. 
                    Puede analizar cuáles países predominan en ciertos tipos de puertos.
                </p>
            </div>
        """, unsafe_allow_html=True)

        fig_type_country = px.histogram(
            filtered_data, x='Type', color='Country', barmode='stack',
            title="Distribución de Tipos de Puerto por País",
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        fig_type_country.update_layout(xaxis_title="Tipo de Puerto", yaxis_title="Cantidad", height=350)
        st.plotly_chart(fig_type_country, use_container_width=True)

    # Calcular la suma de 'Expected Arrivals' y 'Arrivals(Last 24 Hours)' para obtener el total esperado de llegadas
    filtered_data['Total Expected Arrivals'] = filtered_data['Expected Arrivals'] + filtered_data['Arrivals(Last 24 Hours)']

    # --- Gráfico de Correlación entre Total de Llegadas Potenciales y Salidas ---
    st.markdown("""
        <div style="text-align: center; margin-top: 10px;">
            <h4 style="color: #003366;">Correlación entre Total de Llegadas Potenciales y Salidas en las Últimas 24 Horas</h4>
            <p style="font-size: 0.9em; color: #555;">
                Este gráfico explora la relación entre el total de buques que se esperan lleguen a los puertos (llegadas actuales + llegadas esperadas) y los que han salido en las últimas 24 horas. 
                Puede ser útil para entender el flujo de tráfico portuario y las operaciones de entrada y salida.
            </p>
        </div>
    """, unsafe_allow_html=True)

    # Gráfico de dispersión para visualizar la correlación
    fig_corr = px.scatter(
        filtered_data,
        x='Total Expected Arrivals',
        y='Departures(Last 24 Hours)',
        size='Vessels in Port',
        color='Country',
        hover_name='Port Name',
        labels={'Total Expected Arrivals': 'Total Llegadas Potenciales', 'Departures(Last 24 Hours)': 'Salidas Últimas 24 Horas'},
        title="Correlación entre Total de Llegadas Potenciales y Salidas en las Últimas 24 Horas",
        color_discrete_sequence=px.colors.sequential.Blues
    )
    fig_corr.update_layout(
        height=400,
        xaxis_title="Total Llegadas Potenciales (Actuales + Esperadas)",
        yaxis_title="Salidas en las Últimas 24 Horas",
        title_x=0.5,
        title_font_size=16,
        margin=dict(t=50)
    )
    st.plotly_chart(fig_corr, use_container_width=True)

    # --- Detalles de Puertos Seleccionados ---
    st.markdown("""
        <div style="text-align: center; margin-top: 10px;">
            <h4 style="color: #003366;">Detalles de los Puertos con Mayor Correlación entre Llegadas Potenciales y Salidas</h4>
            <p style="font-size: 0.9em; color: #555;">
                Seleccione un puerto para ver información detallada sobre su flujo de buques, incluyendo el total de llegadas potenciales y el número de salidas recientes.
            </p>
        </div>
    """, unsafe_allow_html=True)

    # Ordenar por correlación entre Total Expected Arrivals y Departures
    top_ports_corr = filtered_data.nlargest(5, 'Total Expected Arrivals')[[ 
        'Port Name', 'Country', 'Total Expected Arrivals', 'Arrivals(Last 24 Hours)', 'Expected Arrivals', 'Departures(Last 24 Hours)', 'Vessels in Port'
    ]]

    # Selector de puerto
    port_selected = st.selectbox(
        "Seleccione un puerto para ver detalles adicionales:",
        options=top_ports_corr['Port Name'].tolist()
    )

    # Mostrar información detallada del puerto seleccionado
    selected_port_info = top_ports_corr[top_ports_corr['Port Name'] == port_selected].iloc[0]
    st.markdown(f"**Puerto**: {selected_port_info['Port Name']} ({selected_port_info['Country']})")
    st.markdown(f"- **Total Llegadas Potenciales**: {selected_port_info['Total Expected Arrivals']}")
    st.markdown(f"- **Arribos Actuales**: {selected_port_info['Arrivals(Last 24 Hours)']}")
    st.markdown(f"- **Llegadas Esperadas**: {selected_port_info['Expected Arrivals']}")
    st.markdown(f"- **Salidas en las Últimas 24 Horas**: {selected_port_info['Departures(Last 24 Hours)']}")
    st.markdown(f"- **Buques en Puerto**: {selected_port_info['Vessels in Port']}")


    # Nota final para contextualizar el análisis
    st.markdown("""
        <div style="background-color: #f9f9f9; padding: 15px; border-radius: 8px; margin-top: 20px;">
            <p style="font-size: 0.9em; color: #555; text-align: center;">
                <em>Nota:</em> Este análisis multivariado proporciona una vista en profundidad de la eficiencia operativa y la distribución de los puertos 
                por áreas globales, tipos de puerto y países con mayores llegadas. Úselo para identificar patrones y oportunidades de mejora en la gestión portuaria.
            </p>
        </div>
    """, unsafe_allow_html=True)

# Descripción del criterio de resaltado
highlight_option = st.selectbox(
    "Seleccione criterio para resaltar:",
    ["Top Países con más Puertos", "Tipo de Puerto más Frecuente", "Puertos con Mayor Total de Llegadas Potenciales"],
    help="Seleccione el criterio de resaltado para la tabla de puertos. Puede resaltar países con más puertos, tipos de puerto más frecuentes o puertos con el mayor total de llegadas potenciales (llegadas actuales + llegadas esperadas)."
)

# Descripción adicional para cada opción
if highlight_option == "Top Países con más Puertos":
    st.markdown("""
        <p style="font-size: 0.9em; color: #555;">
            <strong>Top 3 Países con más Puertos:</strong> Resalta los países que tienen el mayor número de puertos en los datos filtrados.
        </p>
    """, unsafe_allow_html=True)
elif highlight_option == "Tipo de Puerto más Frecuente":
    st.markdown("""
        <p style="font-size: 0.9em; color: #555;">
            <strong>Tipo de Puerto más Frecuente:</strong> Resalta los 2 tipos de puerto que aparecen con mayor frecuencia en los datos.
        </p>
    """, unsafe_allow_html=True)
else:  # "Puertos con Mayor Total de Llegadas Potenciales"
    st.markdown("""
        <p style="font-size: 0.9em; color: #555;">
            <strong>Puertos con Mayor Total de Llegadas Potenciales:</strong> Resalta los 5 puertos con el mayor número de llegadas potenciales, calculado como la suma de llegadas actuales y esperadas.
        </p>
    """, unsafe_allow_html=True)


# Calcular los valores para cada criterio
top_countries = filtered_data['Country'].value_counts().nlargest(3).index.tolist()
top_port_types = filtered_data['Type'].value_counts().nlargest(2).index.tolist()

# Crear una columna 'Total Expected Arrivals' para representar el total potencial de llegadas (arribos actuales + esperados)
filtered_data['Total Expected Arrivals'] = filtered_data['Expected Arrivals'] + filtered_data['Arrivals(Last 24 Hours)']

# Seleccionar los puertos con los valores más altos de 'Total Expected Arrivals'
top_ports_total_expected = filtered_data.nlargest(5, 'Total Expected Arrivals')['Port Name'].tolist()

# Aplicar el estilo personalizado basado en el criterio seleccionado
if highlight_option == "Top Países con más Puertos":
    styled_filtered_data = filtered_data.style.apply(lambda row: apply_country_style(row, top_countries), axis=1)
elif highlight_option == "Tipo de Puerto más Frecuente":
    styled_filtered_data = filtered_data.style.apply(lambda row: apply_port_type_style(row, top_port_types), axis=1)
else:  # "Puertos con Mayor Total de Llegadas Potenciales"
    styled_filtered_data = filtered_data.style.apply(lambda row: apply_total_expected_arrivals_style(row, top_ports_total_expected), axis=1)

# Mostrar tabla con estilo aplicado
st.dataframe(
    styled_filtered_data,
    height=400
)


# --- Dashboard de Power BI ---
st.markdown("<h4 style='text-align: center;'>Visualización del Dashboard de Power BI</h4>", unsafe_allow_html=True)

# Agregar botón de descarga para el reporte de Power BI
pdf_path = "./dashboards_pages/data/dashboard_buques.pdf"
if os.path.exists(pdf_path):
    with open(pdf_path, "rb") as file:
        pdf_data = file.read()  # Leer los datos del PDF
    st.download_button(
        label="Descargar Dashboard en PDF",
        data=pdf_data,
        file_name="dashboard_buques.pdf",
        mime="application/pdf"
    )
else:
    st.warning("No se encontró el archivo PDF. Verifica la ruta del archivo.")
