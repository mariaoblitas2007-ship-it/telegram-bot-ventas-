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
ADMIN_ID = 8783569348  # ← TU ID YA ESTÁ PUESTO ✅

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

📸 *IMPORTANTE:*
Cuando pagues, mándame la captura *con la palabra PAGO*
Así te atiendo más rápido 🔥

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

📸 *IMPORTANTE:*
Cuando pagues, mándame la captura *con la palabra PAGO*
Así te atiendo más rápido 🔥

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
→ incluye sexting 🥰
→ Ahorras 60%

━━━━━━━━━━━━━━━
📼 *VIDEOLLAMADAS \- INTERNACIONAL* 📼

$20 USD: 10 min
$30 USD: 20 min

━━━━━━━━━━━━━━━
🪙 *PAGO PAYPAL:* 
👉 https://www\.paypal\.com/qrcodes/p2pqrc/76RWY9FF7Q7RE

📸 *IMPORTANTE:*
Cuando pagues, mándame la captura *con la palabra PAGO*
Así te atiendo más rápido 🔥

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

async def responder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return
    try:
        # SI MANDAN FOTO - FILTRO DE PAGOS
        if update.message.photo:
            user = update.message.from_user
            caption_text = update.message.caption.lower() if update.message.caption else ""
            
            # PALABRAS CLAVE QUE SIGNIFICAN QUE ES UN PAGO
            palabras_pago = ['pago', 'yape', 'plin', 'comprobante', 'transferencia', 'paypal', 'listo', 'pagado', 'enviado', 'ya']
            
            # SI LA FOTO TIENE TEXTO DE PAGO = TE AVISA
            if any(palabra in caption_text for palabra in palabras_pago):
                caption_admin = f"🔥 *NUEVO PAGO RECIBIDO* 🔥\n\nCliente: @{user.username or 'Sin username'}\nNombre: {user.first_name}\nID: `{user.id}`\n\n*Revisa la captura y envía el pack manual* 💋"
                
                await context.bot.send_photo(
                    chat_id=ADMIN_ID,
                    photo=update.message.photo[-1].file_id,
                    caption=caption_admin,
                    parse_mode=ParseMode.MARKDOWN_V2
                )
                
                await update.message.reply_text(
                    "¡Recibí tu comprobante amor! 😘\n\nYa lo estoy revisando\. En 2 min te mando tu pack al toque 🔥\n\nGracias por confiar 💋",
                    reply_markup=get_volver(),
                    parse_mode=ParseMode.MARKDOWN_V2
                )
                return
            
            # SI MANDAN FOTO SIN TEXTO DE PAGO = NO TE AVISA
            else:
                await update.message.reply_text(
                    "Bebé vi tu fotito 😘\n\nPero si es tu comprobante de pago, *mándalo de nuevo y escribe 'PAGO'* en el mensaje\n\nAsí lo reviso al toque y te mando tu pack 🔥\n\nSi no es pago, no intercambio fotitos 🥺",
                    reply_markup=get_volver()
                )
                return
            
        if not update.message.text:
            return
        texto = update.message.text.lower()
        
        # EDAD - 18 AÑOS
        if any(x in texto for x in ['edad', 'años', 'mayor', 'menor', '18']):
            await update.message.reply_text(
                "Mi rey tengo *18 añitos* recién cumplidos 😘\n\n100% legal y con todas las ganas de complacerte\nMi contenido es real y hecho en casa para ti 💋",
                reply_markup=get_volver(),
                parse_mode=ParseMode.MARKDOWN_V2
            )
            return
            
        # PERSONALIZADO EXTRA
        elif any(x in texto for x in ['extra', 'más específico', 'otro personalizado', 'adicional', 'especial']):
            await update.message.reply_text(
                "Amor el *PREMIUM* incluye 1 personalizado básico 💋\n\nSi quieres algo MUY específico o varios videos a tu gusto:\nMándame pago extra y dime en el mensaje qué quieres\n*Sorpréndeme con tu pago* y yo te sorprendo con el video 🔥\n\nMínimo $5 USD extra por pedido especial\nTú me dices qué tan caliente lo quieres 😈",
                reply_markup=get_volver(),
                parse_mode=ParseMode.MARKDOWN_V2
            )
            return
        
        # RESPUESTAS AUTOMÁTICAS
        elif any(x in texto for x in ['intercambio', 'cambiamos', 'nudes x nudes']):
            await update.message.reply_text(
                "Ay bebé no hago intercambios 🥺\n\nMi contenido es mi trabajo y vale mucho\n\nSi quieres ver lo mío real, tengo el *BÁSICO* súper barato 💋\nEs casi como regalado y así ves que no soy estafa\n\n¿Qué dices? ¿Te animas? 🔥",
                reply_markup=get_volver()
            )
        elif any(x in texto for x in ['horario', 'hora', 'demora', 'cuando envias']):
            await update.message.reply_text(
                "Amor estoy activa 24/7 😘\n\nEnvío tu pack *al toque* cuando me llega tu captura con la palabra PAGO 💋\nMax 5 min de demora",
                reply_markup=get_volver()
            )
        elif any(x in texto for x in ['real', 'verdad', 'estafa', 'falso', 'confiar']):
            await update.message.reply_text(
                "Mi rey *tengo referencias* 🥰\n\nMira mi canal de regalitos y mi VIP\. Todo lo que ves ahí es mío\n\nSi quieres, primero prueba con el *BÁSICO* y ves que soy 100% real 💋",
                reply_markup=get_volver(),
                parse_mode=ParseMode.MARKDOWN_V2
            )
        elif any(x in texto for x in ['descuento', 'rebaja', 'promo', 'barato']):
            await update.message.reply_text(
                "Amor mis precios ya están con descuento 🥺\n\n*TOP y PREMIUM ahorras hasta 80%*\n\nNo puedo bajar más bebé, pero te aseguro que vale cada centavo 💋",
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
        try:
            await update.message.reply_text("Recibí tu captura amor 😘\n\nReviso tu pago y te mando tu pack al toque 🔥")
        except:
            pass

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
