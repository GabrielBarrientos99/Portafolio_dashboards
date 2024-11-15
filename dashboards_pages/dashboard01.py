import streamlit as st
import pandas as pd
import plotly.express as px
import os
import base64

# Cargar el dataset
@st.cache_data
def load_data():
    data = pd.read_csv("./dashboards_pages/data/UnicornCompanies_2.csv")
    # Convertir 'Date Joined' a datetime y calcular 'Years to Unicorn'
    data['Date Joined'] = pd.to_datetime(data['Date Joined'], errors='coerce')
    data['Years to Unicorn'] = (data['Date Joined'].dt.year - data['Year Founded']).fillna(0).astype(int)
    return data

# Calcular el porcentaje de compañías por encima y por debajo de la media
def calculate_percentage_above_below(df, column):
    mean_value = df[column].mean()
    above_mean = (df[column] > mean_value).sum()
    below_mean = (df[column] < mean_value).sum()
    total = len(df)
    
    above_percentage = (above_mean / total) * 100 if total > 0 else 0
    below_percentage = (below_mean / total) * 100 if total > 0 else 0
    
    return mean_value, above_percentage, below_percentage


# Función para mostrar métricas, porcentaje de compañías y gráfico
def display_metric_container(col, title, df, column, color):
    with col:
        with st.container():
            # Calcular el valor total y los porcentajes de empresas por encima y por debajo de la media
            total_value = df[column].sum()
            _, above_percentage, below_percentage = calculate_percentage_above_below(df, column)
            
            # Mostrar el valor total como métrica principal
            st.metric(label=title, value=f"${total_value:,.2f}B")
            
            # Simular el `delta` usando HTML para un estilo más prominente
            st.markdown(
                f"<p style='font-size: 16px; font-weight: bold; text-align: left;'>"
                f"<span style='color: red;'>↓ {below_percentage:.2f}%</span> | "
                f"<span style='color: green;'>↑ {above_percentage:.2f}%</span>"
                f"</p>", 
                unsafe_allow_html=True
            )

            # Agrupar los datos por 'Year Founded' y calcular la suma de la columna seleccionada
            df_grouped = df.groupby("Year Founded")[column].sum().reset_index()

            # Crear gráfico de barras para la métrica con las sumas agrupadas por año
            fig = px.bar(df_grouped, x='Year Founded', y=column, title=f"Suma de {title} por Año de Fundación", color_discrete_sequence=[color])

            fig.update_layout(height=300, xaxis_title="Año de Fundación", yaxis_title=title)
            st.plotly_chart(fig, use_container_width=True)

# Función para aplicar el estilo seleccionado
def highlight_top_countries(row, top_countries, style_choice):
    # Definir esquemas de color para tres estilos diferentes
    styles = {
        "Estilo 1": [
            "background-color: #1F4E79; color: white;", 
            "background-color: #3C78A8; color: white;", 
            "background-color: #A9CCE3; color: black;"
        ],
        "Estilo 2": [
        "background-color: #4B5320; color: white;",  # Verde oliva oscuro
        "background-color: #8B9A46; color: black;",  # Verde oliva claro
        "background-color: #FFD700; color: black;"  # Dorado suave
        ],
        "Estilo 3": [
            "background-color: #4A235A; color: white;",  # Púrpura oscuro
            "background-color: #7D3C98; color: white;",  # Púrpura mediano
            "background-color: #FF8C00; color: white;"  # Naranja oscuro para contraste
        ]
    }

    selected_styles = styles.get(style_choice, styles["Estilo 1"])  # Escoger el estilo según selección
    country = row["Country"]
    # Si el país está en los tres principales, aplicar el estilo correspondiente
    if country in top_countries:
        style_index = top_countries.index(country)
        return [selected_styles[style_index]] * len(row)
    return [""] * len(row)

# Cargar datos y configuración inicial
data = load_data()



