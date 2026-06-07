import streamlit as st
from openai import OpenAI
from datetime import datetime

# 1. Configuración de la página de Streamlit
st.set_page_config(
    page_title="GuateEmprende IA Pro 🇬🇹",
    page_icon="📈",
    layout="wide"
)

# Obtener fecha actual para contextualizar la IA al día de hoy
fecha_hoy = datetime.now().strftime("%d de %B de %Y")

# 2. Inicialización de la API Key y Base URL (secrets de Streamlit)
api_key = st.secrets.get("FREELLM_API_KEY", "")
base_url = st.secrets.get("FREELLM_BASE_URL", "https://api.openai.com/v1")

if not api_key:
    st.error("⚠️ No se encontró la API Key. Por favor configúrala en tus Secrets de Streamlit.")
    st.stop()

# Inicializamos cliente compatible con tu Proxy
client = OpenAI(
    api_key=api_key,
    base_url=base_url
)

# 3. Encabezado principal
st.title("🇬🇹 GuateEmprende IA Pro")
st.markdown(f"**Consultor de Negocios Avanzado para Guatemala** | 📅 *Análisis actualizado al: {fecha_hoy}*")
st.markdown("---")

# Sidebar
with st.sidebar:
    st.header("⚙️ Configuración del Motor")
    modelo_seleccionado = st.selectbox(
        "Selecciona el modelo de IA:",
        ["gpt-4o-mini", "gpt-3.5-turbo", "gpt-4"],
        index=0
    )
    st.write("---")
    st.markdown("""
    ### 📊 Fuentes de Análisis estimadas:
    - Tendencias de consumo en GT ({año})
    - Costos de locales comerciales por zona
    - Trámites legales de la SAT y Registro Mercantil
    - Demografía de departamentos clave
    """.format(año=datetime.now().year))

# 4. Pestañas de la Aplicación
tab1, tab2, tab3, tab4 = st.tabs([
    "📍 Buscar Ubicación",
    "💵 Inversión por Capital",
    "🏬 ¿Qué abro en mi zona?",
    "📋 Generador de Plan de Negocios"
])

# --- PESTAÑA 1: Negocio -> Mejor Ubicación ---
with tab1:
    st.header("📍 Análisis de Ubicación Óptima")
    st.write("¿Qué negocio quieres poner? La IA calculará el mejor punto geográfico en Guatemala justificándolo con datos de mercado.")

    with st.form("form_ubicacion"):
        tipo_negocio = st.text_input(
            "Tipo de negocio:",
            placeholder="Ej. Cafetería de especialidad, Farmacia de barrio, Autohotel, Gimnasio"
        )
        submit_1 = st.form_submit_button("Analizar Mercado 🚀")

    if submit_1 and tipo_negocio:
        with st.spinner("Realizando análisis de geomarketing..."):
            prompt = f"""
            Actúa como un experto en geomarketing, bienes raíces comerciales y economía de Guatemala al día de hoy ({fecha_hoy}).
            El usuario quiere poner el siguiente negocio: "{tipo_negocio}".

            Recomienda las 3 mejores ubicaciones de Guatemala justificándolas con datos específicos y realistas (estimaciones de mercado).

            Para cada una de las 3 opciones debes estructurar tu respuesta así:
            1. **Ubicación exacta:** (Ej. Zona 4 de Ciudad de Guatemala, Carretera a El Salvador, Antigua Guatemala, Quetzaltenango).
            2. **Justificación con Datos de Mercado (obligatorio):**
               - Tráfico peatonal/vehicular estimado (Alto/Medio/Bajo y por qué).
               - Nivel Socioeconómico predominante (C+, C, D, etc.).
               - Costo estimado de alquiler por m² para locales en esa área en {datetime.now().year}.
               - Datos demográficos o de tendencias que apoyen la decisión.
            3. **Competencia local:** Nivel de competencia y cómo destacar de los competidores actuales en esa zona.
            4. **Estrategia recomendada:** Formato del negocio adecuado para esta zona.

            Termina con una conclusión comparativa general. Escribe en formato Markdown limpio y con tablas comparativas si es viable.
            """
            try:
                response = client.chat.completions.create(
                    model=modelo_seleccionado,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.7
                )
                st.markdown(response.choices[0].message.content)
            except Exception as e:
                st.error(f"Error: {e}")

