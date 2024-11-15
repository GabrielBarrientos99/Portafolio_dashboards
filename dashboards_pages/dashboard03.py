import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# Cargar el dataset
@st.cache_data
def load_data():
    data = pd.read_csv("./dashboards_pages/data/supermarket_sales.csv")
    data['Date'] = pd.to_datetime(data['Date'])
    data['Income'] = data['Total'] - data['gross income']
    return data

# Función para obtener los pares de correlaciones más altas usando valor absoluto, excluyendo 1 y NaN
def get_top_correlation_pairs(data_corr, top_n=3):
    # Crear una máscara para eliminar duplicados y obtener el valor absoluto de las correlaciones
    mask = np.triu(np.ones_like(data_corr, dtype=bool))
    corr = data_corr.mask(mask).stack().sort_values(ascending=False)
    # Filtrar correlaciones exactamente iguales a 1.0
    corr = corr[corr < 0.9999]
    return corr.head(top_n)

# Función para obtener las correlaciones más altas de una columna específica
def get_top_correlations_for_column(data_corr, column, top_n=3):
    corr = data_corr[column].drop(labels=[column]).sort_values(ascending=False)
    return corr.head(top_n)

# Descripciones de las columnas
column_descriptions = {
    "Invoice ID": "Identificador de factura: un identificador único para cada transacción o compra.",
    "Branch": "Sucursal: Indica la sucursal específica del supermercado donde se realizó la transacción.",
    "City": "Ciudad: La ciudad donde se encuentra la sucursal del supermercado.",
    "Customer type": "Tipo de cliente: define el tipo de cliente (por ejemplo, 'Miembro' o 'Normal').",
    "Gender": "Sexo: el sexo del cliente (por ejemplo, 'masculino' o 'femenino').",
    "Product line": "Línea de productos: especifica la categoría de los productos adquiridos.",
    "Unit price": "Precio unitario: precio de una sola unidad del producto.",
    "Quantity": "Cantidad: Número de unidades compradas en una sola transacción.",
    "Tax 5%": "Impuesto 5%: El importe del impuesto aplicado a la compra, calculado como el 5% del total antes de impuestos.",
    "Total": "Total: importe total pagado por el cliente, incluidos los impuestos.",
    "Date": "Fecha: la fecha de la transacción.",
    "Time": "Hora: La hora de la transacción.",
    "Payment": "Pago: el método de pago utilizado.",
    "cogs": "COGS: Costo de los bienes vendidos.",
    "gross margin percentage": "Porcentaje de margen bruto: diferencia porcentual entre ventas y costo de los bienes vendidos.",
    "gross income": "Ingresos brutos: los ingresos que quedan después de deducir el costo de los bienes vendidos.",
    "Rating": "Calificación: la calificación que el cliente le da al producto o servicio."
}

# Cargar datos
sales = load_data()

# Eliminar la columna 'gross margin percentage' antes de calcular la matriz de correlación
if 'gross margin percentage' in sales.columns:
    sales = sales.drop(columns=['gross margin percentage'])

# Título del Dashboard
st.markdown("<h1 style='text-align: center; color: #003366;'>Análisis de Ventas en Supermercados</h1>", unsafe_allow_html=True)
st.write("Dashboard interactivo para analizar las ventas y comportamientos en diferentes sucursales, géneros y métodos de pago.")

# --- Filtros ---
st.sidebar.header("Filtros")
branch_filter = st.sidebar.multiselect("Selecciona la Sucursal:", options=sales['Branch'].unique(), default=sales['Branch'].unique())
gender_filter = st.sidebar.multiselect("Selecciona Género:", options=sales['Gender'].unique(), default=sales['Gender'].unique())
payment_filter = st.sidebar.multiselect("Selecciona Método de Pago:", options=sales['Payment'].unique(), default=sales['Payment'].unique())
date_range = st.sidebar.date_input("Rango de Fechas:", [sales['Date'].min(), sales['Date'].max()])

# Aplicar filtros
filtered_data = sales[
    (sales['Branch'].isin(branch_filter)) &
    (sales['Gender'].isin(gender_filter)) &
    (sales['Payment'].isin(payment_filter)) &
    (sales['Date'] >= pd.to_datetime(date_range[0])) &
    (sales['Date'] <= pd.to_datetime(date_range[1]))
]

if filtered_data.empty:
    st.warning("No hay datos para los filtros seleccionados. Ajuste los filtros.")