st.markdown(
    """
    <h1 style="text-align: center; color: #2E86C1; font-size: 3em; font-weight: bold; margin-top: -20px;">
        Dashboard de Unicorn Companies
    </h1>
    <p style="text-align: center; color: #5D6D7E; font-size: 1.2em;">
        Exploración detallada del crecimiento y la distribución de compañías unicornio en diferentes industrias y regiones
    </p>
    """, 
    unsafe_allow_html=True
)


# Filtrar datos por año de fundación seleccionado
st.sidebar.header("Filtros")
years = sorted(data['Year Founded'].unique())
start_year, end_year = st.sidebar.select_slider(
    "Seleccione el rango de años de fundación",
    options=years,
    value=(min(years), max(years))
)

# Filtramos los datos por continente usando st.multiselect para permitir múltiples selecciones
continents = sorted(data['Continent'].unique())  # Listar continentes únicos
selected_continents = st.sidebar.multiselect(
    "Seleccione Continentes",
    options=continents,
    default=continents,  # Selecciona todos los continentes por defecto
    placeholder="Selecciona uno o más continentes"
)

# Filtrar por Industry con un expander para ahorrar espacio
industries = sorted(data['Industry'].unique())

with st.sidebar.expander("Seleccione Industrias"):
    selected_industries = st.multiselect(
        "Seleccione una o más industrias",
        options=industries,
        default=industries,  # Selecciona todas las industrias por defecto
        placeholder="Buscar industria..."
    )

# Aplicar el filtro de año, continente y industria seleccionados
filtered_data = data[
    (data['Year Founded'] >= start_year) & 
    (data['Year Founded'] <= end_year) & 
    (data['Continent'].isin(selected_continents)) &
    (data['Industry'].isin(selected_industries))
]

# Selector de estilo en la barra lateral
st.sidebar.header("Opciones de Estilo en la tabla")

style_choice = st.sidebar.selectbox("Selecciona el estilo de resaltado", ["Estilo 1", "Estilo 2", "Estilo 3"])
# Agregamos una nota pequeña para explicar los estilos, que indican los tres principales países por 'Valuation'
st.sidebar.info(
    "Los estilos resaltan los tres principales países por mayor suma de 'Valuation'."
)
# Mostrar métricas clave en contenedores
st.subheader("Estadísticas Generales")

# Crear columnas para cada métrica
col_funding, col_valuation = st.columns(2)

# Mostrar métricas y gráficos para Funding
display_metric_container(col_funding, "Funding", filtered_data, "Funding", color="#29b5e8")

# Mostrar métricas y gráficos para Valuation
display_metric_container(col_valuation, "Valuation", filtered_data, "Valuation", color="#FF9F36")

# filtramos la data filtrada por coluimnas
filtered_data = filtered_data[["Company","Years to Unicorn","Funding", "Valuation", "Year Founded", "Country","Industry",'Latitude', 'Longitude']]
sorted_data = filtered_data.sort_values("Year Founded", ascending=False)

# Identificar los tres países con mayor suma de "Valuation"
valuation_by_country = sorted_data.groupby("Country")["Valuation"].sum().nlargest(3)
top_countries = valuation_by_country.index.tolist()

# Aplicar estilo personalizado al DataFrame filtrado
styled_data = filtered_data.style.apply(highlight_top_countries, axis=1, top_countries=top_countries, style_choice=style_choice)

# Mostrar DataFrame filtrado y gráfico de la distribución de "Industry"

# Crear dos columnas dentro del expander
col1, col2 = st.columns([0.62, 0.38])

# Mostrar el DataFrame estilizado en la primera columna con configuración personalizada de columnas
with col1:
    st.dataframe(
        styled_data,
        column_config={
            "Company": "Nombre de la Compañía",
            "Funding": st.column_config.NumberColumn(
                "Funding ($)",
                help="Fondos recaudados por la compañía",
                format="$%.2f B",
            ),
            "Valuation": st.column_config.NumberColumn(
                "Valuation ($)",
                help="Valoración de la compañía",
                format="$%.2f B",
            ),
            "Year Founded": st.column_config.NumberColumn("Año de Fundación"),
            "Country": st.column_config.TextColumn("País", width="150px"),  # Ajuste de ancho de columna
            "Industry": "Industria"
        },
        hide_index=True,
        height=500  # Ajuste de altura de la tabla
    )

