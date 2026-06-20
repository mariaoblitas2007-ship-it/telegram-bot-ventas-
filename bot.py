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

# ============= FUNCIONES AUXILIARES =============
async def send_fluid(message, textos):
    for i, texto in enumerate(textos):
        if i > 0:
            await asyncio.sleep(random.uniform(0.8, 1.5))
        try:
            await message.reply_text(texto, parse_mode='Markdown')
        except:
            break

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
        ["oye...", "Xd no dejo de pensar en ti 😳"],
        ["papi", "me distraje en clase x tu culpa 😈", "JSKSKS"],
        ["toy aburrida...", "qué haces? 💦 uwu"],
        ["me puse a verme al espejo y...", "🙈 JSKSKSSKS"],
        ["tengo calor 😰", "o eres tú? uwu"],
        ["weno...", "me voy a tener que... ya sabes 💦"],
        ["toy solita y con ganas 😈", "JSKSKS lastima q se acaba pronto"],
        ["JSKSKSSKS", "toy pensando coshitas 🥺"]
    ]

    try:
        mensajes = random.choice(teases)
        for i, texto in enumerate(mensajes):
            if i > 0:
                await asyncio.sleep(1.2)
            await app.bot.send_message(chat_id=user_id, text=texto)
        if tipo == "vip":
            await app.bot.send_message(chat_id=user_id, text="¿Otro PREMIUM? 😈", reply_markup=get_menu())
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

        saludo = random.choice([
            ["olaaa mi rey 😘", "Bienvenido a *YANABICITASA*", "tengo *18 añitos* y ando bien caliente 🔥", "*Te regalo 10 min de chat hot conmigo*", "es tu única vez gratis, aprovecha 💦"],
            ["heyy bebé 💋", "Bienvenido a *YANABICITASA* uwu", "tengo *18* y toy con ganas 😈", "*10 min hot gratis pa ti*", "solo esta vez Xd"]
        ])
        await send_fluid(update.message, saludo)
        asyncio.create_task(auto_tease_task(context.application, user_id, 180, "demo"))
        asyncio.create_task(auto_tease_task(context.application, user_id, 420, "demo"))
    else:
        saludo_vuelta = random.choice([
            ["ola de nuevo mi rey 😘", "ya tienes tu demo usada Xd", "pero puedes comprar *PREMIUM* y seguimos 💋"],
            ["heyy bebé 💋", "uwu ya gastaste tu demo", "pero PREMIUM y te doy *15 min VIP* 🔥"]
        ])
        await send_fluid(update.message, saludo_vuelta)

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
                await send_fluid(update.message, ["Ay no papi", "ya me voy a tener que ir 😢", "Aprovecha rápido", "Qué quieres que haga antes? 💋", "*Otro PREMIUM = seguimos más* 🔥"])
                return

            elif any(x in texto for x in ['hola', 'ola', 'buenas', 'hey', 'wenas', 'hello']):
                await send_fluid(update.message, random.choice([["olaaa 😘", "cómo estás weno?"], ["heyy bebé 💋", "q tal tu día? Xd"], ["oliii JSKSKSKS", "todo bien?", "en q te ayudo uwu"]]))
                return

            elif any(x in texto for x in ['como estas', 'cómo estás', 'que tal', 'k tal', 'estas bien']):
                await send_fluid(update.message, random.choice([["bien mi rey 😘", "gracias x preguntar Xd", "y tú cómo andas? 💋"], ["super bien bebé 🔥", "uwu tú q tal?"], ["bien amor 😏", "acá atendiéndote JSKSKS"]]))
                return

            elif any(x in texto for x in ['que haces', 'qué haces', 'q haces']):
                await send_fluid(update.message, random.choice([["nada acá 🙈", "pensando en ti Xd", "y tú?"], ["toy echada aburrida...", "y tú? uwu"], ["acabo de salir de bañarme 😳", "JSKSKS y tú q haces?"], ["ando de ganas la vdd 💦", "uwu y tú qué? JSKSKSSKS"]]))
                return

            elif any(x in texto for x in ['estas sola', 'estás sola', 'sola']):
                await send_fluid(update.message, random.choice([["sip solita 😈", "xq?"], ["sola y aburrida...", "me haces compañía? Xd"], ["solita en mi cuarto 🙈", "y tú? uwu"], ["sola y con calor 😰", "tú? Xd"]]))
                return

            elif any(x in texto for x in ['que tienes puesto', 'ropa', 'vestida', 'desnuda', 'calata', 'sin ropa']):
                await send_fluid(update.message, random.choice([["mmm nada papi 😏", "solo mi collar...", "te gusta así?", "o me pongo algo pa ti? 💋"], ["uff acabo de salir de bañarme 🔥", "ando con toalla nada más...", "la dejo caer? 😈"], ["bebé ando en ropa interior 😏", "negra de encaje...", "quieres que me la quite? 💦"]]))
                return

            elif any(x in texto for x in ['tocate', 'tócate', 'toca', 'masturba', 'dedos', 'dedéate', 'juega']):
                await send_fluid(update.message, random.choice([["ufff ya me estoy tocando papi 💦", "pensando en ti...", "sigo o te grabo? 😈"], ["mmm me metí los dedos 🥵", "x tu culpa", "estoy que me vengo...", "quieres escuchar? 💋"], ["bebé no sabes cómo me tienes 🔥", "ya estoy mojada...", "te muestro en video? 😏 Xd"]]))
                return

            elif any(x in texto for x in ['muestra', 'muestrame', 'enseña', 'ver', 'foto', 'video', 'pic']):
                await send_fluid(update.message, random.choice([["mmm quieres verme? 🥵", "dime EXACTO qué quieres ver", "y te lo hago 💦"], ["bebé si me pagas te muestro TODO 🔥", "pero si me dices qué quieres ver", "te doy precio especial 😏"]]))
                return

            elif any(x in texto for x in ['ganas', 'caliente', 'cachonda', 'excitada', 'mojada', 'arrecha', 'prendida']):
                await send_fluid(update.message, random.choice([["ay papi estoy que ardo 🥵", "toda mojada...", "qué me haces? 💦"], ["bebé no sabes cómo me tienes 😈", "necesito que me calmes...", "cómo? 🔥 Xd"], ["uff estoy bien cachonda 💦", "me ayudas?", "o me grabo sola? 😏"]]))
                return

            elif any(x in texto for x in ['pene', 'verga', 'pito', 'pinga', 'p']):
                await send_fluid(update.message, random.choice([["uff papi me gustan los p... 😏", "cómo tienes el tuyo?", "cuéntame 💦 Xd"], ["bebé me vuelven loca los p... 🥵", "grande?", "grueso?", "dime todo 🔥"]]))
                return

            elif any(x in texto for x in ['tamaño', 'grande', 'cm', 'centímetros', 'mide', 'largo', 'grueso']):
                await send_fluid(update.message, random.choice([["mmm me gustan grandes papi 😏", "cuántos cm tienes?", "dime y te digo si me entra 💦"], ["bebé el tamaño sí importa 🥵", "cuántos cm?", "si me gusta te grabo algo especial 🔥"]]))
                return

            elif any(x in texto for x in ['jaja', 'xd', 'jiji', 'jsjs', 'jsksks', 'XDD']):
                await send_fluid(update.message, random.choice([["JSKSKSSKS 😘", "de q te ríes bebé?"], ["Xd me haces reír 🔥", "qué pasó uwu"], ["jsksk amor 😏", "eres chistoso"]]))
                return

            elif any(x in texto for x in ['linda', 'bonita', 'hermosa', 'preciosa', 'guapa', 'sexy', 'cute', 'rica']):
                await send_fluid(update.message, random.choice([["aww coshita 🥺", "gracias mi rey"], ["JSKSKSKS coshita linda 😘", "uwu tú también"], ["ay coshita 💕", "me sonrojaste Xd"]]))
                return

            elif any(x in texto for x in ['gracias', 'ok', 'vale', 'bueno', 'dale', 'perfecto', 'weno', 'okaa', 'listo']):
                await send_fluid(update.message, random.choice([["de nada mi rey 😘", "Xd cualquier coshita me avisas 💋"], ["a ti bebé 🔥", "uwu acá toy si necesitas algo"], ["weno amor 😏", "JSKSKS me hablas cuando quieras"]]))
                return

            else:
                await send_fluid(update.message, random.choice([["uff mi rey", "justo me agarraste cambiando 😏", "me acompañas o q? 💋"], ["papi llegaste rico 🔥", "ando bien prendida...", "quieres ver? 😈"], ["ando de ganas bebé 🔥", "qué hacemos? 💦 Xd"], ["uff ando de ganas mal 😈", "me calmas tú?", "o me grabo? 💋"]]))
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
        asyncio.create_task(auto_tease_task(context.application, user_id, 600, "vip"))
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
    logger.info("Bot YANABICITASA iniciado")
    app.run_polling(drop_pending_updates=True, allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
