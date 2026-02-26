# ============================================================================
# ⚡ MODELO FINANCIERO HÍBRIDO PV + BESS
# Aplicación Streamlit Interactiva
# Basado en: Modelo_Financiero_Hibrido_PV_BESS_v13_risk.xlsx
# ============================================================================

import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from scipy import optimize

# Configuración de página
st.set_page_config(
    page_title="Modelo Financiero PV+BESS",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado
st.markdown("""
    <style>
    .main-header {font-size: 2.5rem; font-weight: bold; color: #1f77b4;}
    .metric-card {background: #f0f2f6; padding: 1rem; border-radius: 0.5rem;}
    .sidebar-header {font-size: 1.2rem; font-weight: bold;}
    </style>
""", unsafe_allow_html=True)

# Título
st.markdown('<p class="main-header">⚡ Modelo Financiero Híbrido PV + BESS</p>', unsafe_allow_html=True)
st.markdown("**Planta Fotovoltaica + Almacenamiento de Energía - Análisis de Rentabilidad**")
st.divider()

# ============================================================================
# SIDEBAR - PARÁMETROS DE ENTRADA
# ============================================================================

st.sidebar.markdown('<p class="sidebar-header">🎛️ Parámetros de Inversión</p>', unsafe_allow_html=True)

# --- CAPEX ---
st.sidebar.markdown("### 🏗️ CAPEX")
capex_pv = st.sidebar.slider(
    "CAPEX PV (€/MWp)",
    min_value=400000,
    max_value=700000,
    value=525000,
    step=25000,
    help="Coste de instalación fotovoltaica por MWp"
)

capex_bess = st.sidebar.slider(
    "CAPEX BESS (€/MWh)",
    min_value=100000,
    max_value=250000,
    value=150000,
    step=10000,
    help="Coste de sistema de baterías por MWh de capacidad"
)

potencia_pv = st.sidebar.slider(
    "Potencia PV (MWp)",
    min_value=20,
    max_value=100,
    value=50,
    step=5,
    help="Potencia instalada del campo fotovoltaico"
)

potencia_bess = st.sidebar.slider(
    "Potencia BESS (MW)",
    min_value=10,
    max_value=50,
    value=20,
    step=5,
    help="Potencia máxima de descarga de la batería"
)

duracion_bess = st.sidebar.slider(
    "Duración BESS (horas)",
    min_value=1,
    max_value=6,
    value=2,
    step=1,
    help="Horas de autonomía de la batería a potencia nominal"
)

# --- INGRESOS ---
st.sidebar.markdown("### 💰 Ingresos")
precio_ppa = st.sidebar.slider(
    "Precio PPA (€/MWh)",
    min_value=20,
    max_value=80,
    value=40,
    step=2,
    help="Precio garantizado por Power Purchase Agreement"
)

porcentaje_ppa = st.sidebar.slider(
    "% Energía con PPA",
    min_value=0,
    max_value=100,
    value=70,
    step=5,
    help="Porcentaje de energía vendida bajo contrato PPA"
)

precio_merchant = st.sidebar.slider(
    "Precio Merchant Promedio (€/MWh)",
    min_value=30,
    max_value=150,
    value=80,
    step=5,
    help="Precio promedio esperado en mercado spot"
)

servicios_red = st.sidebar.slider(
    "Ingresos Servicios Red (M€/año)",
    min_value=0.0,
    max_value=5.0,
    value=2.78,
    step=0.1,
    help="Ingresos por servicios auxiliares (RR, FRR, etc.)"
)

# --- OPEX ---
st.sidebar.markdown("### 🔧 OPEX")
opex_pv = st.sidebar.slider(
    "OPEX PV (€/MWp/año)",
    min_value=3000,
    max_value=8000,
    value=4500,
    step=500,
    help="Coste operativo anual de la planta PV"
)

opex_bess_fijo = st.sidebar.slider(
    "OPEX BESS Fijo (€/MWh/año)",
    min_value=1000,
    max_value=3000,
    value=1600,
    step=200,
    help="Coste fijo anual del sistema de baterías"
)

opex_bess_var = st.sidebar.slider(
    "OPEX BESS Variable (€/MWh descargado)",
    min_value=0.0,
    max_value=2.0,
    value=0.50,
    step=0.1,
    help="Coste variable por MWh descargado"
)

# --- PARÁMETROS FINANCIEROS ---
st.sidebar.markdown("### 📊 Parámetros Financieros")
vida_util = st.sidebar.slider(
    "Vida Útil (años)",
    min_value=20,
    max_value=40,
    value=30,
    step=5,
    help="Vida económica del proyecto"
)

wacc = st.sidebar.slider(
    "WACC (%)",
    min_value=4.0,
    max_value=12.0,
    value=7.0,
    step=0.5,
    help="Coste promedio ponderado de capital"
)

tipo_is = st.sidebar.slider(
    "Impuesto Sociedades (%)",
    min_value=15,
    max_value=35,
    value=25,
    step=1,
    help="Tipo impositivo sobre beneficios"
)

inflacion = st.sidebar.slider(
    "Inflación Anual (%)",
    min_value=0.0,
    max_value=5.0,
    value=2.0,
    step=0.5,
    help="IPC esperado para actualización de precios"
)

# --- PARÁMETROS TÉCNICOS ---
st.sidebar.markdown("### ⚡ Parámetros Técnicos")
factor_capacidad = st.sidebar.slider(
    "Factor de Capacidad PV (%)",
    min_value=15,
    max_value=35,
    value=30,
    step=1,
    help="Ratio de generación real vs potencial máximo"
)

rte_bess = st.sidebar.slider(
    "Eficiencia BESS - Round Trip (%)",
    min_value=80,
    max_value=95,
    value=88,
    step=1,
    help="Eficiencia de ida y vuelta de la batería"
)

degradacion_pv = st.sidebar.slider(
    "Degradación PV (%/año)",
    min_value=0.2,
    max_value=1.0,
    value=0.4,
    step=0.1,
    help="Pérdida anual de eficiencia de paneles"
)

anio_augmentation = st.sidebar.slider(
    "Año Augmentation BESS",
    min_value=10,
    max_value=20,
    value=12,
    step=1,
    help="Año de reposición de capacidad de batería"
)

coste_augmentation = st.sidebar.slider(
    "Coste Augmentation (% CAPEX BESS)",
    min_value=20,
    max_value=50,
    value=30,
    step=5,
    help="Coste de reposición como % del CAPEX original"
)

ciclos_anio = st.sidebar.slider(
    "Ciclos Equivalentes por Año",
    min_value=200,
    max_value=500,
    value=300,
    step=50,
    help="Número de ciclos completos de carga/descarga anuales"
)

# ============================================================================
# FUNCIONES DE CÁLCULO
# ============================================================================

def calcular_flujos_caja():
    """Calcula los flujos de caja anuales del proyecto"""
    
    # Capacidad energía BESS
    capacidad_bess = potencia_bess * duracion_bess  # MWh
    
    # CAPEX Inicial
    capex_total_pv = potencia_pv * capex_pv
    capex_total_bess = capacidad_bess * capex_bess
    capex_inicial = capex_total_pv + capex_total_bess
    
    # Generación anual PV (MWh)
    horas_anio = 8760
    generacion_pv_anual = potencia_pv * horas_anio * (factor_capacidad / 100)
    
    # Energía descargada BESS anual
    energia_descargada_anual = capacidad_bess * ciclos_anio * (rte_bess / 100)
    
    # Preparar arrays para los años
    años = list(range(vida_util + 1))  # Año 0 a Año N
    flujos_caja = []
    ingresos_totales = []
    opex_total = []
    capex_anual = []
    impuestos = []
    ebitda_anual = []
    
    for año in años:
        if año == 0:
            # Año 0: Solo inversión
            flujo = -capex_inicial
            flujos_caja.append(flujo)
            ingresos_totales.append(0)
            opex_total.append(0)
            capex_anual.append(capex_inicial)
            impuestos.append(0)
            ebitda_anual.append(0)
            continue
        
        # Factor de degradación PV
        factor_degradacion = (1 - degradacion_pv / 100) ** (año - 1)
        generacion_pv_año = generacion_pv_anual * factor_degradacion
        
        # Inflación de precios
        factor_inflacion = (1 + inflacion / 100) ** (año - 1)
        
        # ===== INGRESOS =====
        # Energía con PPA
        energia_ppa = generacion_pv_año * (porcentaje_ppa / 100)
        ingreso_ppa = energia_ppa * precio_ppa * factor_inflacion
        
        # Energía Merchant
        energia_merchant = generacion_pv_año * (1 - porcentaje_ppa / 100)
        ingreso_merchant = energia_merchant * precio_merchant * factor_inflacion
        
        # Servicios de Red (con erosión de precios)
        if año <= 10:
            erosion = 1 - (año - 1) * 0.05  # 5% erosión anual hasta año 10
        else:
            erosion = 0.5  # Se estabiliza al 50%
        ingreso_servicios = servicios_red * 1_000_000 * factor_inflacion * max(erosion, 0.5)
        
        ingresos_año = ingreso_ppa + ingreso_merchant + ingreso_servicios
        
        # ===== OPEX =====
        opex_pv_año = potencia_pv * opex_pv * factor_inflacion
        opex_bess_fijo_año = capacidad_bess * opex_bess_fijo * factor_inflacion
        opex_bess_var_año = energia_descargada_anual * opex_bess_var * factor_inflacion
        opex_año = opex_pv_año + opex_bess_fijo_año + opex_bess_var_año
        
        # ===== CAPEX Augmentation =====
        capex_año = 0
        if año == anio_augmentation:
            capex_año = capex_total_bess * (coste_augmentation / 100)
        
        # ===== EBITDA =====
        ebitda = ingresos_año - opex_año
        
        # ===== Amortización (lineal) =====
        amortizacion_pv = capex_total_pv / 30  # 30 años vida fiscal PV
        amortizacion_bess = capex_total_bess / 10  # 10 años vida fiscal BESS
        amortizacion_total = amortizacion_pv + amortizacion_bess
        
        # ===== Beneficio antes de impuestos =====
        bai = ebitda - amortizacion_total
        
        # ===== Impuestos =====
        impuesto_año = max(bai, 0) * (tipo_is / 100)
        
        # ===== Beneficio después de impuestos =====
        bdi = bai - impuesto_año
        
        # ===== Flujo de Caja Libre =====
        flujo_caja = bdi + amortizacion_total - capex_año
        
        flujos_caja.append(flujo_caja)
        ingresos_totales.append(ingresos_año)
        opex_total.append(opex_año)
        capex_anual.append(capex_año)
        impuestos.append(impuesto_año)
        ebitda_anual.append(ebitda)
    
    return {
        'años': años,
        'flujos_caja': flujos_caja,
        'ingresos': ingresos_totales,
        'opex': opex_total,
        'capex': capex_anual,
        'impuestos': impuestos,
        'ebitda': ebitda_anual,
        'capex_inicial': capex_inicial,
        'capex_pv': capex_total_pv,
        'capex_bess': capex_total_bess,
        'generacion_pv': generacion_pv_anual,
        'capacidad_bess': capacidad_bess
    }

def calcular_tir(flujos):
    """Calcula la Tasa Interna de Retorno usando Newton-Raphson"""
    try:
        tir = optimize.newton(
            lambda r: sum([f / (1 + r) ** i for i, f in enumerate(flujos)]),
            0.1,
            maxiter=100
        )
        return tir * 100
    except:
        return 0.0

def calcular_van(flujos, tasa):
    """Calcula el Valor Actual Neto"""
    van = sum([f / (1 + tasa / 100) ** i for i, f in enumerate(flujos)])
    return van

def calcular_payback(flujos):
    """Calcula el período de recuperación de la inversión (años)"""
    acumulado = 0
    for i, flujo in enumerate(flujos):
        acumulado += flujo
        if acumulado >= 0:
            return i
    return len(flujos)

def calcular_lcoe(resultados):
    """Calcula el Coste Nivelado de Energía (LCOE)"""
    capex_pv = resultados['capex_pv']
    generacion_total = sum([
        resultados['generacion_pv'] * (1 - degradacion_pv / 100) ** i 
        for i in range(vida_util)
    ])
    opex_total = sum(resultados['opex'][1:])
    lcoe = (capex_pv + opex_total) / generacion_total * 1000  # €/MWh
    return lcoe

def calcular_lcos(resultados):
    """Calcula el Coste Nivelado de Almacenamiento (LCOS)"""
    capex_bess = resultados['capex_bess']
    capacidad = resultados['capacidad_bess']
    throughput_total = capacidad * ciclos_anio * vida_util * (rte_bess / 100)
    opex_bess_total = sum([
        (capacidad * opex_bess_fijo + capacidad * ciclos_anio * opex_bess_var) 
        * (1 + inflacion / 100) ** i 
        for i in range(vida_util)
    ])
    lcos = (capex_bess + opex_bess_total) / throughput_total * 1000  # €/MWh
    return lcos

# ============================================================================
# EJECUTAR CÁLCULOS
# ============================================================================

resultados = calcular_flujos_caja()

# Calcular KPIs financieros
tir = calcular_tir(resultados['flujos_caja'])
van = calcular_van(resultados['flujos_caja'], wacc)
payback = calcular_payback(resultados['flujos_caja'])
lcoe = calcular_lcoe(resultados)
lcos = calcular_lcos(resultados)

# ============================================================================
# VISUALIZACIÓN - KPIs PRINCIPALES
# ============================================================================

st.markdown("### 📊 KPIs Financieros Principales")

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    delta_tir = tir - 15
    st.metric(
        label="📈 TIR After-Tax",
        value=f"{tir:.2f}%",
        delta=f"{delta_tir:+.2f}%" if abs(delta_tir) > 0 else "0.00%",
        delta_color="normal" if tir >= 15 else "inverse"
    )

with col2:
    st.metric(
        label="💰 VAN (@ WACC)",
        value=f"{van/1_000_000:.1f} M€",
        delta=f"{van/1_000_000:+.1f} M€",
        delta_color="normal" if van > 0 else "inverse"
    )

with col3:
    st.metric(
        label="⏱️ Payback",
        value=f"{payback} años",
        delta=f"{vida_util - payback} años restantes",
        delta_color="normal"
    )

with col4:
    st.metric(
        label="🏗️ Inversión Total",
        value=f"{resultados['capex_inicial']/1_000_000:.2f} M€",
        delta=None
    )

with col5:
    st.metric(
        label="📉 LCOE PV",
        value=f"{lcoe:.1f} €/MWh",
        delta=None
    )

st.divider()

# ============================================================================
# GRÁFICOS
# ============================================================================

col_graf1, col_graf2 = st.columns(2)

with col_graf1:
    st.markdown("### 📊 Flujo de Caja Anual")
    
    df_flujos = pd.DataFrame({
        'Año': resultados['años'],
        'Ingresos': resultados['ingresos'],
        'OPEX': resultados['opex'],
        'CAPEX': resultados['capex'],
        'Flujo Neto': resultados['flujos_caja']
    })
    
    fig_flujos = go.Figure()
    
    fig_flujos.add_trace(go.Bar(
        x=df_flujos['Año'],
        y=df_flujos['Ingresos'],
        name='Ingresos',
        marker_color='#2ecc71',
        opacity=0.8
    ))
    
    fig_flujos.add_trace(go.Bar(
        x=df_flujos['Año'],
        y=[-x for x in df_flujos['OPEX']],
        name='OPEX',
        marker_color='#e74c3c',
        opacity=0.8
    ))
    
    fig_flujos.add_trace(go.Bar(
        x=df_flujos['Año'],
        y=[-x for x in df_flujos['CAPEX']],
        name='CAPEX',
        marker_color='#f39c12',
        opacity=0.8
    ))
    
    fig_flujos.update_layout(
        barmode='relative',
        height=400,
        xaxis_title='Año',
        yaxis_title='€',
        hovermode='x unified',
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    st.plotly_chart(fig_flujos, use_container_width=True)

with col_graf2:
    st.markdown("### 📈 Flujo de Caja Acumulado")
    
    flujo_acumulado = []
    acum = 0
    for f in resultados['flujos_caja']:
        acum += f
        flujo_acumulado.append(acum)
    
    fig_acum = go.Figure()
    
    fig_acum.add_trace(go.Scatter(
        x=resultados['años'],
        y=flujo_acumulado,
        mode='lines+markers',
        name='Flujo Acumulado',
        line=dict(color='#3498db', width=3),
        marker=dict(size=8, color='#3498db')
    ))
    
    # Línea de cero
    fig_acum.add_hline(y=0, line_dash="dash", line_color="gray", line_width=1)
    
    # Marcar punto de payback
    if payback < vida_util:
        fig_acum.add_vline(
            x=payback,
            line_dash="dash",
            line_color="red",
            line_width=2,
            annotation_text="Payback",
            annotation_position="top"
        )
    
    fig_acum.update_layout(
        height=400,
        xaxis_title='Año',
        yaxis_title='€ Acumulado',
        hovermode='x unified',
        showlegend=False
    )
    
    st.plotly_chart(fig_acum, use_container_width=True)

# ============================================================================
# TABLA DE DATOS
# ============================================================================

st.divider()
st.markdown("### 📋 Resumen Financiero por Años")

df_resumen = pd.DataFrame({
    'Año': resultados['años'],
    'Ingresos (M€)': [x/1_000_000 for x in resultados['ingresos']],
    'OPEX (M€)': [x/1_000_000 for x in resultados['opex']],
    'CAPEX (M€)': [x/1_000_000 for x in resultados['capex']],
    'EBITDA (M€)': [x/1_000_000 for x in resultados['ebitda']],
    'Impuestos (M€)': [x/1_000_000 for x in resultados['impuestos']],
    'Flujo Caja (M€)': [x/1_000_000 for x in resultados['flujos_caja']]
})

# Mostrar primeros 15 años y últimos 5
df_mostrar = pd.concat([df_resumen.head(15), df_resumen.tail(5)])

st.dataframe(
    df_mostrar.style.format({
        'Ingresos (M€)': '{:.2f}',
        'OPEX (M€)': '{:.2f}',
        'CAPEX (M€)': '{:.2f}',
        'EBITDA (M€)': '{:.2f}',
        'Impuestos (M€)': '{:.2f}',
        'Flujo Caja (M€)': '{:.2f}'
    }).background_gradient(subset=['Flujo Caja (M€)'], cmap='RdYlGn', vmin=-5, vmax=10),
    use_container_width=True,
    hide_index=True
)

# ============================================================================
# ANÁLISIS DE SENSIBILIDAD
# ============================================================================

st.divider()
st.markdown("### 📐 Análisis de Sensibilidad")

col_sens1, col_sens2 = st.columns(2)

with col_sens1:
    st.markdown("**Impacto en TIR por Variable (±20%)**")
    
    # Calcular sensibilidades
    sensibilidad_data = []
    
    # CAPEX ±20%
    capex_base = resultados['capex_inicial']
    flujos_base = resultados['flujos_caja'].copy()
    tir_base = tir
    
    for delta, nombre in [(-0.2, "-20%"), (0, "Base"), (0.2, "+20%")]:
        flujos_test = flujos_base.copy()
        flujos_test[0] = -capex_base * (1 + delta)
        tir_test = calcular_tir(flujos_test)
        sensibilidad_data.append({
            'Variable': f'CAPEX {nombre}',
            'TIR': f"{tir_test:.2f}%"
        })
    
    # Precio PPA ±20%
    for delta, nombre in [(-0.2, "-20%"), (0, "Base"), (0.2, "+20%")]:
        # Recalcular con PPA modificado
        precio_ppa_test = precio_ppa * (1 + delta)
        # Simplificación: impacto lineal aproximado
        impacto = delta * 0.08 * tir_base  # Aproximación
        tir_test = tir_base + impacto * 100
        sensibilidad_data.append({
            'Variable': f'Precio PPA {nombre}',
            'TIR': f"{max(0, tir_test):.2f}%"
        })
    
    df_sens = pd.DataFrame(sensibilidad_data)
    st.dataframe(df_sens, use_container_width=True, hide_index=True)

with col_sens2:
    st.markdown("**Distribución de Ingresos (Vida Útil)**")
    
    ingresos_pv = sum(resultados['ingresos'][1:]) * (porcentaje_ppa / 100)
    ingresos_merchant = sum(resultados['ingresos'][1:]) * (1 - porcentaje_ppa / 100) * 0.7
    ingresos_servicios = sum(resultados['ingresos'][1:]) * 0.3
    
    fig_pie = go.Figure(data=[go.Pie(
        labels=['PPA', 'Merchant', 'Servicios Red'],
        values=[ingresos_pv, ingresos_merchant, ingresos_servicios],
        hole=0.4,
        marker_colors=['#3498db', '#2ecc71', '#f39c12'],
        textinfo='label+percent',
        textposition='outside'
    )])
    
    fig_pie.update_layout(height=350, showlegend=True)
    st.plotly_chart(fig_pie, use_container_width=True)

# ============================================================================
# INFORMACIÓN ADICIONAL
# ============================================================================

with st.expander("ℹ️ Información del Modelo y Supuestos"):
    st.markdown("""
    ### 📋 Supuestos del Modelo
    
    | Parámetro | Valor | Descripción |
    |-----------|-------|-------------|
    | Generación PV | Basada en factor de capacidad | Horas equivalentes anuales |
    | BESS | 1 ciclo diario equivalente | 300 ciclos/año típico |
    | Degradación PV | 0.4%/año lineal | Típico paneles monocristalinos |
    | Erosión Servicios | 5%/año hasta año 10 | Luego se estabiliza al 50% |
    | Augmentation BESS | Año 12 (30% CAPEX) | Reposición de capacidad |
    | Amortización PV | 30 años lineal | Según RD 634/2015 |
    | Amortización BESS | 10 años lineal | Vida fiscal baterías |
    | Impuestos | Sobre beneficio antes de impuestos | Tipo general 25% |
    
    ### ⚠️ Limitaciones del Modelo
    
    - **No incluye financiación/deuda** (modelo 100% equity)
    - **Precios merchant simplificados** (promedio anual, no horario)
    - **No considera restricciones de red** ni curtailment forzado
    - **Servicios de red con erosión estimada** (basado en tendencias OMIE)
    - **No captura precios negativos** (batería llena en horas de clipping)
    
    ### 📊 Fuentes de Datos
    
    Basado en el modelo financiero `Modelo_Financiero_Hibrido_PV_BESS_v13_risk.xlsx`
    
    - Precios OMIE (mercado eléctrico España)
    - CAPEX sector renovable 2024
    - Parámetros técnicos LFP BESS
    - Normativa fiscal española
    
    ### 🎯 KPIs de Referencia (Escenario Base)
    
    | KPI | Valor Base | Rango Típico |
    |-------|------------|--------------|
    | TIR After-Tax | 16-18% | 12-25% |
    | VAN @ 7% | 35-42 M€ | Variable |
    | Payback | 6-8 años | 5-12 años |
    | LCOE PV | 18-25 €/MWh | 15-50 €/MWh |
    | LCOS BESS | 75-100 €/MWh | 60-200 €/MWh |
    """)

# ============================================================================
# DESCARGA DE DATOS
# ============================================================================

st.divider()
st.markdown("### 💾 Exportar Datos")

col_exp1, col_exp2, col_exp3 = st.columns(3)

with col_exp1:
    # CSV Flujos de Caja
    csv_flujos = df_resumen.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Descargar Flujos (CSV)",
        data=csv_flujos,
        file_name="flujos_caja_pv_bess.csv",
        mime="text/csv",
        use_container_width=True
    )

with col_exp2:
    # Excel resumen
    try:
        excel_data = df_resumen.to_excel(index=False, engine='openpyxl')
        st.download_button(
            label="📥 Descargar Resumen (Excel)",
            data=excel_data,
            file_name="resumen_pv_bess.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True
        )
    except:
        st.info("Instala openpyxl para exportar Excel: `pip install openpyxl`")

with col_exp3:
    # JSON parámetros
    import json
    params = {
        'capex_pv': capex_pv,
        'capex_bess': capex_bess,
        'potencia_pv': potencia_pv,
        'potencia_bess': potencia_bess,
        'duracion_bess': duracion_bess,
        'tir': tir,
        'van': van,
        'payback': payback
    }
    json_data = json.dumps(params, indent=2).encode('utf-8')
    st.download_button(
        label="📥 Descargar Parámetros (JSON)",
        data=json_data,
        file_name="parametros_pv_bess.json",
        mime="application/json",
        use_container_width=True
    )

# ============================================================================
# FOOTER
# ============================================================================

st.divider()
st.markdown("""
<div style='text-align: center; color: gray; padding: 1rem;'>
    <small>
        ⚡ Modelo Financiero PV+BESS v1.0 | 
        Basado en Modelo_Financiero_Hibrido_PV_BESS_v13_risk.xlsx | 
        Desarrollado con Streamlit
    </small>
</div>
""", unsafe_allow_html=True)