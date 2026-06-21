import os
import asyncio
import random
import logging
import re
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from telegram.ext import Application, MessageHandler, CallbackQueryHandler, CommandHandler, filters, ContextTypes
from telegram.error import Conflict

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
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

# ✅ DICCIONARIO CALLEJERO COMPLETO
SINONIMOS = {
    'intercambio': ['cambiamos', 'cambias', 'cambio', 'intercambio', 'trueque', 'trueke', 'canje', 'canjeamos', 'inter', 'cambio x cambio'],
    'gratis': ['regalitos', 'regalo', 'muestra', 'muestras', 'gratis', 'free', 'preview', 'adelanto', 'probadita', 'demo', 'sample', 'calame', 'calis'],
    'comprar': ['comprar', 'compro', 'quiero', 'dame', 'pago', 'pagare', 'pagaré', 'yapeo', 'transferencia', 'paypal', 'adquirir', 'llevar', 'deseo'],
    'caro': ['caro', 'mucho', 'rebaja', 'descuento', 'promo', 'barato', 'menos', 'negociar', 'regatear', 'oferta'],
    'pack': ['pack', 'pak', 'paquete', 'contenido', 'videos', 'fotos', 'material', 'cont'],
    'referencias': ['refe', 'referencias', 'referencia', 'refs', 'confiable', 'real', 'seguro', 'estafa', 'legit', 'verdad']
}

# ✅ DICCIONARIO DE EMOJIS - ENTIENDE SIN PALABRAS
EMOJIS_CALIENTES = {
    'hot': ['🥵', '🔥', '😈', '👿', '😏', '🤤', '🥴'],
    'mojada': ['💦', '💧', '🌊', '💨'],
    'pene': ['🍆', '🍌', '🌭', '🥒', '🎤', '📏'],
    'cola': ['🍑', '🍩', '🎂'],
    'senos': ['🍒', '🍈', '🍉', '🥥', '🍊'],
    'sexo': ['🔞', '💋', '👅', '🫦', '🛏️', '🚿', '👉👌', '🤰'],
    'amor': ['❤️', '💕', '💖', '💘', '😍', '🥰', '😘', '💗', '💝'],
    'triste': ['😢', '😭', '🥺', '😔', '💔', '😿', '☹️'],
    'risa': ['😂', '🤣', '😹', 'XD', 'jaja', 'jsjs'],
    'dinero': ['💰', '💵', '💸', '🤑', '💳']
}

PALABRAS_HOT = ['barato', 'descuento', 'promo', 'rebaja', 'oferta', 'caro', 'mucho', 'menos', 'cuotas', 'plazos', 'duda', 'seguro', 'confiable', 'referencias', 'real', 'estafa']
PALABRAS_COMPRA = ['comprar', 'compro', 'quiero', 'dame', 'pago', 'pagare', 'pagaré', 'yape', 'yapeo', 'transferencia', 'paypal']

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

def entender_mensaje(texto):
    texto = texto.lower()
    intenciones = []
    for intencion, palabras in SINONIMOS.items():
        if any(palabra in texto for palabra in palabras):
            intenciones.append(intencion)
    return intenciones

def entender_emojis(texto):
    intenciones = []
    for intencion, emojis in EMOJIS_CALIENTES.items():
        if any(emoji in texto for emoji in emojis):
            intenciones.append(intencion)
    return intenciones

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

