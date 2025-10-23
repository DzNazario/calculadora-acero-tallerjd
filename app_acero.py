# app_acero_editable.py - VERSIÓN CON EDICIÓN Y PIEZAS
import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
import io

# Configurar la página
st.set_page_config(
    page_title="Calculadora de Acero - Taller JD",
    page_icon="🏗️",
    layout="wide"
)

# CSS personalizado MEJORADO - COLORES VISIBLES
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
        font-weight: bold;
    }
    .metric-card {
        background-color: #ffffff;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #1f77b4;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin-bottom: 1rem;
        border: 1px solid #e0e0e0;
    }
    .metric-title {
        color: #333333 !important;
        font-weight: bold;
        font-size: 1.1rem;
        margin-bottom: 0.5rem;
    }
    .metric-value {
        color: #1f77b4;
        font-size: 1.8rem;
        font-weight: bold;
        margin: 0;
    }
    .metric-subvalue {
        color: #2ca02c;
        font-size: 1.2rem;
        font-weight: bold;
        margin: 0.5rem 0 0 0;
    }
    .section-title {
        color: #1f77b4;
        border-bottom: 3px solid #1f77b4;
        padding-bottom: 0.5rem;
        margin-top: 1rem;
        margin-bottom: 1rem;
        font-weight: bold;
    }
    .edit-buttons {
        margin-top: 1rem;
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

class CalculadoraAcero:
    def __init__(self):
        if 'df' not in st.session_state:
            st.session_state.df = pd.DataFrame(columns=[
                'elemento', 'localizacion', 'eje', 'grilla', 'diametro', 
                'refuerzo', 'longitud', 'lg1', 'lg2', 'piezas', 'elementos'
            ])
    
    def agregar_elemento(self, datos):
        nuevo_registro = pd.DataFrame([datos])
        st.session_state.df = pd.concat([st.session_state.df, nuevo_registro], ignore_index=True)
    
    def eliminar_elemento(self, index):
        st.session_state.df = st.session_state.df.drop(index).reset_index(drop=True)
    
    def editar_elemento(self, index, datos):
        for col, valor in datos.items():
            st.session_state.df.at[index, col] = valor
    
    def calcular_totales(self):
        if st.session_state.df.empty:
            return {}
        
        resultados = {}
        df_temp = st.session_state.df.copy()
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
    
    # Inicializar calculadora
    calculadora = CalculadoraAcero()
    
    # Sidebar para entrada de datos
    with st.sidebar:
        st.markdown("### ➕ NUEVO ELEMENTO")
        
        with st.form("nuevo_elemento"):
            elemento = st.text_input("Elemento*", placeholder="Zapata A1")
            localizacion = st.text_input("Localización", placeholder="Cimentación")
            eje = st.text_input("Eje", placeholder="A")
            grilla = st.text_input("Grilla", placeholder="1")
            diametro = st.selectbox("Diámetro (ø)*", options=list(PESOS_VARILLA.keys()))
            refuerzo = st.selectbox("Tipo de Refuerzo*", options=ELEMENTOS)
            
            col1, col2 = st.columns(2)
            with col1:
                longitud = st.number_input("Longitud (m)*", min_value=0.0, step=0.1, value=1.0)
            with col2:
                piezas = st.number_input("Piezas*", min_value=1, step=1, value=1)
            
            col3, col4 = st.columns(2)
            with col3:
                lg1 = st.number_input("Gancho 1 (m)", min_value=0.0, step=0.1, value=0.0)
            with col4:
                lg2 = st.number_input("Gancho 2 (m)", min_value=0.0, step=0.1, value=0.0)
            
            elementos = st.number_input("Elementos*", min_value=1, step=1, value=1)
            
            submitted = st.form_submit_button("✅ AGREGAR ELEMENTO")
            
            if submitted:
                if not elemento:
                    st.error("❌ El campo 'Elemento' es obligatorio")
                else:
                    datos = {
                        'elemento': elemento,
                        'localizacion': localizacion,
                        'eje': eje,
                        'grilla': grilla,
                        'diametro': diametro,
                        'refuerzo': refuerzo,
                        'longitud': longitud,
                        'lg1': lg1,
                        'lg2': lg2,
                        'piezas': piezas,
                        'elementos': elementos
                    }
                    calculadora.agregar_elemento(datos)
                    st.success("✅ Elemento agregado!")
                    st.rerun()

    # Layout principal
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 📋 ELEMENTOS REGISTRADOS")
        
        if not st.session_state.df.empty:
            # Mostrar tabla con cálculos
            df_display = st.session_state.df.copy()
            df_display['longitud_total'] = df_display['longitud'] + df_display['lg1'] + df_display['lg2']
            df_display['subtotal_ml'] = df_display['longitud_total'] * df_display['piezas'] * df_display['elementos']
            
            # Mostrar tabla
            st.dataframe(df_display, use_container_width=True, height=400)
            
            # SECCIÓN DE EDICIÓN
            st.markdown("### ✏️ EDITAR ELEMENTO")
            col_edit1, col_edit2 = st.columns(2)
            
            with col_edit1:
                indices = list(range(len(st.session_state.df)))
                elemento_a_editar = st.selectbox("Selecciona elemento a editar:", indices, format_func=lambda x: f"Fila {x+1}: {st.session_state.df.iloc[x]['elemento']}")
            
            with col_edit2:
                st.write("")  # Espacio
                if st.button("🗑️ ELIMINAR ELEMENTO"):
                    calculadora.eliminar_elemento(elemento_a_editar)
                    st.success("✅ Elemento eliminado!")
                    st.rerun()
            
            # Formulario de edición
            with st.form("editar_elemento"):
                st.write("**Editar datos:**")
                col_edit3, col_edit4 = st.columns(2)
                
                with col_edit3:
                    nuevo_elemento = st.text_input("Elemento", value=st.session_state.df.iloc[elemento_a_editar]['elemento'])
                    nuevo_diametro = st.selectbox("Diámetro", options=list(PESOS_VARILLA.keys()), index=list(PESOS_VARILLA.keys()).index(st.session_state.df.iloc[elemento_a_editar]['diametro']))
                    nueva_longitud = st.number_input("Longitud", min_value=0.0, step=0.1, value=float(st.session_state.df.iloc[elemento_a_editar]['longitud']))
                    nuevo_lg1 = st.number_input("Gancho 1", min_value=0.0, step=0.1, value=float(st.session_state.df.iloc[elemento_a_editar]['lg1']))
                
                with col_edit4:
                    nueva_localizacion = st.text_input("Localización", value=st.session_state.df.iloc[elemento_a_editar]['localizacion'])
                    nuevo_refuerzo = st.selectbox("Refuerzo", options=ELEMENTOS, index=ELEMENTOS.index(st.session_state.df.iloc[elemento_a_editar]['refuerzo']))
                    nuevas_piezas = st.number_input("Piezas", min_value=1, step=1, value=int(st.session_state.df.iloc[elemento_a_editar]['piezas']))
                    nuevo_lg2 = st.number_input("Gancho 2", min_value=0.0, step=0.1, value=float(st.session_state.df.iloc[elemento_a_editar]['lg2']))
                
                nuevos_elementos = st.number_input("Elementos", min_value=1, step=1, value=int(st.session_state.df.iloc[elemento_a_editar]['elementos']))
                
                edit_submitted = st.form_submit_button("💾 GUARDAR CAMBIOS")
                
                if edit_submitted:
                    datos_editados = {
                        'elemento': nuevo_elemento,
                        'localizacion': nueva_localizacion,
                        'diametro': nuevo_diametro,
                        'refuerzo': nuevo_refuerzo,
                        'longitud': nueva_longitud,
                        'lg1': nuevo_lg1,
                        'lg2': nuevo_lg2,
                        'piezas': nuevas_piezas,
                        'elementos': nuevos_elementos
                    }
                    calculadora.editar_elemento(elemento_a_editar, datos_editados)
                    st.success("✅ Cambios guardados!")
                    st.rerun()
            
            # Botones de acción
            st.markdown("---")
            col_btn1, col_btn2, col_btn3 = st.columns(3)
            
            with col_btn1:
                # Exportar a Excel
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='openpyxl') as writer:
                    # Hoja de cuantificación
                    st.session_state.df.to_excel(writer, sheet_name='CUANTIFICACION', index=False)
                    
                    # Hoja de resumen
                    resultados = calculadora.calcular_totales()
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
            
            with col_btn2:
                if st.button("🗑️ LIMPIAR TODO", use_container_width=True):
                    st.session_state.df = pd.DataFrame(columns=[
                        'elemento', 'localizacion', 'eje', 'grilla', 'diametro', 
                        'refuerzo', 'longitud', 'lg1', 'lg2', 'piezas', 'elementos'
                    ])
                    st.rerun()
                    
            with col_btn3:
                st.metric("Elementos", len(st.session_state.df))
                
        else:
            st.info("👆 Usa el formulario para agregar elementos")
            st.write("---")
            st.write("### 💡 Instrucciones:")
            st.write("1. Completa el formulario a la izquierda")
            st.write("2. Haz clic en 'AGREGAR ELEMENTO'")
            st.write("3. Los cálculos se actualizan automáticamente")
            st.write("4. Puedes editar o eliminar elementos después")
            st.write("5. Descarga tu Excel al finalizar")

    with col2:
        st.markdown("### 📊 RESUMEN DEL PROYECTO")
        
        if not st.session_state.df.empty:
            resultados = calculadora.calcular_totales()
            
            # Métricas principales
            total_kg = sum([resultados[d]['kg_total'] for d in resultados])
            total_ml = sum([resultados[d]['ml_total'] for d in resultados])
            total_piezas = sum([resultados[d]['piezas_12m'] for d in resultados])
            
            # Tarjetas de métricas CON TEXTO VISIBLE
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">📏 METROS LINEALES</div>
                <div class="metric-value">{total_ml:,.1f} ML</div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">⚖️ PESO TOTAL</div>
                <div class="metric-value">{total_kg:,.1f} KG</div>
                <div class="metric-subvalue">{total_kg/1000:,.2f} Toneladas</div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">📦 PIEZAS DE 12m</div>
                <div class="metric-value">{total_piezas:.0f}</div>
                <div style="color: #666; font-size: 0.8rem; margin-top: 0.5rem;">Total de varillas necesarias</div>
            </div>
            """, unsafe_allow_html=True)
            
            # Resumen por diámetro
            st.markdown("### 🔍 DETALLE POR DIÁMETRO")
            for diametro, datos in resultados.items():
                with st.expander(f"Diámetro {diametro} - {datos['kg_total']:,.1f} KG", expanded=True):
                    st.write(f"**Metros Lineales:** {datos['ml_total']:,.1f} ML")
                    st.write(f"**Peso Total:** {datos['kg_total']:,.1f} KG")
                    st.write(f"**Piezas de 12m:** {datos['piezas_12m']:.0f}")
                    
        else:
            # Estado inicial - métricas en cero CON TEXTO VISIBLE
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">📏 METROS LINEALES</div>
                <div class="metric-value">0.0 ML</div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">⚖️ PESO TOTAL</div>
                <div class="metric-value">0.0 KG</div>
                <div class="metric-subvalue">0.00 Toneladas</div>
            </div>
            """, unsafe_allow_html=True)
            
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">📦 PIEZAS DE 12m</div>
                <div class="metric-value">0</div>
                <div style="color: #666; font-size: 0.8rem; margin-top: 0.5rem;">Total de varillas necesarias</div>
            </div>
            """, unsafe_allow_html=True)
            
            st.info("Agrega elementos para ver resultados detallados")

    # Footer
    st.markdown("---")
    st.caption(f"**🏗️ Calculadora de Acero - Taller JD** • {datetime.now().strftime('%d/%m/%Y %H:%M')}")

if __name__ == "__main__":
    main()