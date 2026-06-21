import os
import sys
import asyncio
import random
import logging
import re
import signal
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
VIO_PRECIOS = {}
FOLLOWUP_ENVIADO = set()
ULTIMA_RESPUESTA = {}

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
📝 *Referencia:* `yanae`

Mándame captura cuando pagues bebé 🥰
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

Avísame cuando envíes con el comprobante 🥰
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
        texto = f"🔥 *{tipo} DE COMPRA* 🔥\n\n👤 @{username_safe}\n🆔 `{user_id}`\n💬 Mensaje: `{mensaje_safe}`\n⏰ {datetime.now().strftime('%H:%M:%S')}\n\nHáblale rápido antes que se enfríe 🤑"
        await context.bot.send_message(chat_id=ADMIN_ID, text=texto, parse_mode='Markdown')
    except:
        pass

async def follow_up_task(app, user_id, username):
    await asyncio.sleep(1800)
    if user_id in PAGARON or user_id in FOLLOWUP_ENVIADO:
        return
    FOLLOWUP_ENVIADO.add(user_id)
    mensajes = [
        f"oye {username} 😢 sigues ahí? Si compras TOP te regalo 2 videitos extra 🔥",
        f"papi 👉👈 con PREMIUM te agrego 3 fotitos exclusivas que no subo a ningún lado 💋",
        f"amor 🥺 te espero... compra TOP y te mando videito haciendo lo que pidas 😈"
    ]
    try:
        await app.bot.send_message(chat_id=user_id, text=random.choice(mensajes), reply_markup=get_menu(), parse_mode='Markdown')
    except:
        pass

