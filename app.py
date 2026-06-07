"""
╔══════════════════════════════════════════════════════════════════════╗
║         GUATEEMPRENDE IA PRO - Streamlit Cloud + OpenRouter           ║
║     Consultor de Negocios Inteligente para Guatemala                  ║
║     Con exportación a PDF profesional                                 ║
╚══════════════════════════════════════════════════════════════════════╝
"""

import streamlit as st
from openai import OpenAI, APIConnectionError, AuthenticationError, RateLimitError
from datetime import datetime
import traceback
import re
from io import BytesIO

# Para PDF
from fpdf import FPDF
import textwrap

# ═══════════════════════════════════════════════════════════════════════
# 1. CONFIGURACIÓN DE LA PÁGINA
# ═══════════════════════════════════════════════════════════════════════

st.set_page_config(
    page_title="GuateEmprende IA Pro 🇬🇹",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Contexto temporal
fecha_hoy = datetime.now().strftime("%d de %B de %Y")
año_actual = datetime.now().year

# ═══════════════════════════════════════════════════════════════════════
# 2. CARGAR CREDENCIALES
# ═══════════════════════════════════════════════════════════════════════

api_key = st.secrets.get("OPENROUTER_API_KEY", "")

if not api_key:
    st.error("⚠️ API Key de OpenRouter no configurada.")
    st.markdown("""
    **Configuración requerida:**
    1. Obtén tu API Key en [OpenRouter.ai](https://openrouter.ai/keys)
    2. Ve a Streamlit Cloud → **Settings** → **Secrets**
    3. Agrega:
        """)
    st.stop()

base_url = "https://openrouter.ai/api/v1"

try:
    client = OpenAI(api_key=api_key, base_url=base_url)
except Exception as e:
othes
    st.error(f"Error al inicializar el cliente: {e}")
    st.stop()

# ═══════════════════════════════════════════════════════════════════════
# 3. FUNCIONES PARA GENERAR PDF PROFESIONAL
# ═══════════════════════════════════════════════════════════════════════

def crear_pdf(titulo: str, contenido_md: str) -> bytes:
    """
    Convierte contenido Markdown a PDF profesional usando FPDF2.
    Maneja tablas, títulos, listas y texto básico.
    """

    class PDF(FPDF):
        def header(self):
            # Logo o título en cabecera
            self.set_font('Helvetica', 'B', 12)
            self.set_text_color(26, 95, 42)  # Verde Guatemala
            self.cell(0, 10, 'GuateEmprende IA Pro', 0, 0, 'L')
            self.set_text_color(128, 128, 128)
            self.set_font('Helvetica', '', 8)
            self.cell(0, 10, f'Generado: {fecha_hoy}', 0, 0, 'R')
            self.ln(15)
            # Línea decorativa
            self.set_draw_color(26, 95, 42)
            self.line(10, self.get_y(), 200, self.get_y())
            self.ln(5)

        def footer(self):
            self.set_y(-15)
            self.set_font('Helvetica', 'I', 8)
            self.set_text_color(128, 128, 128)
            self.cell(0, 10, f'Página {self.page_no()}', 0, 0, 'C')

    pdf = PDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    # Título principal
    pdf.set_font('Helvetica', 'B', 16)
    pdf.set_text_color(26, 95, 42)
    pdf.multi_cell(0, 10, titulo, align='C')
    pdf.ln(5)
    pdf.set_draw_color(26, 95, 42)
    pdf.line(50, pdf.get_y(), 160, pdf.get_y())
    pdf.ln(10)

    # Procesar contenido Markdown línea por línea
    pdf.set_text_color(0, 0, 0)
    current_y = pdf.get_y()

    for line in contenido_md.split('\n'):
        line = line.strip()
        if not line:
            pdf.ln(3)
            continue

        # Detectar títulos (# ## ###)
        if line.startswith('### '):
            pdf.set_font('Helvetica', 'B', 12)
            pdf.set_text_color(26, 95, 42)
            pdf.ln(2)
            pdf.multi_cell(0, 6, line[4:])
            pdf.ln(1)
            pdf.set_text_color(0, 0, 0)

        elif line.startswith('## '):
            pdf.set_font('Helvetica', 'B', 13)
            pdf.set_text_color(26, 95, 42)
            pdf.ln(3)
            pdf.multi_cell(0, 7, line[3:])
            pdf.ln(1)
            pdf.set_text_color(0, 0, 0)

        elif line.startswith('# '):
            pdf.set_font('Helvetica', 'B', 14)
            pdf.set_text_color(26, 95, 42)
            pdf.ln(4)
            pdf.multi_cell(0, 8, line[2:])
            pdf.ln(2)
            pdf.set_text_color(0, 0, 0)

        # Detectar tablas (| separadores)
        elif line.startswith('|') and line.endswith('|'):
            # Es fila de tabla, la proceso como texto simple para PDF
            pdf.set_font('Helvetica', '', 8)
            # Limpiar formato de tabla
            clean = line.replace('|', ' ').strip()
            # Detectar si es fila separadora (contiene ---)
            if '---' in clean:
                continue
            pdf.set_text_color(60, 60, 60)
            pdf.multi_cell(0, 4, clean)
            pdf.set_text_color(0, 0, 0)

        # Detectar listas
        elif line.startswith('- ') or line.startswith('* '):
            pdf.set_font('Helvetica', '', 10)
            # Limpiar emoji y formato básico
            text = re.sub(r'[#*]', '', line[2:])  # Quitar - y formato
            pdf.cell(5)  # Indent
            pdf.multi_cell(0, 5, f'• {text}')

        # Detectar negritas **texto**
        elif '**' in line:
            pdf.set_font('Helvetica', 'B', 10)
            text = line.replace('**', '')
            pdf.multi_cell(0, 5, text)
            pdf.set_font('Helvetica', '', 10)

        # Texto normal
        else:
            pdf.set_font('Helvetica', '', 10)
            # Limpiar markdown restante básico
            clean_text = re.sub(r'[#*`]', '', line)
            clean_text = clean_text.replace('---', '').strip()
            if clean_text:
                pdf.multi_cell(0, 5, clean_text)

    # Guardar en buffer
    buffer = BytesIO()
    pdf_bytes = pdf.output(dest='S').encode('latin-1', errors='replace')
    return pdf_bytes

def crear_boton_pdf(titulo_descarga: str, titulo_doc: str, contenido: str, key_suffix: str = ""):
    """
    Crea un botón de descarga de PDF con formato profesional.
    """
    try:
        pdf_bytes = crear_pdf(titulo_doc, contenido)

        col1, col2 = st.columns([1, 1])
        with col1:
            st.download_button(
                label=f"📄 Descargar PDF",
                data=pdf_bytes,
                file_name=f"{titulo_descarga}.pdf",
                mime="application/pdf",
                key=f"pdf_{key_suffix}_{st.session_state.get('contador', 0)}"
            )
        with col2:
            # También ofrecemos TXT como respaldo
            st.download_button(
                label="📝 Descargar Texto",
                data=contenido,
                file_name=f"{titulo_descarga}.txt",
                mime="text/plain",
                key=f"txt_{key_suffix}_{st.session_state.get('contador', 0)}"
            )

    except Exception as e:
        st.warning(f"⚠️ No se pudo generar PDF: {e}")
        # Fallback a TXT solamente
        st.download_button(
            label="📝 Descargar Texto (.txt)",
            data=contenido,
            file_name=f"{titulo_descarga}.txt",
            mime="text/plain"
        )

# ═══════════════════════════════════════════════════════════════════════
# 4. INTERFAZ PRINCIPAL
# ═══════════════════════════════════════════════════════════════════════

st.title("🇬🇹 GuateEmprende IA Pro")
st.markdown(f"""
<div style="background: linear-gradient(90deg, #1a5f2a 0%, #2d8a3e 100%);
            padding: 15px 25px; border-radius: 10px; margin-bottom: 20px;">
    <h3 style="color: white; margin: 0;">Consultor de Negocios para Guatemala</h3>
    <p style="color: #d4edda; margin: 5px 0 0 0; font-size: 0.9em;">
        📅 <strong>{fecha_hoy}</strong> | 🧠 OpenRouter: <em>z-ai/glm-4-9b-chat:free</em>
    </p>
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("⚙️ Configuración")

    modelos = [
        "z-ai/glm-4-9b-chat:free",
        "qwen/qwen2.5-72b-instruct:free",
        "microsoft/phi-4:free",
        "deepseek/deepchat:free",
        "meta-llama/llama-3-8b-instruct:free",
    ]

    modelo_seleccionado = st.selectbox("Modelo IA:", modelos, index=0)

    st.write("---")
    st.markdown("""
    **Contexto Económico GT:**
    - PIB: ~$102,000 MDD
    - Moneda: Quetzal (GTQ)
    - Emisor: Banco de Guatemala
    """)

    if "contador" not in st.session_state:
        st.session_state.contador = 0

    st.metric("Consultas realizadas", st.session_state.contador)

    st.info("💡 Exporta resultados a **PDF profesional** o texto plano.")

st.markdown("---")

# ═══════════════════════════════════════════════════════════════════════
# 5. FUNCION HELPER PARA CONSULTAS
# ═══════════════════════════════════════════════════════════════════════

def consultar_ia(prompt_sistema: str, prompt_usuario: str, temperatura: float = 0.6):

    st.session_state.contador += 1

    try:
        with st.spinner("🤖 Analizando con IA..."):
            response = client.chat.completions.create(
                model=modelo_seleccionado,
                messages=[
                    {"role": "system", "content": prompt_sistema},
                    {"role": "user", "content": prompt_usuario}
                ],
                temperature=temperatura,
                max_tokens=4096
            )
            return response.choices[0].message.content

    except AuthenticationError:
        st.error("🔴 API Key inválida. Verifica en Secrets.")
        return None
    except RateLimitError:
        st.error("🔴 Límite de solicitudes alcanzado. Espera o cambia de modelo.")
        return None
    except Exception as e:
        st.error(f"🔴 Error: {str(e)[:200]}")
        return None

# ═══════════════════════════════════════════════════════════════════════
# 6. PESTAÑAS PRINCIPALES
# ═══════════════════════════════════════════════════════════════════════

tab1, tab2, tab3, tab4 = st.tabs([
    "📍 Buscar Ubicación",
    "💵 Inversión por Capital",
    "🏬 ¿Qué abro en mi zona?",
    "📋 Plan de Negocios"
])

# ═══════════════════════════════════════════════════════════════════════
# PESTAÑA 1: UBICACIÓN
# ═══════════════════════════════════════════════════════════════════════

with tab1:
    st.header("📍 Análisis de Ubicación Óptima")

    with st.form("form_ubicacion"):
        tipo_negocio = st.text_input(
            "¿Qué tipo de negocio quieres poner?",
            placeholder="Ej: Cafetería de especialidad, taller mecánico, spa..."
        )
        presupuesto_alquiler = st.number_input(
            "Presupuesto alquiler mensual (Q):",
            min_value=0, max_value=100000, value=10000, step=1000
        )
        contexto_extra = st.text_area("Contexto adicional (opcional):", height=80)
        submit_1 = st.form_submit_button("🔍 Analizar", use_container_width=True)

    if submit_1 and tipo_negocio:
        prompt_sistema = f"Eres experto en geomarketing en Guatemala ({fecha_hoy})."
        prompt_usuario = f"""Analiza ubicaciones para: {tipo_negocio}
        Presupuesto alquiler: Q{presupuesto_alquiler:,.0f}/mes
        Contexto: {contexto_extra or 'Ninguno'}

        Recomienda TOP 3 zonas en Guatemala con tabla de datos (NSE, alquiler/m2, tráfico, competencia, puntaje 1-10).
        Incluye justificación con datos de mercado."""

        respuesta = consultar_ia(prompt_sistema, prompt_usuario)
        if respuesta:
            st.markdown(respuesta)
            crear_boton_pdf(
                titulo_descarga=f"analisis_ubicacion_{tipo_negocio.replace(' ', '_')[:20]}",
                titulo_doc=f"ANÁLISIS DE UBICACIÓN: {tipo_negocio}",
                contenido=respuesta,
                key_suffix="ubic"
            )

# ═══════════════════════════════════════════════════════════════════════
# PESTAÑA 2: CAPITAL
# ═══════════════════════════════════════════════════════════════════════

with tab2:
    st.header("💵 Ideas de Negocio por Capital")

    with st.form("form_capital"):
        col1, col2 = st.columns([3, 1])
        with col1:
            monto = st.number_input("Capital disponible (Q):", min_value=5000, max_value=10000000, value=50000, step=5000)
        with col2:
            moneda_tipo = st.selectbox("Moneda:", ["GTQ", "USD"], index=0)

        perfil_riesgo = st.select_slider("Perfil:", ["Conservador", "Moderado", "Agresivo"], value="Moderado")
        tiempo_rec = st.select_slider("Recuperación:", ["6 meses", "12 meses", "18 meses", "24 meses"], value="18 meses")
        submit_2 = st.form_submit_button("💰 Analizar", use_container_width=True)

    if submit_2:
        capital_str = f"Q{monto:,.0f}" if moneda_tipo == "GTQ" else f"${monto:,.0f} USD"

        prompt_sistema = "Analista financiero de PYMES en Guatemala."
        prompt_usuario = f"""Capital: {capital_str}. Perfil: {perfil_riesgo}. Recuperación: {tiempo_rec}.

        Recomienda 3 negocios con tabla de inversión detallada, proyección financiera 12 meses,
        punto de equilibrio, ROI estimado, estrategia lean. Justifica con datos del mercado guatemalteco."""

        respuesta = consultar_ia(prompt_sistema, prompt_usuario, temperatura=0.5)
        if respuesta:
            st.markdown(respuesta)
            crear_boton_pdf(
                titulo_descarga=f"analisis_capital_{monto:,.0f}_{moneda_tipo}",
                titulo_doc=f"ANÁLISIS DE INVERSIÓN: {capital_str}",
                contenido=respuesta,
                key_suffix="cap"
            )

# ═══════════════════════════════════════════════════════════════════════
# PESTAÑA 3: MI ZONA
# ═══════════════════════════════════════════════════════════════════════

with tab3:
    st.header("🏬 ¿Qué Negocio Falta en mi Zona?")

    with st.form("form_zona"):
        ubicacion = st.text_input("Tu ubicación en Guatemala:", placeholder="Ej: Zona 10, Mixco, Antigua...")
        caracteristicas = st.multiselect("Características del área:", [
            "Residencial alta", "Residencial media", "Comercial", "Industrial",
            "Turística", "Cerca universidad", "Alto tráfico", "Población joven"
        ])
        submit_3 = st.form_submit_button("🎯 Identificar", use_container_width=True)

    if submit_3 and ubicacion:
        perfil = ", ".join(caracteristicas) if caracteristicas else "No especificado"

        prompt_usuario = f"""Ubicación: {ubicacion}. Características: {perfil}.

        Identifica 3 negocios faltantes con alta demanda, justificando con datos
        demográficos, brecha de mercado, competencia, barrera de entrada."""

        respuesta = consultar_ia("Experto en desarrollo económico local de Guatemala.", prompt_usuario, 0.7)
        if respuesta:
            st.markdown(respuesta)
            crear_boton_pdf(
                titulo_descarga=f"diagnostico_zona_{ubicacion.replace(' ', '_')[:15]}",
                titulo_doc=f"DIAGNÓSTICO: {ubicacion}",
                contenido=respuesta,
                key_suffix="zona"
            )

# ═══════════════════════════════════════════════════════════════════════
# PESTAÑA 4: PLAN DE NEGOCIOS
# ═══════════════════════════════════════════════════════════════════════

with tab4:
    st.header("📋 Generador de Plan de Negocios Completo")

    with st.form("form_plan"):
        col_a, col_b = st.columns(2)
        with col_a:
            idea = st.text_input("Idea del negocio:", placeholder="Ej: Cafetería orgánica...")
            lugar = st.text_input("Ubicación:", placeholder="Ej: Zona 15, GT")
            capital = st.number_input("Capital (Q):", min_value=5000, value=75000, step=5000)
        with col_b:
            formato_plan = st.selectbox("Formato:", ["Lean Canvas", "Plan Tradicional", "Trámites SAT"], index=1)
            constitucion = st.selectbox("Constitución:", ["Empresa Individual", "S.A.", "S.R.L.", "Pequeño Contribuyente"])
            empleados = st.number_input("Empleados iniciales:", min_value=0, value=2)

        diferenciador = st.text_area("Diferenciador clave:", height=80)
        submit_4 = st.form_submit_button("📝 Generar Plan", use_container_width=True, type="primary")

    if submit_4 and idea:
        prompt_sistema = f"""Director de consultoría PwC/Deloitte especializado en PYMES guatemaltecas.
        Fecha: {fecha_hoy}. Elabora plan de negocios profesional."""

        prompt_usuario = f"""Plan de negocios para: {idea}
        Ubicación: {lugar} | Capital: Q{capital:,.0f} | Formato: {formato_plan}
        Constitución: {constitucion} | Empleados: {empleados}
        Diferenciador: {diferenciador or 'No especificado'}

        Incluye: Resumen ejecutivo, análisis de mercado con datos GT,
        plan de operaciones, TABLA de trámites legales (SAT, Registro Mercantil,
        IGSS, municipal), proyecciones financieras 12 meses con tabla de inversión
        detallada y flujo de caja, estructura de costos, riesgos, plan de
        implementación 30 días. Usa tablas Markdown para todo dato numérico."""

        respuesta = consultar_ia(prompt_sistema, prompt_usuario, temperatura=0.4)
        if respuesta:
            st.markdown(respuesta)
            crear_boton_pdf(
                titulo_descarga=f"Plan_Negocios_{idea.replace(' ', '_')[:20]}",
                titulo_doc=f"PLAN DE NEGOCIOS: {idea}",
                contenido=respuesta,
                key_suffix="plan"
            )

# ═══════════════════════════════════════════════════════════════════════
# FOOTER
# ═══════════════════════════════════════════════════════════════════════

st.markdown("---")
st.markdown(f"""
<div style="text-align: center; color: #666; font-size: 0.85em;">
    🇬🇹 GuateEmprende IA Pro | Guatemala {año_actual} |
    Motor: OpenRouter ({modelo_seleccionado}) |
    Consultas: {st.session_state.contador}
</div>
""", unsafe_allow_html=True)
