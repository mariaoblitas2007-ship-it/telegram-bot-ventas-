import os
import asyncio
import random
import logging
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# ============= TU TOKEN Y TU ID =============
TOKEN = '8751695788:AAFg5vFlt2EYvR5zOZ_tn29T0KZLYvTZs74'
ADMIN_ID = 8783569348
# ==============================================

# ============= LINKS =============
LINK_CANAL = "https://t.me/+ZWc0FAcw-hQ2MDZh"
LINK_REGALITOS = "https://t.me/+cBI1upnfsN1iYTgx"
LINK_PAYPAL = "https://www.paypal.com/qrcodes/p2pqrc/76RWY9FF7Q7RE"

# ============= DATOS DE PAGO =============
YAPE_PLIN = "923553612"
PAYPAL = "AbigailMaximoofO"
BANK_USA = {
    'banco': 'Community Federal Savings Bank',
    'direccion': '5 Penn Plaza, 14th Floor\nNew York, NY 10001, US',
    'cuenta': '8338233469',
    'routing': '026073150',
    'tipo': 'Checking'
}

# ============= BASE DE DATOS =============
DEMO_HOT = {}
VIP_TEMPORAL = {}
DEMO_USADO = set()

# ============= MENÚS =============
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

# ============= FUNCIONES AUXILIARES - OPTIMIZADAS =============
async def send_fluid(message, textos):
    """Manda todos los mensajes de una - SIN DELAY para no congelar"""
    try:
        for texto in textos:
            await message.reply_text(texto, parse_mode='Markdown')
    except Exception as e:
        logger.error(f"Error send_fluid: {e}")

async def auto_tease_task(context: ContextTypes.DEFAULT_TYPE):
    """JobQueue en vez de asyncio.sleep - NO BLOQUEA"""
    job = context.job
    user_id = job.data['user_id']
    tipo = job.data['tipo']

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
        "tengo calor 😰 o eres tú? uwu",
        "weno... me voy a tener que... ya sabes 💦",
        "toy solita y con ganas 😈 JSKSKS lastima q se acaba pronto",
        "JSKSKSSKS toy pensando coshitas 🥺"
    ]

    try:
        await context.bot.send_message(chat_id=user_id, text=random.choice(teases))
        if tipo == "vip":
            await context.bot.send_message(chat_id=user_id, text="¿Otro PREMIUM? 😈", reply_markup=get_menu())
    except Exception as e:
        logger.error(f"Error en auto-tease: {e}")

# ============= TEXTOS DE PRECIOS =============
PE_PRECIOS = """
🛍 *VIDEOS - PERÚ* 🇵🇪

🎂 *BÁSICO: S/ 15*
→ 5 videos | S/ 3 c/u

🔥 *TOP: S/ 30* ← MÁS VENDIDO
→ 12 videos | S/ 2.50 c/u
→ *Ahorras 50%*

🏆 *PREMIUM: S/ 60*
→ 1 personalizado + 20 videos
→ incluye sexting 🥰
→ *Ahorras 67%*

📼 *VIDEOLLAMADAS* 📼
S/ 60: 10 min
S/ 80: 20 min

💳 *PAGO:*
*YAPE/PLIN:* 923553612

*CUENTO CON REFERENCIAS*

1. Yapeas 2. Captura
"""

MX_PRECIOS = """
🛍 *VIDEOS - MÉXICO* 🇲🇽

🎂 *BÁSICO: $100 MXN*
→ 5 videos | $20 c/u

🔥 *TOP: $200 MXN* ← MÁS VENDIDO
→ 12 videos | $16 c/u
→ *Ahorras 50%*

🏆 *PREMIUM: $400 MXN*
→ 1 personalizado + 20 videos
→ incluye sexting 🥰
→ *Ahorras 80%*

📼 *VIDEOLLAMADAS* 📼
$400 MXN: 10 min
$600 MXN: 20 min

🛍 *PAGO MXN:*
🇲🇽 Transfer/Astropay
→ *Pídeme datos por aquí*

1. Pagas 2. Captura
"""

USA_PRECIOS = """
🛍 *VIDEOS - USA* 🇺🇸

🎂 *BÁSICO: $5 USD*
→ 5 videos | $1 c/u

🔥 *TOP: $9 USD* ← MÁS VENDIDO
→ 12 videos | $0.75 c/u
→ *Ahorras 50%*

🏆 *PREMIUM: $20 USD*
→ 1 personalizado + 20 videos
→ incluye sexting 🥰
→ *Ahorras 60%*

📼 *VIDEOLLAMADAS* 📼
$20 USD: 10 min
$30 USD: 20 min

🪙 *PAGO:*
*PayPal:* AbigailMaximoofO

🏦 *Bank EEUU:*
*Community Federal Savings Bank*
📍 Bank Address:
5 Penn Plaza, 14th Floor
New York, NY 10001, US
0️⃣ Account Number: 8338233469
0️⃣ Routing Number: 026073150
✍️ Account Type: Checking

Avísame cuando envíes con el comprobante 🥰
En cuanto caiga te mando tu pack 🔥

1. Pagas 2. Captura
"""

