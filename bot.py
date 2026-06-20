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

# DEMO GRATIS: {user_id: fecha_expiración} - 10 min
DEMO_HOT = {}
# VIP PAGO: {user_id: fecha_expiración} - 15 min
VIP_TEMPORAL = {}
# REGISTRO: usuarios que YA usaron su demo gratis
DEMO_USADO = set()

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
Manda captura con *"PAGO"* para chat VIP 15 min 🔥

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
Manda captura con *"PAGO"* para chat VIP 15 min 🔥

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
Manda captura con *"PAGO"* para chat VIP 15 min 🔥

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
    user_id = update.effective_user.id
    ahora = datetime.now()
    es_nuevo = user_id not in DEMO_USADO and user_id not in VIP_TEMPORAL

    # SOLO DA DEMO SI ES PRIMERA VEZ
    if es_nuevo:
        DEMO_HOT[user_id] = ahora + timedelta(minutes=10)
        DEMO_USADO.add(user_id)
        text = "Mmm hola mi rey 😈 Bienvenido a *YANABICITASA*\n\nTengo *18 añitos* y ando bien caliente ahorita 🔥\n\n*Te regalo 10 min de chat hot conmigo*\nEs tu única vez gratis, aprovecha 💦\n\nElige tu país bebé:"
    else:
        text = "Hola amor 💋 Bienvenida de vuelta a *YANABICITASA*\n\nTengo *18 añitos* y todo mi contenido es casero para ti 🔥\n\nElige tu país para ver precios:"

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
        DEMO_HOT.pop(user_id, None)
        # Descomenta la línea de abajo si quieres resetear su demo gratis:
        # DEMO_USADO.discard(user_id)
        await update.message.reply_text(f"❌ Usuario {user_id} sacado de VIP/DEMO")
    except:
        await update.message.reply_text("Uso: /unvip ID_DEL_CLIENTE")