# --- PESTAÑA 2: Capital -> Ideas de Negocio ---
with tab2:
    st.header("💵 Oportunidades según Capital de Trabajo")
    st.write("Ingresa tu presupuesto estimado y evaluaremos las industrias y servicios con mejor retorno de inversión en Guatemala hoy.")

    with st.form("form_capital"):
        capital = st.text_input(
            "Monto de inversión inicial (Ej. Q50,000 o $10,000):",
            placeholder="Introduce la cifra y moneda"
        )
        submit_2 = st.form_submit_button("Evaluar Rentabilidad 💰")

    if submit_2 and capital:
        with st.spinner("Calculando modelos financieros y de retorno..."):
            prompt = f"""
            Actúa como un analista financiero y de microinversión en Guatemala en la fecha actual ({fecha_hoy}).
            El usuario cuenta con un presupuesto de arranque de: "{capital}".

            Recomienda 3 sectores, comercios o servicios específicos que den el mejor rendimiento para este presupuesto exacto en Guatemala.

            Para cada opción incluye:
            1. **Nombre del Negocio y Viabilidad.**
            2. **Desglose de Costos de Arranque Estimado (Justificado con datos):** Haz una tabla de cómo gastar este capital (Trámites, Inventario inicial, Alquiler/Garantía, Publicidad, Caja chica).
            3. **Retorno de Inversión (ROI) Estimado:** ¿En cuántos meses se recupera el capital según los márgenes promedio en Guatemala hoy? Justifica con el porcentaje de margen de ganancia operativa estimado de este sector.
            4. **Estrategia de bajo costo (Lean):** Cómo iniciar gastando lo mínimo indispensable para probar el mercado en Guatemala.

            Usa formato Markdown claro y tablas numéricas para los presupuestos.
            """
            try:
                response = client.chat.completions.create(
                    model=modelo_seleccionado,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.7
                )
                st.markdown(response.choices[0].message.content)
            except Exception as e:
                st.error(f"Error: {e}")

# --- PESTAÑA 3: Lugar -> Qué Negocio Falta ---
with tab3:
    st.header("🏬 Diagnóstico Comercial Local")
    st.write("Escribe un municipio, zona o departamento de Guatemala para identificar qué servicios o productos tienen desabasto o alta demanda hoy.")

    with st.form("form_zona"):
        ubicacion_usuario = st.text_input(
            "Ubicación en Guatemala a analizar:",
            placeholder="Ej. Mixco (San Cristóbal), Chimaltenango, Panajachel, Zona 1 de la Capital"
        )
        submit_3 = st.form_submit_button("Buscar Nichos Vacíos 🎯")

    if submit_3 and ubicacion_usuario:
        with st.spinner("Analizando brechas de mercado..."):
            prompt = f"""
            Actúa como un consultor de desarrollo económico local en Guatemala.
            La ubicación a analizar es: "{ubicacion_usuario}" al día de hoy ({fecha_hoy}).

            Presenta un análisis de brechas de mercado identificando 3 negocios o servicios específicos que hagan falta o tengan gran potencial de crecimiento allí.

            Deberás justificar cada idea con:
            1. **La Necesidad Insatisfecha:** ¿Qué problema sufre el vecino de esa área actualmente? (Ej: falta de parqueo, tráfico que impide ir a la capital, clima templado, crecimiento residencial).
            2. **Datos Demográficos e Históricos Estimados:** (Ej. población de la zona, crecimiento urbano reciente, nivel de ingresos promedio).
            3. **El Negocio Propuesto:** Descripción clara.
            4. **Barrera de Entrada Local:** ¿Qué es lo más difícil de abrir este negocio en este lugar específico de Guatemala? (Ej. seguridad pública, escasez de agua, permisos de la municipalidad local).

            Escribe la respuesta estructurada con Markdown y datos analíticos.
            """
            try:
                response = client.chat.completions.create(
                    model=modelo_seleccionado,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.7
                )
                st.markdown(response.choices[0].message.content)
            except Exception as e:
                st.error(f"Error: {e}")