# Gráfico de barras de industria en la parte superior derecha
if "Industry" in filtered_data.columns:
    with col2:
        # Gráfico de barras de industria sin "Otros"
        industry_counts = filtered_data["Industry"].value_counts().reset_index()
        industry_counts.columns = ["Industry", "Count"]
        
        fig_industry = px.bar(
            industry_counts, 
            x="Industry", 
            y="Count", 
            title="Distribución de Compañías por Industria",
            color_discrete_sequence=["#636EFA"]
        )
        fig_industry.update_layout(xaxis_title="Industria", yaxis_title="Cantidad", height=250)
        st.plotly_chart(fig_industry, use_container_width=True)
        
        # Gráfico circular con "Otros" en los países
        top_countries_data = filtered_data["Country"].value_counts()
        top_countries = top_countries_data.nlargest(5)
        other_countries_count = top_countries_data.iloc[5:].sum()
        
        # Crear un DataFrame con los principales países y "Otros"
        top_countries_df = pd.concat([top_countries, pd.Series(other_countries_count, index=["Otros"])]).reset_index()
        top_countries_df.columns = ["Country", "Count"]
        
        fig_country = px.pie(
            top_countries_df, 
            values="Count", 
            names="Country", 
            title="Distribución de Compañías por País (Top 5 + Otros)",
            color_discrete_sequence=px.colors.sequential.RdBu
        )
        fig_country.update_traces(textinfo="percent+label")
        fig_country.update_layout(height=250)
        
        st.plotly_chart(fig_country, use_container_width=True)

# Gráfico de barras apiladas para mostrar la distribución de empresas por industria y país, con "Otros" en los países
industry_country_counts = filtered_data.groupby(["Industry", "Country"]).size().reset_index(name="Count")

# Filtrar solo los 5 principales países y agrupar el resto como "Otros"
top_countries_list = top_countries_df["Country"].tolist()
industry_country_filtered = industry_country_counts.copy()
industry_country_filtered["Country"] = industry_country_filtered["Country"].apply(lambda x: x if x in top_countries_list else "Otros")

# Volver a agrupar los datos después de agregar "Otros"
industry_country_aggregated = industry_country_filtered.groupby(["Industry", "Country"]).sum().reset_index()

fig_industry_country = px.bar(
    industry_country_aggregated,
    x="Industry",
    y="Count",
    color="Country",
    title="Distribución de Empresas por Industria y País (Top 5 Países + Otros)",
    barmode="stack",
    color_discrete_sequence=px.colors.qualitative.Set3
)
fig_industry_country.update_layout(xaxis_title="Industria", yaxis_title="Cantidad de Empresas", height=400)

st.plotly_chart(fig_industry_country, use_container_width=True)





# Filtrar el Top 5 de empresas que más rápido se convirtieron en unicornio
top_5_unicorns = filtered_data.nsmallest(5, 'Years to Unicorn')[['Company', 'Years to Unicorn', 'Funding','Industry', 'Country']]

# Convertir 'Years to Unicorn' menor a 1 año a "Menos de 1 año" para claridad en el gráfico
top_5_unicorns['Years to Unicorn'] = top_5_unicorns['Years to Unicorn'].apply(lambda x: "Menos de 1 año" if x < 1 else x)

