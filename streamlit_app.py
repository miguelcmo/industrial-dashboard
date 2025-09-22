import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import plotly.express as px
from datetime import datetime, timedelta
import time

# Configuración de la página
st.set_page_config(
    page_title="Dashboard Industrial",
    page_icon="🏭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado para mejorar el diseño
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    
    .metric-container {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 1rem;
    }
    
    .status-good {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        color: white;
        padding: 0.5rem;
        border-radius: 5px;
        text-align: center;
        font-weight: bold;
    }
    
    .status-warning {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        padding: 0.5rem;
        border-radius: 5px;
        text-align: center;
        font-weight: bold;
    }
    
    .status-critical {
        background: linear-gradient(135deg, #ff9a9e 0%, #fecfef 100%);
        color: white;
        padding: 0.5rem;
        border-radius: 5px;
        text-align: center;
        font-weight: bold;
    }
    
    .sidebar .sidebar-content {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
    }
</style>
""", unsafe_allow_html=True)

# Función para generar datos simulados
@st.cache_data
def generar_datos_industriales():
    np.random.seed(42)
    fechas = pd.date_range(start='2024-01-01', end='2024-12-31', freq='H')
    
    datos = {
        'Fecha': fechas,
        'Temperatura_Reactor_1': 250 + np.random.normal(0, 10, len(fechas)),
        'Presion_Sistema': 15 + np.random.normal(0, 2, len(fechas)),
        'Flujo_Entrada': 100 + np.random.normal(0, 5, len(fechas)),
        'Nivel_Tanque': 75 + np.random.normal(0, 8, len(fechas)),
        'Consumo_Energia': 450 + np.random.normal(0, 25, len(fechas)),
        'pH_Proceso': 7.2 + np.random.normal(0, 0.3, len(fechas)),
        'Vibration_Motor': 0.5 + np.random.normal(0, 0.1, len(fechas)),
        'Eficiencia_Proceso': 85 + np.random.normal(0, 5, len(fechas))
    }
    
    return pd.DataFrame(datos)

# Función para determinar el estado de una variable
def obtener_estado_variable(valor, variable):
    estados = {
        'Temperatura_Reactor_1': {'bueno': (240, 260), 'advertencia': (230, 270), 'critico': (0, 230)},
        'Presion_Sistema': {'bueno': (12, 18), 'advertencia': (10, 20), 'critico': (0, 10)},
        'Flujo_Entrada': {'bueno': (90, 110), 'advertencia': (80, 120), 'critico': (0, 80)},
        'Nivel_Tanque': {'bueno': (60, 90), 'advertencia': (40, 100), 'critico': (0, 40)},
        'pH_Proceso': {'bueno': (6.8, 7.6), 'advertencia': (6.5, 8.0), 'critico': (0, 6.5)},
        'Eficiencia_Proceso': {'bueno': (80, 100), 'advertencia': (70, 80), 'critico': (0, 70)}
    }
    
    if variable in estados:
        if estados[variable]['bueno'][0] <= valor <= estados[variable]['bueno'][1]:
            return 'Bueno', 'status-good'
        elif estados[variable]['advertencia'][0] <= valor <= estados[variable]['advertencia'][1]:
            return 'Advertencia', 'status-warning'
        else:
            return 'Crítico', 'status-critical'
    
    return 'Desconocido', 'status-warning'

# Título principal
st.markdown('<h1 class="main-header">🏭 Dashboard de Control Industrial</h1>', unsafe_allow_html=True)

# Cargar datos
df = generar_datos_industriales()

# Sidebar para controles
st.sidebar.title("⚙️ Controles del Sistema")

# Selector de fecha
fecha_seleccionada = st.sidebar.date_input(
    "Seleccionar Fecha",
    value=datetime.now().date(),
    min_value=df['Fecha'].min().date(),
    max_value=df['Fecha'].max().date()
)

# Selector de variables
variables_disponibles = [col for col in df.columns if col != 'Fecha']
variables_seleccionadas = st.sidebar.multiselect(
    "Variables a Mostrar",
    variables_disponibles,
    default=variables_disponibles[:4]
)

# Filtro de tiempo
rango_tiempo = st.sidebar.selectbox(
    "Rango de Tiempo",
    ["Última Hora", "Últimas 24 Horas", "Última Semana", "Último Mes"]
)

# Botón de actualización automática
auto_refresh = st.sidebar.checkbox("Actualización Automática (cada 30s)")

if auto_refresh:
    time.sleep(1)
    st.rerun()

# Filtrar datos según la fecha seleccionada
datos_filtrados = df[df['Fecha'].dt.date == fecha_seleccionada]

if not datos_filtrados.empty:
    # Métricas en tiempo real
    st.markdown("## 📊 Métricas en Tiempo Real")
    
    cols = st.columns(4)
    valores_actuales = datos_filtrados.iloc[-1]  # Último valor del día
    
    metricas = [
        ("Temperatura Reactor", "Temperatura_Reactor_1", "°C"),
        ("Presión Sistema", "Presion_Sistema", "Bar"),
        ("Flujo Entrada", "Flujo_Entrada", "L/min"),
        ("Nivel Tanque", "Nivel_Tanque", "%")
    ]
    
    for i, (nombre, variable, unidad) in enumerate(metricas):
        if variable in valores_actuales:
            valor = valores_actuales[variable]
            estado, clase_css = obtener_estado_variable(valor, variable)
            
            with cols[i]:
                st.metric(
                    label=f"{nombre}",
                    value=f"{valor:.1f} {unidad}",
                    delta=f"{np.random.uniform(-2, 2):.1f}"
                )
                st.markdown(f'<div class="{clase_css}">{estado}</div>', unsafe_allow_html=True)

    # Gráficos principales
    st.markdown("## 📈 Tendencias de Variables")
    
    # Crear subplots
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=[var.replace('_', ' ').title() for var in variables_seleccionadas[:4]],
        specs=[[{"secondary_y": False}, {"secondary_y": False}],
               [{"secondary_y": False}, {"secondary_y": False}]]
    )
    
    colores = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728']
    
    for i, variable in enumerate(variables_seleccionadas[:4]):
        row = i // 2 + 1
        col = i % 2 + 1
        
        fig.add_trace(
            go.Scatter(
                x=datos_filtrados['Fecha'],
                y=datos_filtrados[variable],
                mode='lines',
                name=variable.replace('_', ' ').title(),
                line=dict(color=colores[i], width=3),
                fill='tonexty' if i > 0 else None,
                fillcolor=f'rgba{tuple(list(px.colors.hex_to_rgb(colores[i])) + [0.1])}'
            ),
            row=row, col=col
        )
    
    fig.update_layout(
        height=600,
        title_text="Monitoreo de Variables Industriales",
        showlegend=True,
        template='plotly_dark',
        font=dict(size=12)
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Gráfico de correlación
    st.markdown("## 🔍 Análisis de Correlación")
    
    # Seleccionar solo variables numéricas
    variables_numericas = datos_filtrados.select_dtypes(include=[np.number]).columns.tolist()
    matriz_correlacion = datos_filtrados[variables_numericas].corr()
    
    fig_corr = px.imshow(
        matriz_correlacion,
        title="Matriz de Correlación de Variables",
        color_continuous_scale='RdBu',
        aspect='auto'
    )
    
    st.plotly_chart(fig_corr, use_container_width=True)
    
    # Tabla de alarmas
    st.markdown("## 🚨 Sistema de Alarmas")
    
    alarmas = []
    for variable in variables_disponibles:
        if variable in valores_actuales:
            valor = valores_actuales[variable]
            estado, _ = obtener_estado_variable(valor, variable)
            
            if estado != 'Bueno':
                alarmas.append({
                    'Variable': variable.replace('_', ' ').title(),
                    'Valor Actual': f"{valor:.2f}",
                    'Estado': estado,
                    'Timestamp': datetime.now().strftime("%H:%M:%S")
                })
    
    if alarmas:
        df_alarmas = pd.DataFrame(alarmas)
        st.dataframe(df_alarmas, use_container_width=True)
    else:
        st.success("✅ Todas las variables están en estado normal")
    
    # Estadísticas del día
    st.markdown("## 📋 Resumen del Día")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### Estadísticas Generales")
        for variable in variables_seleccionadas:
            if variable in datos_filtrados.columns:
                promedio = datos_filtrados[variable].mean()
                maximo = datos_filtrados[variable].max()
                minimo = datos_filtrados[variable].min()
                
                st.write(f"**{variable.replace('_', ' ').title()}:**")
                st.write(f"- Promedio: {promedio:.2f}")
                st.write(f"- Máximo: {maximo:.2f}")
                st.write(f"- Mínimo: {minimo:.2f}")
                st.write("---")
    
    with col2:
        st.markdown("### Estado del Sistema")
        
        # Calcular eficiencia general
        if 'Eficiencia_Proceso' in datos_filtrados.columns:
            eficiencia_promedio = datos_filtrados['Eficiencia_Proceso'].mean()
            
            fig_gauge = go.Figure(go.Indicator(
                mode = "gauge+number+delta",
                value = eficiencia_promedio,
                domain = {'x': [0, 1], 'y': [0, 1]},
                title = {'text': "Eficiencia del Proceso (%)"},
                delta = {'reference': 85},
                gauge = {
                    'axis': {'range': [None, 100]},
                    'bar': {'color': "darkblue"},
                    'steps': [
                        {'range': [0, 70], 'color': "lightgray"},
                        {'range': [70, 85], 'color': "yellow"},
                        {'range': [85, 100], 'color': "green"}
                    ],
                    'threshold': {
                        'line': {'color': "red", 'width': 4},
                        'thickness': 0.75,
                        'value': 90
                    }
                }
            ))
            
            fig_gauge.update_layout(height=300)
            st.plotly_chart(fig_gauge, use_container_width=True)

else:
    st.warning("No hay datos disponibles para la fecha seleccionada.")

# Footer
st.markdown("---")
st.markdown("🔧 Sistema de Monitoreo Industrial v1.0 | Actualizado: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