def respuesta_hot(texto, nombre, user_id):
    texto = texto.lower()

    def no_repetir(opciones):
        ultima = ULTIMA_RESPUESTA.get(user_id, "")
        opciones_filtradas = [r for r in opciones if r!= ultima]
        if not opciones_filtradas:
            opciones_filtradas = opciones
        respuesta = random.choice(opciones_filtradas)
        ULTIMA_RESPUESTA[user_id] = respuesta
        return respuesta

    if any(x in texto for x in ['hola', 'ola', 'buenas', 'hey', 'wenas', 'alo', 'q tal', 'que tal']):
        return no_repetir([
            f"Olaaa {nombre} 😘 cómo estás bebé? 💋",
            f"Hey {nombre} 🔥 llegaste justo cuando pensaba en ti... qué haces? 😏",
            f"Holaa mi rey 🙈 qué tal tu día? Yo acá calata pensando en ti Xd 💦",
            f"Wenaas {nombre} 😈 andaba aburrida sin ti... qué me cuentas? 🔥"
        ])

    if any(x in texto for x in ['que haces', 'qué haces', 'q haces', 'haciendo']):
        return no_repetir([
            f"Acá {nombre} 🙈 pensando en qué haríamos si estuvieras aquí... y tú? 😏",
            f"Nada, aburrida sin ti 🥺 tú qué haces mi rey? 💋",
            f"Me estaba tocando y pensé en ti 🙊 jksjks tú qué cuentas? 🔥",
            f"Acá solita 😈 esperándote... qué tienes ganas de hacer? 💦"
        ])

    if any(x in texto for x in ['sola', 'solo', 'solita', 'acompañada']):
        return no_repetir([
            f"Sí bebé solita 😈 por qué? Qué tienes en mente? 💦",
            f"Solísima {nombre}... la cama está fría sin ti 🛏️🥺",
            f"Sip, toda la casa para nosotros 🙊 vienes o qué? 🔥",
            f"Sola y caliente {nombre} 🥵 tú me acompañas? 💋"
        ])

    if any(x in texto for x in ['ropa', 'desnuda', 'calata', 'vestida', 'llevas', 'puesto', 'tanga', 'hilo']):
        return no_repetir([
            f"Mmm solo un hilito bebé 😏 te lo quito o quieres que me ponga algo? 💋",
            f"Nada {nombre} 🙈 estoy como Dios me trajo al mundo... te gusta? 🔥",
            f"Una tanga nomás 🍑 me la saco para ti? 😈",
            f"Sin nada {nombre} 💦 toda lista para ti... qué me haces? 🥵"
        ])

    if any(x in texto for x in ['tocate', 'tócate', 'dedos', 'juega', 'mastur', 'toca', 'mete']):
        return no_repetir([
            f"Ufff ya empecé {nombre} 💦 estoy mojándome toda... sigo? 😈",
            f"Ay papi sí 🙈 *se toca* Mmm se siente rico... quieres ver? 🔥",
            f"Ya estoy {nombre} 🥵 pensando en tu boca... te grabo un videito? 💋",
            f"Sí bebé 💦 *mete dedos* ahh... te gusta? Sigo o paro? 😈"
        ])

    if any(x in texto for x in ['muestra', 'muestrame', 'ver', 'foto', 'video', 'enseña', 'ensena', 'manda']):
        return no_repetir([
            f"Mmm picoso 😏 dime QUÉ parte quieres ver y te lo mando ahora 💦",
            f"Todo lo que quieras bebé 🔥 pero dime específico... ¿teta, poto, qué? 😈",
            f"Uy {nombre} 🥵 si me dices qué quieres ver te hago video ahora mismo 💋",
            f"Claro papi 😈 pero tienes que decirme exacto... tetas? culo? toda? 🔥"
        ])

    if any(x in texto for x in ['ganas', 'caliente', 'cachonda', 'mojada', 'excitad', 'ardiendo', 'rico']):
        return no_repetir([
            f"Demasiado {nombre} 🥵 estoy que ardo... ven a apagarme 🔥",
            f"Ay sí 💦 toda mojada por tu culpa... qué me vas a hacer? 😈",
            f"Demasiadas ganas 🙈 si estuvieras aquí ya te habría saltado encima 💋",
            f"Ufff bebé 🔥 no aguanto más... me toco pensando en ti 💦"
        ])

    if any(x in texto for x in ['pene', 'verga', 'pito', 'pinga', 'verg', 'pit0', 'nepe', 'pija']):
        return no_repetir([
            f"Ufff me encantan 😏 cuéntame del tuyo bebé... cómo lo tienes? 💦",
            f"Mmm me gustan venosos {nombre} 🥵 el tuyo cómo es? mándame foto 🙈",
            f"Ay sí 🔥 me fascinan... el tuyo es grande? Dime cm 😈",
            f"Me vuelven loca {nombre} 💋 el tuyo cómo es? Grueso? 😏"
        ])

    if any(x in texto for x in ['tamaño', 'grande', 'cm', 'mide', 'cuanto', 'cuánto', 'centimetros']):
        return no_repetir([
            f"Me gustan de +16cm bebé 😏 el tuyo cuánto mide? Si me gusta te premio 💦",
            f"Mmm mientras me llene estoy feliz 🙈 el tuyo me entraría? Dime 🔥",
            f"Grandes {nombre} 🥵 pero con técnica... el tuyo cómo es? 😈",
            f"De 17 pa arriba me encantan 💋 el tuyo cuánto? Mándame foto 🙈"
        ])

    if any(x in texto for x in ['amor', 'amo', 'quiero', 'novia', 'enamore', 'enamoré', 'te amo', 'bebe']):
        return no_repetir([
            f"Aww {nombre} 🥺 yo también... pero mi novio tiene que ser PREMIUM jiji 💋",
            f"Jiji me sonrojas 😳 demuéstrame que me quieres con el PREMIUM 🔥",
            f"Ay bebé 🥰 eres un amor... pero amor con amor se paga Xd PREMIUM? 💦",
            f"Tú también me gustas {nombre} 😏 pero los novios pagan PREMIUM 🙈"
        ])

    if any(x in texto for x in ['gracias', 'ok', 'vale', 'bueno', 'dale', 'listo', 'perfecto', 'grax', 'oka']):
        return no_repetir([
            f"De nada {nombre} 😘 Xd cualquier cosita caliente me avisas 💋",
            f"Para ti siempre bebé 🔥 tú solo pide 💦",
            f"Ok mi rey 😏 pero no te desaparezcas eh... 🥺",
            f"Vale {nombre} 😈 acá te espero calientita 🔥"
        ])

    if any(x in texto for x in ['jaja', 'xd', 'jiji', 'jsjs', 'jjjj', 'lol', 'ksk', 'jaj', 'jeje']):
        return no_repetir([
            f"JSKSKSSKS 😘 de q te ríes {nombre}? Cuéntame 🔥",
            f"Jiji te dio risa? 🙈 dime por qué 💦",
            f"Jajaja me haces reír bebé 😂 eres tierno 😈",
            f"Jsjsjs {nombre} 😏 me encanta tu risa... qué te causó? 💋"
        ])

    if any(x in texto for x in ['adios', 'adiós', 'chao', 'chau', 'bye', 'nos vemos', 'hasta luego', 'me voy', 'bay']):
        return no_repetir([
            f"Ya te vas {nombre}? 😢 vuelve pronto mi rey 💋",
            f"Chao bebé 😘 me avisas cuando quieras más uwu 🔥",
            f"Adiós papi 🥺 te voy a extrañar... si cambias de opinión aquí estoy 💦",
            f"Bye {nombre} 😘 cuídate mucho Xd y vuelve caliente 😈"
        ])

    if any(x in texto for x in ['linda', 'bonita', 'hermosa', 'sexy', 'rica', 'preciosa', 'guapa', 'bella', 'chula', 'hot', 'diosa']):
        return no_repetir([
            f"Aww {nombre} 🥺 gracias mi rey... tú también estás bien bueno 😏💋",
            f"Jiji me sonrojas 🙈 tú también bebé... qué me harías? 🔥",
            f"Gracias papi 😘 por eso me gustas... eres diferente 💦",
            f"Ay {nombre} 😈 si supieras lo que pienso hacerte... 🙈"
        ])

    return no_repetir([
        f"Mmm {nombre} 😏 y si mejor me dices qué quieres que te haga? 🔥",
        f"Jiji me distraes bebé 🙈 háblame rico o dime qué ver 💦",
        f"Ay {nombre} 🥵 estoy caliente... dime algo hot o te muestro algo? 😈",
        f"Bebé 💋 estoy esperando que me digas qué hacer... te toco? te grabo? 🔥",
        f"Uff {nombre} 😏 me pones nerviosa... dime qué tienes ganas de hacer 💦",
        f"Mmm 🙈 no entendí bien pero me gustas... háblame más rico 😈"
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
        await message.reply_text(f"Amor ya recibí tu pago 😘\n\n✅ *PAGO CONFIRMADO*\n\n📩 *HÁBLAME A MI PRIVADO YA*\n👉 {USERNAME_ADMIN}\n\nAhí te mando tu pack completo sin demora 💋", parse_mode='Markdown')
        return

    if message.text and message.text.lower() == '/start':
        es_nuevo = user_id not in DEMO_USADO
        if es_nuevo:
            DEMO_USADO.add(user_id)
            DEMO_HOT[user_id] = datetime.now() + timedelta(minutes=10)
            saludo = f"olaaa {nombre} 😘 Bienvenido a *YANABICITASA*\n\ntengo *18 añitos* y ando bien caliente 🔥\n\n*Te regalo 10 min de chat hot conmigo*\nes tu única vez gratis, aprovecha 💦"
            await message.reply_text(saludo, parse_mode='Markdown')
        else:
            await message.reply_text(f"ola de nuevo {nombre} 😘 ya tienes tu demo usada Xd\n\npero puedes comprar *PREMIUM* y seguimos 💋", parse_mode='Markdown')
        await message.reply_text("Elige tu país para ver precios bebé:", reply_markup=get_menu(), parse_mode='Markdown')
        return

    if message.photo:
        PAGARON.add(user_id)
        await avisar_interes(context, user_id, username, "ENVÍO CAPTURA DE PAGO", "PAGO RECIBIDO 💰")
        await message.reply_text(
            f"✅ *PAGO RECIBIDO MI REY* 😘\n\n"
            f"Ya vi tu captura {nombre} 🔥\n\n"
            f"📩 *AHORA HÁBLAME A MI PRIVADO*\n"
            f"👉 {USERNAME_ADMIN}\n\n"
            f"Ahí te mando tu pack completo sin demora 💋\n\n"
            f"*No lo mando por aquí por seguridad* 🥺",
            parse_mode='Markdown'
        )
        try:
            caption = f"💰 *NUEVA CAPTURA - PAGO CONFIRMADO*\n\n👤 @{username}\n🆔 `{user_id}`\n⏰ {ahora.strftime('%H:%M:%S')}\n\n*El cliente ya fue enviado a tu privado* ✅"
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

    if any(x in texto.lower() for x in ['comprar', 'compro', 'quiero', 'dame', 'pago', 'pagare', 'pagaré', 'yape', 'paypal', 'transfer']):
        await avisar_interes(context, user_id, username, texto, "QUIERE COMPRAR YA 🤑")
        await message.reply_text(f"Sii {nombre} 😘 Elige tu país para ver precios:", reply_markup=get_menu(), parse_mode='Markdown')
        return

    if any(x in texto.lower() for x in ['precio', 'cuanto', 'cuánto', 'vale', 'costo', 'cuesta', 'peru', 'soles', 's/', 'sol']):
        await avisar_interes(context, user_id, username, texto, "PREGUNTÓ PRECIO")
        VIO_PRECIOS[user_id] = datetime.now()
        asyncio.create_task(follow_up_task(context.application, user_id, username))
        await message.reply_text(PE_PRECIOS, reply_markup=get_volver(), parse_mode='Markdown')
        return
    elif any(x in texto.lower() for x in ['mexico', 'mxn', 'peso', 'méxico']):
        await avisar_interes(context, user_id, username, texto, "PREGUNTÓ PRECIO")
        VIO_PRECIOS[user_id] = datetime.now()
        asyncio.create_task(follow_up_task(context.application, user_id, username))
        await message.reply_text(MX_PRECIOS, reply_markup=get_volver(), parse_mode='Markdown')
        return
    elif any(x in texto.lower() for x in ['usd', 'usa', 'eeuu', 'dolar', 'dólar', 'estados unidos']):
        await avisar_interes(context, user_id, username, texto, "PREGUNTÓ PRECIO")
        VIO_PRECIOS[user_id] = datetime.now()
        asyncio.create_task(follow_up_task(context.application, user_id, username))
        await message.reply_text(USA_PRECIOS, reply_markup=get_volver(), parse_mode='Markdown')
        return
    elif any(x in texto.lower() for x in ['otro', 'internacional', 'colombia', 'argentina', 'chile', 'españa', 'venezuela']):
        await avisar_interes(context, user_id, username, texto, "PREGUNTÓ PRECIO")
        VIO_PRECIOS[user_id] = datetime.now()
        asyncio.create_task(follow_up_task(context.application, user_id, username))
        await message.reply_text(OTRO_PRECIOS, reply_markup=get_volver(), parse_mode='Markdown', disable_web_page_preview=True)
        return

    if any(x in texto.lower() for x in ['intercambio', 'trueque', 'canje']):
        await avisar_interes(context, user_id, username, texto, "QUIERE INTERCAMBIO 👀")
        await message.reply_text(f"Bebé yo no cambio 😅 solo vendo\n\nPero si compras *PREMIUM* te doy 20 videos + 1 personalizado 🔥\n\nEs mejor que un intercambio Xd", reply_markup=get_menu(), parse_mode='Markdown')
        return

    if any(x in texto.lower() for x in ['gratis', 'regalo', 'muestra', 'demo', 'calame']):
        await message.reply_text(f"🎁 *FOTITOS GRATIS* 🔥\n\nToca el botón para verlas bebé:\n\n👉 Si te gustan, *ayúdame compartiendo* con tus amigos 🥺💋\n\n*Si quieres algo más hot...*\nCompra PREMIUM y te doy atención 1 a 1 😈", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("📸 Ver Fotitos GRATIS", callback_data='fotitos')], [InlineKeyboardButton("🛍 Ver Precios", callback_data='volver')]]), parse_mode='Markdown')
        return

    es_vip = user_id in VIP_TEMPORAL and VIP_TEMPORAL[user_id] > ahora
    es_demo = user_id in DEMO_HOT and DEMO_HOT[user_id] > ahora

    if es_demo or es_vip:
        tiempo_restante = (VIP_TEMPORAL[user_id] - ahora).seconds // 60 if es_vip else (DEMO_HOT[user_id] - ahora).seconds // 60
        if not es_vip and tiempo_restante <= 2:
            await message.reply_text(f"Ay {nombre} se nos acaba el tiempo 😢\n\n*Mándame PREMIUM ahora* y seguimos sin corte bebé 🔥", reply_markup=get_menu(), parse_mode='Markdown')
            return
        if es_vip and tiempo_restante <= 5:
            await message.reply_text(f"Papi {tiempo_restante} min y me tengo que ir 😢\n\nQué quieres que haga antes de irme? 🥵\n\n*Otro PREMIUM = me quedo más tiempo* 💋", parse_mode='Markdown')
            return

    respuesta = respuesta_hot(texto, nombre, user_id)
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
    elif data == 'fotitos':
        try:
            await query.answer("Cargando fotitos... 🔥")
            await query.delete_message()

            ruta_base = os.path.dirname(os.path.abspath(__file__))
            fotos_cargadas = []

            caption_tiktok = """📸 *TUS FOTITOS GRATIS BEBÉ* 🥺💋

¿Te gustaron? 😏

✨ *QUIERES HASTA 20 VIDEITOS GRATIS?* ✨
*Es por promocionarme en TikTok* ✅

*Pasitos súper fáciles uwu:*
1️⃣ Ponte un nombrecito + fotito tierna <33
2️⃣ En tu bio pon: *Tg: yanabicitasa* ✨
3️⃣ Sube una fotito a tu story + frasita hot 😋
4️⃣ Comenta coshitas en videos hot, unos 30-100 👀
5️⃣ Mándame captura + videito cuando termines
6️⃣ *Disfruta tus 20 videitos* :3 ❤️‍🔥

*¿Te animas o ño?* 🥺"""

            for i in range(1, 7):
                nombre_archivo = f'fotitos{i}.JPG'
                ruta_completa = os.path.join(ruta_base, nombre_archivo)

                if os.path.isfile(ruta_completa):
                    try:
                        with open(ruta_completa, 'rb') as foto:
                            if i == 1:
                                fotos_cargadas.append(InputMediaPhoto(
                                    media=foto.read(),
                                    caption=caption_tiktok,
                                    parse_mode='Markdown'
                                ))
                            else:
                                fotos_cargadas.append(InputMediaPhoto(media=foto.read()))
                    except Exception as e:
                        logger.error(f"Error foto {i}: {e}")

            if fotos_cargadas:
                await context.bot.send_media_group(
                    chat_id=query.from_user.id,
                    media=fotos_cargadas
                )
                await context.bot.send_message(
                    chat_id=query.from_user.id,
                    text="Elige qué quieres ahora bebé 🔥",
                    reply_markup=get_menu()
                )
            else:
                await context.bot.send_message(
                    chat_id=query.from_user.id,
                    text=f"📸 *FOTITOS GRATIS BEBÉ* 🥺💋\n\n"
                         f"Ay bebé, estoy subiendo fotitos nuevas Xd\n\n"
                         f"*Mientras entra a mi canal:* {LINK_REGALITOS}\n\n"
                         f"✨ *O GANA 20 VIDEITOS GRATIS* ✨\n"
                         f"Promocionándome en TikTok 🥺",
                    parse_mode='Markdown',
                    disable_web_page_preview=True,
                    reply_markup=get_menu()
                )

        except Exception as e:
            logger.error(f"ERROR FOTITOS: {e}")
            try:
                await context.bot.send_message(
                    chat_id=query.from_user.id,
                    text=f"Ups bebé 😢 Error cargando fotos\n\nMejor entra a mi canal 👉 {LINK_REGALITOS}",
                    reply_markup=get_volver()
                )
            except:
                pass
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
    await context.bot.send_message(user_id, "✅ *VIP ACTIVADO* 😈\n\nTienes *15 minutos* conmigo bebé\n\nHáblame rico 🔥")
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
    logger.info("BOT PRENDIDO - MODO HOT 24/7 ACTIVO ✅")
    app.run_polling(drop_pending_updates=True)

if __name__ == '__main__':
    main()
