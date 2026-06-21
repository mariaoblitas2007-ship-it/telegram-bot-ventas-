import os
import sys
import asyncio
import random
import logging
import unicodedata
import signal
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, MessageHandler, CallbackQueryHandler, CommandHandler, filters, ContextTypes
from telegram.error import Conflict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = '8751695788:AAFg5vFlt2EYvR5zOZ_tn29T0KZLYvTZs74'
ADMIN_ID = 8783569348
USERNAME_ADMIN = "@yanabicitasa"

LINK_CANAL = "https://t.me/+ZWc0FAcw-hQ2MDZh"
LINK_PAYPAL = "https://www.paypal.com/qrcodes/p2pqrc/76RWY9FF7Q7RE"

DEMO_HOT = {}
VIP_TEMPORAL = {}
DEMO_USADO = set()
USUARIOS = {}
PAGARON = set()
ULTIMO_MENSAJE = {}
VIO_PRECIOS = {}
FOLLOWUP_ENVIADO = set()
ULTIMAS_3_RESPUESTAS = {}

# FOTOS PARA EL BOTÓN GRATIS - SUBE ESTAS 6 A TU REPO
FOTOS_GRATIS = [
    "fotitos1.JPG", "fotitos2.JPG", "fotitos3.JPG",
    "fotitos4.JPG", "fotitos5.JPG", "fotitos6.JPG"
]

# === PRECIOS PERÚ ===
PE_PRECIOS = """
🛍 *PACKS DISPONIBLES - PERÚ* 🇵🇪

🎂 *BÁSICO: S/ 15*
→ 5 unidades | S/ 3 c/u

🔥 *TOP: S/ 30* ← MÁS VENDIDO
→ 12 unidades | S/ 2.50 c/u
→ *Ahorras 50%*

🏆 *PREMIUM: S/ 60*
→ 20 unidades + 1 personalizado
→ incluye chat 🥰
→ *Ahorras 67%*

📼 *LLAMADITAS* 📼
S/ 60: 10 min
S/ 80: 20 min

💳 *PAGO:* *YAPE/PLIN:* 923553612
*CUENTO CON REFERENCIAS*

1. Yapeas 2. Captura
"""

# === PRECIOS MÉXICO ===
MX_PRECIOS = """
🛍 *PACKS DISPONIBLES - MÉXICO* 🇲🇽

🎂 *BÁSICO: $100 MXN*
→ 5 unidades | $20 c/u

🔥 *TOP: $200 MXN* ← MÁS VENDIDO
→ 12 unidades | $16 c/u
→ *Ahorras 50%*

🏆 *PREMIUM: $400 MXN*
→ 20 unidades + 1 personalizado
→ incluye chat 🥰
→ *Ahorras 80%*

📼 *LLAMADITAS* 📼
$400 MXN: 10 min
$600 MXN: 20 min

🛍 *PAGO MXN:*
🏦 *Banco:* STP
🔢 *CLABE:* `646180546711450910`
📝 *Referencia:* `yanae`

🇲🇽 También acepto: Transfer / Astropay
→ Pídeme datos si usas otro método

Mándame captura cuando pagues 😊
"""

# === PRECIOS USA/USD ===
USA_PRECIOS = """
🛍 *PACKS DISPONIBLES - USA* 🇺🇸

🎂 *BÁSICO: $5 USD*
→ 5 unidades | $1 c/u

🔥 *TOP: $9 USD* ← MÁS VENDIDO
→ 12 unidades | $0.75 c/u
→ *Ahorras 50%*

🏆 *PREMIUM: $20 USD*
→ 20 unidades + 1 personalizado
→ incluye chat 🥰
→ *Ahorras 60%*

📼 *LLAMADITAS* 📼
$20 USD: 10 min
$30 USD: 20 min

🪙 *PAGO:*
*PayPal:* AbigailMaximoofO

🏦 *Bank EEUU:*
Community Federal Savings Bank
📍 *Address:* 5 Penn Plaza, 14th Floor New York, NY 10001
0️⃣ *Account:* 8338233469
0️⃣ *Routing:* 026073150
✍️ *Type:* Checking

Avísame cuando envíes con el comprobante 😊
"""

# === PRECIOS INTERNACIONAL ===
OTRO_PRECIOS = f"""
🛍 *PACKS DISPONIBLES - INTERNACIONAL* 🌎

🎂 *BÁSICO: $5 USD* → 5 unidades | $1 c/u
🔥 *TOP: $9 USD* ← MÁS VENDIDO → 12 unidades | $0.75 c/u
🏆 *PREMIUM: $20 USD* → 20 unidades + 1 personalizado + chat 🥰

📼 *LLAMADITAS* 📼
$20 USD: 10 min | $30 USD: 20 min

🪙 *PAGO:*
*PayPal:* [Click aquí]({LINK_PAYPAL})
/ USDT disponible

Avísame cuando envíes con el comprobante 😊
"""

