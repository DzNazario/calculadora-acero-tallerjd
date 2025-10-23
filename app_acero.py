# app_acero_produccion.py - VERSIÓN ESTABLE PARA STREAMLIT CLOUD
import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import io

# Configuración mínima y estable
st.set_page_config(
    page_title="Calculadora de Acero - Taller JD",
    page_icon="🏗️",
    layout="wide"
)

# CSS simplificado
st.markdown("""
<style>
    .main-header {
        font-size: 2rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
        font-weight: bold;
    }
    .metric-card {
        background-color: #ffffff;
        padding: 1rem;
        border-radius: 8px;
        border-left: 4px solid #1f77b4;
        margin-bottom: 1rem;
        border: 1px solid #e0e0e0;
    }
</style>
""", unsafe_allow_html=True)

# Datos de referencia
PESOS_VARILLA = {
    2: 0.248, 3: 0.557, 4: 0.996, 
    5: 1.56, 6: 2.25, 8: 3.975, 
    10: 6.225, 12: 8.938
}

ELEMENTOS = ["zapata", "losa", "viga", "columna", "dala", "castillo", "muro"]

# Inicialización segura de session_state
if 'df_acero' not in st.session_state:
    st.session_state.df_acero = pd.DataFrame(columns=[
        'elemento', 'localizacion', 'eje', 'grilla', 'diametro', 
        'refuerzo', 'longitud', 'lg1', 'lg2', 'piezas', 'elementos'
    ])

if 'edit_index' not in st.session_state:
    st.session_state.edit_index = 0

def calcular_totales(df):
    if df.empty:
        return {}
    
    resultados = {}
    df_temp = df.copy()
    df_temp['longitud_total'] = df_temp['longitud'] + df_temp['lg1'] + df_temp['lg2']
    df_temp['subtotal_ml'] = df_temp['longitud_total'] * df_temp['piezas'] * df_temp['elementos']
    
    for diametro in df_temp['diametro'].unique():
        ml_total = df_temp[df_temp['diametro'] == diametro]['subtotal_ml'].sum()
        kg_total = ml_total * PESOS_VARILLA.get(diametro, 0)
        piezas_12m = np.ceil(ml_total / 12)
        
        resultados[diametro] = {
            'ml_total': ml_total,
            'kg_total': kg_total,
            'piezas_12m': piezas_12m
        }
    
    return resultados

