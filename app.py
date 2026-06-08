import re
import unicodedata
from datetime import datetime

import streamlit as st
from fpdf import FPDF
from openai import OpenAI

# ═══════════════════════════════════════════════════════════════════════
# CONFIGURACIÓN DE PÁGINA
# ═══════════════════════════════════════════════════════════════════════
st.set_page_config(
    page_title="GuateEmprende IA Pro 🇬🇹",
    page_icon="📈",
    layout="wide",
)

fecha_hoy = datetime.now().strftime("%d de %B de %Y")
anio_actual = datetime.now().year

# ═══════════════════════════════════════════════════════════════════════
# API KEY (OPENROUTER)
# ═══════════════════════════════════════════════════════════════════════
api_key = st.secrets.get("OPENROUTER_API_KEY", "")
base_url = "https://openrouter.ai/api/v1"

if not api_key:
    st.error("⚠️ Agrega OPENROUTER_API_KEY en los Secrets de Streamlit.")
    st.stop()

client = OpenAI(api_key=api_key, base_url=base_url)
MODELO = "openai/gpt-oss-20b:free"

# ═══════════════════════════════════════════════════════════════════════
# FUNCIÓN PARA LIMPIAR TEXTO PARA PDF
# ═══════════════════════════════════════════════════════════════════════
def limpiar_para_pdf(texto: str) -> str:
    if not texto:
        return ""

    # Eliminar emojis
    patron_emojis = re.compile(
        "["
        "\U0001F600-\U0001F64F"
        "\U0001F300-\U0001F5FF"
        "\U0001F680-\U0001F6FF"
        "\U0001F1E0-\U0001F1FF"
        "\U00002702-\U000027B0"
        "\U000024C2-\U0001F251"
        "\U0001F900-\U0001F9FF"
        "\U0001FA00-\U0001FA6F"
        "\U0001FA70-\U0001FAFF"
        "]+",
        flags=re.UNICODE,
    )
    texto = patron_emojis.sub("", texto)

    # Reemplazar comillas y guiones frecuentes
    reemplazos = {
        "´": "'",
        "`": "'",
        "“": '"',
        "”": '"',
        "‘": "'",
        "’": "'",
        "—": "-",
        "–": "-",
        "…": "...",
        "•": "*",
        "·": "*",
    }
    for orig, repl in reemplazos.items():
        texto = texto.replace(orig, repl)

    # Normalización básica para mejorar compatibilidad con PDF
    texto = unicodedata.normalize("NFKD", texto)

    # Filtrar caracteres no imprimibles manteniendo saltos de línea
    texto_limpio = ""
    for char in texto:
        codigo = ord(char)
        if char in ["\n", "\r", "\t"]:
            texto_limpio += char
        elif 32 <= codigo <= 126:
            texto_limpio += char
        elif 160 <= codigo <= 255:
            texto_limpio += char

    return texto_limpio


# ═══════════════════════════════════════════════════════════════════════
# GENERADOR DE PDF
# ═══════════════════════════════════════════════════════════════════════
class ConsultorPDF(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 12)
        self.set_text_color(26, 95, 42)
        self.cell(0, 10, "GUATEEMPRENDE IA PRO", 0, 0, "L")
        self.set_font("Helvetica", "", 8)
        self.set_text_color(100, 100, 100)
        self.cell(0, 10, f"Fecha: {fecha_hoy}", 0, 0, "R")
        self.ln(12)
        self.set_draw_color(26, 95, 42)
        self.line(10, self.get_y(), 200, self.get_y())
        self.ln(8)

    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.set_text_color(150, 150, 150)
        self.cell(0, 10, f"Pagina {self.page_no()}", 0, 0, "C")


def generar_pdf(titulo: str, contenido_md: str) -> bytes:
    pdf = ConsultorPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()

    # Título
    pdf.set_font("Helvetica", "B", 16)
    pdf.set_text_color(20, 20, 20)
    titulo_limpio = limpiar_para_pdf(titulo)
    pdf.multi_cell(0, 10, titulo_limpio.upper(), align="C")
    pdf.ln(5)

    # Contenido
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(40, 40, 40)

    for linea_original in contenido_md.split("\n"):
        linea = limpiar_para_pdf(linea_original.strip())
        if not linea:
            pdf.ln(2)
            continue

        try:
            if linea.startswith("### "):
                pdf.set_font("Helvetica", "B", 11)
                pdf.set_text_color(26, 95, 42)
                pdf.multi_cell(0, 7, linea[4:])
                pdf.set_text_color(40, 40, 40)
                pdf.set_font("Helvetica", "", 10)

            elif linea.startswith("## "):
                pdf.set_font("Helvetica", "B", 13)
                pdf.ln(2)
                pdf.multi_cell(0, 8, linea[3:])
                pdf.set_font("Helvetica", "", 10)

            elif linea.startswith("|"):
                pdf.set_font("Courier", "", 7)
                pdf.multi_cell(0, 4, linea)
                pdf.set_font("Helvetica", "", 10)

            else:
                pdf.multi_cell(0, 5, linea)

        except Exception:
            linea_segura = "".join(c for c in linea if 32 <= ord(c) <= 126 or c in ["\n", "\r", "\t"])
            pdf.multi_cell(0, 5, linea_segura)

    try:
        pdf_bytes = pdf.output(dest="S").encode("latin-1", errors="replace")
    except Exception:
        pdf_bytes = pdf.output(dest="S").encode("ascii", errors="ignore")

    return pdf_bytes