# === TEXTO BOTÓN GRATIS ===
TEXTO_GRATIS = """
🎁 *BONUS GRATIS* 😊

✨ *¿QUIERES UNA RECOMPENSA GRATIS?* ✨
Ayúdame promocionando en TikTok ✅

*Pasitos súper fáciles:*
1️⃣ Ponte un nombre + foto de perfil linda
2️⃣ En tu bio pon: `Tg: yanabicitasa` ✨
3️⃣ Sube una foto a tu story mencionándome
4️⃣ Comenta en videos relacionados, unos 30-100 👀
   Así generamos alcance juntos
5️⃣ Mándame captura cuando termines
6️⃣ Disfruta de tu bonus gratis 🎁

¿Te animas? 😊
(Me avisas cuando cumplas)
"""

def get_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🛍 Precios Perú 🇵🇪", callback_data='pe')],
        [InlineKeyboardButton("🛍 Precios México 🇲🇽", callback_data='mx')],
        [InlineKeyboardButton("🛍 Precios USA 🇺🇸", callback_data='usa')],
        [InlineKeyboardButton("🌎 Otro País", callback_data='otro')],
        [InlineKeyboardButton("🎁 Gratis", callback_data='gratis')],
        [InlineKeyboardButton("🔥 Canal Oficial", url=LINK_CANAL)]
    ])

def get_volver():
    return InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Volver al Menú", callback_data='volver')]])

def normalizar(texto):
    texto = unicodedata.normalize('NFKD', texto).encode('ascii', 'ignore').decode('ascii')
    return texto.lower()

def registrar_usuario(user):
    USUARIOS[user.id] = {
        'nombre': user.first_name,
        'username': user.username or "sin_username",
        'ultimo_mensaje': datetime.now().strftime('%d/%m %H:%M'),
        'demo_usada': user.id in DEMO_USADO,
        'es_vip': user.id in VIP_TEMPORAL and VIP_TEMPORAL[user.id] > datetime.now(),
        'pago': user.id in PAGARON
    }

async def avisar_interes(context, user_id, username, mensaje, tipo="INTERÉS"):
    try:
        username_safe = str(username).replace("_", "\\_").replace("*", "\\*").replace("[", "\\[").replace("`", "\\`")
        mensaje_safe = str(mensaje)[:100].replace("_", "\\_").replace("*", "\\*").replace("[", "\\[").replace("`", "\\`")
        texto = f"🔥 *{tipo} DE COMPRA* 🔥\n\n👤 @{username_safe}\n🆔 `{user_id}`\n💬 Mensaje: `{mensaje_safe}`\n⏰ {datetime.now().strftime('%H:%M:%S')}\n\nHáblale rápido 🤑"
        await context.bot.send_message(chat_id=ADMIN_ID, text=texto, parse_mode='Markdown')
    except:
        pass

async def follow_up_task(app, user_id, username):
    await asyncio.sleep(1800) # 30 min
    if user_id in PAGARON or user_id in FOLLOWUP_ENVIADO:
        return
    FOLLOWUP_ENVIADO.add(user_id)
    mensajes = [
        f"Oye {username} 😊 ¿sigues ahí? Si compras TOP te doy 2 unidades extra 🎁",
        f"Psst 👉👈 con PREMIUM te agrego un bonus exclusivo que no está en el menú ✨",
        f"Hola 🥺 te espero... con TOP te mando algo especial de regalo 🎁"
    ]
    try:
        await app.bot.send_message(chat_id=user_id, text=random.choice(mensajes), reply_markup=get_menu(), parse_mode='Markdown')
    except:
        pass