async def responder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message:
        return
    try:
        user = update.message.from_user
        user_id = user.id
        ahora = datetime.now()

        # CHEQUEAR VIP PAGO - 15 MIN
        es_vip = user_id in VIP_TEMPORAL and VIP_TEMPORAL[user_id] > ahora
        if user_id in VIP_TEMPORAL and not es_vip:
            del VIP_TEMPORAL[user_id]

        # CHEQUEAR DEMO GRATIS - 10 MIN
        es_demo = user_id in DEMO_HOT and DEMO_HOT[user_id] > ahora
        if user_id in DEMO_HOT and not es_demo:
            del DEMO_HOT[user_id]

        # FILTRO DE PAGOS + VIP 15 MIN
        if update.message.photo:
            caption_text = update.message.caption.lower() if update.message.caption else ""
            palabras_pago = ['pago', 'yape', 'plin', 'comprobante', 'transferencia', 'paypal', 'listo', 'pagado', 'enviado', 'ya']

            if any(palabra in caption_text for palabra in palabras_pago):
                # CANCELA DEMO Y ACTIVA VIP 15 MIN
                DEMO_HOT.pop(user_id, None)
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
                    "¡Recibí tu pago mi rey! 😘\n\n*Cancelé el demo y activé tu VIP 15 min* 🔥\n\nAhora sí háblame TODO lo que quieras 💦\n\nSoy toda tuya 😈",
                    reply_markup=get_volver(),
                    parse_mode=ParseMode.MARKDOWN_V2
                )
                return
            else:
                await update.message.reply_text(
                    "Bebé vi tu fotito 😘\n\nPero si es tu comprobante, *mándalo con 'PAGO'*\n\nAsí activo tu VIP 15 min al toque 🔥",
                    reply_markup=get_volver()
                )
                return

        if not update.message.text:
            return
        texto = update.message.text.lower()

        # CHAT HOT - PRIORIDAD: VIP > DEMO
        if es_vip or es_demo:
            tiempo_restante = (VIP_TEMPORAL[user_id] - ahora).seconds // 60 if es_vip else (DEMO_HOT[user_id] - ahora).seconds // 60
            tipo_chat = "VIP" if es_vip else "DEMO"

            # Si es DEMO y quedan 2 min o menos, presiona venta
            if not es_vip and tiempo_restante <= 2:
                await update.message.reply_text(
                    f"Ay papi me quedan {tiempo_restante} min de demo 😢\n\n*Si quieres seguir caliente conmigo...*\n\nCompra *PREMIUM* y te doy *15 min VIP* sin corte 🔥\n\n¿Me dejas ir o me compras? 😈",
                    reply_markup=get_menu()
                )
                return

            respuestas_provoca = [
                f"Uff mi rey justo me agarraste cambiando 😏\n\nTengo {tiempo_restante} min libre [{tipo_chat}]\n¿Me acompañas o qué? 💋",
                f"Papi llegaste rico 🔥\n\nAndo bien prendida y tengo {tiempo_restante} min\n¿Quieres ver lo que estoy haciendo? 😈",
                f"Bebé me encanta tu timing 💦\n\nEn {tiempo_restante} min me voy a grabar\n¿Te lo dedico o se lo mando a otro? 😏",
                f"Mi amor me cachaste sin nada puesto 😈\n\nTengo {tiempo_restante} min antes de vestirme\n¿Aprovechas o te lo pierdes? 🔥",
                f"Rey justo iba a portarme mal en cámara 🥵\n\nMe quedan {tiempo_restante} min\n¿Quieres ser mi cómplice? 💋",
                f"Mmm me tienes pensando cosas 🥺\n\nTengo {tiempo_restante} min libre\n¿Te cuento en qué? O mejor te lo muestro 😏",
                f"Ay papi me pusiste mal 💦\n\nVoy a tener que grabar para calmarme\nTengo {tiempo_restante} min ¿te unes? 😈",
                f"Bebé ando con ganas de hacer travesuras 🔥\n\nEn {tiempo_restante} min empiezo\n¿Quieres ver el detrás de cámaras? 💋",
                f"Mi rey me agarraste caliente 🥵\n\nTengo {tiempo_restante} min antes de mi próxima grabación\n¿Te doy un adelanto exclusivo? 😏",
                f"Uff justo me estaba tocando pensando en ti 😈\n\nMe quedan {tiempo_restante} min\n¿Sigo o me detengo? Tú mandas 💦"
            ]

            # Si pide más tiempo
            if any(x in texto for x in ['mas tiempo', 'más tiempo', 'otro', 'renovar', 'extender', 'seguir']):
                resp = f"Bebé me quedan {tiempo_restante} min 😢\n\nSi quieres seguir calientito...\n*PREMIUM te da 15 min VIP* sin corte 🔥\n\n¿Me mantienes prendida? 😈"
                await update.message.reply_text(resp, reply_markup=get_menu())
                return

            # Si quedan 5 min o menos en VIP, mete urgencia
            elif es_vip and tiempo_restante <= 5:
                await update.message.reply_text(
                    f"Ay no papi me quedan {tiempo_restante} min 😢\n\nAprovecha rápido\n¿Qué quieres que haga antes que se corte? 💋\n\n*Otro PREMIUM = 15 min más* 🔥",
                    reply_markup=get_volver()
                )
                return

            # Normal: provocar
            else:
                resp = random.choice(respuestas_provoca)
                await update.message.reply_text(resp, reply_markup=get_volver())
                return

        # RESPUESTAS CASUALES HUMANAS PARA TODOS - SIN VIP/DEMO
        elif any(x in texto for x in ['hola', 'ola', 'buenas', 'hey', 'hello', 'buenos dias', 'buenas tardes', 'buenas noches']):
            respuestas_saludo = [
                "Holaaa mi rey 😘 ¿Cómo estás tú?",
                "Hey bebé 💋 ¿Qué tal tu día?",
                "Holaaa amor 😏 ¿En qué te puedo ayudar?",
                "Oli mi vida 💕 ¿Todo bien?",
                "Hola papi 😘 ¿Qué buscas hoy?",
                "Holaa hermoso 🔥 ¿Cómo amaneciste?",
                "Hey mi amor 💋 ¿Qué se te ofrece?",
                "Holaaa bebé 🥰 ¿Cómo te va?",
                "Oli rey 😏 ¿Qué cuentas?",
                "Hola mi cielo 💕 ¿En qué te atiendo?"
            ]
            await update.message.reply_text(
                random.choice(respuestas_saludo),
                reply_markup=get_volver()
            )
            return

        elif any(x in texto for x in ['como estas', 'cómo estás', 'que tal', 'qué tal', 'estas bien', 'estás bien', 'como andas']):
            respuestas_estado = [
                "Bien mi rey 😘 Gracias por preguntar\n¿Y tú cómo andas? 💋",
                "Súper bien bebé 🔥 ¿Tú qué tal?",
                "Bien amor 😏 Acá atendiéndote a ti\n¿En qué te ayudo?",
                "Todo bien mi vida 💕 ¿Y tú?",
                "Bien papi 😘 Un poco ocupada pero siempre para ti\n¿Qué necesitas?",
                "Bien hermoso 🔥 ¿Tú cómo vas?",
                "Muy bien mi amor 💋 ¿Y tú qué tal tu día?"
            ]
            await update.message.reply_text(
                random.choice(respuestas_estado),
                reply_markup=get_volver()
            )
            return

        elif any(x in texto for x in ['gracias', 'ok', 'vale', 'bueno', 'dale', 'perfecto', 'listo']):
            respuestas_cierre = [
                "De nada mi rey 😘 Cualquier cosa me avisas 💋",
                "A ti bebé 🔥 Acá estoy si necesitas algo",
                "Vale amor 😏 Me hablas cuando quieras",
                "Dale papi 💕 Cuídate mucho",
                "Ya sabes mi rey 😘 Acá estoy 24/7",
                "Perfecto hermoso 🔥 Cuando quieras"
            ]
            await update.message.reply_text(
                random.choice(respuestas_cierre),
                reply_markup=get_volver()
            )
            return

        elif any(x in texto for x in ['jaja', 'jajaja', 'xd', 'jiji', 'jeje']):
            respuestas_risa = [
                "Jajaja 😘 ¿De qué te ríes bebé?",
                "Jaja me haces reír 🔥 ¿Qué pasó?",
                "Jajaja amor 😏 Eres chistoso",
                "Jeje 💕 Me gusta tu risa",
                "Jaja papi 😘 ¿Qué es tan gracioso?"
            ]
            await update.message.reply_text(
                random.choice(respuestas_risa),
                reply_markup=get_volver()
            )
            return

        # RESPUESTAS DE VENTAS PARA NO-VIP/DEMO
        elif any(x in texto for x in ['edad', 'años', 'mayor', 'menor', '18']):
            await update.message.reply_text(
                "Mi rey tengo *18 añitos* recién cumplidos 😘\n\n100% legal y con todas las ganas de complacerte\nMi contenido es real y hecho en casa para ti 💋",
                reply_markup=get_volver(),
                parse_mode=ParseMode.MARKDOWN_V2
            )
        elif any(x in texto for x in ['demo', 'gratis', 'prueba', 'hot']):
            if user_id in DEMO_USADO:
                await update.message.reply_text(
                    "Bebé el demo gratis ya se te acabó 😢\n\n*Compra PREMIUM y tienes 15 min de chat hot* 🔥\n\n¿Te animas? 😈",
                    reply_markup=get_menu()
                )
            else:
                await update.message.reply_text(
                    "Mi rey escribe /start y te activo tu demo gratis 😏\n\n10 min de chat hot conmigo 💋",
                    reply_markup=get_volver()
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
        elif any(x in texto for x in ['horario', 'hora', 'demora', 'cuando envias', 'cuándo envías']):
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
