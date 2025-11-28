import os
import streamlit as st
from openai import OpenAI
import requests
import json

# Configuración de página para permitir iframe embedding
st.set_page_config(
    page_title="Chatbot Admin - El Picantito",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# para la api de deepseek se openrouter
# === CONFIGURACIÓN DE LA API DE SPRING BOOT ===
SPRINGBOOT_API_BASE = os.environ.get("SPRINGBOOT_API_BASE", "http://localhost:9998")

# === FUNCIONES PARA OBTENER DATOS DE SPRING BOOT ===
def obtener_estadisticas(token=None):
    """Obtiene todas las estadísticas del sistema"""
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    try:
        response = requests.get(f"{SPRINGBOOT_API_BASE}/api/estadisticas/todas", headers=headers, timeout=5)
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        return None

@st.cache_data(ttl=300)
def obtener_usuarios(token=None):
    """Obtiene información de usuarios (sin contraseñas)"""
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    try:
        response = requests.get(f"{SPRINGBOOT_API_BASE}/api/usuarios/dto", headers=headers, timeout=5)
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        return None

@st.cache_data(ttl=300)
def obtener_adicionales(token=None):
    """Obtiene todos los adicionales disponibles"""
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    try:
        response = requests.get(f"{SPRINGBOOT_API_BASE}/api/adicional", headers=headers, timeout=5)
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        return None

@st.cache_data(ttl=300)
def obtener_productos(token=None):
    """Obtiene todos los productos"""
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    try:
        response = requests.get(f"{SPRINGBOOT_API_BASE}/api/productos", headers=headers, timeout=5)
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        return None

@st.cache_data(ttl=300)
def obtener_relaciones_producto_adicional(token=None):
    """Obtiene las relaciones entre productos y adicionales"""
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    try:
        response = requests.get(f"{SPRINGBOOT_API_BASE}/api/adicional/productoAdicionales", headers=headers, timeout=5)
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        return None

def construir_contexto_sistema(token=None):
    """Construye un contexto enriquecido con datos del sistema"""
    contexto_base = """Eres un asistente útil para la página web 'El Picantito', un restaurante mexicano. 
Responde amablemente a las preguntas sobre las funcionalidades del sitio. 
Usa un tono cálido y amigable, con toques de humor mexicano cuando sea apropiado."""
    
    # Intentar obtener datos del sistema
    estadisticas = obtener_estadisticas(token)
    usuarios = obtener_usuarios(token)
    adicionales = obtener_adicionales(token)
    productos = obtener_productos(token)
    relaciones = obtener_relaciones_producto_adicional(token)
    
    # Agregar información al contexto si está disponible
    contexto_adicional = []
    
    if estadisticas:
        contexto_adicional.append(f"\n\n=== ESTADÍSTICAS DEL SISTEMA ===")
        contexto_adicional.append(f"- Total de pedidos: {estadisticas.get('totalPedidos', 'N/A')}")
        contexto_adicional.append(f"- Ingresos totales: ${estadisticas.get('ingresosTotales', 'N/A')}")
        contexto_adicional.append(f"- Ingresos netos: ${estadisticas.get('ingresosNetos', 'N/A')}")
        if estadisticas.get('productosMasVendidos'):
            # Convertir IDs a nombres
            ids = estadisticas['productosMasVendidos']
            nombres = []
            if productos:
                for pid in ids:
                    nombre = next((p.get('nombre') for p in productos if p.get('id') == pid), f"ID {pid}")
                    nombres.append(nombre)
                contexto_adicional.append(f"- Productos más vendidos: {', '.join(nombres)}")
            else:
                contexto_adicional.append(f"- Productos más vendidos (IDs): {ids}")
    
    if usuarios:
        contexto_adicional.append(f"\n\n=== INFORMACIÓN DE USUARIOS ===")
        contexto_adicional.append(f"- Total de usuarios registrados: {len(usuarios)}")
        roles = {}
        for u in usuarios:
            rol = u.get('rol', 'DESCONOCIDO')
            roles[rol] = roles.get(rol, 0) + 1
        contexto_adicional.append(f"- Distribución por roles: {json.dumps(roles)}")
    
    if productos:
        contexto_adicional.append(f"\n\n=== CATÁLOGO DE PRODUCTOS ===")
        contexto_adicional.append(f"- Total de productos: {len(productos)}")
        productos_disponibles = [p for p in productos if p.get('disponible', False)]
        contexto_adicional.append(f"- Productos disponibles: {len(productos_disponibles)}")
        # Listar algunos productos
        if productos_disponibles:
            nombres = [p.get('nombre', 'Sin nombre') for p in productos_disponibles[:5]]
            contexto_adicional.append(f"- Ejemplos: {', '.join(nombres)}")
    
    if adicionales:
        contexto_adicional.append(f"\n\n=== ADICIONALES DISPONIBLES ===")
        contexto_adicional.append(f"- Total de adicionales: {len(adicionales)}")
        adicionales_disponibles = [a for a in adicionales if a.get('disponible', False)]
        contexto_adicional.append(f"- Adicionales disponibles: {len(adicionales_disponibles)}")
        if adicionales_disponibles:
            nombres = [a.get('nombre', 'Sin nombre') for a in adicionales_disponibles[:5]]
            contexto_adicional.append(f"- Ejemplos: {', '.join(nombres)}")
    
    if relaciones:
        contexto_adicional.append(f"\n\n=== PERSONALIZACIÓN ===")
        contexto_adicional.append(f"- Total de combinaciones producto-adicional: {len(relaciones)}")
    
    if contexto_adicional:
        contexto_base += "\n" + "\n".join(contexto_adicional)
        contexto_base += "\n\nUsa esta información para dar respuestas más precisas sobre el estado actual del sistema."
    
    return contexto_base

# === ESTILOS MEXICANOS CON FONDO OSCURO ===
st.markdown(
    """
    <style>
    /* ================== FONDO OSCURO CON PATRÓN MEXICANO ================== */
    .stApp {
        background: linear-gradient(135deg, #2a0c0c 0%, #3a1c1c 25%, #2a0c0c 50%, #3a1c1c 75%, #2a0c0c 100%);
        background-size: 400% 400%;
        animation: gradientBackground 15s ease infinite;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        color: #f8f9fa;
    }
    
    @keyframes gradientBackground {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }

    /* ================== TITULO CON EFECTO MEXICANO ================== */
    .main-title {
        text-align: center;
        font-size: 3rem !important;
        font-weight: 900 !important;
        color: #ff6b6b !important;
        text-shadow: 2px 2px 0px #ff9e00, 4px 4px 0px rgba(0,0,0,0.3);
        margin-bottom: 0.5rem;
        letter-spacing: -0.5px;
        background: linear-gradient(45deg, #ff6b6b, #ff9e00);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        padding: 10px;
    }

    /* ================== ENCABEZADO DECORADO ================== */
    .header-decoration {
        display: flex;
        justify-content: center;
        gap: 20px;
        margin: 10px 0 20px 0;
        font-size: 2rem;
        color: #ff9e00;
    }

    /* ================== TARJETA DE PRESENTACIÓN ================== */
    .welcome-card {
        background: rgba(58, 28, 28, 0.85);
        border-radius: 16px;
        padding: 20px;
        margin: 0 auto 25px auto;
        box-shadow: 0 8px 20px rgba(0,0,0,0.4);
        border-left: 5px solid #ff6b6b;
        border-right: 5px solid #06d6a0;
        max-width: 800px;
        text-align: center;
        color: #f8f9fa;
    }

    /* ================== BURBUJAS DEL USUARIO ================== */
    .stChatMessage[data-testid="stChatMessage-user"] {
        background: linear-gradient(135deg, #ff9e00, #ffb703) !important;
        color: #222 !important;
        padding: 14px 20px;
        border-radius: 18px 18px 0 18px;
        margin: 12px 0;
        font-weight: 600;
        box-shadow: 0 4px 12px rgba(0,0,0,0.4);
        max-width: 75%;
        margin-left: auto;
        border: 2px solid #f77f00;
    }

    /* ================== BURBUJAS DEL ASISTENTE ================== */
    .stChatMessage[data-testid="stChatMessage-assistant"] {
        background: linear-gradient(135deg, #3a3a3a, #4a4a4a) !important;
        color: #f8f9fa !important;
        padding: 14px 20px !important;
        border-radius: 18px 18px 18px 0 !important;
        margin: 12px 0 !important;
        font-weight: 400 !important;
        line-height: 1.6 !important;
        box-shadow: 0 4px 12px rgba(0,0,0,0.4) !important;
        max-width: 75% !important;
        margin-right: auto !important;
        border: 2px solid #ff6b6b;
    }

    /* Forzar que cualquier texto dentro de la burbuja sea blanco */
    .stChatMessage[data-testid="stChatMessage-assistant"] * {
        color: #f8f9fa !important;
        fill: #f8f9fa !important;
    }

    /* ================== INPUT BOX MEJORADO ================== */
    .stTextInput>div>div>input, .stTextInput>div>div>textarea {
        border: 3px solid #ff6b6b !important;
        border-radius: 16px !important;
        padding: 14px !important;
        font-size: 1rem !important;
        background: #3a1c1c !important;
        color: #f8f9fa !important;
        box-shadow: 0 4px 10px rgba(0,0,0,0.3) !important;
        transition: all 0.3s ease !important;
    }
    
    .stTextInput>div>div>input:focus, .stTextInput>div>div>textarea:focus {
        border: 3px solid #06d6a0 !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.4) !important;
        background: #4a2c2c !important;
    }

    /* ================== BOTONES MEJORADOS ================== */
    div[data-testid="stHorizontalBlock"] button[kind="primary"] {
        background: linear-gradient(90deg, #ff6b6b, #ff9e00) !important;
        color: white !important;
        border-radius: 50px !important;
        font-weight: bold !important;
        padding: 12px 24px !important;
        transition: all 0.3s ease !important;
        border: none !important;
        box-shadow: 0 4px 8px rgba(0,0,0,0.3) !important;
    }
    
    div[data-testid="stHorizontalBlock"] button[kind="primary"]:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 12px rgba(0,0,0,0.4) !important;
        background: linear-gradient(90deg, #ff9e00, #ff6b6b) !important;
    }

    /* ================== FOOTER DECORATIVO ================== */
    .footer {
        text-align: center;
        margin-top: 30px;
        padding: 15px;
        color: #adb5bd;
        font-size: 0.9rem;
        border-top: 2px dashed #ff6b6b;
    }

    /* ================== QUITAR ELEMENTOS DE STREAMLIT ================== */
    header[data-testid="stHeader"] {display: none;}
    [data-testid="stToolbar"] {display: none;}
    .reportview-container .main .block-container {padding-top: 2rem;}
    
    /* ================== PERSONALIZAR LA BARRA DE CHAT ================== */
    .stChatInput > div > div > input {
        color: #f8f9fa !important;
    }
    
    .stChatInput > div > div > input::placeholder {
        color: #adb5bd !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# === ELEMENTOS DECORATIVOS ===
st.markdown('<div class="header-decoration">🌮 🌶️ 💃 🎸 🎭</div>', unsafe_allow_html=True)
st.markdown('<h1 class="main-title">💬 Chatbot del PICANTITO</h1>', unsafe_allow_html=True)

# Tarjeta de bienvenida
st.markdown(
    """
    <div class="welcome-card">
        <h3 style="margin:0;color:#ff9e00;">¡Bienvenido al Chatbot DEL PICANTITO! 🎉</h3>
        <p style="margin:10px 0 0 0;">Aquí puedes preguntar todo acerca de las funcionalidades de la página web.<br>
        ¡Soy tu asistente virtual y estoy aquí para ayudarte!</p>
    </div>
    """, 
    unsafe_allow_html=True
)

# Mostrar indicador de conexión con Spring Boot
def verificar_spring_boot():
    """Verifica si Spring Boot está completamente iniciado"""
    try:
        response = requests.get(f"{SPRINGBOOT_API_BASE}/actuator/health", timeout=2)
        if response.status_code == 200:
            # Verificar que el status sea UP
            data = response.json()
            if data.get('status') == 'UP':
                return True, "✅ Conectado a Spring Boot"
            else:
                return False, f"⚠️ Spring Boot está iniciando... (status: {data.get('status')})"
        else:
            return False, f"⚠️ Spring Boot responde pero con estado: {response.status_code}"
    except requests.exceptions.Timeout:
        return False, "⏳ Esperando respuesta de Spring Boot..."
    except requests.exceptions.ConnectionError:
        return False, "❌ No se puede conectar a Spring Boot"
    except Exception as e:
        return False, f"❌ Error al conectar: {str(e)}"

is_connected, connection_msg = verificar_spring_boot()
if is_connected:
    st.success(f"{connection_msg} ({SPRINGBOOT_API_BASE})")
else:
    st.info(f"{connection_msg}. El chatbot funcionará con información limitada hasta que Spring Boot esté listo.")

# Configuración de OpenRouter Admin API: primero st.secrets, fallback a variables de entorno
admin_api_key = None
try:
    admin_api_key = st.secrets.get("ADMIN_API")
except Exception:
    admin_api_key = None

if not admin_api_key:
    admin_api_key = os.environ.get("ADMIN_API")

if not admin_api_key or admin_api_key.strip() == "":
    st.error(
        "🔑 API key faltante. Configure ADMIN_API en .streamlit/secrets.toml para desarrollo o pase la variable ADMIN_API al contenedor."
    )
    st.stop()

openrouter_base_url = "https://openrouter.ai/api/v1"

# === CONFIGURACIÓN DE LA API DE SPRING BOOT ===
SPRINGBOOT_API_BASE = os.environ.get("SPRINGBOOT_API_BASE", "http://localhost:9998")

# === FUNCIÓN PARA OBTENER TOKEN JWT ===
def obtener_token_jwt():
    """Obtiene un token JWT para autenticación con Spring Boot"""
    url = f"{SPRINGBOOT_API_BASE}/api/usuarios/login"
    payload = {
        "nombreUsuario": "admin",  
        "contrasenia": "admin123"  
    }
    try:
        response = requests.post(url, json=payload, timeout=5)
        if response.status_code == 200:
            data = response.json()
            return data.get("token")
        else:
            st.warning(f"Error en login: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        st.warning(f"Error al obtener token: {e}")
        return None

# === FUNCIONES PARA OBTENER DATOS DE SPRING BOOT ===
@st.cache_data(ttl=300)  # Cache por 5 minutos
def obtener_estadisticas(token=None):
    """Obtiene todas las estadísticas del sistema"""
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    try:
        response = requests.get(f"{SPRINGBOOT_API_BASE}/api/estadisticas/todas", headers=headers, timeout=5)
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        return None

@st.cache_data(ttl=300)
def obtener_usuarios(token=None):
    """Obtiene información de usuarios (sin contraseñas)"""
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    try:
        response = requests.get(f"{SPRINGBOOT_API_BASE}/api/usuarios/dto", headers=headers, timeout=5)
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        return None

@st.cache_data(ttl=300)
def obtener_adicionales(token=None):
    """Obtiene todos los adicionales disponibles"""
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    try:
        response = requests.get(f"{SPRINGBOOT_API_BASE}/api/adicional", headers=headers, timeout=5)
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        return None

@st.cache_data(ttl=300)
def obtener_productos(token=None):
    """Obtiene todos los productos"""
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    try:
        response = requests.get(f"{SPRINGBOOT_API_BASE}/api/productos", headers=headers, timeout=5)
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        return None

@st.cache_data(ttl=300)
def obtener_relaciones_producto_adicional(token=None):
    """Obtiene las relaciones entre productos y adicionales"""
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    try:
        response = requests.get(f"{SPRINGBOOT_API_BASE}/api/adicional/productoAdicionales", headers=headers, timeout=5)
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        return None

def construir_contexto_sistema(token=None):
    """Construye un contexto enriquecido con datos del sistema"""
    contexto_base = """Eres un asistente útil para la página web 'El Picantito', un restaurante mexicano. 
Responde amablemente a las preguntas sobre las funcionalidades del sitio. 
Usa un tono cálido y amigable, con toques de humor mexicano cuando sea apropiado."""
    
    # Intentar obtener datos del sistema
    estadisticas = obtener_estadisticas(token)
    usuarios = obtener_usuarios(token)
    adicionales = obtener_adicionales(token)
    productos = obtener_productos(token)
    relaciones = obtener_relaciones_producto_adicional(token)
    
    # Agregar información al contexto si está disponible
    contexto_adicional = []
    
    if estadisticas:
        contexto_adicional.append(f"\n\n=== ESTADÍSTICAS DEL SISTEMA ===")
        contexto_adicional.append(f"- Total de pedidos: {estadisticas.get('totalPedidos', 'N/A')}")
        contexto_adicional.append(f"- Ingresos totales: ${estadisticas.get('ingresosTotales', 'N/A')}")
        contexto_adicional.append(f"- Ingresos netos: ${estadisticas.get('ingresosNetos', 'N/A')}")
        if estadisticas.get('productosMasVendidos'):
            contexto_adicional.append(f"- Productos más vendidos (IDs): {estadisticas['productosMasVendidos']}")
    
    if usuarios:
        contexto_adicional.append(f"\n\n=== INFORMACIÓN DE USUARIOS ===")
        contexto_adicional.append(f"- Total de usuarios registrados: {len(usuarios)}")
        roles = {}
        for u in usuarios:
            rol = u.get('rol', 'DESCONOCIDO')
            roles[rol] = roles.get(rol, 0) + 1
        contexto_adicional.append(f"- Distribución por roles: {json.dumps(roles)}")
    
    if productos:
        contexto_adicional.append(f"\n\n=== CATÁLOGO DE PRODUCTOS ===")
        contexto_adicional.append(f"- Total de productos: {len(productos)}")
        productos_disponibles = [p for p in productos if p.get('disponible', False)]
        contexto_adicional.append(f"- Productos disponibles: {len(productos_disponibles)}")
        # Listar algunos productos
        if productos_disponibles:
            nombres = [p.get('nombre', 'Sin nombre') for p in productos_disponibles[:5]]
            contexto_adicional.append(f"- Ejemplos: {', '.join(nombres)}")
    
    if adicionales:
        contexto_adicional.append(f"\n\n=== ADICIONALES DISPONIBLES ===")
        contexto_adicional.append(f"- Total de adicionales: {len(adicionales)}")
        adicionales_disponibles = [a for a in adicionales if a.get('disponible', False)]
        contexto_adicional.append(f"- Adicionales disponibles: {len(adicionales_disponibles)}")
        if adicionales_disponibles:
            nombres = [a.get('nombre', 'Sin nombre') for a in adicionales_disponibles[:5]]
            contexto_adicional.append(f"- Ejemplos: {', '.join(nombres)}")
    
    if relaciones:
        contexto_adicional.append(f"\n\n=== PERSONALIZACIÓN ===")
        contexto_adicional.append(f"- Total de combinaciones producto-adicional: {len(relaciones)}")
    
    if contexto_adicional:
        contexto_base += "\n" + "\n".join(contexto_adicional)
        contexto_base += "\n\nUsa esta información para dar respuestas más precisas sobre el estado actual del sistema."
    
    return contexto_base

# Obtener token JWT para acceder a endpoints protegidos
token_jwt = obtener_token_jwt()

# Inicializar historial solo una vez
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": construir_contexto_sistema(token_jwt)}
    ]

# Crear cliente de OpenRouter (capturar fallo de autenticación temprano)
try:
    client = OpenAI(api_key=admin_api_key, base_url=openrouter_base_url)
except Exception as e:
    st.error(f"❌ No se pudo inicializar cliente de API: {e}")
    st.stop()

# Mostrar historial previo (omitimos mensajes system)
for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# Campo de input
if prompt := st.chat_input("🌶️ Hazme una pregunta sobre Elpicantito..."):
    # Verificar conexión con Spring Boot y renovar token si es necesario
    try:
        response = requests.get(f"{SPRINGBOOT_API_BASE}/actuator/health", timeout=2)
        if response.status_code == 200:
            data = response.json()
            # Solo renovar token si Spring Boot está completamente UP
            if data.get('status') == 'UP':
                # Verificar si necesitamos renovar el token
                token_jwt = obtener_token_jwt()
                if token_jwt:
                    st.session_state.messages[0] = {"role": "system", "content": construir_contexto_sistema(token_jwt)}
            else:
                st.warning(f"⚠️ Spring Boot aún está iniciando (status: {data.get('status')}). Por favor, espera un momento.")
                st.stop()
        else:
            st.warning(f"⚠️ Spring Boot responde con estado {response.status_code}. Esperando...")
            st.stop()
    except:
        st.warning("⚠️ No se puede conectar a Spring Boot. Intentando obtener token de todas formas...")
        token_jwt = obtener_token_jwt()
        if token_jwt:
            st.session_state.messages[0] = {"role": "system", "content": construir_contexto_sistema(token_jwt)}
        else:
            st.error("❌ No se pudo establecer conexión con Spring Boot. Por favor, espera a que el servicio esté listo.")
            st.stop()
    
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Llamada a la API en streaming con manejo de errores
    try:
        stream = client.chat.completions.create(
            model="openrouter/sherlock-think-alpha",
            messages=st.session_state.messages,
            stream=True,
        )
    except Exception as e:
        st.error(f"❌ Error al llamar a la API: {e}")
        st.stop()

    # Mostrar la respuesta en streaming (st.write_stream se usa en tu código original)
    try:
        with st.chat_message("assistant"):
            response = st.write_stream(stream)
    except Exception as e:
        # Si el helper de stream falla, intentar leer el stream parcial y mostrar error
        st.error(f"❌ Error procesando el stream: {e}")
        response = "Lo siento, hubo un problema al procesar tu solicitud. Por favor, inténtalo de nuevo."

    # Guardar la respuesta en el historial para futuras interacciones
    st.session_state.messages.append({"role": "assistant", "content": response})

# Footer decorativo
st.markdown(
    """
    <div class="footer">
        <p>¡El sabor de México en cada respuesta! 🌮 | Hecho con ❤️ para El Picantito</p>
    </div>
    """,
    unsafe_allow_html=True
)