def respuesta_bot(texto_original, nombre, user_id):
    texto = normalizar(texto_original)

    def no_repetir(opciones):
        historial = ULTIMAS_3_RESPUESTAS.get(user_id, [])
        opciones_filtradas = [r for r in opciones if r not in historial]
        if not opciones_filtradas:
            opciones_filtradas = opciones
            historial = []
        respuesta = random.choice(opciones_filtradas)
        historial.append(respuesta)
        ULTIMAS_3_RESPUESTAS[user_id] = historial[-3:]
        return respuesta

    if any(x in texto for x in ['hola', 'ola', 'buenas', 'hey', 'wenas', 'info']):
        return no_repetir([
            f"¡Hola {nombre}! 😊 ¿Cómo estás? Bienvenido/a",
            f"Hey {nombre} 👋 ¿En qué te ayudo hoy?",
            f"Holaa {nombre} ✨ ¿Qué necesitas saber?",
            f"¡Buenas {nombre}! 😄 Dime, ¿qué buscas?",
            f"Ola {nombre} 🙌 Estoy aquí para ayudarte"
        ])

    if any(x in texto for x in ['que haces', 'q haces', 'haciendo']):
        return no_repetir([
            f"Acá {nombre} 😊 atendiendo pedidos. ¿Y tú?",
            f"Ayudando clientes 🙌 tú qué cuentas?",
            f"Acá activa 😄 esperando ayudarte. ¿Qué necesitas?",
            f"Trabajando {nombre} ✨ ¿En qué te ayudo?"
        ])

    if any(x in texto for x in ['muestra', 'muestrame', 'ver', 'foto', 'info', 'detalles', 'ensena']):
        return no_repetir([
            f"Claro {nombre} 😊 dime qué producto quieres ver y te paso detalles",
            f"Perfecto 👌 ¿Qué opción del menú te interesa más?",
            f"Dime exacto {nombre} ✨ ¿qué pack quieres conocer?",
            f"Sí {nombre} 😄 ¿Sobre qué pack necesitas info?",
            f"Ya {nombre} 🙌 dime cuál te llama la atención"
        ])

    if any(x in texto for x in ['precio', 'cuanto', 'vale', 'costo', 'cuesta']):
        return no_repetir([
            f"Te paso los precios {nombre} 😊👇",
            f"Aquí tienes la lista {nombre} 👇",
            f"Perfecto, estos son los packs disponibles {nombre} 👇"
        ])

    if any(x in texto for x in ['gracias', 'ok', 'vale', 'bueno', 'dale', 'listo']):
        return no_repetir([
            f"De nada {nombre} 😊 Cualquier cosa me avisas",
            f"Para servirte {nombre} ✨",
            f"Ok {nombre} 😄 acá estoy si necesitas algo más",
            f"Vale {nombre} 🙌 que tengas buen día"
        ])

    if any(x in texto for x in ['jaja', 'xd', 'jiji', 'jsjs', 'lol']):
        return no_repetir([
            f"Jaja 😄 me alegra {nombre}. ¿Vemos los packs?",
            f"Jiji 😊 ¿Te ayudo con algo más?",
            f"Jsjs {nombre} 😄 dime, ¿qué necesitas?"
        ])

    if any(x in texto for x in ['adios', 'chao', 'chau', 'bye', 'nos vemos']):
        return no_repetir([
            f"¡Chau {nombre}! 😊 Vuelve cuando quieras",
            f"Nos vemos {nombre} 👋 que estés bien",
            f"Adiós {nombre} ✨ aquí estaré si me necesitas",
            f"Bye {nombre} 😄 cuídate"
        ])

    return no_repetir([
        f"Dime {nombre} 😊 ¿En qué te ayudo hoy?",
        f"Estoy aquí {nombre} ✨ ¿Qué necesitas saber?",
        f"Cuéntame {nombre} 👇 ¿Qué estás buscando?",
        f"{nombre} 😄 pregúntame lo que quieras",
        f"Hola {nombre} 🙌 ¿Vemos los packs disponibles?",
        f"Soy tu asesora {nombre} 😊 ¿Qué te interesa?"
    ])

