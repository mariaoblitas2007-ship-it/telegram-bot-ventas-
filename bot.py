import os
import asyncio
import random
import logging
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, MessageHandler, CallbackQueryHandler, filters, ContextTypes

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

TOKEN = '8751695788:AAFg5vFlt2EYvR5zOZ_tn29T0KZLYvTZs74'
ADMIN_ID = 8783569348
USERNAME_ADMIN = "@yanabicitasa"

LINK_CANAL = "https://t.me/+ZWc0FAcw-hQ2MDZh"
LINK_REGALITOS = "https://t.me/+cBI1upnfsN1iYTgx"
LINK_PAYPAL = "https://www.paypal.com/qrcodes/p2pqrc/76RWY9FF7Q7RE"

DEMO_HOT = {}
VIP_TEMPORAL = {}
DEMO_USADO = set()
USUARIOS = {}

def get_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🛍 VIDEOS - PERÚ 🇵🇪", callback_data='pe')],
        [InlineKeyboardButton("🛍 VIDEOS - MÉXICO 🇲🇽", callback_data='mx')],
        [InlineKeyboardButton("🛍 VIDEOS - USA 🇺🇸", callback_data='usa')],
        [InlineKeyboardButton("🌎 OTRO PAÍS", callback_data='otro')],
        [InlineKeyboardButton("🎁 Regalitos", url=LINK_REGALITOS)],
        [InlineKeyboardButton("🔥 Mi Canal VIP", url=LINK_CANAL)]
    ])

def get_volver():
    return InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Volver al Menú", callback_data='volver')]])

def registrar_usuario(user):
    USUARIOS[user.id] = {
        'nombre': user.first_name,
        'username': user.username or "sin_username",
        'ultimo_mensaje': datetime.now().strftime('%d/%m %H:%M'),
        'demo_usada': user.id in DEMO_USADO,
        'es_vip': user.id in VIP_TEMPORAL and VIP_TEMPORAL[user.id] > datetime.now()
    }

async def auto_tease_task(app, user_id, delay, tipo):
    await asyncio.sleep(delay)
    ahora = datetime.now()
    if tipo == "demo":
        if user_id not in DEMO_HOT or DEMO_HOT[user_id] < ahora:
            return
    else:
        if user_id not in VIP_TEMPORAL or VIP_TEMPORAL[user_id] < ahora:
            return

    teases = [
        "oye... Xd no dejo de pensar en ti 😳",
        "papi me distraje en clase x tu culpa 😈 JSKSKS",
        "toy aburrida... qué haces? 💦 uwu",
        "me puse a verme al espejo y... 🙈 JSKSKSSKS",
        "tengo calor 😰 o eres tú? uwu"
    ]

    try:
        await app.bot.send_message(chat_id=user_id, text=random.choice(teases))
    except Exception as e:
        logger.error(f"Error en auto-tease: {e}")

PE_PRECIOS = """
🛍 *VIDEOS - PERÚ* 🇵🇪

🎂 *BÁSICO: S/ 15*
→ 5 videos | S/ 3 c/u

🔥 *TOP: S/ 30* ← MÁS VENDIDO
→ 12 videos | S/ 2.50 c/u

🏆 *PREMIUM: S/ 60*
→ 1 personalizado + 20 videos
→ incluye sexting 🥰

📼 *VIDEOLLAMADAS* 📼
S/ 60: 10 min
S/ 80: 20 min

💳 *YAPE/PLIN:* 923553612
"""

MX_PRECIOS = """
🛍 *VIDEOS - MÉXICO* 🇲🇽

🎂 *BÁSICO: $100 MXN*
→ 5 videos | $20 c/u

🔥 *TOP: $200 MXN* ← MÁS VENDIDO
→ 12 videos | $16 c/u

🏆 *PREMIUM: $400 MXN*
→ 1 personalizado + 20 videos
→ incluye sexting 🥰

📼 *VIDEOLLAMADAS* 📼
$400 MXN: 10 min
$600 MXN: 20 min
"""

USA_PRECIOS = """
🛍 *VIDEOS - USA* 🇺🇸

🎂 *BÁSICO: $5 USD*
→ 5 videos | $1 c/u

🔥 *TOP: $9 USD* ← MÁS VENDIDO
→ 12 videos | $0.75 c/u

🏆 *PREMIUM: $20 USD*
→ 1 personalizado + 20 videos
→ incluye sexting 🥰

📼 *VIDEOLLAMADAS* 📼
$20 USD: 10 min
$30 USD: 20 min

🪙 *PayPal:* AbigailMaximoofO

🏦 *Bank EEUU:*
*Community Federal Savings Bank*
Account: 8338233469
Routing: 026073150
"""

OTRO_PRECIOS = f"""
🛍 *VIDEOS - INTERNACIONAL* 🌎

🎂 *BÁSICO: $5 USD*
🔥 *TOP: $9 USD* ← MÁS VENDIDO
🏆 *PREMIUM: $20 USD*

📼 *VIDEOLLAMADAS* 📼
$20 USD: 10 min
$30 USD: 20 min

🪙 *PayPal:* [Click aquí]({LINK_PAYPAL})
"""

