import streamlit as st
from openai import OpenAI
from datetime import datetime
from fpdf import FPDF
import re
from io import BytesIO

# ═══════════════════════════════════════════════════════════════════════
# CONFIGURACIÓN DE PÁGINA Y ESTILOS
# ═══════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="GuateEmprende IA Pro 🇬🇹",
    page_icon="📈",
    layout="wide"
)

# Fecha dinámica para la IA
fecha_hoy = datetime.now().strftime("%d de %B de %Y")
año_actual = datetime.now().year

# ═══════════════════════════════════════════════════════════════════════
# GESTIÓN DE API (OPENROUTER)
# ═══════════════════════════════════════════════════════════════════════
# Se espera que OPENROUTER_API_KEY esté en Streamlit Secrets
api_key = st.secrets.get("OPENROUTER_API_KEY", "")
base_url = "https://openrouter.ai/api/v1"

if not api_key:
    st.error("⚠️ Configuración requerida: Agrega OPENROUTER_API_KEY en los Secrets de Streamlit.")
    st.stop()

client = OpenAI(api_key=api_key, base_url=base_url)

# ═══════════════════════════════════════════════════════════════════════
# CLASE PARA GENERACIÓN DE PDF PROFESIONAL
# ═══════════════════════════════════════════════════════════════════════
class ConsultorPDF(FPDF):
    def header(self):
        self.set_font('Helvetica', 'B', 12)
        self.set_text_color(26, 95, 42) # Verde Guatemala
        self.cell(0, 10, 'GUATEEMPRENDE IA PRO - CONSULTORÍA', 0, 0, 'L')
        self.set_font('Helvetica', '', 8)
        self.set_text_color(100, 100, 100)
        self.cell(0, 10, f'Fecha: {fecha_hoy}', 0, 0, 'R')
        self.ln(12)
        self.set_draw_color(26, 95, 42)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(8)

    def footer(self):
        self.set_y(-15)
        self.set_font('Helvetica', 'I', 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f'Página {self.page_no()} | GuateEmprende IA - El reporte es una estimación basada en IA.', 0, 0, 'C')

def generar_pdf_binario(titulo_doc, contenido_md):
    pdf = ConsultorPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    # Título
    pdf.set_font('Helvetica', 'B', 16)
    pdf.set_text_color(20, 20, 20)
    pdf.multi_cell(0, 10, titulo_doc.upper(), align='C')
    pdf.ln(5)

    # Procesamiento básico de Markdown a PDF
    pdf.set_font('Helvetica', '', 10)
    pdf.set_text_color(40, 40, 40)

    lineas = contenido_md.split('\n')
    for linea in lineas:
        linea = linea.strip()
        if not linea:
            pdf.ln(2)
            continue

        # Formateo de encabezados
        if linea.startswith('###'):
            pdf.set_font('Helvetica', 'B', 11)
            pdf.set_text_color(26, 95, 42)
            pdf.multi_cell(0, 7, linea.replace('###', '').strip())
            pdf.set_text_color(40, 40, 40)
            pdf.set_font('Helvetica', '', 10)
        elif linea.startswith('##'):
            pdf.set_font('Helvetica', 'B', 13)
            pdf.ln(2)
            pdf.multi_cell(0, 8, linea.replace('##', '').strip())
            pdf.set_font('Helvetica', '', 10)
        elif linea.startswith('|'):
            # Representación simple de tablas
            pdf.set_font('Courier', '', 8)
            pdf.multi_cell(0, 4, linea)
            pdf.set_font('Helvetica', '', 10)
        else:
            # Limpiar negritas de MD para el PDF
            texto_limpio = linea.replace('**', '').replace('__', '')
            pdf.multi_cell(0, 5, texto_limpio)

    return pdf.output()

