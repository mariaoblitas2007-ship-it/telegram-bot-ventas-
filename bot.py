import os
import asyncio
import random
import logging
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from telegram.ext import Application, MessageHandler, CallbackQueryHandler, CommandHandler, filters, ContextTypes
from telegram.error import Conflict

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
PAGARON = set()
ULTIMO_MENSAJE = {}

# ✅ PRECIOS COMPLETOS
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
🏦 *Banco:* STP
🔢 *CLABE:* `646180546711450910`
📝 *Referencia/Concepto:* `yanae`

🇲🇽 *También acepto:* Transfer / Astropay
→ *Pídeme datos si usas otro método*

Mándame captura cuando pagues bebé 🥰
En cuanto caiga te mando tu pack 🔥

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

def get_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🛍 VIDEOS - PERÚ 🇵🇪", callback_data='pe')],
        [InlineKeyboardButton("🛍 VIDEOS - MÉXICO 🇲🇽", callback_data='mx')],
        [InlineKeyboardButton("🛍 VIDEOS - USA 🇺🇸", callback_data='usa')],
        [InlineKeyboardButton("🌎 OTRO PAÍS", callback_data='otro')],
        [InlineKeyboardButton("📸 Fotitos GRATIS", callback_data='fotitos')],
        [InlineKeyboardButton("🔥 Mi Canal VIP", url=LINK_CANAL)]
    ])

def get_volver():
    return InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Volver al Menú", callback_data='volver')]])

def get_no_entiendo():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📸 Ver Fotitos GRATIS", callback_data='fotitos')],
        [InlineKeyboardButton("🛍 Ver Precios", callback_data='volver')]
    ])

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
        texto = f"🔥 *{tipo} DE COMPRA* 🔥\n\n"
        texto += f"👤 @{username}\n"
        texto += f"🆔 `{user_id}`\n"
        texto += f"💬 Mensaje: `{mensaje[:100]}`\n"
        texto += f"⏰ {datetime.now().strftime('%H:%M:%S')}\n\n"
        texto += f"Háblale rápido antes que se enfríe 🤑"
        
        await context.bot.send_message(chat_id=ADMIN_ID, text=texto, parse_mode='Markdown')
    except Exception as e:
        logger.error(f"Error avisando interés: {e}")

async def auto_tease_task(app, user_id, delay, tipo):
    await asyncio.sleep(delay)
    ahora = datetime.now()
    if user_id in PAGARON:
        return
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
        if tipo == "vip":
            await app.bot.send_message(chat_id=user_id, text="¿Otro PREMIUM? 😈", reply_markup=get_menu())
    except Exception as e:
        logger.error(f"Error en auto-tease: {e}")

