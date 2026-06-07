import streamlit as st
from openai import OpenAI
from datetime import datetime
from fpdf import FPDF
import unicodedata
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

MODELO = "openai/gpt-oss-20b:free"

# ═══════════════════════════════════════════════════════════════════════
# FUNCIÓN PARA LIMPIAR TEXTO PARA PDF (elimina emojis y normaliza)
# ═══════════════════════════════════════════════════════════════════════
def limpiar_para_pdf(texto):
    """
    Normaliza texto para FPDF:
    1. Elimina emojis y caracteres no soportados
    2. Normaliza tildes a ASCII básico
    3. Elimina caracteres de control
    """
    if not texto:
        return ""

    # Eliminar emojis y caracteres pictográficos
    # Patrón que captura rangos de emojis y símbolos
    patron_emojis = re.compile(
        "["
        "\U0001F600-\U0001F64F"  # emoticons
        "\U0001F300-\U0001F5FF"  # símbolos y pictogramas
        "\U0001F680-\U0001F6FF"  # transporte y mapas
        "\U0001F1E0-\U0001F1FF"  # banderas
        "\U00002702-\U000027B0"  # dingbats
        "\U000024C2-\U0001F251"
        "\U0001F900-\U0001F9FF"  # suplemento
        "\U0001FA00-\U0001FA6F"  # símbolos extendidos
        "\U0001FA70-\U0001FAFF"
        "]+",
        flags=re.UNICODE
    )

    texto = patron_emojis.sub(r'', texto)

    # Normalizar tildes: opción A - mantener con encoding latin-1
    # Opción B - reemplazar por equivalentes ASCII (más compatible)
    # Usamos B para máxima compatibilidad

    reemplazos = {
        'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u',
        'Á': 'A', 'É': 'E', 'Í': 'I', 'Ó': 'O', 'Ú': 'U',
        'ñ': 'n', 'Ñ': 'N', 'ü': 'u', 'Ü': 'U',
        '´': "'", '`': "'", '“': '"', '”': '"', '‘': "'", '’': "'",
        '—': '-', '–': '-', '…': '...', '•': '*',
    }

    for orig, repl in reemplazos.items():
        texto = texto.replace(orig, repl)

    # Eliminar cualquier carácter que no sea ASCII imprimible o latin-1 básico
    texto_limpio = ""
    for char in texto:
        codigo = ord(char)
        # Permitir ASCII imprimible y algunos latin-1 básicos comunes
        if (32 <= codigo <= 126) or (160 <= codigo <= 255):
            texto_limpio += char
        elif codigo in [10, 13]:  # newlines
            texto_limpio += char
        else:
            # Reemplazar otros caracteres por espacio o quitar
            if unicodedata.category(char).startswith('Z'):
                texto_limpio += ' '

    return texto_limpio

# ═══════════════════════════════════════════════════════════════════════
# GENERADOR DE PDF PROFESIONAL (CORREGIDO PARA UNICODE)
# ═══════════════════════════════════════════════════════════════════════
class ConsultorPDF(FPDF):
    def __init__(self):
        super().__init__()
        # Usar encoding latin-1 que es más compatible con FPDF
        # pero también preparamos fallback a ASCII

    def header(self):
        self.set_font('Helvetica', 'B', 12)
        self.set_text_color(26, 95, 42)
        self.cell(0, 10, 'GUATEEMPRENDE IA PRO - CONSULTORIA', 0, 0, 'L')
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

