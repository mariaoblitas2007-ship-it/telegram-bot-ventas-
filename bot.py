import os
import logging
import random
import asyncio
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from telegram.constants import ParseMode

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

TOKEN = os.environ.get('TOKEN')
ADMIN_ID = 8783569348

# VIP TEMPORAL: {user_id: fecha_expiración}
VIP_TEMPORAL = {}

def get_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🛍 PERÚ 🇵🇪", callback_data='pe')],
        [InlineKeyboardButton("🛍 MÉXICO 🇲🇽", callback_data='mx')],
        [InlineKeyboardButton("🛍 USA 🇺🇸", callback_data='usd')],
        [InlineKeyboardButton("🌍 OTRO PAÍS / INTERNATIONAL", callback_data='intl')],
        [InlineKeyboardButton("🎁 REGALITOS", callback_data='regalitos')],
        [InlineKeyboardButton("🔥 MI CANAL VIP", callback_data='canal')]
    ])

def get_volver():
    return InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Volver al Menú Principal", callback_data='volver')]])

PE_PRECIOS = """
🛍 *VIDEOS \- PERÚ* 🇵🇪

🎂 *BÁSICO: S/ 15*
→ 5 videos \| S/ 3 c/u

🔥 *TOP: S/ 30* ← MÁS VENDIDO
→ 12 videos \| S/ 2\.50 c/u
→ Ahorras 50%

🏆 *PREMIUM: S/ 60*
→ 1 personalizado \+ 20 videos
→ *Incluye chat hot 15 min* 🥰
→ Ahorras 67%

━━━━━━━━━━━━━━━
📼 *VIDEOLLAMADAS \- PERÚ* 📼

S/ 60: 10 min
S/ 80: 20 min

━━━━━━━━━━━━━━━
💳 *PAGO:*
*YAPE/PLIN:* `923553612`

📸 *IMPORTANTE:*
Manda captura con *"PAGO"* para activar tu chat VIP 🔥

1\. Yapeas 2\. Captura \+ PAGO
"""

MX_PRECIOS = """
🛍 *VIDEOS \- MÉXICO* 🇲🇽

🎂 *BÁSICO: $100 MXN*
→ 5 videos \| $20 c/u

🔥 *TOP: $200 MXN* ← MÁS VENDIDO
→ 12 videos \| $16 c/u
→ Ahorras 50%

🏆 *PREMIUM: $400 MXN*
→ 1 personalizado \+ 20 videos
→ *Incluye chat hot 15 min* 🥰
→ Ahorras 80%

━━━━━━━━━━━━━━━
📼 *VIDEOLLAMADAS \- MÉXICO* 📼

$400 MXN: 10 min
$600 MXN: 20 min

━━━━━━━━━━━━━━━
🛍 *PAGO MXN:*
🇲🇽 Transfer/Astropay → *Pídeme datos*

📸 *IMPORTANTE:*
Manda captura con *"PAGO"* para activar tu chat VIP 🔥

1\. Pagas 2\. Captura \+ PAGO
"""

USD_PRECIOS = """
🛍 *VIDEOS \- USD/INTERNACIONAL* 🌍

🎂 *BÁSICO: $5 USD*
→ 5 videos \| $1 c/u

🔥 *TOP: $9 USD* ← MÁS VENDIDO
→ 12 videos \| $0\.75 c/u
→ Ahorras 50%

🏆 *PREMIUM: $20 USD*
→ 1 personalizado \+ 20 videos
→ *Incluye chat hot 15 min* 🥰
→ Ahorras 60%

━━━━━━━━━━━━━━━
📼 *VIDEOLLAMADAS \- INTERNACIONAL* 📼

$20 USD: 10 min
$30 USD: 20 min

━━━━━━━━━━━━━━━
🪙 *PAGO PAYPAL:*
👉 https://www\.paypal\.com/qrcodes/p2pqrc/76RWY9FF7Q7RE

📸 *IMPORTANTE:*
Manda captura con *"PAGO"* para activar tu chat VIP 🔥

1\. Pagas 2\. Captura \+ PAGO
"""

REGALITOS = """
🎁 *REGALITOS PARA TI* 🔥

Aquí tienes contenido gratis amor:

👉 https://t\.me/\+cBI1upnfsN1iYTgx

Entra y disfruta 😘
"""