async def manejar_todo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message or update.business_message
    if not message or not message.from_user or message.from_user.is_bot:
        return
        
    user = message.from_user
    user_id = user.id
    
    # ✅ NO PROCESAR TUS MENSAJES
    if user_id == ADMIN_ID:
        return
    
    username = user.username or "sin_username"
    registrar_usuario(user)
    ahora = datetime.now()

    if user_id in PAGARON:
        await message.reply_text(
            "Amor ya recibí tu pago 😘\n\n"
            f"Estoy revisando y te mando tu pack en unos minutos\n\n"
            f"Cualquier cosa háblame a {USERNAME_ADMIN} 💋",
            parse_mode='Markdown'
        )
        return

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

    if message.photo:
        PAGARON.add(user_id)
        await avisar_interes(context, user_id, username, "ENVÍO CAPTURA DE PAGO", "PAGO RECIBIDO 💰")
        
        await message.reply_text(
            f"Recibí tu captura amor 😘\n\n"
            f"✅ *PAGO EN REVISIÓN*\n"
            f"Te mando tu pack en 5-10 min\n\n"
            f"Si demora más de 20min háblame a {USERNAME_ADMIN}\n\n"
            f"*Gracias por confiar* 🔥",
            parse_mode='Markdown'
        )
        try:
            caption = f"💰 *NUEVA CAPTURA - MARCAR COMO PAGADO*\n\n👤 @{username}\n🆔 `{user_id}`\n⏰ {ahora.strftime('%H:%M:%S')}"
            await context.bot.send_photo(chat_id=ADMIN_ID, photo=message.photo[-1].file_id, caption=caption, parse_mode='Markdown')
        except Exception as e:
            logger.error(f"Error reenviando: {e}")
        return

    if not message.text:
        return

    texto = message.text.lower().strip()
    
    if ULTIMO_MENSAJE.get(user_id) == texto:
        return
    ULTIMO_MENSAJE[user_id] = texto
    
    if len(texto) < 2:
        return
        
    es_vip = user_id in VIP_TEMPORAL and VIP_TEMPORAL[user_id] > ahora
    es_demo = user_id in DEMO_HOT and DEMO_HOT[user_id] > ahora

    if es_vip or es_demo:
        tiempo_restante = (VIP_TEMPORAL[user_id] - ahora).seconds // 60 if es_vip else (DEMO_HOT[user_id] - ahora).seconds // 60

        if not es_vip and tiempo_restante <= 2:
            await message.reply_text("Ay papi se me va a acabar el tiempo 😢\n\n*Si quieres seguir caliente conmigo...*\n\nCompra *PREMIUM* y seguimos sin corte 🔥", reply_markup=get_menu(), parse_mode='Markdown')
            return

        if any(x in texto for x in ['mas tiempo', 'más tiempo', 'otro', 'renovar', 'seguir']):
            await message.reply_text("Bebé se me está acabando 😢\n\nSi quieres seguir calientito...\n*PREMIUM y seguimos* sin corte 🔥", reply_markup=get_menu(), parse_mode='Markdown')
            return

        elif es_vip and tiempo_restante <= 5:
            await message.reply_text("Ay no papi ya me voy a tener que ir 😢\n\nAprovecha rápido\n\nQué quieres que haga antes? 💋\n\n*Otro PREMIUM = seguimos más* 🔥", parse_mode='Markdown')
            return

        if any(x in texto for x in ['hola', 'ola', 'buenas', 'hey', 'wenas']):
            await message.reply_text("olaaa 😘 cómo estás weno?", parse_mode='Markdown')
            return
        elif any(x in texto for x in ['como estas', 'cómo estás', 'que tal']):
            await message.reply_text("bien mi rey 😘 gracias x preguntar Xd y tú cómo andas? 💋", parse_mode='Markdown')
            return
        elif any(x in texto for x in ['que haces', 'qué haces']):
            await message.reply_text("nada acá 🙈 pensando en ti Xd y tú?", parse_mode='Markdown')
            return
        elif any(x in texto for x in ['estas sola', 'estás sola']):
            await message.reply_text("sip solita 😈 xq?", parse_mode='Markdown')
            return
        elif any(x in texto for x in ['que tienes puesto', 'ropa', 'desnuda', 'calata']):
            await message.reply_text("mmm nada papi 😏 solo mi collar... te gusta así? o me pongo algo pa ti? 💋", parse_mode='Markdown')
            return
        elif any(x in texto for x in ['tocate', 'tócate', 'dedos', 'juega']):
            await message.reply_text("ufff ya me estoy tocando papi 💦 pensando en ti... sigo o te grabo? 😈", parse_mode='Markdown')
            return
        elif any(x in texto for x in ['muestra', 'muestrame', 'ver', 'foto', 'video']):
            await message.reply_text("mmm quieres verme? 🥵 dime EXACTO qué quieres ver y te lo hago 💦", parse_mode='Markdown')
            return
        elif any(x in texto for x in ['ganas', 'caliente', 'cachonda', 'mojada']):
            await message.reply_text("ay papi estoy que ardo 🥵 toda mojada... qué me haces? 💦", parse_mode='Markdown')
            return
        elif any(x in texto for x in ['pene', 'verga', 'pito', 'pinga']):
            await message.reply_text("uff papi me gustan los p... 😏 cómo tienes el tuyo? cuéntame 💦 Xd", parse_mode='Markdown')
            return
        elif any(x in texto for x in ['tamaño', 'grande', 'cm', 'mide']):
            await message.reply_text("mmm me gustan grandes papi 😏 cuántos cm tienes? dime y te digo si me entra 💦", parse_mode='Markdown')
            return
        elif any(x in texto for x in ['jaja', 'xd', 'jiji', 'jsjs']):
            await message.reply_text("JSKSKSSKS 😘 de q te ríes bebé?", parse_mode='Markdown')
            return
        elif any(x in texto for x in ['linda', 'bonita', 'hermosa', 'sexy', 'rica']):
            await message.reply_text("aww coshita 🥺 gracias mi rey", parse_mode='Markdown')
            return
        elif any(x in texto for x in ['gracias', 'ok', 'vale', 'bueno', 'dale']):
            await message.reply_text("de nada mi rey 😘 Xd cualquier coshita me avisas 💋", parse_mode='Markdown')
            return
        else:
            await message.reply_text(
                "No entendí bien amor 😅\n\nElige qué quieres ver:",
                reply_markup=get_menu(),
                parse_mode='Markdown'
            )
            return

    if any(x in texto for x in ['precio', 'cuanto', 'cuánto', 'vale', 'costo', 'cuesta', 'peru', 'soles', 's/']):
        await avisar_interes(context, user_id, username, texto, "PREGUNTÓ PRECIO")
        await message.reply_text(PE_PRECIOS, reply_markup=get_volver(), parse_mode='Markdown')
    elif any(x in texto for x in ['mexico', 'mxn', 'peso']):
        await avisar_interes(context, user_id, username, texto, "PREGUNTÓ PRECIO")
        await message.reply_text(MX_PRECIOS, reply_markup=get_volver(), parse_mode='Markdown')
    elif any(x in texto for x in ['usd', 'usa', 'eeuu', 'dolar', 'dólar']):
        await avisar_interes(context, user_id, username, texto, "PREGUNTÓ PRECIO")
        await message.reply_text(USA_PRECIOS, reply_markup=get_volver(), parse_mode='Markdown')
    elif any(x in texto for x in ['otro', 'internacional', 'colombia', 'argentina', 'chile', 'españa']):
        await avisar_interes(context, user_id, username, texto, "PREGUNTÓ PRECIO")
        await message.reply_text(OTRO_PRECIOS, reply_markup=get_volver(), parse_mode='Markdown', disable_web_page_preview=True)
    elif any(x in texto for x in ['comprar', 'compra', 'pagar', 'pago', 'quiero', 'dame']):
        await avisar_interes(context, user_id, username, texto, "QUIERE COMPRAR 🤑")
        await message.reply_text(
            "Sii bebé 😘 Elige tu país para ver precios:",
            reply_markup=get_menu(),
            parse_mode='Markdown'
        )
    elif any(x in texto for x in ['gratis', 'free', 'muestra', 'regalo', 'fotitos']):
        await message.reply_text(f"🎁 *FOTITOS GRATIS* 🔥\n\nToca el botón para verlas bebé:\n\n👉 Si te gustan, *ayúdame compartiendo* con tus amigos 🥺💋\n\n*Si quieres algo más hot...*\nCompra PREMIUM y te doy atención 1 a 1 😈", reply_markup=get_no_entiendo(), parse_mode='Markdown')
    else:
        await message.reply_text(
            "No entendí amor 😅\n\nElige una opción:",
            reply_markup=get_menu(),
            parse_mode='Markdown'
        )

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    user_id = query.from_user.id
    username = query.from_user.username or "sin_username"
    
    if data in ['pe', 'mx', 'usa', 'otro']:
        await avisar_interes(context, user_id, username, f"Tocó botón: {data.upper()}", "VIO PRECIOS 👀")
    
    if data == 'pe':
        await query.edit_message_text(PE_PRECIOS, reply_markup=get_volver(), parse_mode='Markdown')
    elif data == 'mx':
        await query.edit_message_text(MX_PRECIOS, reply_markup=get_volver(), parse_mode='Markdown')
    elif data == 'usa':
        await query.edit_message_text(USA_PRECIOS, reply_markup=get_volver(), parse_mode='Markdown')
    elif data == 'otro':
        await query.edit_message_text(OTRO_PRECIOS, reply_markup=get_volver(), parse_mode='Markdown', disable_web_page_preview=True)
    
    elif data == 'fotitos':
        try:
            await query.delete_message()
            
            fotos_enviadas = []
            for i in range(1, 7):
                try:
                    fotos_enviadas.append(InputMediaPhoto(open(f'fotitos{i}.JPG', 'rb')))
                except FileNotFoundError:
                    logger.warning(f"No encontré fotitos{i}.JPG")
            
            if fotos_enviadas:
                for i in range(0, len(fotos_enviadas), 3):
                    await context.bot.send_media_group(
                        chat_id=query.from_user.id, 
                        media=fotos_enviadas[i:i+3]
                    )
            
            await context.bot.send_message(
                chat_id=query.from_user.id,
                text=f"""📸 *TUS FOTITOS GRATIS BEBÉ* 🥺💋

¿Te gustaron? 😏

✨ *QUIERES HASTA 20 VIDEITOS GRATIS?* ✨
*Es por promocionarme en TikTok* ✅

*Pasitos súper fáciles uwu:*
1️⃣ Ponte un nombrecito + fotito tierna <33
2️⃣ En tu bio pon: *Tg: yanabicitasa* ✨
3️⃣ Sube una fotito a tu story + frasita hot 😋
4️⃣ Comenta coshitas en videos hot, unos 30-100 👀
   *Así generamos vistas juntos*
5️⃣ Mándame captura + videito cuando termines
6️⃣ *Disfruta tus 20 videitos* :3 ❤️‍🔥

*¿Te animas o ño?* 🥺
(Me avisas cuando cumplas mi rey)""",
                parse_mode='Markdown',
                disable_web_page_preview=True,
                reply_markup=get_menu()
            )
        except Exception as e:
            logger.error(f"Error enviando fotitos: {e}")
            await context.bot.send_message(
                chat_id=query.from_user.id,
                text="Ay bebé hubo un error enviando las fotitos 😢\n\nMejor entra directo a mi canal 👉 " + LINK_REGALITOS,
                reply_markup=get_volver()
            )
    
    elif data == 'volver':
        await query.edit_message_text("Elige tu país para ver precios bebé:", reply_markup=get_menu(), parse_mode='Markdown')

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
    asyncio.create_task(auto_tease_task(context.application, user_id, 600, "vip"))
    await context.bot.send_message(user_id, "✅ *VIP ACTIVADO* 😈\n\nTienes *15 minutos* conmigo bebé\n\nHáblame rico 🔥")
    await update.message.reply_text(f"✅ VIP activado para {user_id}")

