import streamlit as st
from openai import OpenAI, APIConnectionError, AuthenticationError, RateLimitError
from datetime import datetime
import traceback

# ═══════════════════════════════════════════════════════════════════════
# 1. CONFIGURACIÓN DE LA PÁGINA
# ═══════════════════════════════════════════════════════════════════════

st.set_page_config(
    page_title="GuateEmprende IA Pro 🇬🇹",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Contexto temporal para la IA
fecha_hoy = datetime.now().strftime("%d de %B de %Y")
año_actual = datetime.now().year
año_actual_str = str(año_actual)

# ═══════════════════════════════════════════════════════════════════════
# 2. CARGAR CREDENCIALES DESDE STREAMLIT SECRETS
# ═══════════════════════════════════════════════════════════════════════

# OpenRouter usa API key propia, NO la de OpenAI
# Base URL de OpenRouter: https://openrouter.ai/api/v1
api_key = st.secrets.get("OPENROUTER_API_KEY", "")
base_url = "https://openrouter.ai/api/v1"

# Validación básica
if not api_key:
    st.error("⚠️ API Key de OpenRouter no configurada.")
    st.markdown("""
    **Pasos para configurar:**
    1. Obtén tu API Key en [OpenRouter.ai](https://openrouter.ai/keys)
    2. Ve a tu app en Streamlit Cloud → **Settings** → **Secrets**
    3. Agrega:
toml
OPENROUTER_API_KEY = "sk-or-v1-tu-key-aqui"


    """)
    st.stop()

# Inicializar cliente de OpenAI (compatible con OpenRouter)
try:
    client = OpenAI(api_key=api_key, base_url=base_url)
except Exception as e:
    st.error(f"Error al inicializar el cliente: {e}")
    st.stop()

# ═══════════════════════════════════════════════════════════════════════
# 3. HEADER Y CONFIGURACIÓN
# ═══════════════════════════════════════════════════════════════════════

st.title("🇬🇹 GuateEmprende IA Pro")
st.markdown(f"""
<div style="background: linear-gradient(90deg, #1a5f2a 0%, #2d8a3e 100%);
            padding: 15px 25px; border-radius: 10px; margin-bottom: 20px;">
    <h3 style="color: white; margin: 0;">Tu Consultor de Negocios Inteligente</h3>
    <p style="color: #d4edda; margin: 5px 0 0 0; font-size: 0.9em;">
        📅 Análisis actualizado al <strong>{fecha_hoy}</strong> |
        🧠 Motor: <strong>z-ai/glm-4-9b-chat:free</strong> via OpenRouter
    </p>
</div>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("⚙️ Configuración")

    # Modelos disponibles (OpenRouter tiene muchos, priorizamos el gratuito)
    modelos = [
        "z-ai/glm-4-9b-chat:free",
        "qwen/qwen2.5-72b-instruct:free",
        "microsoft/phi-4:free",
        "deepseek/deepseek-prover-v2:free",
        "anthropic/claude-3.5-sonnet:free",
        "meta-llama/llama-3-8b-instruct:free",
    ]

    modelo_seleccionado = st.selectbox(
        "Modelo de IA:",
        modelos,
        index=0,
        help="Los modelos :free tienen costo cero o muy bajo. Cambia según disponibilidad."
    )

    st.write("---")
    st.markdown("""
    **📊 Contexto económico GT:**
    - PIB {año}: ~$102,000 MDD
    - Inflación estimada: ~4-5%
    - Población: ~18 millones
    - Moneda: Quetzal (GTQ)
    """.format(año=año_actual_str))

    # Contador de consultas (sesión)
    if "contador" not in st.session_state:
        st.session_state.contador = 0

    st.metric("Consultas esta sesión", st.session_state.contador)

    # Info de OpenRouter
    st.info("💡 Usa el modelo **glm-4-9b** para mejor rendimiento gratuito.")

st.markdown("---")

# ═══════════════════════════════════════════════════════════════════════
# 4. DEFINICIÓN DE TABS
# ═══════════════════════════════════════════════════════════════════════

tab1, tab2, tab3, tab4 = st.tabs([
    "📍 Buscar Ubicación",
    "💵 Inversión por Capital",
    "🏬 ¿Qué abro en mi zona?",
    "📋 Plan de Negocios Completo"
])

# ═══════════════════════════════════════════════════════════════════════
# 5. FUNCIÓN HELPER PARA CONSULTAS A LA IA
# ═══════════════════════════════════════════════════════════════════════

def consultar_ia(
    prompt_sistema: str,
    prompt_usuario: str,
    temperatura: float = 0.6,
    max_tokens: int = 4096
) -> str | None:
    """
    Wrapper centralizado para todas las llamadas a la API de OpenRouter.
    Maneja errores, cuenta consultas y formatea respuestas.
    """

    # Incrementar contador de sesión
    st.session_state.contador += 1

    # Mostrar spinner con contexto
    mensajes_container = st.empty()

    try:
        with st.spinner("🤖 IA analizando tu consulta..."):

            response = client.chat.completions.create(
                model=modelo_seleccionado,
                messages=[
                    {"role": "system", "content": prompt_sistema},
                    {"role": "user", "content": prompt_usuario}
                ],
                temperature=temperatura,
                max_tokens=max_tokens
            )

            contenido = response.choices[0].message.content

            if contenido:
                # Mensaje de éxito discreto
                st.success(f"✅ Respuesta generada (consulta #{st.session_state.contador})")
                return contenido
            else:
                st.warning("⚠️ La IA devolvió una respuesta vacía. Intenta reformular tu consulta.")
                return None

    except AuthenticationError:
        st.error("🔴 API Key inválida. Verifica tu OPENROUTER_API_KEY en los Secrets.")
        return None

    except RateLimitError:
        st.error("""
        🔴 **Límite de solicitudes alcanzado.**

        OpenRouter tiene límites de uso gratuito. Espera unos minutos o cambia a otro modelo free.

        Modelos alternativos con tier gratuito:
        - `qwen/qwen2.5-72b-instruct:free`
        - `meta-llama/llama-3-8b-instruct:free`
        """)
        return None

    except APIConnectionError as e:
        st.error(f"""
        🔴 **Error de conexión a OpenRouter.**

        Posibles causas:
        - Problema temporal de red
        - El modelo seleccionado no está disponible

        Detalle: {str(e)[:150]}
        """)
        return None

    except Exception as e:
        st.error(f"🔴 Error inesperado: {str(e)}")
        with st.expander("📋 Detalles técnicos"):
            st.code(traceback.format_exc())
        return None

# ═══════════════════════════════════════════════════════════════════════
# ╔══════════════════════════════════════════════════════════════════════╗
# ║                    PESTAÑA 1: BUSCAR UBICACIÓN                       ║
# ╚══════════════════════════════════════════════════════════════════════╝

with tab1:
    st.header("📍 Análisis de Ubicación Óptima para tu Negocio")
    st.markdown("""
    Describe el tipo de negocio que deseas establecer. La IA analizará el mercado
    guatemalteco y te recomendará las **mejores zonas** con justificación basada en
    datos de mercado actuales.
    """)

    with st.form("form_ubicacion", clear_on_submit=False):
        col1, col2 = st.columns([3, 1])
        with col1:
            tipo_negocio = st.text_input(
                "🏪 ¿Qué tipo de negocio quieres poner?",
                placeholder="Ej: Cafetería de especialidad, Farmacia de barrio, Lavandería automática, Gym boutique, Restaurante familiar...",
                help="Sé lo más específico posible para mejores resultados"
            )
        with col2:
            presupuesto_alquiler = st.number_input(
                "Presupuesto alquiler (Q/mes):",
                min_value=0,
                max_value=100000,
                value=10000,
                step=1000,
                help="Máximo que puedes pagar de alquiler mensuales"
            )

        contexto_extra = st.text_area(
            "📝 Contexto adicional (opcional):",
            placeholder="Ej: Busco zona segura con buen tráfico vehicular, público objetivo joven (18-35), prefiero area cerca de universidades...",
            help="Cualquier restricción o preferencia adicional"
        )

        submit_1 = st.form_submit_button("🔍 Analizar Mercado Guatemalteco", use_container_width=True)

    if submit_1 and tipo_negocio:
        prompt_sistema = f"""Eres un director de geomarketing y desarrollo comercial en Guatemala
        con 20 años de experiencia analizando zonas comerciales. Tienes acceso a datos actualizados
        del mercado guatemalteco ({fecha_hoy}).

        Tu especialidad es recomendar ubicaciones estratégicas para negocios basándote en:
        - Niveles socioeconómicos por zona (A/B, C+, C, D)
        - Tráfico peatonal y vehicular ( conteos horarios )
        - Costo de alquiler por metro cuadrado actualizado
        - Perfil demográfico y hábitos de consumo
        - Competencia directa existente
        - Tendencias de desarrollo urbano

        Guatemala tiene zonas comerciales clave: Zona 4, 9, 10, 14, 15, 16 de Ciudad de Guatemala;
        Carretera a El Salvador; Antigua Guatemala; Zona 1; Periférico; así como ciudades
        secundarias como Quetzaltenango, Cobán, Retalhuleu, Puerto San José, Panajachel.

        IMPORTANTE: Usa datos razonables y estimados para {año_actual_str}. Si no tienes el dato
        exacto, proporciona rangos estimados razonables y marca como [estimado]."""

        prompt_usuario = f"""ANÁLISIS DE UBICACIÓN COMERCIAL

NEGOCIO PROPUESTO: {tipo_negocio}
PRESUPUESTO DE ALQUILER: Q{presupuesto_alquiler:,.0f} mensuales
CONTEXTO ADICIONAL: {contexto_extra if contexto_extra else "No proporcionado"}

REQUISITOS DE LA RESPUESTA:

## 1. TOP 3 ZONAS RECOMENDADAS

Para cada zona, proporciona una tabla con:

| Característica | Detalle |
|---|---|
| **Zona Exacta** | Nombre específico |
| **Nivel Socioeconómico** | Clase A/B, C+, C, D |
| **Tráfico Peatonal** |[estimado] personas/hora en horarios pico |
| **Tráfico Vehicular** |[estimado] vehículos/hora |
| **Alquiler Approx/m²** | Q[estimado]/m² mensual |
| **Competencia Directa** | Cantidad estimada de negocios similares |
| **Viabilidad 1-10** | Con justificación breve |

## 2. DATOS DE MERCADO PARA ESTE SECTOR EN GUATEMALA

- Tamaño estimado del mercado en GT
- Tasa de crecimiento anual del sector
- Gasto promedio per cápita en este tipo de negocio
- Proyección de demanda para {año_actual_str}

## 3. ANÁLISIS COMPARATIVO

Tabla resumen:
| Zona | Costo/m² | Tráfico | Competencia | Puntaje |
|---|---|---|---|---|
| ... | ... | ... | ... | ... |

## 4. RECOMENDACIÓN FINAL

Zona elegida #1 + justificación de ROI esperado a 12 meses.

Usa Markdown profesional, tablas, negritas y emojis. Sé específico y realista."""

        respuesta = consultar_ia(prompt_sistema, prompt_usuario)
        if respuesta:
            st.markdown(respuesta)
            st.download_button(
                "💾 Descargar análisis (.txt)",
                data=respuesta,
                file_name=f"analisis_ubicacion_{tipo_negocio.replace(' ', '_')[:30]}.txt",
                mime="text/plain"
            )

# ═══════════════════════════════════════════════════════════════════════
# ╔══════════════════════════════════════════════════════════════════════╗
# ║                  PESTAÑA 2: INVERSIÓN POR CAPITAL                    ║
# ╚══════════════════════════════════════════════════════════════════════╝

with tab2:
    st.header("💵 Oportunidades de Inversión según tu Capital")
    st.markdown("""
    Indica tu presupuesto de arranque. La IA calculará las **3 opciones más rentables**
    para ese monto en el contexto económico actual de Guatemala.
    """)

    with st.form("form_capital", clear_on_submit=False):
        col_moneda, col_monto = st.columns([1, 3])
        with col_moneda:
            moneda = st.selectbox("Moneda:", ["Q (Quetzales GTQ)", "USD (Dólares)"], index=0)
        with col_monto:
            monto = st.number_input(
                "Monto de inversión:",
                min_value=1000,
                max_value=50000000,
                value=50000,
                step=5000,
                help="Cantidad total disponible para arrancar"
            )

        col_riesgo, col_tiempo = st.columns(2)
        with col_riesgo:
            riesgo = st.select_slider(
                "Perfil de riesgo:",
                options=["Conservador (bajo riesgo, retorno estable)",
                        "Moderado (equilibrio riesgo/ganancia)",
                        "Agresivo (alto riesgo, alto retorno)"],
                value="Moderado (equilibrio riesgo/ganancia)"
            )
        with col_tiempo:
            tiempo_deseado = st.select_slider(
                "Tiempo máximo de recuperación:",
                options=["6 meses", "12 meses", "18 meses", "24 meses", "3+ años"],
                value="18 meses"
            )

        submit_2 = st.form_submit_button("💰 Analizar Rentabilidad", use_container_width=True)

    if submit_2:
        simbolo = "Q" if "Q" in moneda else "___CODE_BLOCK_4___quot;
        capital = f"{simbolo}{monto:,.0f}"

        prompt_sistema = f"""Eres un analista financiero senior de una firma de inversión
        guatemalteca especializada en PYMES. Tienes acceso a datos económicos actualizados
        de Guatemala ({fecha_hoy}) incluyendo:

        - Tasas de interés bancario y de microfinanzas
        - Inflación anual y proyecciones
        - Sectores con mayor crecimiento en {año_actual_str}
        - Márgenes de ganancia típicos por sector comercial
        - Costos operativos promedio en Ciudad de Guatemala y ciudades secundarias
        - Regulaciones fiscales y laborales de Guatemala

        IMPORTANTE: Proporciona datos financieros razonables y估算ados para el contexto
        guatemalteco actual. Si no tienes el dato exacto, usa rangos sensatos."""

        prompt_usuario = f"""ANÁLISIS DE INVERSIÓN EN GUATEMALA

PERFIL DEL INVERSIONISTA:
- Capital disponible: **{capital}**
- Moneda base: **{moneda.split(" ")[0]}**
- Perfil de riesgo: **{riesgo}**
- Tiempo máximo de recuperación: **{tiempo_deseado}**

REQUISITOS DE LA RESPUESTA:

## 1. TOP 3 NEGOCIOS RECOMENDADOS

Para cada negocio, estructura:

### 📊 [Nombre del Negocio 1/2/3]

**Tabla de Inversión Inicial Detallada:**
| Rubro de Inversión | % del Capital | Monto | Notas |
|---|---|---|---|
| Trámites legales (SAT, Registro Mercantil) | X% | Q X,XXX | [estimado] |
| Licencia de funcionamiento (municipal) | X% | Q X,XXX | [estimado] |
| Infraestructura / Adecuación del local | X% | Q X,XXX | [estimado] |
| Equipamiento y mobiliario | X% | Q X,XXX | [estimado] |
| Inventario / Materia prima inicial | X% | Q X,XXX | [estimado] |
| Marketing de lanzamiento | X% | Q X,XXX | [estimado] |
| Caja chica (3 meses operación) | X% | Q X,XXX | [estimado] |
| **TOTAL** | **100%** | **{capital}** | |

**Proyección Financiera (12 meses):**
| Mes | Ingresos Estimados | Egresos | Ganancia Neta | Acumulado |
|---|---|---|---|---|
| Mes 1 | Q XX,XXX | Q XX,XXX | Q XX,XXX | Q XX,XXX |
| Mes 3 | Q XX,XXX | Q XX,XXX | Q XX,XXX | Q XX,XXX |
| Mes 6 | Q XX,XXX | Q XX,XXX | Q XX,XXX | Q XX,XXX |
| Mes 12 | Q XX,XXX | Q XX,XXX | Q XX,XXX | Q XX,XXX |

**Métricas Clave:**
- Punto de equilibrio: Mes [X]
- Ingreso mensual mínimo para cubrir gastos: Q [XX,XXX]
- Margen bruto estimado: [XX]%
- ROI proyectado a 12 meses: [XX]%
- ROI proyectado a 24 meses: [XX]%

**Estrategia Lean para Guatemala:**
Cómo validar el negocio gastando solo el 60% del capital primero.

**Riesgo Principal + Mitigación:**
Especificar riesgo propio de Guatemala (temporal, inseguridad,変動 cambiaria, etc.)

## 2. ANÁLISIS COMPARATIVO

| Negocio | Inversión | ROI 12m | ROI 24m | Riesgo | Puntaje |
|---|---|---|---|---|---|
| ... | ... | ... | ... | ... | ... |

## 3. RECOMENDACIÓN FINAL

Elección #1 + justificación de por qué es la mejor opción para este capital y perfil.

Usa tablas Markdown, cálculos numéricos específicos, y sea realista con los márgenes guatemaltecos."""

        respuesta = consultar_ia(prompt_sistema, prompt_usuario, temperatura=0.5)
        if respuesta:
            st.markdown(respuesta)

# ═══════════════════════════════════════════════════════════════════════
# ╔══════════════════════════════════════════════════════════════════════╗
# ║              PESTAÑA 3: ¿QUÉ NEGOCIO EN MI ZONA?                     ║
# ╚══════════════════════════════════════════════════════════════════════╝

with tab3:
    st.header("🏬 Detección de Nichos Vacíos en tu Ubicación")
    st.markdown("""
    Indica tu municipio, zona o departamento en Guatemala. La IA identificará
    **negocios de alta demanda y baja oferta** específicos para tu área.
    """)

    with st.form("form_zona", clear_on_submit=False):
        ubicacion = st.text_input(
            "📍 Tu ubicación exacta en Guatemala:",
            placeholder="Ej: San Lucas Sacatepéquez (centro), Zona 18 de Mixco, Panajachel (frente al lago), Puerto San José (zona hotelera)...",
            help="Entre más específico, mejor el análisis"
        )

        caracteristicas = st.multiselect(
            "Características del área (selecciona las que apliquen):",
            [
                "Residencial clase alta (condominios, residenciales privados)",
                "Residencial clase media (colonias tradicionales)",
                "Residencial popular (barriadas, loteos populares)",
                "Zona comercial consolidada (tiendas, bancos, restaurantes)",
                "Zona comercial de barrio (pulperías, servicios locales)",
                "Zona industrial",
                "Área turística (hoteles, restaurantes para turistas)",
                "Cercano a universidad o instituto",
                "Cercano a oficinas gubernamentales o judiciales",
                "Alto tráfico vehicular (boulevard, carretera principal)",
                "Alta densidad poblacional (>5,000 hab/km²)",
                "Población joven predominante (<30 años)",
                "Población madura predominante (>40 años)",
                "Acceso a transporte público frecuente",
                "Seguridad concernciente (robos, pandillas)",
                "Problemas de infraestructura (baches, inundaciones)"
            ],
            default=[],
            help="Ayuda a refinar el análisis"
        )

        submit_3 = st.form_submit_button("🎯 Identificar Oportunidades", use_container_width=True)

    if submit_3 and ubicacion:
        perfil = ", ".join(caracteristicas) if caracteristicas else "No especificado"

        prompt_sistema = f"""Eres un consultor de desarrollo económico local del Ministerio de Economía
        de Guatemala con conocimiento profundo de las dinámicas comerciales de cada municipio
        y zona del país. Fecha del análisis: {fecha_hoy}.

        Conoces bien:
        - Demografía por zona (INE, censos recientes)
        - Patrones de consumo según nivel socioeconómico
        - Brechas de mercado (sectores oversaturados vs. desabastecidos)
        - Regulaciones municipales por jurisdicción
        - Infraestructura y logística de acceso
        - Factores de riesgo de seguridad por zona

        IMPORTANTE: Sé específico. No recomiences negocios genéricos. Si la zona es rural,
        no sugieras modelos que requieren alto tráfico peatonal urbano."""

        prompt_usuario = f"""DIAGNÓSTICO DE BRECHAS DE MERCADO

UBICACIÓN: **{ubicacion}**
CARACTERÍSTICAS DEL ÁREA: {perfil}

REQUISITOS DE LA RESPUESTA:

## 1. ANÁLISIS DE LA ZONA

**Perfil Demográfico Estimado:**
| Dato | Estimación |
|---|---|
| Población del radio de 1-3 km | [XX,XXX personas] [estimado] |
| Nivel socioeconómico predominante | [Clase A/B, C+, C, D] |
| Edad promedio predominante | [XX] años |
| Ingreso familiar promedio estimado | Q [XX,XXX]/mes [estimado] |
| Densidad habitacional | [Alta/Media/Baja] |

**Flujo Comercial:**
| Tipo de Flujo | Estimación |
|---|---|
| Tráfico peatonal en día laboral | [X,XXX-X,XXX personas/hora] [estimado] |
| Tráfico vehicular | [XXX-X,XXX vehículos/hora] [estimado] |
| Horarios de mayor actividad | [horas específicas] |
| Días de mayor flujo | [días de la semana] |

## 2. TOP 3 OPORTUNIDADES (Negocios Faltantes)

Para cada oportunidad:

### 💡 Oportunidad [1/2/3]: [Nombre del Negocio]

**Necesidad Insatisfecha Detectada:**
- ¿Qué problema no está siendo resuelto en esta zona?
- ¿Quién es el vecino que sufre esta carencia?
- ¿Cuántos competidores DIRECTOS hay a 500m? [estimado]

**Perfil del Cliente Objetivo:**
- Edad, género, nivel de ingreso
- Frecuencia de compra esperada
- Ticket promedio estimado

**Propuesta de Valor Diferencial:**
¿Cómo sería TU versión del negocio para dominar esta zona?

**Inversión Estimada para Arrancar:**
Q [XX,XXX] - Q [XX,XXX] [estimado]

**Rentabilidad Esperada:**
- Margen bruto: [XX]% [estimado]
- Tiempo de recuperación: [X-X] meses [estimado]

**Barreras de Entrada Específicas:**
- Trámite más complejo en esta municipalidad
- Costo de licencia de funcionamiento [estimado]
- Factor logística o geográfico clave
- Consideración de seguridad para horarios de operación

**Potencial de Escalamiento:**
¿Puede crecer a 2da o 3ra sucursal en la misma región?

## 3. COMPARATIVA DE OPORTUNIDADES

| Oportunidad | Inversión Est. | ROI 12m | Competencia | Facilidad | Puntaje |
|---|---|---|---|---|---|
| ... | ... | ... | ... | ... | ... |

## 4. RECOMENDACIÓN PRIORITARIA

Oportunidad #1 recomendada + razón específica por la cual es la mejor opción
para esta ubicación.

Sé muy específico a la zona. No genérico. Usa Markdown, tablas y emojis."""

        respuesta = consultar_ia(prompt_sistema, prompt_usuario, temperatura=0.7)
        if respuesta:
            st.markdown(respuesta)

# ═══════════════════════════════════════════════════════════════════════
# ╔══════════════════════════════════════════════════════════════════════╗
# ║           PESTAÑA 4: GENERADOR DE PLAN DE NEGOCIOS                    ║
# ╚══════════════════════════════════════════════════════════════════════╝

with tab4:
    st.header("📋 Generador de Plan de Negocios Profesional")
    st.markdown("""
    Completa los datos de tu idea de negocio y genera un **plan de negocios
    completo** estructurado, listo para presentar a un banco, inversionista
    o tramitär ante entidades gubernamentales de Guatemala.
    """)

    with st.form("form_plan", clear_on_submit=False):
        st.subheader("📝 Datos del Proyecto")

        col_izq, col_der = st.columns(2)

        with col_izq:
            idea_negocio = st.text_input(
                "Nombre o descripción del negocio:",
                placeholder="Ej: 'BiteBox' - Comida rápida saludable tipo food truck con menú vegano"
            )
            ubicacion_plan = st.text_input(
                "Ubicación planificada:",
                placeholder="Ej: Zona 15 (sectores comerciales)"
            )
            capital_inicial = st.number_input(
                "Capital total de inversión (Q):",
                min_value=5000,
                max_value=10000000,
                value=75000,
                step=5000
            )

        with col_der:
            formato_doc = st.selectbox(
                "Formato del documento:",
                [
                    "📄 Lean Canvas (1 página, ágil para validación)",
                    "📊 Plan Tradicional Completo (banco/inversionista)",
                    "📋 Plan para Trámites Gubernamentales (SAT, municipal)"
                ],
                index=1
            )
            tipo_constitucion = st.selectbox(
                "Constitución legal:",
                [
                    "Empresa Individual (Persona Individual)",
                    "Sociedad Anónima (S.A.)",
                    "S.R.L. (Sociedad de Responsabilidad Limitada)",
                    "Aún no definido / Pequeño Contribuyente"
                ],
                index=0
            )
            empleados = st.number_input(
                "Empleados al inicio:",
                min_value=0,
                max_value=100,
                value=2
            )

        st.write("---")
        st.subheader("🎯 Propuesta de Valor")

        propuesta_valor = st.text_area(
            "¿Qué hace diferente a tu negocio? (Diferenciador clave):",
            placeholder="Ej: Somos el único restaurante con certificación orgánica en toda la zona 10, con ingredientes de productores locales del altiplano...",
            height=80
        )

        submit_4 = st.form_submit_button(
            "📝 Generar Plan de Negocios Profesional",
            use_container_width=True,
            type="primary"
        )

    if submit_4 and idea_negocio:
        formato_elegido = formato_doc.split(" - ")[0] if " - " in formato_doc else formato_doc

        prompt_sistema = f"""Eres el socio director de una firma de consultoría de negocios
        de alto nivel en Guatemala (similar a PwC o Deloitte pero enfocada en PYMES locales).
        Tienes 25 años de experiencia redactando planes de negocio para presentaciones bancarias,
        inversores ángeles, y trámites ante instituciones del Estado de Guatemala.
        Fecha del documento: {fecha_hoy}.

        Conoces profundamente:
        - Requisitos exactos del Registro Mercantil para constitución de empresas en Guatemala
        - Trámites y costos ante la SAT (régimen de Pequeño Contribuyente, Régimen General, etc.)
        - Licencias de funcionamiento municipales (Ciudad de Guatemala y principales municipios)
        - Requisitos del IGSS,INTECAP para patronos
        - Proyecciones financieras realistas para el mercado guatemalteco
        - Márgenes de ganancia típicos por sector comercial en GT
        - Costos operativos promedio (alquiler, energía, agua, mano de obra) en Ciudad de Guatemala y ciudades principales
        - Estrategia de marketing digital efectiva para Guatemala (Facebook, Instagram, WhatsApp Business dominantes)

        IMPORTANTE: Este documento será presentado a un banco o inversor. Debe ser
        profesional, detallado, con datos financieros específicos y realistas."""

        prompt_usuario = f"""DOCUMENTO: PLAN DE NEGOCIOS COMPLETO PARA GUATEMALA

DATOS DEL PROYECTO:
- **Nombre/Idea:** {idea_negocio}
- **Ubicación:** {ubicacion_plan}
- **Capital de Inversión:** Q{capital_inicial:,.0f}
- **Formato solicitado:** {formato_elegido}
- **Tipo de constitución:** {tipo_constitucion}
- **Empleados iniciales:** {empleados}
- **Diferenciador clave:** {propuesta_valor if propuesta_valor else "No especificado"}

═══════════════════════════════════════════════════════════════
                    ESTRUCTURA DEL DOCUMENTO
═══════════════════════════════════════════════════════════════

# 📋 PLAN DE NEGOCIOS: {idea_negocio.upper()}

---

## 1. RESUMEN EJECUTIVO
(300 palabras máximo, orientado a banco o inversor)

Resumen del negocio, mercado objetivo, capital requerido, y retorno esperado en 24 meses.

---

## 2. ANÁLISIS DE MERCADO

### 2.1 Tamaño del Mercado
- Mercado total direccionable en Guatemala (TAM): Q [XXX millones] [estimado]
- Mercado objetivo (SAM): Q [XX millones] [estimado]
- Mercado capturable (SOM) Año 1: Q [X millones] [estimado]

### 2.2 Tendencias de Consumo {año_actual_str}
Análisis de tendencias actuales relevantes para este sector en Guatemala.

### 2.3 Análisis Competitivo
Mapeo de 5 competidores principales (nombre ficticio o tipo, ubicación, precio, fortalezas, debilidades).

### 2.4 Análisis FODA
| | Positivo | Negativo |
|---|---|---|
| **Interno** | Fortalezas | Debilidades |
| **Externo** | Oportunidades | Amenazas |

---

## 3. PLAN DE MARKETING Y VENTAS

### 3.1 Estrategia de Marketing Digital (Guatemala)
- **Redes sociales principales:** Facebook, Instagram, WhatsApp Business
- **Presupuesto mensual recomendado:** Q [X,XXX] [estimado]
- **Contenido sugerido:** [tipos de contenido]
- **KPI objetivo mes 1-3:** [métricas específicas]

### 3.2 Estrategia de Precios
Tabla de productos/servicios con precio de venta, costo unitario y margen:

| Producto/Servicio | Costo Unit. | Precio Venta | Margen | Precio Competidor Prom. |
|---|---|---|---|---|
| ... | Q XX | Q XX | XX% | Q XX |

### 3.3 Canal de Ventas
Descripción del proceso de venta, desde captación hasta cierre.

---

## 4. PLAN DE OPERACIONES

### 4.1 Modelo Operativo
- Horario de atención sugerido para Guatemala
- Proveedores clave identificados (nacionales/importados)
- Cadena de suministro básica
- Equipo necesario

### 4.2 Necesidad de Personal
| Puesto | Cantidad | Salario Mensual (Q) | Funciones |
|---|---|---|---|
| ... | X | Q X,XXX | ... |

### 4.3 Tecnología y Herramientas
Sistemas, software, equipos tecnológicos necesarios.

---

## 5. ESTRUCTURA LEGAL Y TRÁMITES EN GUATEMALA

### 5.1 Pasos de Constitución ({tipo_constitucion})

| # | Trámite | Entidad | Costo Estimado (Q) | Tiempo | Prioridad |
|---|---|---|---|---|---|
| 1 | ... | ... | Q XXX | X días | Alta |
| 2 | ... | ... | Q XXX | X días | Alta |
| ... | ... | ... | ... | ... | ... |

### 5.2 Obligaciones Fiscales
- Régimen selectedo: [Pequeño Contribuyente / Régimen General]
- Impuesto sobre la renta (ISR): [X]% sobre utilidades
- Facturación electrónica: Requisitos SAT
- Libros contables: Requeridos

### 5.3 Obligaciones Laborales
- IGSS (trabajador): [X]% del salario
- Patrono IGSS: [XX.XX]% sobre planilla
- INTECAP: [X]% sobre planilla
-IRTRA: [X]% sobre planilla

---

## 6. PROYECCIONES FINANCIERAS

### 6.1 Inversión Inicial Detallada

| Rubro | Monto (Q) | % del Capital | Notas |
|---|---|---|---|
| Trámites y constitución | Q X,XXX | X% | [estimado] |
| Licencia municipal | Q X,XXX | X% | [estimado] |
| Adecuación del local | Q X,XXX | X% | [estimado] |
| Equipo y mobiliario | Q X,XXX | X% | [estimado] |
| Inventario inicial | Q X,XXX | X% | [estimado] |
| Marketing lanzamiento | Q X,XXX | X% | [estimado] |
| Caja chica (3 meses) | Q X,XXX | X% | [estimado] |
| **TOTAL** | **Q {capital_inicial:,.0f}** | **100%** | |

### 6.2 Proyección de Ingresos y Egresos (Meses 1-12)

| Mes | Ingresos | Alquiler | Proveedores | Planilla | Marketing | Servicios | Otros | Egresos Totales | Ganancia Neta | Acumulado |
|---|---|---|---|---|---|---|---|---|---|---|
| Mes 1 | Q X,XXX | Q X,XXX | Q X,XXX | Q X,XXX | Q X,XXX | Q X,XXX | Q X,XXX | Q X,XXX | Q X,XXX | Q X,XXX |
| Mes 3 | Q X,XXX | Q X,XXX | Q X,XXX | Q X,XXX | Q X,XXX | Q X,XXX | Q X,XXX | Q X,XXX | Q X,XXX | Q X,XXX |
| Mes 6 | Q X,XXX | Q X,XXX | Q X,XXX | Q X,XXX | Q X,XXX | Q X,XXX | Q X,XXX | Q X,XXX | Q X,XXX | Q X,XXX |
| Mes 12 | Q X,XXX | Q X,XXX | Q X,XXX | Q X,XXX | Q X,XXX | Q X,XXX | Q X,XXX | Q X,XXX | Q X,XXX | Q X,XXX |

*Nota: Los meses 2, 4, 5, 7-11 no shown para brevedad pero deben seguir la tendencia.*

### 6.3 Métricas Clave

| Métrica | Valor Estimado |
|---|---|
| **Punto de Equilibrio** | Mes [X] |
| **Ingreso mensual mínimo** | Q [XX,XXX] |
| **Margen bruto promedio** | [XX]% |
| **Margen neto promedio (mes 6+)** | [XX]% |
| **ROI a 12 meses** | [XX]% |
| **ROI a 24 meses** | [XX]% |

---

## 7. ANÁLISIS DE RIESGOS Y CONTINGENCIAS

| Riesgo | Probabilidad | Impacto | Plan de Mitigación |
|---|---|---|---|
| [Riesgo 1] | Alta/Media/Baja | Alto/Medio/Bajo | [Estrategia] |
| [Riesgo 2] | Alta/Media/Baja | Alto/Medio/Bajo | [Estrategia] |
| [Riesgo 3] | Alta/Media/Baja | Alto/Medio/Bajo | [Estrategia] |

*Riesgos típicos en Guatemala: volatilidad del tipo de cambio (si hay importación), estacionalidad, inseguridad, temporalidad, cambios regulatorios.*

---

## 8. PLAN DE IMPLEMENTACIÓN (PRIMEROS 30 DÍAS)

| Semana | Acción | Responsable | Entregable |
|---|---|---|---|
| Semana 1 | ... | ... | ... |
| Semana 2 | ... | ... | ... |
| Semana 3 | ... | ... | ... |
| Semana 4 | ... | ... | ... |

---

## 9. METAS A 6, 12 Y 24 MESES

| Horizonte | Meta de Ingresos | Clientes/Mes | Empleados | Observaciones |
|---|---|---|---|---|
| 6 meses | Q [XX,XXX]/mes | [XX] clientes | X | [Notas] |
| 12 meses | Q [XX,XXX]/mes | [XX] clientes | X | [Notas] |
| 24 meses | Q [XX,XXX]/mes | [XX] clientes | X | ¿2da sucursal? |

---

## 10. CONCLUSIÓN

Resumen ejecutivo final + llamado a la acción (si es para inversor).

═══════════════════════════════════════════════════════════════

REGLAS DE FORMATO:
- Usar TODAS las tablas Markdown posibles para datos numéricos
- Párrafos máximo 3-4 líneas
- Datos estimados deben marcarse con [estimado]
- Incluir emojis en títulos principales para navegación visual
- Tono: profesional, ejecutivo, presentable a entidad bancaria
- Ser realista: no exagerar márgenes ni subestimar costos
- Si el capital parece insuficiente para la idea, indicarlo claramente"""

        respuesta = consultar_ia(prompt_sistema, prompt_usuario, temperatura=0.4, max_tokens=8192)
        if respuesta:
            st.markdown(respuesta)

            # Descarga
            st.download_button(
                "💾 Descargar Plan de Negocios completo (.txt)",
                data=respuesta,
                file_name=f"Plan_Negocios_{idea_negocio.replace(' ', '_')[:25]}_{fecha_hoy.replace(' ', '_').replace(',','')}.txt",
                mime="text/plain"
            )

# ═══════════════════════════════════════════════════════════════════════
# FOOTER
# ═══════════════════════════════════════════════════════════════════════

st.markdown("---")
st.markdown(f"""
<div style="text-align: center; padding: 20px; background: #f8f9fa;
            border-radius: 10px; margin-top: 30px;">
    <p style="color: #666; font-size: 0.9em; margin: 0;">
        🇬🇹 <strong>GuateEmprende IA Pro</strong> |
        Desarrollado para emprendedores guatemaltecos | {año_actual_str}
    </p>
    <p style="color: #999; font-size: 0.8em; margin: 5px 0 0 0;">
        💡 Datos generados por IA. Verificar siempre con contadores públicos y
       专业人士 legales antes de tomar decisiones de inversión.
    </p>
    <p style="color: #aaa; font-size: 0.75em; margin: 10px 0 0 0;">
        Motor: OpenRouter | Modelo: {modelo_seleccionado} |
        Consultas esta sesión: {st.session_state.contador}
    </p>
</div>
""", unsafe_allow_html=True)