CANAL_VIP = """
🔥 *MI CANAL VIP EXCLUSIVO* 💋

Todo mi contenido más caliente está aquí:

👉 https://t\.me/\+ZWc0FAcw\-hQ2MDZh

*Solo para mis reyes* 👑
"""

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = "Hola amor 💋 Bienvenido a *YANABICITASA*\n\nTengo *18 añitos* y todo mi contenido es casero para ti 🔥\n\nElige tu país para ver precios:"
    try:
        if update.message:
            await update.message.reply_text(text, reply_markup=get_menu(), parse_mode=ParseMode.MARKDOWN_V2)
        elif update.callback_query:
            await update.callback_query.edit_message_text(text, reply_markup=get_menu(), parse_mode=ParseMode.MARKDOWN_V2)
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
            await query.edit_message_text(PE_PRECIOS, reply_markup=get_volver(), parse_mode=ParseMode.MARKDOWN_V2)
        elif data == 'mx':
            await query.edit_message_text(MX_PRECIOS, reply_markup=get_volver(), parse_mode=ParseMode.MARKDOWN_V2)
        elif data == 'usd' or data == 'intl':
            await query.edit_message_text(USD_PRECIOS, reply_markup=get_volver(), parse_mode=ParseMode.MARKDOWN_V2)
        elif data == 'regalitos':
            await query.edit_message_text(REGALITOS, reply_markup=get_volver(), parse_mode=ParseMode.MARKDOWN_V2, disable_web_page_preview=True)
        elif data == 'canal':
            await query.edit_message_text(CANAL_VIP, reply_markup=get_volver(), parse_mode=ParseMode.MARKDOWN_V2, disable_web_page_preview=True)
        elif data == 'volver':
            await start(update, context)
    except Exception as e:
        logger.error(f"Error en button: {e}")

async def quitar_vip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id!= ADMIN_ID:
        return
    try:
        user_id = int(context.args[0])
        VIP_TEMPORAL.pop(user_id, None)
        await update.message.reply_text(f"❌ Usuario {user_id} sacado de VIP")
    except:
        await update.message.reply_text("Uso: /unvip ID_DEL_CLIENTE")