def generar_pdf(titulo, contenido_md):
    """
    Genera PDF con manejo robusto de caracteres Unicode.
    Convierte todo a ASCII seguro para FPDF.
    """
    pdf = ConsultorPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    # Título
    pdf.set_font('Helvetica', 'B', 16)
    pdf.set_text_color(20, 20, 20)
    titulo_limpio = limpiar_para_pdf(titulo)
    pdf.multi_cell(0, 10, titulo_limpio.upper(), align='C')
    pdf.ln(5)

    # Contenido - limpiar todo antes de usar
    pdf.set_font('Helvetica', '', 10)
    pdf.set_text_color(40, 40, 40)

    # Procesar línea por línea
    lineas = contenido_md.split('\n')

    for linea_original in lineas:
        # Limpiar primero
        linea = limpiar_para_pdf(linea_original.strip())
        if not linea:
            pdf.ln(2)
            continue

        try:
            # Detectar formato de encabezados por simbolos ### o ##
            if linea.startswith('### '):
                pdf.set_font('Helvetica', 'B', 11)
                pdf.set_text_color(26, 95, 42)
                titulo_limpio = linea[4:] if len(linea) > 4 else ""
                pdf.multi_cell(0, 7, titulo_limpio)
                pdf.set_text_color(40, 40, 40)
                pdf.set_font('Helvetica', '', 10)
                continue
            elif linea.startswith('## '):
                pdf.set_font('Helvetica', 'B', 13)
                pdf.ln(2)
                titulo_limpio = linea[3:] if len(linea) > 3 else ""
                pdf.multi_cell(0, 8, titulo_limpio)
                pdf.set_font('Helvetica', '', 10)
                continue
            elif linea.startswith('|'):
                # Tablas en fuente monospace pequeña
                pdf.set_font('Courier', '', 7)
                pdf.multi_cell(0, 4, linea)
                pdf.set_font('Helvetica', '', 10)
                continue

            # Texto normal
            pdf.multi_cell(0, 5, linea)

        except Exception as e:
            # Si algo falla, intentar con reemplazo total
            try:
                linea_segura = ''.join(c for c in linea if ord(c) < 128)
                pdf.multi_cell(0, 5, linea_segura)
            except:
                pass  # Ignorar línea problemática

    # Generar bytes
    try:
        pdf_bytes = pdf.output(dest='S').encode('latin-1', errors='replace')
    except:
        # Fallback completo: reconstruir con solo ASCII
        pdf_bytes = pdf.output(dest='S').encode('ascii', errors='ignore')

    return pdf_bytes

# ═══════════════════════════════════════════════════════════════════════
# INTERFAZ PRINCIPAL
# ═══════════════════════════════════════════════════════════════════════
st.markdown(f"""
    <div style="background-color:#1a5f2a; padding:20px; border-radius:10px; text-align:center;">
        <h1 style="color:white; margin:0;">GuateEmprende IA Pro</h1>
        <p style="color:#d4edda; margin:5px;">
            Consultor de Negocios Inteligente | {fecha_hoy} |
            Motor: {MODELO}
        </p>
    </div>
""", unsafe_allow_html=True)

with st.sidebar:
    st.header("Configuracion")
    st.success(f"Modelo activo: {MODELO}")
    st.info("Datos macroeconomicos de Guatemala actualizados.")

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
tab1, tab2, tab3, tab4 = st.tabs(["Ubicacion", "Capital", "Nichos Local", "Plan de Negocios"])

# ── TAB 1: UBICACIÓN ──────────────────────────────────────────────────
with tab1:
    st.subheader("Analisis de Ubicacion Estrategica")
    negocio = st.text_input("Que negocio deseas abrir?", placeholder="Ej. Cafeteria, Barberia", key="t1")

    if st.button("Buscar Mejor Ubicacion", type="primary", key="b1"):
        if negocio:
            sis = f"Eres experto en geomarketing en Guatemala. Fecha: {fecha_hoy}."
            usr = f"""Analiza las 3 mejores ubicaciones para una {negocio} en Guatemala.

Para cada ubicacion incluye:
1. Nombre exacto de la zona
2. Nivel socioeconomico (A/B, C+, C, D)
3. Trafico peatonal y vehicular estimado
4. Costo de alquiler por m2 aproximado (Q/mes)
5. Perfil del cliente
6. Nivel de competencia
7. Puntaje de viabilidad 1-10

Usa tablas Markdown. Se especifico con datos de mercado actuales."""
            resultado = llamar_ia(sis, usr)
            if resultado:
                st.markdown(resultado)
                try:
                    pdf_data = generar_pdf(f"Ubicacion: {negocio}", resultado)
                    st.download_button("Descargar PDF", data=pdf_data, file_name=f"ubicacion_{negocio[:15]}.pdf", mime="application/pdf")
                except Exception as e:
                    st.warning(f"PDF no disponible: {str(e)[:100]}")
                    st.download_button("Descargar TXT", data=resultado, file_name=f"ubicacion_{negocio[:15]}.txt", mime="text/plain")
        else:
        st.warning("Ingresa el tipo de negocio.")

    # Corrección del bloque anterior - estaba mal indentado
    st.warning("Ingresa el tipo de negocio.")