# ═══════════════════════════════════════════════════════════════════════
# INTERFAZ
# ═══════════════════════════════════════════════════════════════════════
st.markdown(
    f"""
    <div style="background-color:#1a5f2a; padding:20px; border-radius:10px; text-align:center;">
        <h1 style="color:white; margin:0;">GuateEmprende IA Pro</h1>
        <p style="color:#d4edda; margin:5px;">
            Consultor de Negocios Inteligente | {fecha_hoy} |
            Motor: {MODELO}
        </p>
    </div>
""",
    unsafe_allow_html=True,
)

with st.sidebar:
    st.header("Configuración")
    st.success(f"Modelo activo: {MODELO}")
    st.info("Datos macroeconómicos de Guatemala actualizados.")


def llamar_ia(sistema: str, usuario: str):
    try:
        with st.spinner("Analizando con IA..."):
            res = client.chat.completions.create(
                model=MODELO,
                messages=[
                    {"role": "system", "content": sistema},
                    {"role": "user", "content": usuario},
                ],
                temperature=0.4,
            )
            return res.choices[0].message.content
    except Exception as e:
        st.error(f"Error: {e}")
        return None


# ═══════════════════════════════════════════════════════════════════════
# PESTAÑAS
# ═══════════════════════════════════════════════════════════════════════
tab1, tab2, tab3, tab4 = st.tabs(["Ubicación", "Capital", "Nichos Local", "Plan de Negocios"])

# ── TAB 1: UBICACIÓN ──────────────────────────────────────────────────
with tab1:
    st.subheader("Análisis de Ubicación Estratégica")
    negocio = st.text_input("¿Qué negocio deseas abrir?", placeholder="Ej. Cafetería, Barbería", key="t1")

    if st.button("Buscar Mejor Ubicación", type="primary", key="b1"):
        if not negocio:
            st.warning("Ingresa el tipo de negocio.")
        else:
            sis = f"Eres experto en geomarketing en Guatemala. Fecha: {fecha_hoy}."
            usr = f"""Analiza las 3 mejores ubicaciones para una {negocio} en Guatemala.

Para cada ubicación incluye:
1. Nombre exacto de la zona
2. Nivel socioeconómico (A/B, C+, C, D)
3. Tráfico peatonal y vehicular estimado
4. Costo de alquiler por m2 aproximado (Q/mes)
5. Perfil del cliente
6. Nivel de competencia
7. Puntaje de viabilidad 1-10

Usa tablas Markdown. Sé específico y utiliza datos de mercado actuales."""

            resultado = llamar_ia(sis, usr)
            if resultado:
                st.markdown(resultado)
                try:
                    pdf_data = generar_pdf(f"Ubicación: {negocio}", resultado)
                    st.download_button(
                        "Descargar PDF",
                        data=pdf_data,
                        file_name="ubicacion.pdf",
                        mime="application/pdf",
                        key="download_ubicacion_pdf",
                    )
                except Exception as e:
                    st.warning(f"Error PDF: {e}")
                    st.download_button(
                        "Descargar TXT",
                        data=resultado,
                        file_name="ubicacion.txt",
                        mime="text/plain",
                        key="download_ubicacion_txt",
                    )

# ── TAB 2: CAPITAL ───────────────────────────────────────────────────
with tab2:
    st.subheader("Inversión por Capital")
    monto = st.number_input("Capital disponible (Q):", min_value=1000, value=50000, step=1000, key="t2")

    if st.button("Ver Oportunidades", type="primary", key="b2"):
        sis = f"Eres analista financiero senior de PYMES en Guatemala. Año {anio_actual}."
        usr = f"""Con un capital de Q{monto:,.0f}, recomienda los 3 negocios más rentables en Guatemala para {fecha_hoy}.

Para cada negocio incluye:
1. Nombre del negocio
2. Distribución del capital (tabla)
3. Proyección de ingresos mensuales
4. Punto de equilibrio
5. ROI a 12 meses
6. Margen de ganancia bruto
7. Principal riesgo y mitigación

Usa tablas Markdown."""

        resultado = llamar_ia(sis, usr)
        if resultado:
            st.markdown(resultado)
            try:
                pdf_data = generar_pdf(f"Inversión Q{monto:,.0f}", resultado)
                st.download_button(
                    "Descargar PDF",
                    data=pdf_data,
                    file_name="inversion.pdf",
                    mime="application/pdf",
                    key="download_inversion_pdf",
                )
            except Exception as e:
                st.warning(f"Error PDF: {e}")
                st.download_button(
                    "Descargar TXT",
                    data=resultado,
                    file_name="inversion.txt",
                    mime="text/plain",
                    key="download_inversion_txt",
                )

