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

TOKEN = '8751695788:AAENlUN4KTzaBmVNdbDf3AAr0kmro3pM6VI'
ADMIN_ID = 8783569348
USERNAME_ADMIN = "@yanabicitasa"

LINK_CANAL = "https://t.me/+ZWc0FAcw-hQ2MDZh"
LINK_PAYPAL = "https://www.paypal.com/qrcodes/p2pqrc/76RWY9FF7Q7RE"

VIP_TEMPORAL = {}
DEMO_USADO = set()
USUARIOS = {}
PAGARON = set() # MODIFICACIÓN 3: Si está aquí, el bot no responde
ULTIMO_MENSAJE = {}
VIO_PRECIOS = {}
FOLLOWUP_ENVIADO = set()

FOTOS_GRATIS = [
    "fotitos1.JPG", "fotitos2.JPG", "fotitos3.JPG",
    "fotitos4.JPG", "fotitos5.JPG", "fotitos6.JPG"
]

PE_PRECIOS = """
🛍 *PACKS DISPONIBLES - PERÚ* 🇵🇪😏

💦 *PRUEBA: S/ 5*
→ 3 fotitos | S/ 1.66 c/u
→ Para que me conozcas 🙈

🎂 *BÁSICO: S/ 10*
→ 6 unidades | S/ 1.66 c/u
→ *+1 foto extra HOY*

🔥 *TOP: S/ 20* ← MÁS VENDIDO
→ 12 unidades | S/ 1.66 c/u
→ *Ahorras 50%*
→ *REGALO: 2 fotos extra*

🏆 *PREMIUM: S/ 35*
→ 20 unidades + 1 personalizado
→ incluye chat privado 24h 🥰
→ *Ahorras 50%*

👑 *VIP: S/ 50* ← MÁXIMO 28 UNIDADES
→ 28 unidades + 2 personalizados
→ Chat 3 días + videollamada 5min
→ *TODO INCLUIDO* 😈

📼 *LLAMADITAS* 📼
S/ 30: 10 min 😈
S/ 50: 20 min + 3 fotos

⚡ *COMBO FLASH: S/ 45*
→ Pack PREMIUM + Llamada 10min
→ *Ahorras S/ 20*

💳 *PAGO:* *YAPE/PLIN:* 923553612
*100% REAL - PIDEME REFERENCIAS*

1. Yapeas 2. Captura 3. Disfrutas 😏
"""

MX_PRECIOS = """
🛍 *PACKS DISPONIBLES - MÉXICO* 🇲🇽😏

💦 *PRUEBA: $60 MXN*
→ 3 fotitos | $20 c/u
→ Para que me conozcas 🙈
→ *Precio final con comisión*

🎂 *BÁSICO: $90 MXN*
→ 6 unidades | $15 c/u
→ *+1 foto extra HOY*
→ *Precio final con comisión*

🔥 *TOP: $145 MXN* ← MÁS VENDIDO
→ 12 unidades | $12 c/u
→ *Ahorras 50%*
→ *REGALO: 2 fotos extra*
→ *Precio final con comisión*

🏆 *PREMIUM: $230 MXN*
→ 20 unidades + 1 personalizado
→ incluye chat privado 24h 🥰
→ *Ahorras 50%*
→ *Precio final con comisión*

👑 *VIP: $320 MXN* ← MÁXIMO 28 UNIDADES
→ 28 unidades + 2 personalizados
→ Chat 3 días + videollamada 5min
→ *TODO INCLUIDO* 😈
→ *Precio final con comisión*

📼 *LLAMADITAS* 📼
$205 MXN: 10 min 😈
$320 MXN: 20 min + 3 fotos

🛍 *PAGO MXN:*
🏦 *Banco:* STP
🔢 *CLABE:* `646180546711450910`
📝 *Referencia:* `yanae`

🇲🇽 También: Transfer / Astropay
⚠️ *Precio final - incluye comisión bancaria*

Mándame captura cuando pagues 😊
"""