async def follow_up_task(app, user_id, username):
    await asyncio.sleep(1800)
    if user_id in PAGARON or user_id in FOLLOWUP_ENVIADO:
        return
    FOLLOWUP_ENVIADO.add(user_id)
    mensajes_followup = [
        "oye bebé 😢 sigues ahí? Si compras el TOP te regalo 2 videitos extra solo para ti 🔥",
        "papi 👉👈 no te vayas... si llevas PREMIUM te agrego 3 fotitos exclusivas que no subo a ningún lado 💋",
        "amor 🥺 te espero... compra el TOP y te mando un videito extra haciendo lo que me pidas 😈",
        "bebé 😘 con PREMIUM te doy acceso a mi canal VIP 24 horas gratis 🎁"
    ]
    try:
        await app.bot.send_message(chat_id=user_id, text=random.choice(mensajes_followup), reply_markup=get_menu(), parse_mode='Markdown')
        await app.bot.send_message(chat_id=ADMIN_ID, text=f"🎁 *FOLLOW UP CON EXTRAS ENVIADO* 🎁\n\n👤 @{username}\n🆔 `{user_id}`\n\nLe ofrecí extras visuales. Ciérralo tú 🤑", parse_mode='Markdown')
    except Exception as e:
        logger.error(f"Error en follow up: {e}")

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
    teases = ["oye... Xd no dejo de pensar en ti 😳", "papi me distraje en clase x tu culpa 😈 JSKSKS", "toy aburrida... qué haces? 💦 uwu", "me puse a verme al espejo y... 🙈 JSKSKSSKS", "tengo calor 😰 o eres tú? uwu"]
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
    if user_id == ADMIN_ID:
        return
    username = user.username or "sin_username"
    registrar_usuario(user)
    ahora = datetime.now()

    if user_id in PAGARON:
        await message.reply_text("Amor ya recibí tu pago 😘\n\nEstoy revisando y te mando tu pack en unos minutos\n\nCualquier cosa háblame a @yanabicitasa 💋", parse_mode='Markdown')
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
        await message.reply_text(f"Recibí tu captura amor 😘\n\n✅ *PAGO EN REVISIÓN*\nTe mando tu pack en 5-10 min\n\nSi demora más de 20min háblame a {USERNAME_ADMIN}\n\n*Gracias por confiar* 🔥", parse_mode='Markdown')
        try:
            caption = f"💰 *NUEVA CAPTURA - MARCAR COMO PAGADO*\n\n👤 @{username}\n🆔 `{user_id}`\n⏰ {ahora.strftime('%H:%M:%S')}"
            await context.bot.send_photo(chat_id=ADMIN_ID, photo=message.photo[-1].file_id, caption=caption, parse_mode='Markdown')
        except Exception as e:
            logger.error(f"Error reenviando: {e}")
        return

    if not message.text:
        return

    texto = message.text.strip()
    texto_lower = texto.lower()

    if ULTIMO_MENSAJE.get(user_id) == texto_lower:
        return
    ULTIMO_MENSAJE[user_id] = texto_lower

    if len(texto_lower) < 2 and not any(e in texto for e in ['😂','🥵','💦','🍆','🍑','🍒','❤️','🥺','😭','?']):
        return

    # ✅ DETECTOR DE INTENCIONES CALLEJERO + EMOJIS
    intenciones = entender_mensaje(texto_lower)
    intenciones_emojis = entender_emojis(texto)

    # ✅ RESPONDE A EMOJIS CALIENTES PRIMERO
    if 'hot' in intenciones_emojis:
        await message.reply_text("ufff bebé 🥵 estás caliente? Yo también... qué quieres ver? 💦", parse_mode='Markdown')
        await message.reply_text("Elige qué te calienta más:", reply_markup=get_menu(), parse_mode='Markdown')
        return
    if 'mojada' in intenciones_emojis:
        await message.reply_text("ay papi 💦 toda mojada por tu culpa... qué me haces? 😈", parse_mode='Markdown')
        return
    if 'pene' in intenciones_emojis:
        await message.reply_text("mmm 🍆 me gustan grandes bebé 😏 cuántos cm tienes? 💦", parse_mode='Markdown')
        return
    if 'cola' in intenciones_emojis:
        await message.reply_text("te gusta mi 🍑 bebé? 😏 compra PREMIUM y te mando videito moviéndola 🔥", parse_mode='Markdown')
        return
    if 'senos' in intenciones_emojis:
        await message.reply_text("quieres ver mis 🍒? 😈 TOP te da 12 videos... ahí salen 💋", reply_markup=get_menu(), parse_mode='Markdown')
        return
    if 'sexo' in intenciones_emojis:
        await message.reply_text("ay bebé 🔞 quieres algo más hot? Videollamada PREMIUM y hacemos lo que quieras 💦", parse_mode='Markdown')
        return
    if 'amor' in intenciones_emojis:
        respuestas_amor = ["aww coshita 🥺 yo también te quiero... compra PREMIUM y somos novios virtuales 💋", "jiji me haces sonrojar 😳 si me quieres de verdad demuéstralo con el PREMIUM 🔥", "ay bebé 🥰 eres un amor... pero mi novio tiene que ser PREMIUM Xd 💦"]
        await message.reply_text(random.choice(respuestas_amor), parse_mode='Markdown')
        return
    if 'triste' in intenciones_emojis:
        await message.reply_text("por qué triste bebé? 😢 ven, yo te alegro... compra PREMIUM y te mimo 💋", parse_mode='Markdown')
        return
    if 'dinero' in intenciones_emojis:
        await message.reply_text("hablando de 💰 bebé? Elige tu país y te paso precios 😏", reply_markup=get_menu(), parse_mode='Markdown')
        return

    # ✅ SALUDOS PARA TODOS
    if any(x in texto_lower for x in ['hola', 'ola', 'buenas', 'hey', 'wenas', 'buenos dias', 'buenas tardes', 'buenas noches', 'q tal', 'que tal', 'qué tal', 'alo']):
        await message.reply_text("olaaa bebé 😘 cómo estás? 💋", parse_mode='Markdown')
        await asyncio.sleep(1)
        await message.reply_text("Elige tu país para ver precios:", reply_markup=get_menu(), parse_mode='Markdown')
        return
    elif any(x in texto_lower for x in ['como estas', 'cómo estás', 'como andas', 'cómo andas']):
        await message.reply_text("bien mi rey 😘 gracias x preguntar uwu y tú? 💋", parse_mode='Markdown')
        return
    elif any(x in texto_lower for x in ['gracias', 'ok', 'vale', 'bueno', 'dale', 'listo', 'perfecto', 'grax']):
        await message.reply_text("de nada mi rey 😘 Xd cualquier coshita me avisas 💋", parse_mode='Markdown')
        return
    elif any(x in texto_lower for x in ['jaja', 'xd', 'jiji', 'jsjs', 'jjjj', 'lol', 'ksk']):
        await message.reply_text("JSKSKSSKS 😘 de q te ríes bebé?", parse_mode='Markdown')
        return
    elif any(x in texto_lower for x in ['adios', 'adiós', 'chao', 'chau', 'bye', 'nos vemos', 'hasta luego', 'me voy', 'bay']):
        despedidas = ["ya te vas? 😢 vuelve pronto mi rey 💋", "chao bebé 😘 me avisas cuando quieras más uwu", "adiós papi 🥺 te voy a extrañar... si cambias de opinión aquí estoy 🔥", "bye mi rey 😘 cuídate mucho Xd"]
        await message.reply_text(random.choice(despedidas), parse_mode='Markdown')
        return
    elif any(x in texto_lower for x in ['linda', 'bonita', 'hermosa', 'sexy', 'rica', 'preciosa', 'guapa', 'bella', 'chula']):
        await message.reply_text("aww coshita 🥺 gracias mi rey... tú también estás bien bueno 😏💋", parse_mode='Markdown')
        return
    elif any(x in texto_lower for x in ['eres hombre', 'eres chico', 'eres vato', 'eres wey', 'eres men', 'eres gay', 'voz de hombre', 'travesti']):
        await message.reply_text("jajaja nooo bebé 😂 soy chica, tengo 18 añitos 💋 mira mis fotos Xd", parse_mode='Markdown')
        return
    elif any(x in texto_lower for x in ['eres real', 'eres bot', 'eres ia', 'robot', 'fake']):
        await message.reply_text("claro que soy real papi 😏 de carne y hueso... quieres videollamada y te muestro? 🔥", parse_mode='Markdown')
        return
    elif any(x in texto_lower for x in ['tu edad', 'cuantos años', 'cuántos años tienes', 'edad']):
        await message.reply_text("tengo 18 añitos recién cumplidos bebé 😘 por eso ando bien loquita 🔥", parse_mode='Markdown')
        return
    elif any(x in texto_lower for x in ['de donde eres', 'dónde vives', 'donde vives', 'país']):
        await message.reply_text("de Perú bebé 🇵🇪 pero atiendo a todo el mundo uwu 💋", parse_mode='Markdown')
        return
    elif any(x in texto_lower for x in ['te amo', 'te quiero', 'enamoré', 'enamore', 'novia', 'mi amor']):
        respuestas_amor = ["aww coshita 🥺 yo también te quiero... compra PREMIUM y somos novios virtuales 💋", "jiji me haces sonrojar 😳 si me quieres de verdad demuéstralo con el PREMIUM 🔥", "ay bebé 🥰 eres un amor... pero mi novio tiene que ser PREMIUM Xd 💦"]
        await message.reply_text(random.choice(respuestas_amor), parse_mode='Markdown')
        return
    elif any(x in texto_lower for x in ['?', '??', '...', '..']):
        await message.reply_text("dime bebé 😏 qué quieres saber? 💋", parse_mode='Markdown')
        return

    # ✅ MANEJO INTELIGENTE DE INTENCIONES
    if 'intercambio' in intenciones:
        await avisar_interes(context, user_id, username, texto, "QUIERE INTERCAMBIO 👀")
        await message.reply_text("bebé yo no cambio 😅 solo vendo\n\nPero si compras *PREMIUM* te doy 20 videos + 1 personalizado 🔥\n\nEs mejor que un intercambio Xd", reply_markup=get_menu(), parse_mode='Markdown')
        return

    if 'gratis' in intenciones:
        await message.reply_text(f"🎁 *FOTITOS GRATIS* 🔥\n\nToca el botón para verlas bebé:\n\n👉 Si te gustan, *ayúdame compartiendo* con tus amigos 🥺💋\n\n*Si quieres algo más hot...*\nCompra PREMIUM y te doy atención 1 a 1 😈", reply_markup=get_no_entiendo(), parse_mode='Markdown')
        return

    if 'referencias' in intenciones:
        await avisar_interes(context, user_id, username, texto, "PIDE REFERENCIAS 👀")
        await message.reply_text(f"claro bebé 😘 tengo referencias\n\nMira mi canal: {LINK_CANAL}\n\nAhí ves que soy real 🔥\n\nAhora elige tu país:", reply_markup=get_menu(), parse_mode='Markdown')
        return

    es_vip = user_id in VIP_TEMPORAL and VIP_TEMPORAL[user_id] > ahora
    es_demo = user_id in DEMO_HOT and DEMO_HOT[user_id] > ahora

    # ✅ DETECTA PALABRAS CALIENTES Y TE AVISA URGENTE
    if any(palabra in texto_lower for palabra in PALABRAS_HOT):
        await avisar_interes(context, user_id, username, texto, "CLIENTE CALIENTE 🔥")

    # ✅ DETECTA INTENCIÓN DE COMPRA
    if any(palabra in texto_lower for palabra in PALABRAS_COMPRA):
        await avisar_interes(context, user_id, username, texto, "QUIERE COMPRAR YA 🤑")

    if es_vip or es_demo:
        tiempo_restante = (VIP_TEMPORAL[user_id] - ahora).seconds // 60 if es_vip else (DEMO_HOT[user_id] - ahora).seconds // 60
        if not es_vip and tiempo_restante <= 2:
            await message.reply_text("Ay papi se me va a acabar el tiempo 😢\n\n*Si quieres seguir caliente conmigo...*\n\nCompra *PREMIUM* y seguimos sin corte 🔥", reply_markup=get_menu(), parse_mode='Markdown')
            return
        if any(x in texto_lower for x in ['mas tiempo', 'más tiempo', 'otro', 'renovar', 'seguir']):
            await message.reply_text("Bebé se me está acabando 😢\n\nSi quieres seguir calientito...\n*PREMIUM y seguimos* sin corte 🔥", reply_markup=get_menu(), parse_mode='Markdown')
            return
        elif es_vip and tiempo_restante <= 5:
            await message.reply_text("Ay no papi ya me voy a tener que ir 😢\n\nAprovecha rápido\n\nQué quieres que haga antes? 💋\n\n*Otro PREMIUM = seguimos más* 🔥", parse_mode='Markdown')
            return
        if any(x in texto_lower for x in ['que haces', 'qué haces']):
            await message.reply_text("nada acá 🙈 pensando en ti Xd y tú?", parse_mode='Markdown')
            return
        elif any(x in texto_lower for x in ['estas sola', 'estás sola']):
            await message.reply_text("sip solita 😈 xq?", parse_mode='Markdown')
            return
        elif any(x in texto_lower for x in ['que tienes puesto', 'ropa', 'desnuda', 'calata']):
            await message.reply_text("mmm nada papi 😏 solo mi collar... te gusta así? o me pongo algo pa ti? 💋", parse_mode='Markdown')
            return
        elif any(x in texto_lower for x in ['tocate', 'tócate', 'dedos', 'juega']):
            await message.reply_text("ufff ya me estoy tocando papi 💦 pensando en ti... sigo o te grabo? 😈", parse_mode='Markdown')
            return
        elif any(x in texto_lower for x in ['muestra', 'muestrame', 'ver', 'foto', 'video']):
            await message.reply_text("mmm quieres verme? 🥵 dime EXACTO qué quieres ver y te lo hago 💦", parse_mode='Markdown')
            return
        elif any(x in texto_lower for x in ['ganas', 'caliente', 'cachonda', 'mojada']):
            await message.reply_text("ay papi estoy que ardo 🥵 toda mojada... qué me haces? 💦", parse_mode='Markdown')
            return
        elif any(x in texto_lower for x in ['pene', 'verga', 'pito', 'pinga']):
            await message.reply_text("uff papi me gustan los p... 😏 cómo tienes el tuyo? cuéntame 💦 Xd", parse_mode='Markdown')
            return
        elif any(x in texto_lower for x in ['tamaño', 'grande', 'cm', 'mide']):
            await message.reply_text("mmm me gustan grandes papi 😏 cuántos cm tienes? dime y te digo si me entra 💦", parse_mode='Markdown')
            return
        else:
            await message.reply_text("No entendí bien amor 😅\n\nElige qué quieres ver:", reply_markup=get_menu(), parse_mode='Markdown')
            return

    # ✅ PRECIOS + ACTIVA FOLLOW UP
    if any(x in texto_lower for x in ['precio', 'cuanto', 'cuánto', 'vale', 'costo', 'cuesta', 'peru', 'soles', 's/', 'sol']):
        await avisar_interes(context, user_id, username, texto, "PREGUNTÓ PRECIO")
        VIO_PRECIOS[user_id] = datetime.now()
        asyncio.create_task(follow_up_task(context.application, user_id, username))
        await message.reply_text(PE_PRECIOS, reply_markup=get_volver(), parse_mode='Markdown')
    elif any(x in texto_lower for x in ['mexico', 'mxn', 'peso', 'méxico']):
        await avisar_interes(context, user_id, username, texto, "PREGUNTÓ PRECIO")
        VIO_PRECIOS[user_id] = datetime.now()
        asyncio.create_task(follow_up_task(context.application, user_id, username))
        await message.reply_text(MX_PRECIOS, reply_markup=get_volver(), parse_mode='Markdown')
    elif any(x in texto_lower for x in ['usd', 'usa', 'eeuu', 'dolar', 'dólar', 'estados unidos']):
        await avisar_interes(context, user_id, username, texto, "PREGUNTÓ PRECIO")
        VIO_PRECIOS[user_id] = datetime.now()
        asyncio.create_task(follow_up_task(context.application, user_id, username))
        await message.reply_text(USA_PRECIOS, reply_markup=get_volver(), parse_mode='Markdown')
    elif any(x in texto_lower for x in ['otro', 'internacional', 'colombia', 'argentina', 'chile', 'españa', 'venezuela']):
        await avisar_interes(context, user_id, username, texto, "PREGUNTÓ PRECIO")
        VIO_PRECIOS[user_id] = datetime.now()
        asyncio.create_task(follow_up_task(context.application, user_id, username))
        await message.reply_text(OTRO_PRECIOS, reply_markup=get_volver(), parse_mode='Markdown', disable_web_page_preview=True)
    elif any(x in texto_lower for x in ['comprar', 'compra', 'pagar', 'pago', 'quiero', 'dame']):
        await avisar_interes(context, user_id, username, texto, "QUIERE COMPRAR 🤑")
        await message.reply_text("Sii bebé 😘 Elige tu país para ver precios:", reply_markup=get_menu(), parse_mode='Markdown')
    else:
        await message.reply_text("No entendí amor 😅\n\nElige una opción:", reply_markup=get_menu(), parse_mode='Markdown')

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
            await query.delete_message()
            fotos_enviadas = []
            for i in range(1, 7):
                try:
                    fotos_enviadas.append(InputMediaPhoto(open(f'fotitos{i}.JPG', 'rb')))
                except FileNotFoundError:
                    logger.warning(f"No encontré fotitos{i}.JPG")
            if fotos_enviadas:
                for i in range(0, len(fotos_enviadas), 3):
                    await context.bot.send_media_group(chat_id=query.from_user.id, media=fotos_enviadas[i:i+3])
            await context.bot.send_message(chat_id=query.from_user.id, text=f"""📸 *TUS FOTITOS GRATIS BEBÉ* 🥺💋

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
(Me avisas cuando cumplas mi rey)""", parse_mode='Markdown', disable_web_page_preview=True, reply_markup=get_menu())
        except Exception as e:
            logger.error(f"Error enviando fotitos: {e}")
            await context.bot.send_message(chat_id=query.from_user.id, text="Ay bebé hubo un error