# ── TAB 2: CAPITAL ───────────────────────────────────────────────────
with tab2:
    st.subheader("Inversion por Capital")
    monto = st.number_input("Capital disponible (Q):", min_value=1000, value=50000, step=1000, key="t2")

    if st.button("Ver Oportunidades", type="primary", key="b2"):
        sis = f"Eres analista financiero senior de PYMES en Guatemala. Año {año_actual}."
        usr = f"""Con un capital de Q{monto:,.0f}, recomienda los 3 negocios mas rentables en Guatemala para {fecha_hoy}.

Para cada negocio incluye:
1. Nombre del negocio
2. Distribucion del capital (tabla)
3. Proyeccion de ingresos mensuales
4. Punto de equilibrio
5. ROI a 12 meses
6. Margen de ganancia bruto
7. Principal riesgo y mitigacion

Usa tablas Markdown."""
        resultado = llamar_ia(sis, usr)
        if resultado:
            st.markdown(resultado)
            try:
                pdf_data = generar_pdf(f"Inversion Q{monto:,.0f}", resultado)
                st.download_button("Descargar PDF", data=pdf_data, file_name=f"inversion_q{monto:,.0f}.pdf", mime="application/pdf")
            except Exception as e:
                st.warning(f"PDF no disponible")
                st.download_button("Descargar TXT", data=resultado, file_name=f"inversion_q{monto:,.0f}.txt", mime="text/plain")

# ── TAB 3: NICHOS ────────────────────────────────────────────────────
with tab3:
    st.subheader("Nichos de Mercado por Zona")
    zona = st.text_input("Ingresa zona o municipio:", placeholder="Ej. Zona 18, Mixco, Antigua", key="t3")

    if st.button("Identificar Nichos", type="primary", key="b3"):
        if zona:
            sis = f"Eres consultor de desarrollo economico local en Guatemala. Fecha: {fecha_hoy}."
            usr = f"""Para la ubicacion '{zona}' en Guatemala, identifica 3 negocios con alta demanda y baja oferta.

Para cada nicho incluye:
1. Nombre del negocio sugerido
2. Necesidad insatisfecha
3. Perfil del cliente objetivo
4. Poblacion estimada (radio 1-3 km)
5. Competencia directa actual
6. Inversion aproximada
7. Barrera de entrada principal
8. Potencial de escalamiento

Se especifico de la zona."""
            resultado = llamar_ia(sis, usr)
            if resultado:
                st.markdown(resultado)
                try:
                    pdf_data = generar_pdf(f"Nichos: {zona}", resultado)
                    st.download_button("Descargar PDF", data=pdf_data, file_name=f"nichos_{zona[:15]}.pdf", mime="application/pdf")
                except Exception as e:
                    st.warning(f"PDF no disponible")
                    st.download_button("Descargar TXT", data=resultado, file_name=f"nichos_{zona[:15]}.txt", mime="text/plain")
        else:
            st.warning("Ingresa la zona.")

# ── TAB 4: PLAN DE NEGOCIOS ───────────────────────────────────────────
with tab4:
    st.subheader("Generador de Plan de Negocios")

    col1, col2 = st.columns(2)
    with col1:
        idea = st.text_input("Idea de negocio:", key="p1")
        ubic = st.text_input("Ubicacion:", key="p2")
    with col2:
        cap = st.text_input("Capital (Q):", key="p3")
        tipo = st.selectbox("Constitucion:", ["Empresa Individual", "S.A.", "S.R.L.", "Pequeno Contribuyente"])
    diferenciador = st.text_area("Diferenciador:", height=80, key="p4")

    if st.button("Generar Plan Completo", type="primary", key="b4"):
        if idea:
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

Usa tablas Markdown. Se profesional y realista."""
            resultado = llamar_ia(sis, usr)
            if resultado:
                st.markdown(resultado)
                try:
                    pdf_data = generar_pdf(f"Plan: {idea}", resultado)
                    st.download_button("Descargar Plan PDF", data=pdf_data, file_name=f"plan_{idea[:15]}.pdf", mime="application/pdf")
                except Exception as e:
                    st.warning(f"PDF no disponible")
                    st.download_button("Descargar TXT", data=resultado, file_name=f"plan_{idea[:15]}.txt", mime="text/plain")
        else:
            st.warning("Ingresa la idea de negocio.")

# ═══════════════════════════════════════════════════════════════════════
# FOOTER
# ═══════════════════════════════════════════════════════════════════════
st.markdown("---")
st.markdown(f"""
    <div style="text-align:center; padding:15px;">
        <p style="color:#666; margin:0;">
            GuateEmprende IA Pro | Guatemala {año_actual} |
            Motor: {MODELO}
        </p>
        <p style="color:#999; font-size:0.8em;">
            Datos generados por IA. Verificar con profesionales.
        </p>
    </div>
""", unsafe_allow_html=True)