async def responder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return
    try:
        user = update.message.from_user
        user_id = user.id
        ahora = datetime.now()

        # CHEQUEAR SI TIENE VIP ACTIVO
        es_vip = user_id in VIP_TEMPORAL and VIP_TEMPORAL[user_id] > ahora
        if user_id in VIP_TEMPORAL and not es_vip:
            del VIP_TEMPORAL[user_id]

        # FILTRO DE PAGOS + VIP 15 MIN AUTOMÁTICO
        if update.message.photo:
            caption_text = update.message.caption.lower() if update.message.caption else ""
            palabras_pago = ['pago', 'yape', 'plin', 'comprobante', 'transferencia', 'paypal', 'listo', 'pagado', 'enviado', 'ya']

            if any(palabra in caption_text for palabra in palabras_pago):
                expiracion = ahora + timedelta(minutes=15)
                VIP_TEMPORAL[user_id] = expiracion

                caption_admin = f"🔥 *PAGO + VIP 15MIN* 🔥\n\nCliente: @{user.username or 'Sin username'}\nNombre: {user.first_name}\nID: `{user.id}`\nExpira: {expiracion.strftime('%H:%M:%S')}\n\n*Si no es PREMIUM usa /unvip {user.id}* 💋"

                await context.bot.send_photo(
                    chat_id=ADMIN_ID,
                    photo=update.message.photo[-1].file_id,
                    caption=caption_admin,
                    parse_mode=ParseMode.MARKDOWN_V2
                )

                await update.message.reply_text(
                    "¡Recibí tu pago mi rey! 😘\n\n*Activé tu chat VIP por 15 minutos* 🔥\n\nAhora háblame rico mientras reviso tu pago y preparo tu pack 💦\n\nAprovecha que estoy que ardo 😈",
                    reply_markup=get_volver(),
                    parse_mode=ParseMode.MARKDOWN_V2
                )
                return
            else:
                await update.message.reply_text(
                    "Bebé vi tu fotito 😘\n\nPero si es tu comprobante, *mándalo con 'PAGO'* en el texto\n\nAsí activo tu chat VIP al toque 🔥",
                    reply_markup=get_volver()
                )
                return

        if not update.message.text:
            return
        texto = update.message.text.lower()

        # CHAT HOT FLUIDO SOLO PARA VIPS ACTIVOS - 15 MIN
        if es_vip:
            tiempo_restante = (VIP_TEMPORAL[user_id] - ahora).seconds // 60

            respuestas_hot = [
                f"Mmm me tienes mal papi 😏\n\nMe quedan {tiempo_restante} min de chat VIP\n¿En qué me vas a usar? 💋",
                f"Uff justo pensaba en ti 🔥\n\nAndo bien caliente y tengo {tiempo_restante} min para ti\n¿Qué quieres que haga? 😈",
                f"Mi rey me encanta cuando me hablas así 💦\n\nAprovecha que tengo {tiempo_restante} min libre\nVoy a grabar algo nuevo... ¿te lo dedico? 🥵",
                f"Jajaja me pones bien cachonda 😈\n\nQuedan {tiempo_restante} min de chat\nDime tu fantasía y veo si te la cumplo 💋",
                f"Bebé no sabes cómo me tienes 🔥\n\nTengo {tiempo_restante} min antes que se acabe el VIP\n¿Quieres que me toque pensando en ti? 😏",
                f"Ay papi me derrites 💦\n\nEn {tiempo_restante} min se corta el chat\nRápido dime qué quieres ver de mí 😈",
                f"Estoy que ardo por tu culpa 🥵\n\nMe quedan {tiempo_restante} min libre\n¿Te grabo algo ahorita mismo o qué? 💋",
                f"Mmm me gusta tu energía 😏\n\nTengo {tiempo_restante} min para ponernos hot\n¿Empezamos? 🔥"
            ]

            if any(x in texto for x in ['mas tiempo', 'más tiempo', 'otro', 'renovar', 'extender']):
                await update.message.reply_text(
                    f"Bebé me quedan {tiempo_restante} min 😢\n\nSi quieres más tiempo rico conmigo...\n*Compra otro PREMIUM y te doy 15 min más* 🔥\n\n¿Me mantienes caliente? 😈",
                    reply_markup=get_menu()
                )
                return

            resp = random.choice(respuestas_hot)
            await update.message.reply_text(resp, reply_markup=get_volver())
            return

        # RESPUESTAS NORMALES PARA NO-VIP
        elif any(x in texto for x in ['edad', 'años', 'mayor', 'menor', '18']):
            await update.message.reply_text(
                "Mi rey tengo *18 añitos* recién cumplidos 😘\n\n100% legal y con todas las ganas de complacerte\nMi contenido es real y hecho en casa para ti 💋",
                reply_markup=get_volver(),
                parse_mode=ParseMode.MARKDOWN_V2
            )
        elif any(x in texto for x in ['extra', 'más específico', 'otro personalizado', 'adicional', 'especial']):
            await update.message.reply_text(
                "Amor el *PREMIUM* incluye 1 personalizado básico 💋\n\nSi quieres algo MUY específico:\nMándame pago extra y dime qué quieres\n*Sorpréndeme con tu pago* y yo te sorprendo 🔥\n\nMínimo $5 USD extra por pedido especial",
                reply_markup=get_volver(),
                parse_mode=ParseMode.MARKDOWN_V2
            )
        elif any(x in texto for x in ['intercambio', 'cambiamos', 'nudes x nudes']):
            await update.message.reply_text(
                "Ay bebé no hago intercambios 🥺\n\nMi contenido es mi trabajo\n\nSi quieres verme real, el *BÁSICO* está súper barato 💋\nAsí ves que no soy estafa 🔥",
                reply_markup=get_volver()
            )
        elif any(x in texto for x in ['horario', 'hora', 'demora', 'cuando envias']):
            await update.message.reply_text(
                "Amor estoy activa 24/7 😘\n\nEnvío tu pack *al toque* cuando mandas captura con PAGO 💋\nMax 5 min de demora",
                reply_markup=get_volver()
            )
        elif any(x in texto for x in ['real', 'verdad', 'estafa', 'falso', 'confiar']):
            await update.message.reply_text(
                "Mi rey *tengo referencias* 🥰\n\nMira mi canal de regalitos y mi VIP\n\nPrueba con el *BÁSICO* y ves que soy 100% real 💋",
                reply_markup=get_volver(),
                parse_mode=ParseMode.MARKDOWN_V2
            )
        elif any(x in texto for x in ['peru', 'soles', 's/', 'yape']):
            await update.message.reply_text(PE_PRECIOS, reply_markup=get_volver(), parse_mode=ParseMode.MARKDOWN_V2)
        elif any(x in texto for x in ['mexico', 'mxn', 'peso', 'astropay']):
            await update.message.reply_text(MX_PRECIOS, reply_markup=get_volver(), parse_mode=ParseMode.MARKDOWN_V2)
        elif any(x in texto for x in ['usa', 'paypal', 'bank', 'dolar', 'internacional']):
            await update.message.reply_text(USD_PRECIOS, reply_markup=get_volver(), parse_mode=ParseMode.MARKDOWN_V2)
        elif any(x in texto for x in ['regalito', 'gratis', 'free', 'muestra']):
            await update.message.reply_text(REGALITOS, reply_markup=get_volver(), parse_mode=ParseMode.MARKDOWN_V2, disable_web_page_preview=True)
        elif any(x in texto for x in ['canal', 'vip']):
            await update.message.reply_text(CANAL_VIP, reply_markup=get_volver(), parse_mode=ParseMode.MARKDOWN_V2, disable_web_page_preview=True)
        else:
            await update.message.reply_text(
                "No entendí bebé 🥺\n\n*Usa los botones del menú* o escribe:\n→ `Peru` `Mexico` `Paypal`\n\nY te ayudo al toque 💋",
                reply_markup=get_menu(),
                parse_mode=ParseMode.MARKDOWN_V2
            )
    except Exception as e:
        logger.error(f"Error en responder: {e}")

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Exception: {context.error}", exc_info=context.error)

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("unvip", quitar_vip))
    app.add_handler(CallbackQueryHandler(button))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, responder))
    app.add_handler(MessageHandler(filters.PHOTO, responder))
    app.add_error_handler(error_handler)
    logger.info("Bot YANABICITASA iniciado")
    app.run_polling(drop_pending_updates=True, allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
