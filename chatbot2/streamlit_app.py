import os
import streamlit as st
from openai import OpenAI
import requests
import json

# Configuración de página para permitir iframe embedding
st.set_page_config(
    page_title="Chatbot Usuario - El Picantito",
    page_icon="🌮",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# === CONFIGURACIÓN DE LA API DE SPRING BOOT ===
SPRINGBOOT_API_BASE = os.environ.get("SPRINGBOOT_API_BASE", "http://localhost:9998")

# === FUNCIONES PARA OBTENER DATOS DE SPRING BOOT (SOLO DATOS PÚBLICOS) ===
@st.cache_data(ttl=300)
def obtener_adicionales():
    """Obtiene todos los adicionales disponibles"""
    try:
        response = requests.get(f"{SPRINGBOOT_API_BASE}/api/adicional", timeout=5)
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        return None

@st.cache_data(ttl=300)
def obtener_productos():
    """Obtiene todos los productos"""
    try:
        response = requests.get(f"{SPRINGBOOT_API_BASE}/api/productos", timeout=5)
        if response.status_code == 200:
            return response.json()
        return None
    except Exception as e:
        return None

def construir_contexto_usuario():
    """Construye un contexto orientado a usuarios finales"""
    contexto_base = """Eres un asistente útil para clientes de 'El Picantito', un restaurante mexicano. 
Ayuda a los usuarios a conocer nuestro menú, precios, y navegar por la página web.
Usa un tono cálido, amigable y entusiasta, con toques de humor mexicano cuando sea apropiado.

REGLAS IMPORTANTES:
- NO menciones nada de precios solo menciona funcionalidades y nombres del producto

NAVEGACIÓN DE LA PÁGINA:
- Botón "Crear Taco" está en la parte inferior de la lista de productos
- Perfil y órdenes están en el icono de persona en la esquina superior derecha
- Carrito de compras está en la parte superior de la pantalla
- Para agregar productos al carrito, usa el botón "Agregar al carrito" en cada producto
- Para personalizar tu taco, selecciona los adicionales que desees

NO tienes acceso a estadísticas, información de usuarios, ni funciones administrativas.
Si te preguntan sobre eso, sugiere amablemente que contacten con el personal del restaurante."""
    
    # Obtener productos y adicionales
    adicionales = obtener_adicionales()
    productos = obtener_productos()
    
    contexto_adicional = []
    
    # Agregar información de productos
    if productos:
        contexto_adicional.append(f"\n\n=== NUESTRO MENÚ ===")
        contexto_adicional.append(f"- Total de productos: {len(productos)}")
        productos_disponibles = [p for p in productos if p.get('disponible', False)]
        contexto_adicional.append(f"- Productos disponibles: {len(productos_disponibles)}")
        
        if productos_disponibles:
            contexto_adicional.append("\nProductos destacados:")
            for producto in productos_disponibles[:10]:  # Mostrar hasta 10 productos
                nombre = producto.get('nombre', 'Sin nombre')
                precio = producto.get('precio', 0)
                descripcion = producto.get('descripcion', 'Sin descripción')
                contexto_adicional.append(f"  • {nombre} - ${precio:.2f}")
                if descripcion and descripcion != 'Sin descripción':
                    contexto_adicional.append(f"    {descripcion}")
    
    # Agregar información de adicionales
    if adicionales:
        contexto_adicional.append(f"\n\n=== PERSONALIZA TU ORDEN ===")
        adicionales_disponibles = [a for a in adicionales if a.get('disponible', False)]
        contexto_adicional.append(f"- Adicionales disponibles: {len(adicionales_disponibles)}")
        
        if adicionales_disponibles:
            # Agrupar adicionales por tipo si tienen esa información
            tipos = {}
            for adicional in adicionales_disponibles:
                nombre = adicional.get('nombre', 'Sin nombre')
                precio = adicional.get('precio', 0)
                tipo = adicional.get('tipo', 'Otros')  # Asumiendo que existe un campo tipo
                
                if tipo not in tipos:
                    tipos[tipo] = []
                tipos[tipo].append(f"  • {nombre} - ${precio:.2f}")
            
            for tipo, items in tipos.items():
                contexto_adicional.append(f"\n{tipo}:")
                contexto_adicional.extend(items)
    
    if contexto_adicional:
        contexto_base += "\n" + "\n".join(contexto_adicional)
        contexto_base += "\n\nUsa esta información para ayudar a los clientes a elegir sus productos favoritos."
    
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
st.markdown('<h1 class="main-title">💬 Asistente Virtual</h1>', unsafe_allow_html=True)

# Tarjeta de bienvenida
st.markdown(
    """
    <div class="welcome-card">
        <h3 style="margin:0;color:#ff9e00;">¡Bienvenido a El Picantito! 🎉</h3>
        <p style="margin:10px 0 0 0;">Estoy aquí para ayudarte con nuestro menú, precios y navegar por la página.<br>
        ¡Pregúntame sobre nuestros deliciosos platillos mexicanos!</p>
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
            data = response.json()
            if data.get('status') == 'UP':
                return True, "✅ Sistema listo"
            else:
                return False, f"⚠️ Sistema iniciando... (status: {data.get('status')})"
        else:
            return False, f"⚠️ Sistema responde con estado: {response.status_code}"
    except requests.exceptions.Timeout:
        return False, "⏳ Esperando respuesta del sistema..."
    except requests.exceptions.ConnectionError:
        return False, "❌ No se puede conectar al sistema"
    except Exception as e:
        return False, f"❌ Error: {str(e)}"

is_connected, connection_msg = verificar_spring_boot()
if is_connected:
    st.success(connection_msg)
else:
    st.info(f"{connection_msg}. El asistente funcionará con información limitada hasta que el sistema esté listo.")

# Configuración de API (usar USUARIO_API en lugar de ADMIN_API)
usuario_api_key = None
try:
    usuario_api_key = st.secrets.get("USUARIO_API")
except Exception:
    usuario_api_key = None

if not usuario_api_key:
    usuario_api_key = os.environ.get("USUARIO_API")

if not usuario_api_key or usuario_api_key.strip() == "":
    st.error(
        "🔑 API key faltante. Configure USUARIO_API en .streamlit/secrets.toml para desarrollo o pase la variable USUARIO_API al contenedor."
    )
    st.stop()

openrouter_base_url = "https://openrouter.ai/api/v1"

# Inicializar historial solo una vez
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": construir_contexto_usuario()}
    ]

# Crear cliente de OpenRouter
try:
    client = OpenAI(api_key=usuario_api_key, base_url=openrouter_base_url)
except Exception as e:
    st.error(f"❌ No se pudo inicializar cliente de API: {e}")
    st.stop()

# Mostrar historial previo (omitimos mensajes system)
for message in st.session_state.messages:
    if message["role"] != "system":
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

# Campo de input
if prompt := st.chat_input("🌶️ ¿Qué te gustaría saber sobre nuestro menú?"):
    # Actualizar contexto con datos frescos
    st.session_state.messages[0] = {"role": "system", "content": construir_contexto_usuario()}
    
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

    # Mostrar la respuesta en streaming
    try:
        with st.chat_message("assistant"):
            response = st.write_stream(stream)
    except Exception as e:
        st.error(f"❌ Error procesando el stream: {e}")
        response = "Lo siento, hubo un problema al procesar tu solicitud. Por favor, inténtalo de nuevo."

    # Guardar la respuesta en el historial
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
