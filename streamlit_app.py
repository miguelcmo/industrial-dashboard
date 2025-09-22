import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime, timedelta
import time
import altair as alt

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
    
    # Crear gráficos usando matplotlib y streamlit
    if len(variables_seleccionadas) > 0:
        cols_graficos = st.columns(2)
        
        for i, variable in enumerate(variables_seleccionadas[:4]):
            col_idx = i % 2
            
            with cols_graficos[col_idx]:
                # Crear gráfico con Altair (incluido en Streamlit)
                chart = alt.Chart(datos_filtrados).mark_line(
                    point=True,
                    strokeWidth=3
                ).add_selection(
                    alt.selection_interval()
                ).encode(
                    x=alt.X('Fecha:T', title='Tiempo'),
                    y=alt.Y(f'{variable}:Q', title=variable.replace('_', ' ').title()),
                    color=alt.value('#1f77b4'),
                    tooltip=['Fecha:T', f'{variable}:Q']
                ).properties(
                    width=350,
                    height=250,
                    title=variable.replace('_', ' ').title()
                ).interactive()
                
                st.altair_chart(chart, use_container_width=True)
    
    # Gráfico de líneas combinado
    st.markdown("### 📊 Vista Combinada de Variables")
    
    if len(variables_seleccionadas) >= 2:
        # Preparar datos para gráfico combinado
        datos_melted = datos_filtrados.melt(
            id_vars=['Fecha'], 
            value_vars=variables_seleccionadas[:4],
            var_name='Variable',
            value_name='Valor'
        )
        
        # Normalizar valores para comparación
        for var in variables_seleccionadas[:4]:
            if var in datos_filtrados.columns:
                datos_melted.loc[datos_melted['Variable'] == var, 'Valor_Norm'] = (
                    (datos_melted.loc[datos_melted['Variable'] == var, 'Valor'] - 
                     datos_filtrados[var].min()) / 
                    (datos_filtrados[var].max() - datos_filtrados[var].min()) * 100
                )
        
        chart_combined = alt.Chart(datos_melted).mark_line(strokeWidth=2).encode(
            x=alt.X('Fecha:T', title='Tiempo'),
            y=alt.Y('Valor_Norm:Q', title='Valor Normalizado (0-100%)'),
            color=alt.Color('Variable:N', title='Variables'),
            tooltip=['Fecha:T', 'Variable:N', 'Valor:Q', 'Valor_Norm:Q']
        ).properties(
            width=800,
            height=400,
            title='Tendencias Normalizadas de Variables Industriales'
        ).interactive()
        
        st.altair_chart(chart_combined, use_container_width=True)
    
    # Matriz de correlación
    st.markdown("## 🔍 Análisis de Correlación")
    
    # Seleccionar solo variables numéricas
    variables_numericas = datos_filtrados.select_dtypes(include=[np.number]).columns.tolist()
    if len(variables_numericas) > 1:
        matriz_correlacion = datos_filtrados[variables_numericas].corr()
        
        # Crear heatmap con matplotlib
        fig_corr, ax = plt.subplots(figsize=(10, 8))
        sns.heatmap(
            matriz_correlacion, 
            annot=True, 
            cmap='RdBu_r', 
            center=0,
            square=True,
            fmt='.2f',
            cbar_kws={"shrink": .8}
        )
        plt.title('Matriz de Correlación de Variables', fontsize=16, pad=20)
        plt.xticks(rotation=45, ha='right')
        plt.yticks(rotation=0)
        plt.tight_layout()
        
        st.pyplot(fig_corr)
    else:
        st.info("Se necesitan al menos 2 variables numéricas para calcular correlaciones.")
    
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
            
            # Crear gauge simple con progress bar
            st.markdown("#### Eficiencia del Proceso")
            st.progress(eficiencia_promedio / 100)
            
            # Mostrar valor numérico
            col_eff1, col_eff2, col_eff3 = st.columns(3)
            with col_eff1:
                st.metric("Eficiencia Actual", f"{eficiencia_promedio:.1f}%")
            with col_eff2:
                target = 85
                delta = eficiencia_promedio - target
                st.metric("vs Objetivo", f"{target}%", f"{delta:.1f}%")
            with col_eff3:
                if eficiencia_promedio >= 90:
                    estado_eficiencia = "🟢 Excelente"
                elif eficiencia_promedio >= 80:
                    estado_eficiencia = "🟡 Bueno"
                else:
                    estado_eficiencia = "🔴 Crítico"
                st.metric("Estado", estado_eficiencia)
            
            # Histograma de eficiencia
            st.markdown("#### Distribución de Eficiencia")
            
            chart_hist = alt.Chart(datos_filtrados).mark_bar(
                opacity=0.7,
                binSpacing=2
            ).encode(
                x=alt.X('Eficiencia_Proceso:Q', bin=alt.Bin(maxbins=20), title='Eficiencia (%)'),
                y=alt.Y('count()', title='Frecuencia'),
                color=alt.value('#2E86AB')
            ).properties(
                width=400,
                height=200,
                title='Distribución de Valores de Eficiencia'
            )
            
            st.altair_chart(chart_hist, use_container_width=True)

else:
    st.warning("No hay datos disponibles para la fecha seleccionada.")

# Footer
st.markdown("---")
st.markdown("🔧 Sistema de Monitoreo Industrial v1.0 | Actualizado: " + datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
