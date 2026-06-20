import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from telegram.constants import ParseMode

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

TOKEN = os.environ.get('TOKEN')
if not TOKEN:
    logger.error("FATAL: No se encontró TOKEN en Environment Variables")
    raise ValueError("Falta TOKEN en Render")

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
→ incluye sexting 🥰
→ Ahorras 67%

━━━━━━━━━━━━━━━
📼 *VIDEOLLAMADAS \- PERÚ* 📼

S/ 60: 10 min
S/ 80: 20 min

━━━━━━━━━━━━━━━
💳 *PAGO:*
*YAPE/PLIN:* `923553612`

*CUENTO CON REFERENCIAS*

1\. Yapeas 2\. Captura
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
→ incluye sexting 🥰
→ Ahorras 80%

━━━━━━━━━━━━━━━
📼 *VIDEOLLAMADAS \- MÉXICO* 📼

$400 MXN: 10 min
$600 MXN: 20 min

━━━━━━━━━━━━━━━
🛍 *PAGO MXN:*
🇲🇽 Transfer/Astropay
→ *Pídeme datos por aquí*

1\. Pagas 2\. Captura
"""

# 🌍 USD/INTERNACIONAL - SOLO PAYPAL ✅
USD_PRECIOS = """
🛍 *VIDEOS \- USD/INTERNACIONAL* 🌍

🎂 *BÁSICO: $5 USD*
→ 5 videos \| $1 c/u

🔥 *TOP: $9 USD* ← MÁS VENDIDO
→ 12 videos \| $0\.75 c/u
→ Ahorras 50%

🏆 *PREMIUM: $20 USD*
→ 1 personalizado \+ 20 videos
→ incluye sexting 🥰
→ Ahorras 60%

━━━━━━━━━━━━━━━
📼 *VIDEOLLAMADAS \- INTERNACIONAL* 📼

$20 USD: 10 min
$30 USD: 20 min

━━━━━━━━━━━━━━━
🪙 *PAGO PAYPAL:* 
👉 https://www\.paypal\.me/yanabicitasa

Avísame cuando envíes con el comprobante 🥰
En cuanto caiga te mando tu pack 🔥

1\. Pagas 2\. Captura
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
    text = "Hola amor 💋 Bienvenido a *YANABICITASA*\n\nElige tu país para ver precios:"
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

async def responder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return
    try:
        if update.message.photo:
            await update.message.reply_text(
                "Recibí tu captura amor 😘\n\nReviso tu pago y te mando tu pack al toque 🔥",
                reply_markup=get_volver()
            )
            return
        if not update.message.text:
            return
        texto = update.message.text.lower()
        if any(x in texto for x in ['peru', 'soles', 's/', 'yape']):
            await update.message.reply_text(PE_PRECIOS, reply_markup=get_volver(), parse_mode=ParseMode.MARKDOWN_V2)
        elif any(x in texto for x in ['mexico', 'mxn', 'peso', 'astropay']):
            await update.message.reply_text(MX_PRECIOS, reply_markup=get_volver(), parse_mode=ParseMode.MARKDOWN_V2)
        elif any(x in texto for x in ['usa', 'paypal', 'bank', 'dolar']):
            await update.message.reply_text(USD_PRECIOS, reply_markup=get_volver(), parse_mode=ParseMode.MARKDOWN_V2)
        elif any(x in texto for x in ['regalito', 'gratis', 'free', 'muestra']):
            await update.message.reply_text(REGALITOS, reply_markup=get_volver(), parse_mode=ParseMode.MARKDOWN_V2, disable_web_page_preview=True)
        elif any(x in texto for x in ['canal', 'vip']):
            await update.message.reply_text(CANAL_VIP, reply_markup=get_volver(), parse_mode=ParseMode.MARKDOWN_V2, disable_web_page_preview=True)
        else:
            await update.message.reply_text(
                "Amor, estos son los precios internacionales 🌍\n\n" + USD_PRECIOS,
                reply_markup=get_volver(),
                parse_mode=ParseMode.MARKDOWN_V2
            )
    except Exception as e:
        logger.error(f"Error en responder: {e}")

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Exception: {context.error}", exc_info=context.error)

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, responder))
    app.add_handler(MessageHandler(filters.PHOTO, responder))
    app.add_error_handler(error_handler)
    logger.info("Bot YANABICITASA iniciado")
    app.run_polling(drop_pending_updates=True, allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