async def manejar_todo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message or update.business_message
    if not message or not message.from_user or message.from_user.is_bot:
        return
    user = message.from_user
    user_id = user.id
    if user_id == ADMIN_ID:
        return
    username = user.username or "sin_username"
    registrar_usuario(user)
    ahora = datetime.now()
    nombre = user.first_name

    if user_id in PAGARON:
        await message.reply_text(f"¡Pago confirmado {nombre}! 😊\n\n✅ *LISTO*\n\n📩 *Escríbeme al privado*\n👉 {USERNAME_ADMIN}\n\nAhí coordinamos tu pedido", parse_mode='Markdown')
        return

    if message.text and message.text.lower() == '/start':
        es_nuevo = user_id not in DEMO_USADO
        if es_nuevo:
            DEMO_USADO.add(user_id)
            DEMO_HOT[user_id] = datetime.now() + timedelta(minutes=10)
            saludo = f"¡Hola {nombre}! 😊 Bienvenido/a\n\n*Soy tu asesora online*\n\n*Tienes 10 min de atención prioritaria gratis* ✨\nAprovecha para consultar lo que quieras"
            await message.reply_text(saludo, parse_mode='Markdown')
        else:
            await message.reply_text(f"¡Hola de nuevo {nombre}! 😊\n\nYa usaste tu demo, pero puedes ver los packs disponibles 👇", parse_mode='Markdown')
        await message.reply_text("Elige tu país para ver precios:", reply_markup=get_menu(), parse_mode='Markdown')
        return

    if message.photo:
        PAGARON.add(user_id)
        await avisar_interes(context, user_id, username, "ENVÍO CAPTURA DE PAGO", "PAGO RECIBIDO 💰")
        await message.reply_text(
            f"✅ *PAGO RECIBIDO* 😊\n\n"
            f"Gracias {nombre}\n\n"
            f"📩 *AHORA ESCRÍBEME AL PRIVADO*\n"
            f"👉 {USERNAME_ADMIN}\n\n"
            f"Ahí coordinamos tu pedido sin demora\n\n"
            f"*No lo gestiono por aquí por seguridad*",
            parse_mode='Markdown'
        )
        try:
            caption = f"💰 *NUEVA CAPTURA - PAGO CONFIRMADO*\n\n👤 @{username}\n🆔 `{user_id}`\n⏰ {ahora.strftime('%H:%M:%S')}\n\n*Cliente enviado a tu privado* ✅"
            await context.bot.send_photo(chat_id=ADMIN_ID, photo=message.photo[-1].file_id, caption=caption, parse_mode='Markdown')
        except Exception as e:
            logger.error(f"Error reenviando: {e}")
        return

    if not message.text:
        return

    texto = message.text.strip()

    if ULTIMO_MENSAJE.get(user_id) == texto.lower():
        return
    ULTIMO_MENSAJE[user_id] = texto.lower()

    if any(x in normalizar(texto) for x in ['comprar', 'compro', 'quiero', 'pago', 'pagare']):
        await avisar_interes(context, user_id, username, texto, "QUIERE COMPRAR YA 🤑")
        await message.reply_text(f"Perfecto {nombre} 😊 Elige tu opción:", reply_markup=get_menu(), parse_mode='Markdown')
        return

    if any(x in normalizar(texto) for x in ['precio', 'cuanto', 'vale', 'costo', 'cuesta', 'peru', 'soles']):
        await avisar_interes(context, user_id, username, texto, "PREGUNTÓ PRECIO")
        VIO_PRECIOS[user_id] = datetime.now()
        asyncio.create_task(follow_up_task(context.application, user_id, username))
        await message.reply_text(PE_PRECIOS, reply_markup=get_volver(), parse_mode='Markdown')
        return
    elif any(x in normalizar(texto) for x in ['mexico', 'mxn', 'peso']):
        await avisar_interes(context, user_id, username, texto, "PREGUNTÓ PRECIO")
        VIO_PRECIOS[user_id] = datetime.now()
        asyncio.create_task(follow_up_task(context.application, user_id, username))
        await message.reply_text(MX_PRECIOS, reply_markup=get_volver(), parse_mode='Markdown')
        return
    elif any(x in normalizar(texto) for x in ['usd', 'usa', 'eeuu', 'dolar', 'estados unidos']):
        await avisar_interes(context, user_id, username, texto, "PREGUNTÓ PRECIO")
        VIO_PRECIOS[user_id] = datetime.now()
        asyncio.create_task(follow_up_task(context.application, user_id, username))
        await message.reply_text(USA_PRECIOS, reply_markup=get_volver(), parse_mode='Markdown')
        return
    elif any(x in normalizar(texto) for x in ['otro', 'internacional', 'colombia', 'argentina', 'chile', 'mundial']):
        await avisar_interes(context, user_id, username, texto, "PREGUNTÓ PRECIO")
        VIO_PRECIOS[user_id] = datetime.now()
        asyncio.create_task(follow_up_task(context.application, user_id, username))
        await message.reply_text(OTRO_PRECIOS, reply_markup=get_volver(), parse_mode='Markdown', disable_web_page_preview=True)
        return

    es_vip = user_id in VIP_TEMPORAL and VIP_TEMPORAL[user_id] > ahora
    es_demo = user_id in DEMO_HOT and DEMO_HOT[user_id] > ahora

    if es_demo or es_vip:
        tiempo_restante = (VIP_TEMPORAL[user_id] - ahora).seconds // 60 if es_vip else (DEMO_HOT[user_id] - ahora).seconds // 60
        if not es_vip and tiempo_restante <= 2:
            await message.reply_text(f"{nombre} se nos acaba el tiempo 😢\n\n*Mira el PREMIUM ahora* y seguimos sin corte ✨", reply_markup=get_menu(), parse_mode='Markdown')
            return
        if es_vip and tiempo_restante <= 5:
            await message.reply_text(f"{nombre}, {tiempo_restante} min y me tengo que ir 😢\n\n¿Qué necesitas antes de irme? ✨", parse_mode='Markdown')
            return

    respuesta = respuesta_bot(texto, nombre, user_id)
    await message.reply_text(respuesta, parse_mode='Markdown')

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    user_id = query.from_user.id
    username = query.from_user.username or "sin_username"

    if data in ['pe', 'mx', 'usa', 'otro']:
        await avisar_interes(context, user_id, username, f"Tocó botón: {data.upper()}", "VIO PRECIOS 👀")
        VIO_PRECIOS[user_id] = datetime.now()
        asyncio.create_task(follow_up_task(context.application, user_id, username))

    if data == 'pe':
        await query.edit_message_text(PE_PRECIOS, reply_markup=get_volver(), parse_mode='Markdown')
    elif data == 'mx':
        await query.edit_message_text(MX_PRECIOS, reply_markup=get_volver(), parse_mode='Markdown')
    elif data == 'usa':
        await query.edit_message_text(USA_PRECIOS, reply_markup=get_volver(), parse_mode='Markdown')
    elif data == 'otro':
        await query.edit_message_text(OTRO_PRECIOS, reply_markup=get_volver(), parse_mode='Markdown', disable_web_page_preview=True)
    elif data == 'gratis':
        await query.edit_message_text(TEXTO_GRATIS, parse_mode='Markdown')
        # ENVÍA LAS 6 FOTOS
        for foto in FOTOS_GRATIS:
            try:
                with open(foto, 'rb') as f:
                    await context.bot.send_photo(chat_id=user_id, photo=f)
                await asyncio.sleep(0.5)
            except Exception as e:
                logger.error(f"No se pudo enviar {foto}: {e}")
        await context.bot.send_message(chat_id=user_id, text="¡Listo! 😊 Sigue los pasos y me avisas", reply_markup=get_volver())

    elif data == 'volver':
        await query.edit_message_text("Elige tu país para ver precios:", reply_markup=get_menu(), parse_mode='Markdown')