# ── TAB 3: NICHOS ────────────────────────────────────────────────────
with tab3:
    st.subheader("Nichos de Mercado por Zona")
    zona = st.text_input("Ingresa zona o municipio:", placeholder="Ej. Zona 18, Mixco, Antigua", key="t3")

    if st.button("Identificar Nichos", type="primary", key="b3"):
        if not zona:
            st.warning("Ingresa la zona.")
        else:
            sis = f"Eres consultor de desarrollo económico local en Guatemala. Fecha: {fecha_hoy}."
            usr = f"""Para la ubicación '{zona}' en Guatemala, identifica 3 negocios con alta demanda y baja oferta.

Para cada nicho incluye:
1. Nombre del negocio sugerido
2. Necesidad insatisfecha
3. Perfil del cliente objetivo
4. Población estimada (radio 1-3 km)
5. Competencia directa actual
6. Inversión aproximada
7. Barrera de entrada principal
8. Potencial de escalamiento

Sé específico respecto de la zona."""

            resultado = llamar_ia(sis, usr)
            if resultado:
                st.markdown(resultado)
                try:
                    pdf_data = generar_pdf(f"Nichos: {zona}", resultado)
                    st.download_button(
                        "Descargar PDF",
                        data=pdf_data,
                        file_name="nichos.pdf",
                        mime="application/pdf",
                        key="download_nichos_pdf",
                    )
                except Exception as e:
                    st.warning(f"Error PDF: {e}")
                    st.download_button(
                        "Descargar TXT",
                        data=resultado,
                        file_name="nichos.txt",
                        mime="text/plain",
                        key="download_nichos_txt",
                    )

# ── TAB 4: PLAN DE NEGOCIOS ───────────────────────────────────────────
with tab4:
    st.subheader("Generador de Plan de Negocios")

    col1, col2 = st.columns(2)
    with col1:
        idea = st.text_input("Idea de negocio:", key="p1")
        ubic = st.text_input("Ubicación:", key="p2")
    with col2:
        cap = st.text_input("Capital (Q):", key="p3")
        tipo = st.selectbox("Constitución:", ["Empresa Individual", "S.A.", "S.R.L.", "Pequeño Contribuyente"])

    diferenciador = st.text_area("Diferenciador:", height=80, key="p4")

    if st.button("Generar Plan Completo", type="primary", key="b4"):
        if not idea:
            st.warning("Ingresa la idea de negocio.")
        else:
            sis = f"Eres consultor senior de negocios en Guatemala. Experto en SAT y Registro Mercantil. Fecha: {fecha_hoy}."
            usr = f"""Crea un plan de negocios para Guatemala:

NEGOCIO: {idea}
UBICACION: {ubic}
CAPITAL: {cap}
CONSTITUCION: {tipo}
DIFERENCIADOR: {diferenciador or 'No especificado'}

ESTRUCTURA:
1. RESUMEN EJECUTIVO
2. ANALISIS DE MERCADO
3. MARKETING DIGITAL EN GUATEMALA
4. PLAN DE OPERACIONES
5. ESTRUCTURA LEGAL Y TRAMITES (tabla)
6. PROYECCION FINANCIERA (tabla)
7. ANALISIS DE RIESGOS
8. PLAN DE IMPLEMENTACION (30 dias)

Usa tablas Markdown. Sé profesional y realista."""

            resultado = llamar_ia(sis, usr)
            if resultado:
                st.markdown(resultado)
                try:
                    pdf_data = generar_pdf(f"Plan: {idea}", resultado)
                    st.download_button(
                        "Descargar Plan PDF",
                        data=pdf_data,
                        file_name="plan.pdf",
                        mime="application/pdf",
                        key="download_plan_pdf",
                    )
                except Exception as e:
                    st.warning(f"Error PDF: {e}")
                    st.download_button(
                        "Descargar TXT",
                        data=resultado,
                        file_name="plan.txt",
                        mime="text/plain",
                        key="download_plan_txt",
                    )

# ═══════════════════════════════════════════════════════════════════════
# FOOTER
# ═══════════════════════════════════════════════════════════════════════
st.markdown("---")
st.markdown(
    f"""
    <div style="text-align:center; padding:15px;">
        <p style="color:#666; margin:0;">
            GuateEmprende IA Pro | Guatemala {anio_actual} |
            Motor: {MODELO}
        </p>
        <p style="color:#999; font-size:0.8em;">
            Datos generados por IA. Verifique la información con profesionales especializados.
        </p>
    </div>
""",
    unsafe_allow_html=True,
)