USA_PRECIOS = """
🛍 *PACKS DISPONIBLES - USA* 🇺🇸😏

💦 *PRUEBA: $2 USD*
→ 3 fotitos | $0.66 c/u
→ Para que me pruebes 🙈

🎂 *BÁSICO: $3.50 USD*
→ 6 unidades | $0.58 c/u
→ *+1 foto extra HOY*

🔥 *TOP: $7 USD* ← MÁS VENDIDO
→ 12 unidades | $0.58 c/u
→ *Ahorras 50%*
→ *REGALO: 2 fotos extra*

🏆 *PREMIUM: $12 USD*
→ 20 unidades + 1 personalizado
→ incluye chat privado 24h 🥰
→ *Ahorras 50%*

👑 *VIP: $20 USD* ← MÁXIMO 28 UNIDADES
→ 28 unidades + 2 personalizados
→ Chat 3 días + videollamada 5min
→ *MEJOR VALOR* 😈

📼 *LLAMADITAS* 📼
$10 USD: 10 min 😈
$20 USD: 20 min + 3 fotos

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

OTRO_PRECIOS = f"""
🛍 *PACKS DISPONIBLES - INTERNACIONAL* 🌎😏

💦 *PRUEBA: $2 USD*
→ 3 fotitos | $0.66 c/u
→ Para que me conozcas 🙈

🎂 *BÁSICO: $3.50 USD*
→ 6 unidades | $0.58 c/u
→ *+1 foto extra HOY*

🔥 *TOP: $7 USD* ← MÁS VENDIDO
→ 12 unidades | $0.58 c/u
→ *Ahorras 50%*
→ *REGALO: 2 fotos extra*

🏆 *PREMIUM: $12 USD*
→ 20 unidades + 1 personalizado
→ incluye chat privado 24h 🥰
→ *Ahorras 50%*

👑 *VIP: $20 USD* ← MÁXIMO 28 UNIDADES
→ 28 unidades + 2 personalizados
→ Chat 3 días + videollamada 5min
→ *MEJOR VALOR* 😈

📼 *LLAMADITAS* 📼
$10 USD: 10 min 😈
$20 USD: 20 min + 3 fotos

🪙 *PAGO:*
*PayPal:* [Click aquí]({LINK_PAYPAL})
/ USDT disponible

