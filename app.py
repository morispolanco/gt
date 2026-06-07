import streamlit as st
from openai import OpenAI
from datetime import datetime
from fpdf import FPDF
import re

# ═══════════════════════════════════════════════════════════════════════
# CONFIGURACIÓN DE PÁGINA
# ═══════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="GuateEmprende IA Pro 🇬🇹",
    page_icon="📈",
    layout="wide"
)

fecha_hoy = datetime.now().strftime("%d de %B de %Y")
año_actual = datetime.now().year

# ═══════════════════════════════════════════════════════════════════════
# API KEY (OPENROUTER)
# ═══════════════════════════════════════════════════════════════════════
api_key = st.secrets.get("OPENROUTER_API_KEY", "")
base_url = "https://openrouter.ai/api/v1"

if not api_key:
    st.error("⚠️ Agrega OPENROUTER_API_KEY en los Secrets de Streamlit.")
    st.stop()

client = OpenAI(api_key=api_key, base_url=base_url)

# Modelo fijo
MODELO = "openai/gpt-oss-20b:free"

# ═══════════════════════════════════════════════════════════════════════
# GENERADOR DE PDF PROFESIONAL
# ═══════════════════════════════════════════════════════════════════════
class ConsultorPDF(FPDF):
    def header(self):
        self.set_font('Helvetica', 'B', 12)
        self.set_text_color(26, 95, 42)
        self.cell(0, 10, 'GUATEEMPRENDE IA PRO', 0, 0, 'L')
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
        self.cell(0, 10, f'Pagina {self.page_no()} | GuateEmprende IA Pro', 0, 0, 'C')

def generar_pdf(titulo, contenido):
    pdf = ConsultorPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    pdf.set_font('Helvetica', 'B', 16)
    pdf.set_text_color(20, 20, 20)
    pdf.multi_cell(0, 10, titulo.upper(), align='C')
    pdf.ln(5)
    pdf.set_font('Helvetica', '', 10)
    pdf.set_text_color(40, 40, 40)

    for linea in contenido.split('\n'):
        linea = linea.strip()
        if not linea:
            pdf.ln(2)
            continue
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
            pdf.set_font('Courier', '', 7)
            pdf.multi_cell(0, 4, linea)
            pdf.set_font('Helvetica', '', 10)
        else:
            texto = linea.replace('**', '').replace('__', '').replace('*', '')
            pdf.multi_cell(0, 5, texto)

    return pdf.output(dest='S').encode('latin-1', errors='replace')

