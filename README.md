# ⚡ Modelo Financiero Híbrido PV + BESS

Aplicación web interactiva para calcular la rentabilidad de plantas híbridas fotovoltaicas con almacenamiento de energía.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.31.0-red.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

## 📋 Descripción

Esta aplicación replica los cálculos del modelo financiero `Modelo_Financiero_Hibrido_PV_BESS_v13_risk.xlsx` en una interfaz web interactiva. Permite:

- ✅ Ajustar parámetros de inversión en tiempo real
- ✅ Calcular TIR, VAN, Payback automáticamente
- ✅ Visualizar flujos de caja con gráficos interactivos
- ✅ Exportar resultados en CSV/Excel/JSON
- ✅ Análisis de sensibilidad integrado

## 🚀 Instalación y Ejecución

### Opción 1: Entorno Local

```bash
# 1. Clonar o descargar el repositorio
git clone https://github.com/tuusuario/pv-bess-app.git
cd pv-bess-app

# 2. Crear entorno virtual
python -m venv venv

# 3. Activar entorno
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 4. Instalar dependencias
pip install -r requirements.txt

# 5. Ejecutar la aplicación
streamlit run app.py