# --- PESTAÑA 4: Plan de Negocios (NUEVA) ---
with tab4:
    st.header("📋 Generador de Plan de Negocios Estructurado")
    st.write("Escribe la idea de negocio que elegiste en las pestañas anteriores para crear un plan de negocios formal adaptado a Guatemala.")

    with st.form("form_plan"):
        col1, col2 = st.columns(2)
        with col1:
            idea_negocio = st.text_input("Idea del negocio:", placeholder="Ej. Cafetería de Especialidad para estudiantes")
            ubicacion_plan = st.text_input("Ubicación planeada:", placeholder="Ej. Zona 15, Ciudad de Guatemala")
        with col2:
            capital_plan = st.text_input("Capital disponible:", placeholder="Ej. Q45,000")
            formato_plan = st.selectbox("Formato del Plan:", ["Plan Lean Canvas (Ágil)", "Plan de Negocios Tradicional Completo"])

        submit_4 = st.form_submit_button("Generar Plan de Negocios Profesional 📝")

    if submit_4 and idea_negocio:
        with st.spinner("Redactando plan de negocios personalizado..."):
            prompt = f"""
            Actúa como un consultor de negocios senior de la Cámara de Comercio de Guatemala y experto en emprendimiento.
            Fecha de análisis actual: {fecha_hoy}.

            Desarrolla un plan de negocios sumamente detallado y estructurado para la siguiente idea de negocio:
            - **Negocio:** {idea_negocio}
            - **Ubicación:** {ubicacion_plan}
            - **Capital Inicial:** {capital_plan}
            - **Formato solicitado:** {formato_plan}

            El plan debe incluir obligatoriamente los siguientes módulos adaptados estrictamente a la realidad y leyes de Guatemala en {datetime.now().year}:

            1. **Propuesta de Valor Única:** ¿Por qué te van a comprar a ti y no a la competencia?
            2. **Análisis de Clientes (Target):** Quién es el "shoper" o consumidor guatemalteco de este negocio.
            3. **Estructura Legal y Trámites en Guatemala:**
               - Pasos exactos y costos aproximados ante la SAT (ej. Pequeño Contribuyente, Régimen General).
               - Trámites ante el Registro Mercantil (Empresa Individual o S.A.) y Licencia Sanitaria (si aplica).
            4. **Plan de Operaciones y Proveedores:** Dónde buscar materias primas o proveedores clave en Guatemala (menciona áreas de distribución realistas como El Guarda, Zona 4, importadoras locales, etc., según corresponda).
            5. **Estrategia de Marketing Local:** Canales digitales (Facebook Ads, Instagram, TikTok son vitales en GT) y tácticas físicas.
            6. **Proyecciones Financieras Básicas:**
               - Punto de equilibrio estimado en Quetzales.
               - Proyección de ingresos y egresos para los primeros 3 meses.
               - Estrategia de precios competitiva para el mercado guatemalteco.

            Redacta en un tono sumamente profesional, realista, motivador y claro. Utiliza títulos, listas de viñetas, tablas de costos y negritas para una lectura impecable.
            """
            try:
                response = client.chat.completions.create(
                    model=modelo_seleccionado,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.7
                )
                st.markdown(response.choices[0].message.content)
            except Exception as e:
                st.error(f"Error: {e}")