OTRO_PRECIOS = f"""
🛍 *VIDEOS - INTERNACIONAL* 🌎

🎂 *BÁSICO: $5 USD*
→ 5 videos | $1 c/u

🔥 *TOP: $9 USD* ← MÁS VENDIDO
→ 12 videos | $0.75 c/u
→ *Ahorras 50%*

🏆 *PREMIUM: $20 USD*
→ 1 personalizado + 20 videos
→ incluye sexting 🥰
→ *Ahorras 60%*

📼 *VIDEOLLAMADAS* 📼
$20 USD: 10 min
$30 USD: 20 min

🪙 *PAGO:*
*PayPal:* [Click aquí]({LINK_PAYPAL})

Mándame captura cuando pagues bebé 🥰
En cuanto caiga te mando tu pack 🔥

1. Pagas 2. Captura
"""

# ============= HANDLERS =============
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    es_nuevo = user_id not in DEMO_USADO

    if es_nuevo:
        DEMO_USADO.add(user_id)
        DEMO_HOT[user_id] = datetime.now() + timedelta(minutes=10)

        # Auto-tease con JobQueue - NO BLOQUEA
        context.job_queue.run_once(auto_tease_task, 180, data={'user_id': user_id, 'tipo': 'demo'})
        context.job_queue.run_once(auto_tease_task, 420, data={'user_id': user_id, 'tipo': 'demo'})

        saludo = ["olaaa mi rey 😘 Bienvenido a *YANABICITASA*\n\ntengo *18 añitos* y ando bien caliente 🔥\n\n*Te regalo 10 min de chat hot conmigo*\nes tu única vez gratis, aprovecha 💦"]
        await update.message.reply_text(saludo[0], parse_mode='Markdown')
    else:
        saludo_vuelta = "ola de nuevo mi rey 😘 ya tienes tu demo usada Xd\n\npero puedes comprar *PREMIUM* y seguimos 💋"
        await update.message.reply_text(saludo_vuelta, parse_mode='Markdown')

    text = "Elige tu país para ver precios bebé:"
    try:
        if update.message:
            await update.message.reply_text(text, reply_markup=get_menu(), parse_mode='Markdown')
        elif update.callback_query:
            await update.callback_query.edit_message_text(text, reply_markup=get_menu(), parse_mode='Markdown')
    except Exception as e:
        logger.error(f"Error en start: {e}")

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    if not query:
        return
    await query.answer()
    try:
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
            await start(update, context)
    except Exception as e:
        logger.error(f"Error en button: {e}")

