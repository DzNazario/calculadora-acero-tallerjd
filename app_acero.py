# app_acero_simple.py - VERSIÓN MÍNIMA Y ESTABLE
import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime

# Configuración básica
st.set_page_config(page_title="Calculadora Acero", layout="wide")

st.title("🏗️ CALCULADORA DE ACERO - TALLER JD")

# Datos básicos
PESOS_VARILLA = {3: 0.557, 4: 0.996, 6: 2.25}
ELEMENTOS = ["zapata", "losa", "viga", "columna"]

# Inicializar datos
if 'elementos' not in st.session_state:
    st.session_state.elementos = []

# Formulario simple
with st.sidebar:
    st.header("➕ AGREGAR ELEMENTO")
    
    with st.form("elemento_form"):
        elemento = st.text_input("Elemento", "Zapata A1")
        diametro = st.selectbox("Diámetro", [3, 4, 6])
        refuerzo = st.selectbox("Tipo", ELEMENTOS)
        longitud = st.number_input("Longitud (m)", 1.0, 10.0, 2.0)
        piezas = st.number_input("Piezas", 1, 100, 4)
        
        if st.form_submit_button("AGREGAR"):
            nuevo = {
                'elemento': elemento,
                'diametro': diametro,
                'refuerzo': refuerzo,
                'longitud': longitud,
                'piezas': piezas,
                'ml_totales': longitud * piezas,
                'kg_totales': (longitud * piezas) * PESOS_VARILLA[diametro]
            }
            st.session_state.elementos.append(nuevo)
            st.success("✅ Agregado!")

# Mostrar datos
if st.session_state.elementos:
    st.header("📋 ELEMENTOS AGREGADOS")
    df = pd.DataFrame(st.session_state.elementos)
    st.dataframe(df)
    
    # Cálculos
    total_ml = df['ml_totales'].sum()
    total_kg = df['kg_totales'].sum()
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("📏 ML TOTALES", f"{total_ml:.1f}")
    with col2:
        st.metric("⚖️ KG TOTALES", f"{total_kg:.1f}")
    with col3:
        st.metric("📦 TN TOTALES", f"{total_kg/1000:.2f}")
    
    # Botón limpiar
    if st.button("🗑️ LIMPIAR TODO"):
        st.session_state.elementos = []
        st.rerun()
else:
    st.info("👈 Usa el formulario para agregar elementos")

st.caption("🏗️ Taller JD - Calculadora de Acero")