# Verificar si hay datos en top_5_unicorns
if not top_5_unicorns.empty:
    with st.expander("Ver detalles de las Empresas que más rápido se convirtieron en Unicornio"):
        # Verificar si todos los valores de 'Years to Unicorn' son menores a 1 año
        if (top_5_unicorns['Years to Unicorn'] == "Menos de 1 año").all():
            # Mostrar un gráfico de puntos para diferenciar las empresas por financiamiento en billones
            fig_top5 = px.scatter(
                top_5_unicorns,
                y="Company",
                x="Funding",
                size="Funding",
                labels={"Funding": "Financiamiento (billones de USD)"},
                color="Company",
            )
            fig_top5.update_layout(
                height=350,
                xaxis_title="Financiamiento (billones de USD)",
                yaxis_title="",
                showlegend=False
            )
        else:
            # Configuración del gráfico de barras en caso de que haya empresas con más de 1 año
            fig_top5 = px.bar(
                top_5_unicorns,
                y="Company",
                x="Years to Unicorn",
                color="Funding",
                color_continuous_scale=px.colors.sequential.Blues,
                labels={"Years to Unicorn": "Años para Unicornio", "Funding": "Financiamiento (billones de USD)"},
                orientation="h"
            )
            fig_top5.update_layout(
                height=350,
                xaxis_title="Años para convertirse en Unicornio",
                yaxis_title="",
                margin=dict(l=0, r=0, t=30, b=0)
            )

        # Título estilizado del header con Markdown y HTML
        st.markdown(
            "<div style='padding:10px; border-left: 4px solid #636EFA; background-color: #333333; color: #ffffff;'>"
            "Top 5 Empresas que más rápido se convirtieron en Unicornio"
            "</div>", unsafe_allow_html=True
        )

        # Mostrar el gráfico y la información de las empresas en dos columnas
        col1, col2 = st.columns(2)

        # Gráfico en la primera columna
        with col2:
            st.plotly_chart(fig_top5, use_container_width=True)

        # Información detallada de cada empresa en la segunda columna
        with col1:
            st.subheader("Detalles de la Empresa")

            company_selected = st.selectbox(
                "Seleccione una empresa para ver más detalles",
                options=top_5_unicorns["Company"].tolist()
            )

            selected_info = top_5_unicorns[top_5_unicorns["Company"] == company_selected].iloc[0]

            st.markdown(f"### {selected_info['Company']}")
            st.markdown(f"- **Años para convertirse en Unicornio**: {selected_info['Years to Unicorn']}")
            st.markdown(f"- **Financiamiento**: ${selected_info['Funding']:,.2f}B")
            st.markdown(f"- **Industria**: {selected_info['Industry']}")
            st.markdown(f"- **País**: {selected_info['Country']}")
                    
else:
    st.warning("No hay empresas en el Top 5 debido a los filtros aplicados.")
    

# Renombrar columnas para cumplir con los requisitos de st.map
map_data = filtered_data[['Latitude', 'Longitude', 'Valuation', 'Country', 'Company']].dropna()
map_data = map_data.rename(columns={'Latitude': 'latitude', 'Longitude': 'longitude'})

# Verificamos que haya datos para mostrar en el mapa
if not map_data.empty:
    with st.expander("Ver Mapa de Empresas Unicornio"):
        # Crear un gráfico de dispersión en el mapa usando Plotly Express
        fig = px.scatter_mapbox(
            map_data,
            lat="latitude",
            lon="longitude",
            size="Valuation",  # Tamaño de los puntos basado en Valuation
            color="Country",  # Color de los puntos basado en Country
            hover_name="Company",  # Nombre de la empresa al pasar el cursor
            hover_data={"Valuation": True, "Country": True},  # Datos adicionales en el hover
            color_continuous_scale=px.colors.cyclical.IceFire,
            size_max=20,  # Tamaño máximo de los puntos
            zoom=1,
            height=500
        )

        # Configurar el estilo del mapa
        fig.update_layout(mapbox_style="carto-positron")
        fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})  # Sin márgenes alrededor del mapa

        # Mostrar el gráfico en Streamlit
        st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("No hay datos disponibles para mostrar en el mapa.")


def get_binary_file_downloader_html(bin_file, file_name, button_text):
    bin_str = bin_file.read()
    b64 = base64.b64encode(bin_str).decode()
    href = f'<a href="data:application/octet-stream;base64,{b64}" download="{file_name}">{button_text}</a>'
    return href