async def vip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id!= ADMIN_ID:
        return
    if not context.args:
        await update.message.reply_text("Uso: /vip ID_DEL_CLIENTE")
        return
    user_id = int(context.args[0])
    VIP_TEMPORAL[user_id] = datetime.now() + timedelta(minutes=15)
    PAGARON.add(user_id)
    DEMO_HOT.pop(user_id, None)
    await context.bot.send_message(user_id, "✅ *CHAT VIP ACTIVADO* 😊\n\nTienes *15 minutos* de atención prioritaria\n\nPregúntame lo que quieras ✨")
    await update.message.reply_text(f"✅ VIP activado para {user_id}")

async def usuarios(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id!= ADMIN_ID:
        return
    if not USUARIOS:
        await update.message.reply_text("No hay usuarios aún")
        return
    texto = "📊 *USUARIOS REGISTRADOS* 📊\n\n"
    for uid, data in USUARIOS.items():
        estado = "💰 PAGÓ" if data['pago'] else "🔥 VIP" if data['es_vip'] else "💦 DEMO" if data['demo_usada'] else "👀 NUEVO"
        texto += f"👤 {data['nombre']} @{data['username']}\n🆔 `{uid}` | {estado}\n⏰ {data['ultimo_mensaje']}\n\n"
    texto += f"*Total: {len(USUARIOS)} usuarios*"
    await update.message.reply_text(texto, parse_mode='Markdown')

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    if isinstance(context.error, Conflict):
        logger.error("⚠️ Conflicto: Otro bot está corriendo. Detenlo en Render/otros sitios")
    else:
        logger.error(f"Error: {context.error}", exc_info=context.error)

def shutdown_handler(signum, frame):
    logger.info("Apagando bot...")
    sys.exit(0)

signal.signal(signal.SIGINT, shutdown_handler)
signal.signal(signal.SIGTERM, shutdown_handler)

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler('vip', vip))
    app.add_handler(CommandHandler('usuarios', usuarios))
    app.add_handler(CallbackQueryHandler(button))
    app.add_handler(MessageHandler(filters.ALL, manejar_todo))
    app.add_error_handler(error_handler)
    logger.info("BOT PRENDIDO - MODO 24/7 ACTIVO ✅")
    app.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    main()