else:
    # --- Métricas Generales ---
    st.subheader("Métricas Generales")
    col1, col2, col3 = st.columns(3)
    col1.metric("Total Ventas", f"${filtered_data['Total'].sum():,.2f}")
    col2.metric("Promedio de Ventas", f"${filtered_data['Total'].mean():,.2f}")
    col3.metric("Número de Transacciones", len(filtered_data))

    # --- Análisis de Correlaciones ---
    st.subheader("Análisis de Correlaciones")
    with st.expander("Correlaciones entre Variables"):
        # Cálculo de la matriz de correlación
        data_corr = filtered_data.corr(numeric_only=True).fillna(0)

        # Tabla de correlación con estilo
        st.markdown("""
            <div style="background-color: #f9f9f9; padding: 15px; border-radius: 8px;">
                <p style="font-size: 0.9em; color: #333; text-align: center;">
                    <em>Nota:</em> Los valores sombreados en la tabla de correlaciones representan la relación entre variables. 
                    Las correlaciones cercanas a 1 (color más oscuro) indican una relación fuerte entre las variables, 
                    mientras que los valores cercanos a 0 indican poca o ninguna relación.
                </p>
            </div>
        """, unsafe_allow_html=True)
        
        # Estilos de cmap para la tabla de correlación
        cmap_styles = ['magma', 'coolwarm', 'viridis', 'inferno', 'plasma', 'cividis', 'Blues', 'Greens', 'Reds', 'Purples']
        
        # Selección de estilo de cmap
        selected_cmap = st.selectbox("Seleccione el estilo de cmap para la tabla de correlación:", cmap_styles, index=0)
        
        st.dataframe(data_corr.style.background_gradient(cmap=selected_cmap, axis=None).format("{:.2f}"))

        # Selección de columna para encontrar sus top 3 correlaciones más altas
        selected_column = st.selectbox("Seleccione una columna para encontrar sus top 3 correlaciones más altas:", data_corr.columns)
        top_corrs_for_column = get_top_correlations_for_column(data_corr, selected_column, top_n=3)
        
        if not top_corrs_for_column.empty:
            st.markdown(f"<h4 style='color: #003366;'>Top 3 Correlaciones más Altas para {selected_column}</h4>", unsafe_allow_html=True)
            
            correlation_options = []
            for idx, (var, corr_value) in enumerate(top_corrs_for_column.items(), 1):
                correlation_options.append(f"{selected_column} y {var}")
                st.markdown(f"<p style='font-size: 1.1em; color: #003366;'><strong>{idx}.</strong> {selected_column} y {var}: <strong>{corr_value:.2f}</p>", unsafe_allow_html=True)
                st.markdown(f"<p style='font-size: 0.9em; color: #555;'>{column_descriptions.get(selected_column, 'Descripción no disponible')}<br>{column_descriptions.get(var, 'Descripción no disponible')}</p>", unsafe_allow_html=True)

            # Selección de correlación para graficar
            selected_correlation = st.selectbox("Seleccione una correlación para graficar:", correlation_options)
            var1, var2 = selected_correlation.split(" y ")

            # Graficar la correlación seleccionada
            st.markdown(f"<h4 style='color: #003366; text-align: center;'>Gráfico de {var1} vs {var2}</h4>", unsafe_allow_html=True)
            fig_corr = px.scatter(filtered_data, x=var1, y=var2, trendline="ols", title=f"Correlación entre {var1} y {var2}")
            st.plotly_chart(fig_corr, use_container_width=True)

    # --- Análisis de Ventas ---
    st.subheader("Análisis de Ventas")

    # Diseño de gráficos en columnas
    col1, col2 = st.columns(2)

    with col1:
        st.markdown("<h4 style='color: #003366; text-align: center;'>Ventas por Género</h4>", unsafe_allow_html=True)
        fig_gender = px.pie(
            filtered_data, names='Gender', values='Total',
            color_discrete_sequence=px.colors.sequential.RdBu
        )
        fig_gender.update_traces(textinfo="percent+label")
        st.plotly_chart(fig_gender, use_container_width=True)

    with col2:
        st.markdown("<h4 style='color: #003366; text-align: center;'>Ventas por Método de Pago</h4>", unsafe_allow_html=True)
        fig_payment = px.bar(
            filtered_data.groupby('Payment')['Total'].sum().reset_index(),
            x='Payment', y='Total', color='Payment',
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        fig_payment.update_layout(xaxis_title="Método de Pago", yaxis_title="Total Ventas", height=350)
        st.plotly_chart(fig_payment, use_container_width=True)

    # --- Análisis Multivariado ---
    st.subheader("Análisis Multivariado")
    st.markdown("""
        <div style="text-align: center; margin-top: 10px; padding: 10px; background-color: #e0f7fa; border-radius: 8px;">
            <h4 style="color: #00796b;">Relación entre Precio Unitario y Cantidad por Línea de Producto</h4>
            <p style="color: #555;">
                Explore cómo el precio unitario y la cantidad vendida se relacionan según la línea de producto.
            </p>
        </div>
    """, unsafe_allow_html=True)
    fig_multi = px.scatter(
        filtered_data, x='Unit price', y='Quantity', size='Total',
        color='Product line', hover_name='Product line',
        color_discrete_sequence=px.colors.sequential.Viridis
    )
    fig_multi.update_layout(xaxis_title="Precio Unitario", yaxis_title="Cantidad", height=400)
    st.plotly_chart(fig_multi, use_container_width=True)

    # --- Tabla Detallada ---

    st.markdown("""
        <style>
        .dataframe-container {
            width: 100%;
            overflow-x: auto;
            text-align: center;
        }
        .dataframe-container table {
            width: 100%;
            border-collapse: collapse;
            margin: 0 auto;
        }
        .dataframe-container th, .dataframe-container td {
            padding: 8px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }
        .dataframe-container th {
            background-color: #f2f2f2;
        }
        .dataframe-container tr:hover {
            background-color: #f5f5f5;
        }
        </style>
    """, unsafe_allow_html=True)

    st.markdown("""
        <div class="dataframe-container">
            <h4 style="text-align: center; color: #003366;">Tabla Detallada de Ventas</h4>
            <p style="text-align: center; color: #555;">
                Esta tabla muestra los detalles de las ventas filtradas, incluyendo la fecha, sucursal, género, línea de producto, total y método de pago.
            </p>
        </div>
    """, unsafe_allow_html=True)

    st.dataframe(
        filtered_data[['Date', 'Branch', 'Gender', 'Product line', 'Total', 'Payment']].style.highlight_max(axis=0),
        height=600
    )

    # Explicación del criterio de pintado
    st.markdown("""
        <div style="background-color: #f0f8ff; padding: 15px; border-radius: 8px; margin-top: 20px;">
            <p style="font-size: 0.9em; color: #555; text-align: center;">
                <em>Nota:</em> En la tabla de ventas detallada, los valores más altos de cada columna numérica 
                están resaltados para ayudar a identificar rápidamente los registros con mayores ventas, 
                géneros predominantes y métodos de pago más comunes. Este pintado facilita el análisis visual 
                de los datos de forma efectiva.
            </p>
        </div>
    """, unsafe_allow_html=True)

# Descripción de las columnas
column_descriptions = {
    "Invoice ID": "Identificador de factura: un identificador único para cada transacción o compra.",
    "Branch": "Sucursal: Indica la sucursal específica del supermercado donde se realizó la transacción.",
    "City": "Ciudad: La ciudad donde se encuentra la sucursal del supermercado.",
    "Customer type": "Tipo de cliente: define el tipo de cliente (por ejemplo, 'Miembro' o 'Normal').",
    "Gender": "Sexo: el sexo del cliente (por ejemplo, 'masculino' o 'femenino').",
    "Product line": "Línea de productos: especifica la categoría de los productos adquiridos.",
    "Unit price": "Precio unitario: precio de una sola unidad del producto.",
    "Quantity": "Cantidad: Número de unidades compradas en una sola transacción.",
    "Tax 5%": "Impuesto 5%: El importe del impuesto aplicado a la compra, calculado como el 5% del total antes de impuestos.",
    "Total": "Total: importe total pagado por el cliente, incluidos los impuestos.",
    "Date": "Fecha: la fecha de la transacción.",
    "Time": "Hora: La hora de la transacción.",
    "Payment": "Pago: el método de pago utilizado.",
    "COGS": "COGS: Costo de los bienes vendidos.",
    "gross margin percentage": "Porcentaje de margen bruto: La diferencia porcentual entre las ventas y el costo de los bienes vendidos.",
    "gross income": "Ingresos brutos: los ingresos que quedan después de deducir el costo de los bienes vendidos de las ventas totales.",
    "Rating": "Calificación: la calificación que el cliente le da al producto o servicio."
}