async def responder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return
    try:
        user_id = update.effective_user.id
        ahora = datetime.now()

        es_vip = user_id in VIP_TEMPORAL and VIP_TEMPORAL[user_id] > ahora
        es_demo = user_id in DEMO_HOT and DEMO_HOT[user_id] > ahora

        if update.message.photo:
            await update.message.reply_text(
                "Recibí tu captura amor 😘\n\nReviso tu pago y te mando tu pack al toque 🔥",
                reply_markup=get_volver()
            )
            return

        if not update.message.text:
            return

        texto = update.message.text.lower()

        if es_vip or es_demo:
            tiempo_restante = (VIP_TEMPORAL[user_id] - ahora).seconds // 60 if es_vip else (DEMO_HOT[user_id] - ahora).seconds // 60

            if not es_vip and tiempo_restante <= 2:
                await update.message.reply_text("Ay papi se me va a acabar el tiempo 😢\n\n*Si quieres seguir caliente conmigo...*\n\nCompra *PREMIUM* y seguimos sin corte 🔥", reply_markup=get_menu(), parse_mode='Markdown')
                return

            if any(x in texto for x in ['mas tiempo', 'más tiempo', 'otro', 'renovar', 'seguir']):
                await update.message.reply_text("Bebé se me está acabando 😢\n\nSi quieres seguir calientito...\n*PREMIUM y seguimos* sin corte 🔥", reply_markup=get_menu(), parse_mode='Markdown')
                return

            elif es_vip and tiempo_restante <= 5:
                await update.message.reply_text("Ay no papi ya me voy a tener que ir 😢\n\nAprovecha rápido\n\nQué quieres que haga antes? 💋\n\n*Otro PREMIUM = seguimos más* 🔥", parse_mode='Markdown')
                return

            # Respuestas rápidas sin delay
            respuestas = {
                'hola': "olaaa 😘 cómo estás weno?",
                'ola': "heyy bebé 💋 q tal tu día? Xd",
                'como estas': "bien mi rey 😘 gracias x preguntar Xd y tú cómo andas? 💋",
                'que haces': "nada acá 🙈 pensando en ti Xd y tú?",
                'estas sola': "sip solita 😈 xq?",
                'que tienes puesto': "mmm nada papi 😏 solo mi collar... te gusta así? o me pongo algo pa ti? 💋",
                'tocate': "ufff ya me estoy tocando papi 💦 pensando en ti... sigo o te grabo? 😈",
                'muestra': "mmm quieres verme? 🥵 dime EXACTO qué quieres ver y te lo hago 💦",
                'ganas': "ay papi estoy que ardo 🥵 toda mojada... qué me haces? 💦",
                'pene': "uff papi me gustan los p... 😏 cómo tienes el tuyo? cuéntame 💦 Xd",
                'tamaño': "mmm me gustan grandes papi 😏 cuántos cm tienes? dime y te digo si me entra 💦",
                'jaja': "JSKSKSSKS 😘 de q te ríes bebé?",
                'linda': "aww coshita 🥺 gracias mi rey",
                'gracias': "de nada mi rey 😘 Xd cualquier coshita me avisas 💋"
            }

            for key, resp in respuestas.items():
                if key in texto:
                    await update.message.reply_text(resp, parse_mode='Markdown')
                    return

            # Respuesta genérica
            await update.message.reply_text("uff mi rey justo me agarraste cambiando 😏 me acompañas o q? 💋", parse_mode='Markdown')
            return

        if any(x in texto for x in ['precio', 'peru', 'soles', 's/']):
            await update.message.reply_text(PE_PRECIOS, reply_markup=get_volver(), parse_mode='Markdown')
        elif any(x in texto for x in ['mexico', 'mxn', 'peso']):
            await update.message.reply_text(MX_PRECIOS, reply_markup=get_volver(), parse_mode='Markdown')
        elif any(x in texto for x in ['usd', 'dolar', 'usa', 'eeuu']):
            await update.message.reply_text(USA_PRECIOS, reply_markup=get_volver(), parse_mode='Markdown')
        elif any(x in texto for x in ['otro', 'internacional', 'colombia', 'argentina', 'chile', 'españa', 'europa']):
            await update.message.reply_text(OTRO_PRECIOS, reply_markup=get_volver(), parse_mode='Markdown', disable_web_page_preview=True)
        elif any(x in texto for x in ['gratis', 'free', 'muestra', 'regalo']):
            await update.message.reply_text(f"🎁 *CONTENIDO GRATIS* 🔥\n\nÚnete a mi canal gratis bebé:\n\n👉 {LINK_REGALITOS}\n\n*Pero si quieres algo más hot...*\nCompra PREMIUM y te doy atención 1 a 1 😈", reply_markup=get_volver(), parse_mode='Markdown', disable_web_page_preview=False)
        else:
            await update.message.reply_text(
                "No entendí amor 😅\n\nElige una opción:",
                reply_markup=get_menu()
            )
    except Exception as e:
        logger.error(f"Error en responder: {e}")

async def vip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id!= ADMIN_ID:
        return
    try:
        if not context.args:
            await update.message.reply_text("Uso: /vip ID_DEL_CLIENTE")
            return
        user_id = int(context.args[0])
        VIP_TEMPORAL[user_id] = datetime.now() + timedelta(minutes=15)
        DEMO_HOT.pop(user_id, None)
        # JobQueue para VIP
        context.job_queue.run_once(auto_tease_task, 600, data={'user_id': user_id, 'tipo': 'vip'})
        await context.bot.send_message(user_id, "✅ *VIP ACTIVADO* 😈\n\nTienes *15 minutos* conmigo bebé\n\nHáblame rico 🔥")
        await update.message.reply_text(f"✅ VIP activado para {user_id}")
    except Exception as e:
        await update.message.reply_text(f"Error: {e}")

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Exception: {context.error}", exc_info=context.error)

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("vip", vip))
    app.add_handler(CallbackQueryHandler(button))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, responder))
    app.add_handler(MessageHandler(filters.PHOTO, responder))
    app.add_error_handler(error_handler)
    logger.info("Bot YANABICITASA iniciado - OPTIMIZADO")
    app.run_polling(drop_pending_updates=True, allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