# ═══════════════════════════════════════════════════════════════════════
# INTERFAZ PRINCIPAL
# ═══════════════════════════════════════════════════════════════════════
st.markdown(f"""
    <div style="background-color:#1a5f2a; padding:20px; border-radius:10px; text-align:center;">
        <h1 style="color:white; margin:0;">🇬🇹 GuateEmprende IA Pro</h1>
        <p style="color:#d4edda; margin:5px;">
            Consultor de Negocios Inteligente | {fecha_hoy} |
            Motor: {MODELO}
        </p>
    </div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.header("⚙️ Configuración")
    st.success(f"Modelo activo: `{MODELO}`")
    st.info("Desarrollado para emprendedores guatemaltecos.")

def llamar_ia(sistema, usuario):
    try:
        with st.spinner("Analizando con IA..."):
            res = client.chat.completions.create(
                model=MODELO,
                messages=[
                    {"role": "system", "content": sistema},
                    {"role": "user", "content": usuario}
                ],
                temperature=0.4
            )
            return res.choices[0].message.content
    except Exception as e:
        st.error(f"Error: {e}")
        return None

# ═══════════════════════════════════════════════════════════════════════
# PESTAÑAS
# ═══════════════════════════════════════════════════════════════════════
tab1, tab2, tab3, tab4 = st.tabs(["📍 Ubicación", "💵 Capital", "🏬 Nichos Local", "📋 Plan de Negocios"])

# ── TAB 1: UBICACIÓN ──────────────────────────────────────────────────
with tab1:
    st.subheader("📍 Análisis de Ubicación Estratégica")
    negocio = st.text_input("¿Qué negocio deseas abrir?", placeholder="Ej. Cafetería, Barbería...")

    if st.button("Buscar Mejor Ubicación", type="primary"):
        if negocio:
            sis = f"Eres experto en geomarketing en Guatemala. Conoces todas las zonas comerciales de Ciudad de Guatemala y departamentos. Fecha actual: {fecha_hoy}."
            usr = f"""Analiza las 3 mejores ubicaciones para abrir una {negocio} en Guatemala.

Para cada ubicación incluye:
1. Nombre exacto de la zona
2. Nivel socioeconómico (A/B, C+, C, D)
3. Tráfico peatonal y vehicular estimado
4. Costo de alquiler por m² aproximado (Q/mes)
5. Perfil del cliente
6. Nivel de competencia
7. Puntaje de viabilidad 1-10

Usa tablas Markdown. Sé específico con datos de mercado actuales."""
            resultado = llamar_ia(sis, usr)
            if resultado:
                st.markdown(resultado)
                pdf_data = generar_pdf(f"Ubicacion: {negocio}", resultado)
                st.download_button("📄 Descargar PDF", data=pdf_data, file_name=f"ubicacion_{negocio[:15]}.pdf", mime="application/pdf")
        else:
            st.warning("Ingresa el tipo de negocio.")

# ── TAB 2: CAPITAL ───────────────────────────────────────────────────
with tab2:
    st.subheader("💵 Inversión por Capital")
    monto = st.number_input("Capital disponible (Q):", min_value=1000, value=50000, step=1000)

    if st.button("Ver Oportunidades", type="primary"):
        sis = f"Eres analista financiero senior especializado en PYMES en Guatemala. Conoces márgenes de ganancia, costos operativos y tendencias de {año_actual}."
        usr = f"""Con un capital de Q{monto:,.0f}, recomenda los 3 negocios más rentables en Guatemala para {fecha_hoy}.

Para cada negocio incluye:
1. Nombre del negocio
2. Distribución del capital (tabla: alquiler, equipos, inventario, marketing, trámites, caja)
3. Proyección de ingresos mensuales (meses 1-6)
4. Punto de equilibrio estimado
5. ROI a 12 meses
6. Margen de ganancia bruto estimado
7. Principal riesgo en Guatemala y cómo mitigarlo

Usa tablas Markdown con números específicos."""

        resultado = llamar_ia(sis, usr)
        if resultado:
            st.markdown(resultado)
            pdf_data = generar_pdf(f"Inversion Q{monto:,.0f}", resultado)
            st.download_button("📄 Descargar PDF", data=pdf_data, file_name=f"inversion_q{monto:,.0f}.pdf", mime="application/pdf")

# ── TAB 3: NICHOS ────────────────────────────────────────────────────
with tab3:
    st.subheader("🏬 Nichos de Mercado por Zona")
    zona = st.text_input("Ingresa zona o municipio:", placeholder="Ej. Zona 18, Mixco, Antigua, Quetzaltenango...")

    if st.button("Identificar Nichos", type="primary"):
        if zona:
            sis = f"Eres consultor de desarrollo económico local en Guatemala. Conoces la demografía y商业模式 de cada zona del país. Fecha: {fecha_hoy}."
            usr = f"""Para la ubicación '{zona}' en Guatemala, identifica 3 negocios que tengan alta demanda y baja oferta (nichos).

Para cada nicho incluye:
1. Nombre del negocio sugerido
2. Necesidad insatisfecha que resuelve
3. Perfil demográfico del cliente objetivo
4. Población estimada en el radio de 1-3 km
5. Competencia directa actual (cuántos hay a 500m)
6. Inversión aproximada para arrancar
7. Principal barrera de entrada en esa zona
8. Potencial de escalamiento

Sé muy específico de la zona. No sugieras negocios genéricos."""

            resultado = llamar_ia(sis, usr)
            if resultado:
                st.markdown(resultado)
                pdf_data = generar_pdf(f"Nichos: {zona}", resultado)
                st.download_button("📄 Descargar PDF", data=pdf_data, file_name=f"nichos_{zona[:15]}.pdf", mime="application/pdf")
        else:
            st.warning("Ingresa la zona.")

# ── TAB 4: PLAN DE NEGOCIOS ───────────────────────────────────────────
with tab4:
    st.subheader("📋 Generador de Plan de Negocios")

    with st.container():
        col1, col2 = st.columns(2)
        with col1:
            idea = st.text_input("Idea de negocio:", placeholder="Ej. Cafetería de especialidad")
            ubic = st.text_input("Ubicación:", placeholder="Ej. Zona 15, Guatemala")
        with col2:
            cap = st.text_input("Capital (Q):", placeholder="Ej. Q75,000")
            tipo = st.selectbox("Tipo de constitución:",
                              ["Empresa Individual", "S.A.", "S.R.L.", "Pequeño Contribuyente"])
        diferenciador = st.text_area("Diferenciador (qué te hace diferente):", height=80)

    if st.button("Generar Plan Completo", type="primary"):
        if idea:
            sis = f"Eres consultor senior de negocios en Guatemala. Experto en trámites del Registro Mercantil, SAT, IGSS y proyecciones financieras. Fecha: {fecha_hoy}."
            usr = f"""Crea un plan de negocios profesional para Guatemala:

NEGOCIO: {idea}
UBICACIÓN: {ubic}
CAPITAL: {cap}
CONSTITUCIÓN: {tipo}
DIFERENCIADOR: {diferenciador or 'No especificado'}

ESTRUCTURA DEL PLAN:

1. RESUMEN EJECUTIVO (200 palabras)

2. ANÁLISIS DE MERCADO
- Tamaño del mercado en Guatemala (estimado)
- Competidores principales (5 nombres ficticios con ubicación y precio)
- Análisis FODA

3. MARKETING DIGITAL EN GUATEMALA
- Estrategia Facebook/Instagram/WhatsApp
- Presupuesto mensual recomendado
- KPIs principales

4. PLAN DE OPERACIONES
- Horario sugerido
- Proveedores clave en GT
- Herramientas tecnológicas

5. ESTRUCTURA LEGAL Y TRÁMITES (TABLA OBLIGATORIA)
| Trámite | Entidad | Costo (Q) | Tiempo | Prioridad |
|---|---|---|---|---|
| Constitución | Registro Mercantil | [estimado] | X días | Alta |
| RTU | SAT | Gratis | X días | Alta |
| Licencia municipal | Alcaldía | [estimado] | X días | Alta |
| Patrón IGSS | IGSS | [X%] planilla | - | Alta |
| Patrón INTECAP | INTECAP | [X%] planilla | - | Media |

6. PROYECCIÓN FINANCIERA (TABLA)
- Tabla de inversión inicial detallada
- Flujo de caja meses 1-12
- Punto de equilibrio
- ROI 12 y 24 meses

7. ANÁLISIS DE RIESGOS
- 3 riesgos principales específicos de Guatemala
- Plan de mitigación

8. PLAN DE IMPLEMENTACIÓN (30 DÍAS)
- Checklist semana por semana

Usa tablas Markdown. Sé profesional y realista."""

            resultado = llamar_ia(sis, usr)
            if resultado:
                st.markdown(resultado)
                pdf_data = generar_pdf(f"Plan: {idea}", resultado)
                st.download_button("📄 Descargar Plan PDF", data=pdf_data, file_name=f"plan_{idea[:15]}.pdf", mime="application/pdf")
        else:
            st.warning("Ingresa la idea de negocio.")

# ═══════════════════════════════════════════════════════════════════════
# FOOTER
# ═══════════════════════════════════════════════════════════════════════
st.markdown("---")
st.markdown(f"""
    <div style="text-align:center; padding:15px; background:#f8f9fa; border-radius:8px;">
        <p style="color:#666; margin:0;">
            🇬🇹 <strong>GuateEmprende IA Pro</strong> | Guatemala {año_actual} |
            Motor: {MODELO} | OpenRouter
        </p>
        <p style="color:#999; font-size:0.8em; margin:3px;">
            Datos generados por IA. Verificar con profesionales antes de invertir.
        </p>
    </div>
""", unsafe_allow_html=True)
