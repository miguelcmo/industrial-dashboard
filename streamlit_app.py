import streamlit as st
import pandas as pd
import numpy as np
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
    
    .kpi-card {
        background: white;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        border-left: 4px solid #1f77b4;
        margin-bottom: 1rem;
    }
    
    .alert-high {
        background-color: #ffebee;
        border-left: 4px solid #f44336;
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 4px;
    }
    
    .alert-medium {
        background-color: #fff3e0;
        border-left: 4px solid #ff9800;
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 4px;
    }
    
    .alert-low {
        background-color: #e8f5e8;
        border-left: 4px solid #4caf50;
        padding: 1rem;
        margin: 0.5rem 0;
        border-radius: 4px;
    }
</style>
""", unsafe_allow_html=True)

# Función para generar datos simulados
@st.cache_data
def generar_datos_industriales():
    np.random.seed(42)
    # Generar más puntos para mejor visualización
    fechas = pd.date_range(start='2024-09-20', end='2024-09-22 23:59', freq='30min')
    
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

# Información del sistema
st.sidebar.markdown("---")
st.sidebar.markdown("### 📊 Info del Sistema")
st.sidebar.info(f"Total de registros: {len(df):,}")
st.sidebar.info(f"Última actualización: {datetime.now().strftime('%H:%M:%S')}")

if auto_refresh:
    time.sleep(1)
    st.rerun()

# Filtrar datos según la fecha seleccionada
datos_filtrados = df[df['Fecha'].dt.date == fecha_seleccionada]

if not datos_filtrados.empty:
    # Estado general del sistema
    st.markdown("## 🚦 Estado General del Sistema")
    
    col_estado1, col_estado2, col_estado3, col_estado4 = st.columns(4)
    
    with col_estado1:
        st.markdown('<div class="alert-low"><strong>🟢 Sistemas Operativos</strong><br>6/8 variables normales</div>', unsafe_allow_html=True)
    
    with col_estado2:
        st.markdown('<div class="alert-medium"><strong>🟡 Advertencias</strong><br>2 variables en alerta</div>', unsafe_allow_html=True)
    
    with col_estado3:
        st.markdown('<div class="alert-low"><strong>⚡ Eficiencia</strong><br>87.3% promedio</div>', unsafe_allow_html=True)
    
    with col_estado4:
        st.markdown('<div class="alert-low"><strong>🔧 Uptime</strong><br>99.2% disponibilidad</div>', unsafe_allow_html=True)

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

    # Gráficos principales usando Altair
    st.markdown("## 📈 Tendencias de Variables")
    
    if len(variables_seleccionadas) > 0:
        # Gráficos individuales
        cols_graficos = st.columns(2)
        
        colores = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b']
        
        for i, variable in enumerate(variables_seleccionadas[:6]):
            col_idx = i % 2
            
            with cols_graficos[col_idx]:
                # Crear gráfico con Altair
                chart = alt.Chart(datos_filtrados).mark_line(
                    point=alt.OverlayMarkDef(color=colores[i % len(colores)]),
                    strokeWidth=3,
                    color=colores[i % len(colores)]
                ).encode(
                    x=alt.X('Fecha:T', title='Tiempo'),
                    y=alt.Y(f'{variable}:Q', title=variable.replace('_', ' ').title()),
                    tooltip=['Fecha:T', f'{variable}:Q']
                ).properties(
                    width=350,
                    height=250,
                    title=variable.replace('_', ' ').title()
                ).interactive()
                
                st.altair_chart(chart, use_container_width=True)
    
    # Gráfico de líneas combinado
    st.markdown("### 📊 Vista Combinada de Variables Principales")
    
    if len(variables_seleccionadas) >= 2:
        # Seleccionar principales variables para comparación
        vars_principales = ['Temperatura_Reactor_1', 'Presion_Sistema', 'Flujo_Entrada', 'Eficiencia_Proceso']
        vars_a_mostrar = [v for v in vars_principales if v in variables_seleccionadas][:4]
        
        if len(vars_a_mostrar) >= 2:
            # Preparar datos para gráfico combinado
            datos_melted = datos_filtrados.melt(
                id_vars=['Fecha'], 
                value_vars=vars_a_mostrar,
                var_name='Variable',
                value_name='Valor'
            )
            
            # Normalizar valores para comparación (0-100%)
            for var in vars_a_mostrar:
                if var in datos_filtrados.columns:
                    min_val = datos_filtrados[var].min()
                    max_val = datos_filtrados[var].max()
                    mask = datos_melted['Variable'] == var
                    datos_melted.loc[mask, 'Valor_Norm'] = (
                        (datos_melted.loc[mask, 'Valor'] - min_val) / 
                        (max_val - min_val) * 100
                    )
            
            chart_combined = alt.Chart(datos_melted).mark_line(strokeWidth=3).encode(
                x=alt.X('Fecha:T', title='Tiempo'),
                y=alt.Y('Valor_Norm:Q', title='Valor Normalizado (0-100%)', scale=alt.Scale(domain=[0, 100])),
                color=alt.Color('Variable:N', title='Variables', scale=alt.Scale(range=colores)),
                tooltip=['Fecha:T', 'Variable:N', 'Valor:Q', 'Valor_Norm:Q']
            ).properties(
                width=800,
                height=400,
                title='Tendencias Normalizadas de Variables Industriales'
            ).interactive()
            
            st.altair_chart(chart_combined, use_container_width=True)

    # Análisis de correlación simplificado
    st.markdown("## 🔍 Análisis de Correlación")
    
    variables_numericas = datos_filtrados.select_dtypes(include=[np.number]).columns.tolist()
    if len(variables_numericas) > 1:
        # Calcular correlaciones y mostrar en tabla
        matriz_correlacion = datos_filtrados[variables_numericas].corr()
        
        st.markdown("### Matriz de Correlación")
        st.dataframe(matriz_correlacion.style.background_gradient(cmap='RdBu_r', axis=None), use_container_width=True)
        
        # Mostrar correlaciones más fuertes
        st.markdown("### Correlaciones Significativas (|r| > 0.5)")
        correlaciones_fuertes = []
        
        for i in range(len(variables_numericas)):
            for j in range(i+1, len(variables_numericas)):
                var1 = variables_numericas[i]
                var2 = variables_numericas[j]
                corr = matriz_correlacion.loc[var1, var2]
                
                if abs(corr) > 0.5:
                    correlaciones_fuertes.append({
                        'Variable 1': var1.replace('_', ' ').title(),
                        'Variable 2': var2.replace('_', ' ').title(),
                        'Correlación': f"{corr:.3f}",
                        'Interpretación': 'Fuerte Positiva' if corr > 0.7 else 'Fuerte Negativa' if corr < -0.7 else 'Moderada'
                    })
        
        if correlaciones_fuertes:
            df_correlaciones = pd.DataFrame(correlaciones_fuertes)
            st.dataframe(df_correlaciones, use_container_width=True)
        else:
            st.info("No se encontraron correlaciones significativas entre las variables.")
    
    # Sistema de alarmas
    st.markdown("## 🚨 Sistema de Alarmas")
    
    alarmas = []
    for variable in variables_disponibles:
        if variable in valores_actuales:
            valor = valores_actuales[variable]
            estado, _ = obtener_estado_variable(valor, variable)
            
            if estado != 'Bueno':
                prioridad = 'Alta' if estado == 'Crítico' else 'Media'
                alarmas.append({
                    'Prioridad': prioridad,
                    'Variable': variable.replace('_', ' ').title(),
                    'Valor Actual': f"{valor:.2f}",
                    'Estado': estado,
                    'Timestamp': datetime.now().strftime("%H:%M:%S"),
                    'Acción Recomendada': 'Revisar inmediatamente' if estado == 'Crítico' else 'Monitorear'
                })
    
    if alarmas:
        df_alarmas = pd.DataFrame(alarmas)
        
        # Separar por prioridad
        alarmas_altas = df_alarmas[df_alarmas['Prioridad'] == 'Alta']
        alarmas_medias = df_alarmas[df_alarmas['Prioridad'] == 'Media']
        
        if not alarmas_altas.empty:
            st.markdown("### 🔴 Alarmas de Prioridad Alta")
            st.dataframe(alarmas_altas, use_container_width=True)
        
        if not alarmas_medias.empty:
            st.markdown("### 🟡 Alarmas de Prioridad Media")
            st.dataframe(alarmas_medias, use_container_width=True)
    else:
        st.success("✅ Todas las variables están en estado normal")
    
    # Estadísticas del día
    st.markdown("## 📋 Resumen del Día")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📊 Estadísticas Generales")
        
        # Crear tabla de estadísticas
        stats_data = []
        for variable in variables_seleccionadas[:6]:
            if variable in datos_filtrados.columns:
                stats_data.append({
                    'Variable': variable.replace('_', ' ').title(),
                    'Promedio': f"{datos_filtrados[variable].mean():.2f}",
                    'Máximo': f"{datos_filtrados[variable].max():.2f}",
                    'Mínimo': f"{datos_filtrados[variable].min():.2f}",
                    'Desv. Est.': f"{datos_filtrados[variable].std():.2f}"
                })
        
        if stats_data:
            df_stats = pd.DataFrame(stats_data)
            st.dataframe(df_stats, use_container_width=True)
    
    with col2:
        st.markdown("### 🎯 Indicadores de Rendimiento")
        
        # Calcular KPIs
        if 'Eficiencia_Proceso' in datos_filtrados.columns:
            eficiencia_promedio = datos_filtrados['Eficiencia_Proceso'].mean()
            
            # Mostrar eficiencia con progress bar
            st.markdown("#### Eficiencia del Proceso")
            st.progress(min(eficiencia_promedio / 100, 1.0))
            
            # Métricas de rendimiento
            col_eff1, col_eff2 = st.columns(2)
            with col_eff1:
                st.metric("Eficiencia Actual", f"{eficiencia_promedio:.1f}%")
            with col_eff2:
                target = 85
                delta = eficiencia_promedio - target
                st.metric("vs Objetivo (85%)", f"{delta:+.1f}%")
            
            # Estado visual
            if eficiencia_promedio >= 90:
                st.success("🟢 Rendimiento Excelente")
            elif eficiencia_promedio >= 80:
                st.warning("🟡 Rendimiento Aceptable")
            else:
                st.error("🔴 Rendimiento Crítico")
            
            # Histograma de eficiencia usando Altair
            st.markdown("#### Distribución de Eficiencia")
            
            chart_hist = alt.Chart(datos_filtrados).mark_bar(
                opacity=0.7,
                color='#2E86AB'
            ).encode(
                x=alt.X('Eficiencia_Proceso:Q', bin=alt.Bin(maxbins=15), title='Eficiencia (%)'),
                y=alt.Y('count()', title='Frecuencia')
            ).properties(
                width=400,
                height=200,
                title='Distribución de Valores de Eficiencia'
            )
            
            st.altair_chart(chart_hist, use_container_width=True)
        
        # Indicadores adicionales
        st.markdown("#### Otros Indicadores")
        
        # Calcular uptime simulado
        uptime = np.random.uniform(98, 99.8)
        st.metric("Uptime del Sistema", f"{uptime:.1f}%")
        
        # Calcular throughput
        if 'Flujo_Entrada' in datos_filtrados.columns:
            throughput = datos_filtrados['Flujo_Entrada'].sum()
            st.metric("Throughput Total", f"{throughput:.0f} L")

else:
    st.warning("⚠️ No hay datos disponibles para la fecha seleccionada.")
    st.info("Selecciona una fecha entre el 20 y 22 de septiembre de 2024.")

# Footer con información del sistema
st.markdown("---")
col_footer1, col_footer2, col_footer3 = st.columns(3)

with col_footer1:
    st.markdown("🔧 **Sistema de Monitoreo Industrial v2.0**")

with col_footer2:
    st.markdown(f"🕒 **Última actualización:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

with col_footer3:
    st.markdown(f"📡 **Estado de conexión:** 🟢 En línea")

# Información adicional en sidebar
st.sidebar.markdown("---")
st.sidebar.markdown("### 🛠️ Herramientas")

if st.sidebar.button("🔄 Recargar Datos"):
    st.cache_data.clear()
    st.rerun()

if st.sidebar.button("📊 Exportar Reporte"):
    st.sidebar.success("Reporte exportado exitosamente!")

if st.sidebar.button("⚙️ Calibrar Sensores"):
    st.sidebar.info("Calibración iniciada...")

st.sidebar.markdown("---")
st.sidebar.markdown("### 📞 Soporte")
st.sidebar.markdown("📧 soporte@industrial.com")
st.sidebar.markdown("📱 +1-800-INDUSTRY")