# ═══════════════════════════════════════════════════════════════════════
# LÓGICA DE INTERFAZ Y CONSULTAS
# ═══════════════════════════════════════════════════════════════════════
st.markdown(f"""
    <div style="background-color:#1a5f2a; padding:20px; border-radius:10px; text-align:center;">
        <h1 style="color:white; margin:0;">🇬🇹 GuateEmprende IA Pro</h1>
        <p style="color:#d4edda; margin:5px;">Consultor de Negocios | Fecha: {fecha_hoy}</p>
    </div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.header("⚙️ Configuración")
    modelo = st.selectbox("Motor de IA (OpenRouter):",
                         ["z-ai/glm-4-9b-chat:free", "meta-llama/llama-3-8b-instruct:free"])
    st.info("Este consultor utiliza datos macroeconómicos de Guatemala actualizados para sus proyecciones.")

def llamar_ia(prompt_sistema, prompt_usuario):
    try:
        with st.spinner("Analizando datos de mercado..."):
            res = client.chat.completions.create(
                model=modelo,
                messages=[
                    {"role": "system", "content": prompt_sistema},
                    {"role": "user", "content": prompt_usuario}
                ],
                temperature=0.4
            )
            return res.choices[0].message.content
    except Exception as e:
        st.error(f"Error de conexión: {e}")
        return None

# PESTAÑAS
tab1, tab2, tab3, tab4 = st.tabs(["📍 Ubicación", "💵 Capital", "🏬 Nichos Local", "📋 Plan de Negocios"])

# TAB 1: UBICACIÓN
with tab1:
    st.subheader("📍 Análisis de Ubicación Estratégica")
    negocio = st.text_input("¿Qué negocio deseas abrir?", placeholder="Ej. Cafetería, Barbería...")
    if st.button("Buscar Mejor Ubicación"):
        sis = f"Eres experto en geomarketing en Guatemala. Fecha: {fecha_hoy}."
        usr = f"Dime las 3 mejores ubicaciones para un(a) {negocio} en Guatemala. Justifica con datos de NSE, tráfico y costo de alquiler por m2 al día de hoy."
        resultado = llamar_ia(sis, usr)
        if resultado:
            st.markdown(resultado)
            pdf_data = generar_pdf_binario(f"Ubicación: {negocio}", resultado)
            st.download_button("Descargar Reporte PDF", data=pdf_data, file_name="ubicacion_gt.pdf", mime="application/pdf")

# TAB 2: CAPITAL
with tab2:
    st.subheader("💵 Inversión por Capital")
    monto = st.number_input("Capital disponible (Q):", min_value=1000, value=50000)
    if st.button("Ver Oportunidades"):
        sis = f"Analista financiero de PYMES en Guatemala. Año {año_actual}."
        usr = f"Con un capital de Q{monto}, ¿qué 3 negocios son más rentables hoy en Guatemala? Incluye tabla de inversión, ROI estimado y punto de equilibrio."
        resultado = llamar_ia(sis, usr)
        if resultado:
            st.markdown(resultado)
            pdf_data = generar_pdf_binario(f"Inversión de Q{monto}", resultado)
            st.download_button("Descargar Análisis Financiero PDF", data=pdf_data, file_name="inversion_gt.pdf", mime="application/pdf")

# TAB 3: NICHOS
with tab3:
    st.subheader("🏬 Nichos de Mercado por Zona")
    zona = st.text_input("Ingresa una zona o municipio:", placeholder="Ej. Zona 18, Mixco, Antigua...")
    if st.button("Identificar Nichos"):
        sis = f"Consultor de desarrollo local en Guatemala. Fecha: {fecha_hoy}."
        usr = f"Para la ubicación {zona}, identifica 3 negocios que falten o tengan alta demanda insatisfecha. Justifica con datos demográficos y brechas de mercado actuales."
        resultado = llamar_ia(sis, usr)
        if resultado:
            st.markdown(resultado)
            pdf_data = generar_pdf_binario(f"Nichos en {zona}", resultado)
            st.download_button("Descargar Diagnóstico PDF", data=pdf_data, file_name="nichos_gt.pdf", mime="application/pdf")

# TAB 4: PLAN DE NEGOCIOS
with tab4:
    st.subheader("📋 Generador de Plan de Negocios")
    col1, col2 = st.columns(2)
    with col1:
        idea = st.text_input("Idea de negocio:", key="p1")
        ubi = st.text_input("Ubicación prevista:", key="p2")
    with col2:
        cap = st.text_input("Capital estimado:", key="p3")
        soc = st.selectbox("Tipo de sociedad:", ["Empresa Individual", "S.A.", "Pequeño Contribuyente"])

    if st.button("Generar Plan Completo"):
        sis = f"Consultor senior de negocios en Guatemala. Experto en SAT y Registro Mercantil. Fecha: {fecha_hoy}."
        usr = f"Crea un plan de negocios para '{idea}' en '{ubi}' con un capital de '{cap}'. Incluye: Resumen, Tabla de trámites legales en Guatemala (SAT/Registro Mercantil), Costos operativos y Estrategia de Marketing."
        resultado = llamar_ia(sis, usr)
        if resultado:
            st.markdown(resultado)
            pdf_data = generar_pdf_binario(f"Plan de Negocio: {idea}", resultado)
            st.download_button("Descargar Plan de Negocios PDF", data=pdf_data, file_name="plan_negocio_gt.pdf", mime="application/pdf")

st.markdown("---")
st.caption(f"© {año_actual} GuateEmprende IA - Datos para fines informativos basados en proyecciones de inteligencia artificial.")