async def usuarios(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id!= ADMIN_ID:
        return

    if not USUARIOS:
        await update.message.reply_text("Aún no habla nadie con el bot 😢")
        return

    texto = "📊 *USUARIOS QUE HABLARON CON EL BOT*\n\n"
    for user_id, datos in list(USUARIOS.items())[-20:]:
        estado = "💰 PAGÓ" if user_id in PAGARON else "🔥 VIP" if datos['es_vip'] else "💦 DEMO" if datos['demo_usada'] else "👀 Nuevo"
        texto += f"*{datos['nombre']}* @{datos['username']}\n"
        texto += f"ID: `{user_id}` | {estado}\n"
        texto += f"Último: {datos['ultimo_mensaje']}\n\n"

    texto += f"\n*Total: {len(USUARIOS)} usuarios | Pagaron: {len(PAGARON)}*"
    await update.message.reply_text(texto, parse_mode='Markdown')

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Exception: {context.error}", exc_info=context.error)

def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(MessageHandler(filters.ALL, manejar_todo))
    app.add_handler(CallbackQueryHandler(button))
    app.add_handler(CommandHandler("vip", vip))
    app.add_handler(CommandHandler("usuarios", usuarios))
    app.add_error_handler(error_handler)
    
    logger.info("BOT PRENDIDO - AVISOS DE VENTA ACTIVOS ✅")
    
    try:
        app.run_polling(drop_pending_updates=True, allowed_updates=Update.ALL_TYPES)
    except Conflict:
        logger.error("Hay otra instancia corriendo. Cerrando esta...")
        os._exit(1)

if __name__ == '__main__':
    main()