# ESTE HANDLER AGARRA TODO: /start, texto, fotos, business
async def manejar_todo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Agarra mensajes normales Y de Business
    message = update.message or update.business_message
    if not message:
        return
        
    user = message.from_user
    user_id = user.id
    registrar_usuario(user)
    ahora = datetime.now()

    # DETECTA /start AQUÍ EN VEZ DE CommandHandler
    if message.text and message.text.lower() == '/start':
        es_nuevo = user_id not in DEMO_USADO
        if es_nuevo:
            DEMO_USADO.add(user_id)
            DEMO_HOT[user_id] = datetime.now() + timedelta(minutes=10)
            asyncio.create_task(auto_tease_task(context.application, user_id, 180, "demo"))
            asyncio.create_task(auto_tease_task(context.application, user_id, 420, "demo"))
            saludo = "olaaa mi rey 😘 Bienvenido a *YANABICITASA*\n\ntengo *18 añitos* y ando bien caliente 🔥\n\n*Te regalo 10 min de chat hot conmigo*\nes tu única vez gratis, aprovecha 💦"
            await message.reply_text(saludo, parse_mode='Markdown')
        else:
            await message.reply_text("ola de nuevo mi rey 😘 ya tienes tu demo usada Xd\n\npero puedes comprar *PREMIUM* y seguimos 💋", parse_mode='Markdown')
        await message.reply_text("Elige tu país para ver precios bebé:", reply_markup=get_menu(), parse_mode='Markdown')
        return

    # FOTOS
    if message.photo:
        username = user.username or "sin_username"
        await message.reply_text(
            f"Recibí tu captura amor 😘\n\n"
            f"⚠️ *IMPORTANTE:*\n"
            f"1️⃣ Escríbeme el *MONTO EXACTO* que pagaste\n"
            f"2️⃣ Háblame a mi perfil {USERNAME_ADMIN}\n\n"
            f"*Por ahí te envío tus videitos* 🔥",
            parse_mode='Markdown'
        )
        try:
            caption = f"💰 *NUEVA CAPTURA*\n\n👤 @{username}\n🆔 `{user_id}`"
            await context.bot.send_photo(chat_id=ADMIN_ID, photo=message.photo[-1].file_id, caption=caption, parse_mode='Markdown')
        except:
            pass
        return

    if not message.text:
        return

    texto = message.text.lower()
    es_vip = user_id in VIP_TEMPORAL and VIP_TEMPORAL[user_id] > ahora
    es_demo = user_id in DEMO_HOT and DEMO_HOT[user_id] > ahora

    # RESPUESTAS DEMO/VIP
    if es_vip or es_demo:
        if any(x in texto for x in ['hola', 'ola', 'buenas', 'hey']):
            await message.reply_text("olaaa 😘 cómo estás weno?")
            return
        elif any(x in texto for x in ['tocate', 'tócate', 'juega']):
            await message.reply_text("ufff ya me estoy tocando papi 💦 pensando en ti... sigo o te grabo? 😈")
            return
        else:
            await message.reply_text("uff mi rey justo me agarraste cambiando 😏 me acompañas o q? 💋")
            return

    # RESPUESTAS SIN DEMO
    if any(x in texto for x in ['peru', 'soles', 's/']):
        await message.reply_text(PE_PRECIOS, reply_markup=get_volver(), parse_mode='Markdown')
    elif any(x in texto for x in ['mexico', 'mxn']):
        await message.reply_text(MX_PRECIOS, reply_markup=get_volver(), parse_mode='Markdown')
    elif any(x in texto for x in ['usd', 'usa', 'eeuu']):
        await message.reply_text(USA_PRECIOS, reply_markup=get_volver(), parse_mode='Markdown')
    else:
        await message.reply_text("No entendí amor 😅\n\nElige una opción:", reply_markup=get_menu())

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    if data == 'pe':
        await query.edit_message_text(PE_PRECIOS, reply_markup=get_volver(), parse_mode='Markdown')
    elif data == 'mx':
        await query.edit_message_text(MX_PRECIOS, reply_markup=get_volver(), parse_mode='Markdown')
    elif data == 'usa':
        await query.edit_message_text(USA_PRECIOS, reply_markup=get_volver(), parse_mode='Markdown')
    elif data == 'otro':
        await query.edit_message_text(OTRO_PRECIOS, reply_markup=get_volver(), parse_mode='Markdown', disable_web_page_preview=True)
    elif data == 'volver':
        await query.edit_message_text("Elige tu país para ver precios bebé:", reply_markup=get_menu(), parse_mode='Markdown')

def main():
    app = Application.builder().token(TOKEN).build()
    
    # SOLO 2 HANDLERS: UNO PARA TODO, OTRO PARA BOTONES
    app.add_handler(MessageHandler(filters.ALL, manejar_todo))
    app.add_handler(CallbackQueryHandler(button))
    
    logger.info("BOT PRENDIDO - RESPONDE /start Y TODO")
    app.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    main()