Avísame cuando envíes con el comprobante 😊
"""

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

async def avisar_pago(context, user_id, username, nombre, foto_id):
    try:
        username_display = f"@{username}" if username!= "sin_username" else f"{nombre}"
        link_chat = f"tg://user?id={user_id}"

        caption = f"💰 *PAGO RECIBIDO* 💰\n\n" \
                  f"👤 {username_display}\n" \
                  f"🆔 `{user_id}`\n" \
                  f"⏰ {datetime.now().strftime('%H:%M:%S')}\n\n" \
                  f"👉 [Escribirle al cliente]({link_chat})\n\n" \
                  f"*Cliente enviado a tu privado* ✅\n\n" \
                  f"Usa `/activar {user_id}` para reactivar el bot en ese chat"

        await context.bot.send_photo(chat_id=ADMIN_ID, photo=foto_id, caption=caption, parse_mode='Markdown')
    except Exception as e:
        logger.error(f"Error enviando pago: {e}")

async def follow_up_task(app, user_id, username):
    await asyncio.sleep(1800)
    if user_id in PAGARON or user_id in FOLLOWUP_ENVIADO:
        return
    FOLLOWUP_ENVIADO.add(user_id)
    mensajes = [
        f"Oye {username} 😏 ¿sigues ahí? Si compras TOP te doy 2 unidades extra 🎁",
        f"Psst 👉👈 con PREMIUM te agrego un bonus que te va a encantar ✨",
        f"Hola 🥺 te espero... con TOP te mando algo especial 🙈"
    ]
    try:
        await app.bot.send_message(chat_id=user_id, text=random.choice(mensajes), reply_markup=get_menu(), parse_mode='Markdown')
    except:
        pass

async def enviar_gratis(chat_id, context):
    await context.bot.send_message(chat_id=chat_id, text=TEXTO_GRATIS, parse_mode='Markdown')
    for foto in FOTOS_GRATIS:
        try:
            with open(foto, 'rb') as f:
                await context.bot.send_photo(chat_id=chat_id, photo=f)
            await asyncio.sleep(0.5)
        except Exception as e:
            logger.error(f"No se pudo enviar {foto}: {e}")
    await context.bot.send_message(chat_id=chat_id, text="¡Listo! 😊 Sigue los pasos y me avisas", reply_markup=get_volver())

async def manejar_todo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message or update.business_message
    if not message or not message.from_user or message.from_user.is_bot:
        return
    user = message.from_user
    user_id = user.id

    # MODIFICACIÓN 3: Si ya pagó, el bot no responde NADA a menos que lo reactives
    if user_id in PAGARON and user_id!= ADMIN_ID:
        return # Bot muerto para ese usuario

    if user_id == ADMIN_ID:
        pass # Admin siempre puede hablar
    else:
        username = user.username or "sin_username"
        registrar_usuario(user)

    ahora = datetime.now()
    nombre = user.first_name

    if message.text and message.text.lower() == '/start':
        DEMO_USADO.add(user_id)
        saludo = f"Mmmm {nombre}... 😏✨ llegaste justo cuando te pensaba 🙈"
        await message.reply_text(saludo, parse_mode='Markdown')
        await message.reply_text("¿Qué se te antoja hoy? 👇", reply_markup=get_menu(), parse_mode='Markdown')
        return

    # MODIFICACIÓN 3: Al recibir foto = pago = bot se desactiva para ese user
    if message.photo:
        PAGARON.add(user_id) # Se agrega a lista de "pagados/desactivados"
        foto_id = message.photo[-1].file_id
        await avisar_pago(context, user_id, username, nombre, foto_id)
        await message.reply_text(
            f"✅ *PAGO RECIBIDO* 😊\n\n"
            f"Gracias {nombre}, ya te registro\n"
            f"📩 *AHORA ESCRÍBEME AL PRIVADO*\n"
            f"👉 {USERNAME_ADMIN}\n\n"
            f"Ahí coordinamos tu pedido 😏\n\n"
            f"*El bot se desactiva aquí por seguridad*",
            parse_mode='Markdown'
        )
        return # Después de esto ya no responde más

    if not message.text:
        return

    texto = message.text.strip()

    if ULTIMO_MENSAJE.get(user_id) == texto.lower():
        return
    ULTIMO_MENSAJE[user_id] = texto.lower()

    if any(x in normalizar(texto) for x in ['gratis', 'free', 'regalo', 'bonus', 'muestra gratis']):
        await enviar_gratis(user_id, context)
        return

    if any(x in normalizar(texto) for x in ['comprar', 'compro', 'quiero', 'pago', 'pagare', 'llevo', 'lo quiero']):
        await message.reply_text(f"¡Así me gusta {nombre}! 😍🔥 Elige tu pack 👇", reply_markup=get_menu(), parse_mode='Markdown')
        return

    if any(x in normalizar(texto) for x in ['precio', 'cuanto', 'vale', 'costo', 'cuesta', 'peru', 'soles']):
        VIO_PRECIOS[user_id] = datetime.now()
        asyncio.create_task(follow_up_task(context.application, user_id, username))
        await message.reply_text(PE_PRECIOS, reply_markup=get_volver(), parse_mode='Markdown')
        return
    elif any(x in normalizar(texto) for x in ['mexico', 'mxn', 'peso']):
        VIO_PRECIOS[user_id] = datetime.now()
        asyncio.create_task(follow_up_task(context.application, user_id, username))
        await message.reply_text(MX_PRECIOS, reply_markup=get_volver(), parse_mode='Markdown')
        return
    elif any(x in normalizar(texto) for x in ['usd', 'usa', 'eeuu', 'dolar', 'estados unidos']):
        VIO_PRECIOS[user_id] = datetime.now()
        asyncio.create_task(follow_up_task(context.application, user_id, username))
        await message.reply_text(USA_PRECIOS, reply_markup=get_volver(), parse_mode='Markdown')
        return
    elif any(x in normalizar(texto) for x in ['otro', 'internacional', 'colombia', 'argentina', 'chile', 'mundial']):
        VIO_PRECIOS[user_id] = datetime.now()
        asyncio.create_task(follow_up_task(context.application, user_id, username))
        await message.reply_text(OTRO_PRECIOS, reply_markup=get_volver(), parse_mode='Markdown', disable_web_page_preview=True)
        return

    es_vip = user_id in VIP_TEMPORAL and VIP_TEMPORAL[user_id] > ahora

    if es_vip:
        tiempo_restante = (VIP_TEMPORAL[user_id] - ahora).seconds // 60
        if tiempo_restante <= 5:
            await message.reply_text(f"{nombre}, {tiempo_restante} min y me tengo que ir 😢\n\n¿Qué necesitas antes de irme? ✨", parse_mode='Markdown')
            return

    await message.reply_text("Elige una opción 😏👇", reply_markup=get_menu(), parse_mode='Markdown')

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    user_id = query.from_user.id

    # MODIFICACIÓN 3: Si ya pagó, no responde botones tampoco
    if user_id in PAGARON and user_id!= ADMIN_ID:
        return

    if data == 'pe':
        await query.edit_message_text(PE_PRECIOS, reply_markup=get_volver(), parse_mode='Markdown')
    elif data == 'mx':
        await query.edit_message_text(MX_PRECIOS, reply_markup=get_volver(), parse_mode='Markdown')
    elif data == 'usa':
        await query.edit_message_text(USA_PRECIOS, reply_markup=get_volver(), parse_mode='Markdown')
    elif data == 'otro':
        await query.edit_message_text(OTRO_PRECIOS, reply_markup=get_volver(), parse_mode='Markdown', disable_web_page_preview=True)
    elif data == 'gratis':
        # MODIFICACIÓN 2: Botón volver va en el mismo mensaje del texto
        await query.edit_message_text(TEXTO_GRATIS, reply_markup=get_volver(), parse_mode='Markdown')
        for foto in FOTOS_GRATIS:
            try:
                with open(foto, 'rb') as f:
                    await context.bot.send_photo(chat_id=user_id, photo=f)
                await asyncio.sleep(0.5)
            except Exception as e:
                logger.error(f"No se pudo enviar {foto}: {e}")

    elif data == 'volver':
        await query.edit_message_text("¿Qué se te antoja hoy? 👇", reply_markup=get_menu(), parse_mode='Markdown')

async def vip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id!= ADMIN_ID:
        return
    if not context.args:
        await update.message.reply_text("Uso: /vip ID_DEL_CLIENTE")
        return
    user_id = int(context.args[0])
    VIP_TEMPORAL[user_id] = datetime.now() + timedelta(minutes=15)
    await context.bot.send_message(user_id, "✅ *CHAT VIP ACTIVADO* 😊\n\nTienes *15 minutos* de atención prioritaria\n\nPregúntame lo que quieras ✨")
    await update.message.reply_text(f"✅ VIP activado para {user_id}")

# MODIFICACIÓN 3: Comando para reactivar el bot en un chat después del pago
async def activar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id!= ADMIN_ID:
        return
    if not context.args:
        await update.message.reply_text("Uso: /activar ID_DEL_CLIENTE")
        return
    user_id = int(context.args[0])
    if user_id in PAGARON:
        PAGARON.remove(user_id)
        await context.bot.send_message(user_id, "😏 Bot reactivado. ¿En qué te ayudo?")
        await update.message.reply_text(f"✅ Bot reactivado para {user_id}")
    else:
        await update.message.reply_text(f"⚠️ El usuario {user_id} no estaba desactivado")

async def usuarios(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id!= ADMIN_ID:
        return
    if not USUARIOS:
        await update.message.reply_text("No hay usuarios aún")
        return
    texto = "📊 *USUARIOS REGISTRADOS* 📊\n\n"
    for uid, data in USUARIOS.items():
        estado = "💰 PAGÓ/DESACTIVADO" if data['pago'] else "🔥 VIP" if data['es_vip'] else "👀 NUEVO"
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
    app.add_handler(CommandHandler('activar', activar)) # MODIFICACIÓN 3: Nuevo comando
    app.add_handler(CommandHandler('usuarios', usuarios))
    app.add_handler(CallbackQueryHandler(button))
    app.add_handler(MessageHandler(filters.ALL, manejar_todo))
    app.add_error_handler(error_handler)
    logger.info("BOT PRENDIDO - MODO 24/7 ACTIVO ✅")
    app.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    main()