def main():
    # Header principal
    st.markdown('<h1 class="main-header">🏗️ CALCULADORA DE ACERO - TALLER JD</h1>', unsafe_allow_html=True)
    
    # Sidebar para entrada de datos
    with st.sidebar:
        st.markdown("### ➕ NUEVO ELEMENTO")
        
        with st.form("nuevo_elemento", clear_on_submit=True):
            elemento = st.text_input("Elemento*", placeholder="Zapata A1")
            
            col1, col2 = st.columns(2)
            with col1:
                localizacion = st.text_input("Localización", placeholder="Cimentación")
            with col2:
                diametro = st.selectbox("Diámetro (ø)*", options=list(PESOS_VARILLA.keys()))
            
            refuerzo = st.selectbox("Tipo de Refuerzo*", options=ELEMENTOS)
            
            col3, col4 = st.columns(2)
            with col3:
                longitud = st.number_input("Longitud (m)*", min_value=0.0, step=0.1, value=1.0)
            with col4:
                piezas = st.number_input("Piezas*", min_value=1, step=1, value=1)
            
            col5, col6 = st.columns(2)
            with col5:
                lg1 = st.number_input("Gancho 1 (m)", min_value=0.0, step=0.1, value=0.0)
            with col6:
                lg2 = st.number_input("Gancho 2 (m)", min_value=0.0, step=0.1, value=0.0)
            
            elementos = st.number_input("Elementos*", min_value=1, step=1, value=1)
            
            submitted = st.form_submit_button("✅ AGREGAR ELEMENTO")
            
            if submitted:
                if not elemento:
                    st.error("❌ El campo 'Elemento' es obligatorio")
                else:
                    nuevo_registro = pd.DataFrame([{
                        'elemento': elemento,
                        'localizacion': localizacion,
                        'eje': '',
                        'grilla': '',
                        'diametro': diametro,
                        'refuerzo': refuerzo,
                        'longitud': longitud,
                        'lg1': lg1,
                        'lg2': lg2,
                        'piezas': piezas,
                        'elementos': elementos
                    }])
                    
                    st.session_state.df_acero = pd.concat([st.session_state.df_acero, nuevo_registro], ignore_index=True)
                    st.success("✅ Elemento agregado!")

    # Layout principal
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 📋 ELEMENTOS REGISTRADOS")
        
        if not st.session_state.df_acero.empty:
            # Mostrar tabla
            df_display = st.session_state.df_acero.copy()
            st.dataframe(df_display, use_container_width=True, height=300)
            
            # Sección de gestión
            with st.expander("✏️ GESTIÓN DE ELEMENTOS", expanded=False):
                col_sel, col_del = st.columns([2, 1])
                
                with col_sel:
                    indices = list(range(len(st.session_state.df_acero)))
                    st.session_state.edit_index = st.selectbox(
                        "Selecciona elemento:",
                        indices,
                        format_func=lambda x: f"{x+1}. {st.session_state.df_acero.iloc[x]['elemento']}"
                    )
                
                with col_del:
                    st.write("")
                    if st.button("🗑️ ELIMINAR", use_container_width=True):
                        st.session_state.df_acero = st.session_state.df_acero.drop(st.session_state.edit_index).reset_index(drop=True)
                        st.success("✅ Elemento eliminado!")
                        st.rerun()
            
            # Botones de exportación
            st.markdown("---")
            st.markdown("### 📤 EXPORTAR DATOS")
            
            col_exp1, col_exp2 = st.columns(2)
            
            with col_exp1:
                # Exportar a Excel
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    st.session_state.df_acero.to_excel(writer, sheet_name='CUANTIFICACION', index=False)
                    resultados = calcular_totales(st.session_state.df_acero)
                    resumen_data = []
                    for diam, datos in resultados.items():
                        resumen_data.append({
                            'Diámetro': diam,
                            'Total_ML': datos['ml_total'],
                            'Total_KG': datos['kg_total'],
                            'Piezas_12m': datos['piezas_12m']
                        })
                    pd.DataFrame(resumen_data).to_excel(writer, sheet_name='RESUMEN', index=False)
                
                st.download_button(
                    label="📥 DESCARGAR EXCEL",
                    data=output.getvalue(),
                    file_name=f"acero_{datetime.now().strftime('%d%m%Y_%H%M')}.xlsx",
                    mime="application/vnd.ms-excel",
                    use_container_width=True
                )
            
            with col_exp2:
                if st.button("🗑️ LIMPIAR TODO", use_container_width=True):
                    st.session_state.df_acero = pd.DataFrame(columns=[
                        'elemento', 'localizacion', 'eje', 'grilla', 'diametro', 
                        'refuerzo', 'longitud', 'lg1', 'lg2', 'piezas', 'elementos'
                    ])
                    st.success("✅ Todos los elementos eliminados!")
                    st.rerun()
                
        else:
            st.info("👆 Usa el formulario para agregar elementos")
            st.write("---")
            st.write("**💡 Instrucciones:**")
            st.write("1. Completa el formulario a la izquierda")
            st.write("2. Haz clic en 'AGREGAR ELEMENTO'")
            st.write("3. Los cálculos se actualizan automáticamente")
            st.write("4. Descarga tu Excel al finalizar")

    with col2:
        st.markdown("### 📊 RESUMEN DEL PROYECTO")
        
        if not st.session_state.df_acero.empty:
            resultados = calcular_totales(st.session_state.df_acero)
            
            total_kg = sum([resultados[d]['kg_total'] for d in resultados])
            total_ml = sum([resultados[d]['ml_total'] for d in resultados])
            total_piezas = sum([resultados[d]['piezas_12m'] for d in resultados])
            
            # Métricas
            st.markdown(f"""
            <div class="metric-card">
                <strong>📏 METROS LINEALES</strong><br>
                <span style="color: #1f77b4; font-size: 1.5rem; font-weight: bold;">{total_ml:,.1f} ML</span>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="metric-card">
                <strong>⚖️ PESO TOTAL</strong><br>
                <span style="color: #ff7f0e; font-size: 1.5rem; font-weight: bold;">{total_kg:,.1f} KG</span><br>
                <span style="color: #2ca02c; font-weight: bold;">{total_kg/1000:,.2f} Toneladas</span>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="metric-card">
                <strong>📦 PIEZAS DE 12m</strong><br>
                <span style="color: #d62728; font-size: 1.5rem; font-weight: bold;">{total_piezas:.0f}</span><br>
                <small>Total de varillas</small>
            </div>
            """, unsafe_allow_html=True)
            
            # Detalle por diámetro
            st.markdown("**🔍 DETALLE POR DIÁMETRO**")
            for diametro, datos in resultados.items():
                with st.expander(f"Diámetro {diametro} - {datos['kg_total']:,.1f} KG"):
                    st.write(f"**ML:** {datos['ml_total']:,.1f}")
                    st.write(f"**KG:** {datos['kg_total']:,.1f}")
                    st.write(f"**Piezas 12m:** {datos['piezas_12m']:.0f}")
                    
        else:
            st.markdown(f"""
            <div class="metric-card">
                <strong>📏 METROS LINEALES</strong><br>
                <span style="color: #1f77b4; font-size: 1.5rem; font-weight: bold;">0.0 ML</span>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="metric-card">
                <strong>⚖️ PESO TOTAL</strong><br>
                <span style="color: #ff7f0e; font-size: 1.5rem; font-weight: bold;">0.0 KG</span><br>
                <span style="color: #2ca02c; font-weight: bold;">0.00 Toneladas</span>
            </div>
            """, unsafe_allow_html=True)
            
            st.info("Agrega elementos para ver resultados")

    # Footer
    st.markdown("---")
    st.caption(f"**🏗️ Calculadora de Acero - Taller JD** • {datetime.now().strftime('%d/%m/%Y %H:%M')}")

if __name__ == "__main__":
    main()
