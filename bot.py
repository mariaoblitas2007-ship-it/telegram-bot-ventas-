import os
import sys
import asyncio
import random
import logging
import unicodedata
import signal
import re
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ChatMemberUpdated
from telegram.ext import Application, MessageHandler, CallbackQueryHandler, CommandHandler, filters, ContextTypes, ChatMemberHandler
from telegram.error import Conflict, Forbidden

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = '8751695788:AAHJYzHxsSlcjnYOfqMEEb1XMBEMqqYDvW8'
ADMIN_ID = 8783569348
USERNAME_ADMIN = "@yanabicitasa"
CANAL_ID = -1004473732783

LINK_CANAL = "https://t.me/+ZWc0FAcw-hQ2MDZh"
LINK_PAYPAL = "https://www.paypal.com/qrcodes/p2pqrc/76RWY9FF7Q7RE"

VIP_TEMPORAL = {}
DEMO_USADO = set()
USUARIOS = {}
PAGARON = set()
ULTIMO_MENSAJE = {}
VIO_PRECIOS = {}
FOLLOWUP_ENVIADO = set()

# Sistema de referidos
REFERIDOS = {}
INVITACIONES = {}
INVITADOS = {} # NUEVO: Guarda quién invitó a quién {user_id: referidor_id}

FOTOS_GRATIS = [
    "fotitos1.JPG", "fotitos2.JPG", "fotitos3.JPG",
    "fotitos4.JPG", "fotitos5.JPG", "fotitos6.JPG"
]

def escape_md(text):
    """Escapa caracteres especiales de Markdown"""
    return re.sub(r'([_*\[\]()~`>#+\-=|{}.!])', r'\\\1', text)

PE_PRECIOS = """
🛍 PACKS DISPONIBLES - PERÚ 🇵🇪😏

💦 PRUEBA: S/ 5
→ 3 fotitos | S/ 1.66 c/u
→ Para que me conozcas 🙈

🎂 BÁSICO: S/ 10
→ 6 unidades | S/ 1.66 c/u
→ +1 foto extra HOY

🔥 TOP: S/ 20 ← MÁS VENDIDO
→ 12 unidades | S/ 1.66 c/u
→ Ahorras 50%
→ REGALO: 2 fotos extra

🏆 PREMIUM: S/ 35
→ 20 unidades + 1 personalizado
→ incluye chat privado 24h 🥰
→ Ahorras 50%

👑 VIP: S/ 50 ← MÁXIMO 28 UNIDADES
→ 28 unidades + 2 personalizados
→ Chat 3 días + videollamada 5min
→ TODO INCLUIDO 😈

📼 LLAMADITAS 📼
S/ 30: 10 min 😈
S/ 50: 20 min + 3 fotos

⚡ COMBO FLASH: S/ 45
→ Pack PREMIUM + Llamada 10min
→ Ahorras S/ 20

💳 PAGO: YAPE/PLIN: 923553612
100% REAL - PIDEME REFERENCIAS

1. Yapeas 2. Captura 3. Disfrutas 😏
"""

MX_PRECIOS = """
🛍 PACKS DISPONIBLES - MÉXICO 🇲🇽😏

💦 PRUEBA: $60 MXN
→ 3 fotitos | $20 c/u
→ Para que me conozcas 🙈

🎂 BÁSICO: $90 MXN
→ 6 unidades | $15 c/u
→ +1 foto extra HOY

🔥 TOP: $145 MXN ← MÁS VENDIDO
→ 12 unidades | $12 c/u
→ Ahorras 50%
→ REGALO: 2 fotos extra

🏆 PREMIUM: $230 MXN
→ 20 unidades + 1 personalizado
→ incluye chat privado 24h 🥰
→ Ahorras 50%

👑 VIP: $320 MXN ← MÁXIMO 28 UNIDADES
→ 28 unidades + 2 personalizados
→ Chat 3 días + videollamada 5min
→ TODO INCLUIDO 😈

📼 LLAMADITAS 📼
$205 MXN: 10 min 😈
$320 MXN: 20 min + 3 fotos

🛍 PAGO MXN:
🏦 Banco: STP
🔢 CLABE: 646180546711450910
📝 Referencia: yanae

🇲🇽 También: Transfer / Astropay

Mándame captura cuando pagues 😊
"""

USA_PRECIOS = """
🛍 PACKS DISPONIBLES - USA 🇺🇸😏

💦 PRUEBA: $2 USD
→ 3 fotitos | $0.66 c/u
→ Para que me pruebes 🙈

🎂 BÁSICO: $3.50 USD
→ 6 unidades | $0.58 c/u
→ +1 foto extra HOY

🔥 TOP: $7 USD ← MÁS VENDIDO
→ 12 unidades | $0.58 c/u
→ Ahorras 50%
→ REGALO: 2 fotos extra

🏆 PREMIUM: $12 USD
→ 20 unidades + 1 personalizado
→ incluye chat privado 24h 🥰
→ Ahorras 50%

👑 VIP: $20 USD ← MÁXIMO 28 UNIDADES
→ 28 unidades + 2 personalizados
→ Chat 3 días + videollamada 5min
→ MEJOR VALOR 😈

📼 LLAMADITAS 📼
$10 USD: 10 min 😈
$20 USD: 20 min + 3 fotos

🪙 PAGO:
PayPal: AbigailMaximoofO

🏦 Bank EEUU:
Community Federal Savings Bank
📍 Address: 5 Penn Plaza, 14th Floor New York, NY 10001
0️⃣ Account: 8338233469
0️⃣ Routing: 026073150
✍️ Type: Checking

Avísame cuando envíes con el comprobante 😊
"""

OTRO_PRECIOS = f"""
🛍 PACKS DISPONIBLES - INTERNACIONAL 🌎😏

💦 PRUEBA: $2 USD
→ 3 fotitos | $0.66 c/u
→ Para que me conozcas 🙈

🎂 BÁSICO: $3.50 USD
→ 6 unidades | $0.58 c/u
→ +1 foto extra HOY

🔥 TOP: $7 USD ← MÁS VENDIDO
→ 12 unidades | $0.58 c/u
→ Ahorras 50%
→ REGALO: 2 fotos extra

🏆 PREMIUM: $12 USD
→ 20 unidades + 1 personalizado
→ incluye chat privado 24h 🥰
→ Ahorras 50%

👑 VIP: $20 USD ← MÁXIMO 28 UNIDADES
→ 28 unidades + 2 personalizados
→ Chat 3 días + videollamada 5min
→ MEJOR VALOR 😈

📼 LLAMADITAS 📼
$10 USD: 10 min 😈
$20 USD: 20 min + 3 fotos

🪙 PAGO:
PayPal: {LINK_PAYPAL}
/ USDT disponible

Avísame cuando envíes con el comprobante 😊
"""

TEXTO_GRATIS = """
🔥 VIDEOS GRATIS #HORMO - SÚBEME LA TEMP 🔥

¿Sin plata bebé? 😏 Trabaja por mí y te mojo...

🥉 NIVEL TIBIO - 5 MIEMBROS:
1 videito pa que me pruebes 🥵

🔥 NIVEL CALIENTE - 20 MIEMBROS:
2-3 videitos... ya me pones nerviosa 😈

😈 NIVEL ARDIENDO - 50 MIEMBROS:
4-10 videitos 🥵 Te voy a dejar sin aire

🥵 NIVEL INFIERNO - 100 MIEMBROS:
10-20 videitos 🔥 Ya soy toda tuya

👑 NIVEL DIABLA - 200 MIEMBROS:
+20 videitos + VIDEO FETICHE solo para ti 😈🍑
Aquí me entrego completa...

¿Caliente y con prisa? Toca "💎 COMPRAR" y te atiendo YA 🔥

Saca tu link en "🔗 MI LINK" y ponte a reclutar #HORMOS 😏
"""

# Premios por referidos ESCALONADOS Y PICANTES
PREMIOS_REFERIDOS = {
    5: "1 videito pa calentar 🥵",
    20: "2-3 videitos... ya me mojo 🔥",
    50: "4-10 videitos 😈 te dejo sin aire",
    100: "10-20 videitos 🥵 ya soy tuya",
    200: "+20 videitos + VIDEO FETICHE 👑🍑"
}

def get_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("💎 COMPRAR PACKS", callback_data='comprar')],
        [InlineKeyboardButton("🎁 GRATIS - Misiones", callback_data='gratis')],
        [InlineKeyboardButton("🔗 MI LINK - Referidos", callback_data='milink')],
        [InlineKeyboardButton("📊 RANKING", callback_data='ranking')],
        [InlineKeyboardButton("🔥 Canal Oficial", url=LINK_CANAL)]
    ])

def get_precios_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🇵🇪 Perú", callback_data='pe')],
        [InlineKeyboardButton("🇲🇽 México", callback_data='mx')],
        [InlineKeyboardButton("🇺🇸 USA/Otros", callback_data='usa')],
        [InlineKeyboardButton("🌎 Internacional", callback_data='otro')],
        [InlineKeyboardButton("⬅️ Volver", callback_data='volver')]
    ])

def get_volver():
    return InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Volver al Menú", callback_data='volver')]])

def normalizar(texto):
    texto = unicodedata.normalize('NFKD', texto).encode('ascii', 'ignore').decode('ascii')
    return texto.lower()

def registrar_usuario(user):
    USUARIOS[user.id] = {
        'nombre': user.first_name,
        'username': user.username or "sin_username",
        'ultimo_mensaje': datetime.now().strftime('%d/%m %H:%M'),
        'demo_usada': user.id in DEMO_USADO,
        'es_vip': user.id in VIP_TEMPORAL and VIP_TEMPORAL[user.id] > datetime.now(),
        'pago': user.id in PAGARON
    }

async def avisar_pago(context, user_id, username, nombre, foto_id):
    try:
        username_display = f"@{username}" if username!= "sin_username" else f"{nombre}"
        link_chat = f"tg://user?id={user_id}"

        caption = f"💰 PAGO RECIBIDO 💰\n\n" \
                  f"👤 {username_display}\n" \
                  f"🆔 {user_id}\n" \
                  f"⏰ {datetime.now().strftime('%H:%M:%S')}\n\n" \
                  f"👉 Escribirle al cliente: {link_chat}\n\n" \
                  f"Cliente enviado a tu privado ✅\n\n" \
                  f"Usa /activar {user_id} para reactivar el bot en ese chat"

        await context.bot.send_photo(chat_id=ADMIN_ID, photo=foto_id, caption=caption)
    except Exception as e:
        logger.error(f"Error enviando pago: {e}")

async def follow_up_task(app, user_id, username):
    await asyncio.sleep(1800)
    if user_id in PAGARON or user_id in FOLLOWUP_ENVIADO:
        return
    FOLLOWUP_ENVIADO.add(user_id)
    mensajes = [
        f"Oye {username} 😏 ¿sigues ahí? Si compras TOP te doy 2 unidades extra 🎁",
        f"Psst 👉👈 con PREMIUM te agrego un bonus que te va a encantar ✨",
        f"Hola 🥺 te espero... con TOP te mando algo especial 🙈"
    ]
    try:
        await app.bot.send_message(chat_id=user_id, text=random.choice(mensajes), reply_markup=get_menu())
    except:
        pass

# Crear link único para referidos
async def crear_link_referido(context, user_id, username):
    try:
        if user_id in REFERIDOS:
            return REFERIDOS[user_id]['link']

        link_name = f"ref-{username}" if username!= "sin_username" else f"ref-{user_id}"
        invite_link = await context.bot.create_chat_invite_link(
            chat_id=CANAL_ID,
            name=link_name,
            creates_join_request=False
        )
        REFERIDOS[user_id] = {
            'link': invite_link.invite_link,
            'contador': 0,
            'username': f"@{username}" if username!= "sin_username" else f"ID:{user_id}"
        }
        INVITACIONES[invite_link.invite_link] = user_id
        logger.info(f"Link creado para {username}: {invite_link.invite_link}")
        return invite_link.invite_link
    except Exception as e:
        logger.error(f"Error creando link para {username}: {e}")
        if "not enough rights" in str(e).lower():
            error_msg = "❌ No soy admin o me falta permiso 'Invitar usuarios'"
        elif "chat not found" in str(e).lower():
            error_msg = f"❌ CANAL_ID incorrecto: {CANAL_ID}"
        else:
            error_msg = f"❌ Error: {str(e)}"

        await context.bot.send_message(chat_id=user_id, text=error_msg)
        return None

# Chequear premios ESCALONADOS
async def chequear_premio(context, user_id):
    if user_id not in REFERIDOS:
        return

    contador = REFERIDOS[user_id]['contador']
    for meta, premio in sorted(PREMIOS_REFERIDOS.items()):
        if contador == meta:
            username = REFERIDOS[user_id]['username']
            mensajes_meta = {
                5: f"🔥 NIVEL TIBIO DESBLOQUEADO 🔥\n\n{contador} #HORMOS metiste 😏\nPremio: {premio}\n\nTe lo mando al pv en 10min... pa que me pruebes 🥵",
                20: f"🔥 NIVEL CALIENTE DESBLOQUEADO 🔥\n\n{contador} #HORMOS 😈\nPremio: {premio}\n\nYa me pones nerviosa... te escribo al pv 🥵",
                50: f"😈 NIVEL ARDIENDO DESBLOQUEADO 😈\n\n{contador} #HORMOS 🔥\nPremio: {premio}\n\nMe tienes sin aire... voy al pv ya 🥵",
                100: f"🥵 NIVEL INFIERNO DESBLOQUEADO 🥵\n\n{contador} #HORMOS 😈\nPremio: {premio}\n\nYa soy toda tuya... revisa tu pv 🔥",
                200: f"👑 NIVEL DIABLA DESBLOQUEADO 👑\n\n{contador} #HORMOS 🍑\nPremio: {premio}\n\nME ENTREGO COMPLETA... video fetiche + todo\nRevisa tu pv YA 😈🥵"
            }
            try:
                await context.bot.send_message(
                    chat_id=user_id,
                    text=mensajes_meta.get(meta, f"🏆 META {meta} ALCANZADA 🏆\n\nPremio: {premio}\n\nTe escribo al pv 😏")
                )
            except Forbidden:
                logger.warning(f"No puedo escribirle a {user_id}, no inició el bot")
            # Aviso al admin
            await context.bot.send_message(
                chat_id=ADMIN_ID,
                text=f"🔥 PREMIO DESBLOQUEADO 🔥\n\n👤 {username}\n🆔 {user_id}\n📊 {meta} miembros\n🎁 {premio}\n\n👉 Escribirle: tg://user?id={user_id}"
            )

async def enviar_gratis(chat_id, context):
    await context.bot.send_message(chat_id=chat_id, text=TEXTO_GRATIS, reply_markup=get_volver())
    # Solo enviar fotos si el usuario inició el bot
    try:
        for foto in FOTOS_GRATIS:
            with open(foto, 'rb') as f:
                await context.bot.send_photo(chat_id=chat_id, photo=f)
            await asyncio.sleep(0.5)
    except Forbidden:
        pass # Silencioso, ya no avisa nada
    except FileNotFoundError:
        logger.warning(f"Foto no encontrada, saltando...")
    except Exception as e:
        logger.error(f"No se pudo enviar fotos: {e}")

# ESTA FUNCIÓN ES LA CLAVE - Detecta cuando alguien entra o sale del canal
async def track_join(update: Update, context: ContextTypes.DEFAULT_TYPE):
    result = update.chat_member
    logger.info(f"ChatMember update: {result.new_chat_member.status} en {result.chat.id}")

    # Cuando ENTRA alguien al canal
    if result.new_chat_member.status == "member" and result.old_chat_member.status in ["left", "kicked"]:
        user = result.new_chat_member.user
        if user.is_bot:
            return

        # Verificar si entró por link de referido
        if result.invite_link and result.invite_link.invite_link in INVITACIONES:
            referidor_id = INVITACIONES[result.invite_link.invite_link]
            if referidor_id in REFERIDOS:
                REFERIDOS[referidor_id]['contador'] += 1
                INVITADOS[user.id] = referidor_id # Guardamos quién lo invitó
                nivel = '👑 DIABLA' if REFERIDOS[referidor_id]['contador']>=200 else '🥵 INFIERNO' if REFERIDOS[referidor_id]['contador']>=100 else '😈 ARDIENDO' if REFERIDOS[referidor_id]['contador']>=50 else '🔥 CALIENTE' if REFERIDOS[referidor_id]['contador']>=20 else '🥵 TIBIO' if REFERIDOS[referidor_id]['contador']>=5 else '🥉 FRÍO'
                try:
                    await context.bot.send_message(
                        chat_id=referidor_id,
                        text=f"🔥 +1 #HORMO 🔥\n\n{user.first_name} cayó por tu link 😏\nProgreso: {REFERIDOS[referidor_id]['contador']}/200\nNivel: {nivel}\n\nMe tienes más caliente... sigue 🥵"
                    )
                except Forbidden:
                    pass
                await chequear_premio(context, referidor_id)
                logger.info(f"Referido contado: {user.first_name} para {referidor_id}. Total: {REFERIDOS[referidor_id]['contador']}")

    # Cuando SE SALE alguien del canal 👇 ESTO ES LO NUEVO
    elif result.new_chat_member.status in ["left", "kicked"] and result.old_chat_member.status == "member":
        user = result.new_chat_member.user
        if user.is_bot:
            return

        # Si sabemos quién lo invitó, le restamos
        if user.id in INVITADOS:
            referidor_id = INVITADOS[user.id]
            if referidor_id in REFERIDOS and REFERIDOS[referidor_id]['contador'] > 0:
                REFERIDOS[referidor_id]['contador'] -= 1
                nivel = '👑 DIABLA' if REFERIDOS[referidor_id]['contador']>=200 else '🥵 INFIERNO' if REFERIDOS[referidor_id]['contador']>=100 else '😈 ARDIENDO' if REFERIDOS[referidor_id]['contador']>=50 else '🔥 CALIENTE' if REFERIDOS[referidor_id]['contador']>=20 else '🥵 TIBIO' if REFERIDOS[referidor_id]['contador']>=5 else '🥉 FRÍO'
                try:
                    await context.bot.send_message(
                        chat_id=referidor_id,
                        text=f"💔 -1 #HORMO 💔\n\n{user.first_name} se salió del canal 😢\nProgreso: {REFERIDOS[referidor_id]['contador']}/200\nNivel: {nivel}\n\nTráelo de vuelta bebé 😏"
                    )
                except Forbidden:
                    pass
                logger.info(f"Referido perdido: {user.first_name} se salió. Total de {referidor_id}: {REFERIDOS[referidor_id]['contador']}")
            # Borramos el registro
            del INVITADOS[user.id]

async def manejar_todo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message or update.business_message
    if not message or not message.from_user or message.from_user.is_bot:
        return
    user = message.from_user
    user_id = user.id

    if user_id in PAGARON and user_id!= ADMIN_ID:
        logger.info(f"Usuario {user_id} bloqueado por pago")
        return

    username = user.username or "sin_username"
    registrar_usuario(user)
    ahora = datetime.now()
    nombre = user.first_name

    if message.text and message.text.lower() == '/start':
        DEMO_USADO.add(user_id)
        saludo = f"Mmmm {nombre}... 😏✨ llegaste justo cuando te pensaba 🙈"
        await message.reply_text(saludo)
        await message.reply_text("¿Qué se te antoja hoy? 👇", reply_markup=get_menu())
        return

    # Comando /milink
    if message.text and message.text.lower() == '/milink':
        link = await crear_link_referido(context, user_id, username)
        if link:
            contador = REFERIDOS[user_id]['contador'] if user_id in REFERIDOS else 0
            nivel = '👑 DIABLA' if contador>=200 else '🥵 INFIERNO' if contador>=100 else '😈 ARDIENDO' if contador>=50 else '🔥 CALIENTE' if contador>=20 else '🥵 TIBIO' if contador>=5 else '🥉 FRÍO'
            await message.reply_text(
                f"🔗 TU LINK #HORMO 🔗\n\n{link}\n\n📊 TU PROGRESO:\nMiembros: {contador}/200\nNivel: {nivel}\n\n🎯 PREMIOS ESCALONADOS:\n5 = 1 videito 🥵\n20 = 2-3 videitos 🔥\n50 = 4-10 videitos 😈\n100 = 10-20 videitos 🥵\n200 = +20 videitos + VIDEO FETICHE 👑🍑\n\n⚠️ REGLAS:\nSolo cuentan reales +24h en el canal\nBots = te baneo y no hay nada ❌\n\nSpamea tu link y me vas desnudando 😈🔥",
                reply_markup=get_volver()
            )
        return

    # Comando /misreferidos
    if message.text and message.text.lower() == '/misreferidos':
        if user_id in REFERIDOS:
            contador = REFERIDOS[user_id]['contador']
            link = REFERIDOS[user_id]['link']
            nivel = '👑 DIABLA' if contador>=200 else '🥵 INFIERNO' if contador>=100 else '😈 ARDIENDO' if contador>=50 else '🔥 CALIENTE' if contador>=20 else '🥵 TIBIO' if contador>=5 else '🥉 FRÍO'
            await message.reply_text(
                f"📊 TUS #HORMOS 📊\n\n👤 Usuario: @{username}\n👥 Has metido: {contador}/200\n🎯 Te faltan: {200-contador} para mi VIDEO FETICHE 👑\nNivel actual: {nivel}\n\nTu link: {link}\n\nSigue caliente y sigue spameando 🔥",
                reply_markup=get_volver()
            )
        else:
            await message.reply_text("Aún no tienes link bebé 😏 Usa /milink para crear uno y empezar a ganar")
        return

    # Comando /ranking
    if message.text and message.text.lower() == '/ranking':
        if not REFERIDOS:
            await message.reply_text("Aún no hay #HORMOS activos 😢 Sé el primero en mojarme con /milink")
            return

        top = sorted(REFERIDOS.items(), key=lambda x: x[1]['contador'], reverse=True)[:10]
        texto = "🏆 TOP #HORMOS MÁS CALIENTES 🏆\n\n"
        for i, (uid, data) in enumerate(top, 1):
            nivel = "👑 DIABLA" if data['contador'] >= 200 else "🥵 INFIERNO" if data['contador'] >= 100 else "😈 ARDIENDO" if data['contador'] >= 50 else "🔥 CALIENTE" if data['contador'] >= 20 else "🥵 TIBIO" if data['contador'] >= 5 else "🥉 FRÍO"
            texto += f"{i}. {data['username']} - {data['contador']} miembros {nivel}\n"
        texto += "\n¿Vas a dejar que te ganen mi VIDEO FETICHE? Usa /milink 😈🍑"
        await message.reply_text(texto, reply_markup=get_volver())
        return

    if message.photo:
        if user_id!= ADMIN_ID:
            PAGARON.add(user_id)
        foto_id = message.photo[-1].file_id
        await avisar_pago(context, user_id, username, nombre, foto_id)
        await message.reply_text(
            f"✅ PAGO RECIBIDO 😊\n\n"
            f"Gracias {nombre}, ya te registro\n"
            f"📩 AHORA ESCRÍBEME AL PRIVADO\n"
            f"👉 {USERNAME_ADMIN}\n\n"
            f"Ahí coordinamos tu pedido 😏\n\n"
            f"El bot se desactiva aquí por seguridad"
        )
        return

    if not message.text:
        return

    texto = message.text.strip()

    if ULTIMO_MENSAJE.get(user_id) == texto.lower():
        return
    ULTIMO_MENSAJE[user_id] = texto.lower()

    if any(x in normalizar(texto) for x in ['gratis', 'free', 'regalo', 'bonus', 'muestra gratis']):
        await enviar_gratis(user_id, context)
        return

    if any(x in normalizar(texto) for x in ['comprar', 'compro', 'quiero', 'pago', 'pagare', 'llevo', 'lo quiero']):
        await message.reply_text(f"¡Así me gusta {nombre}! 😍🔥 Elige tu pack 👇", reply_markup=get_precios_menu())
        return

    if any(x in normalizar(texto) for x in ['precio', 'cuanto', 'vale', 'costo', 'cuesta', 'peru', 'soles']):
        VIO_PRECIOS[user_id] = datetime.now()
        asyncio.create_task(follow_up_task(context.application, user_id, username))
        await message.reply_text(PE_PRECIOS, reply_markup=get_volver())
        return
    elif any(x in normalizar(texto) for x in ['mexico', 'mxn', 'peso']):
        VIO_PRECIOS[user_id] = datetime.now()
        asyncio.create_task(follow_up_task(context.application, user_id, username))
        await message.reply_text(MX_PRECIOS, reply_markup=get_volver())
        return
    elif any(x in normalizar(texto) for x in ['usd', 'usa', 'eeuu', 'dolar', 'estados unidos']):
        VIO_PRECIOS[user_id] = datetime.now()
        asyncio.create_task(follow_up_task(context.application, user_id, username))
        await message.reply_text(USA_PRECIOS, reply_markup=get_volver())
        return
    elif any(x in normalizar(texto) for x in ['otro', 'internacional', 'colombia', 'argentina', 'chile', 'mundial']):
        VIO_PRECIOS[user_id] = datetime.now()
        asyncio.create_task(follow_up_task(context.application, user_id, username))
        await message.reply_text(OTRO_PRECIOS, reply_markup=get_volver(), disable_web_page_preview=True)
        return

    es_vip = user_id in VIP_TEMPORAL and VIP_TEMPORAL[user_id] > ahora

    if es_vip:
        tiempo_restante = (VIP_TEMPORAL[user_id] - ahora).seconds // 60
        if tiempo_restante <= 5:
            await message.reply_text(f"{nombre}, {tiempo_restante} min y me tengo que ir 😢\n\n¿Qué necesitas antes de irme? ✨")
            return

    await message.reply_text("Elige una opción 😏👇", reply_markup=get_menu())

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    user_id = query.from_user.id
    username = query.from_user.username or "sin_username"

    if user_id in PAGARON and user_id!= ADMIN_ID:
        logger.info(f"Botón ignorado: usuario {user_id} bloqueado por pago")
        return

    logger.info(f"Botón presionado: {data} por {user_id}")

    if data == 'comprar':
        await query.edit_message_text("💎 ELIGE TU PAÍS 💎\n\nToca tu bandera para ver precios 👇", reply_markup=get_precios_menu())
    elif data == 'pe':
        await query.edit_message_text(PE_PRECIOS, reply_markup=get_volver())
    elif data == 'mx':
        await query.edit_message_text(MX_PRECIOS, reply_markup=get_volver())
    elif data == 'usa':
        await query.edit_message_text(USA_PRECIOS, reply_markup=get_volver())
    elif data == 'otro':
        await query.edit_message_text(OTRO_PRECIOS, reply_markup=get_volver(), disable_web_page_preview=True)
    elif data == 'gratis':
        await query.edit_message_text(TEXTO_GRATIS, reply_markup=get_volver())
        try:
            for foto in FOTOS_GRATIS:
                with open(foto, 'rb') as f:
                    await context.bot.send_photo(chat_id=user_id, photo=f)
                await asyncio.sleep(0.5)
        except Forbidden:
            pass # YA NO SPAMEA EL MENSAJE DE /start 😈
        except FileNotFoundError:
            logger.warning(f"Foto no encontrada, saltando...")
        except Exception as e:
            logger.error(f"No se pudo enviar fotos: {e}")

    # Botón MI LINK PICANTE
    elif data == 'milink':
        link = await crear_link_referido(context, user_id, username)
        if link:
            contador = REFERIDOS[user_id]['contador']
            nivel = '👑 DIABLA' if contador>=200 else '🥵 INFIERNO' if contador>=100 else '😈 ARDIENDO' if contador>=50 else '🔥 CALIENTE' if contador>=20 else '🥵 TIBIO' if contador>=5 else '🥉 FRÍO'
            await query.edit_message_text(
                f"🔗 TU LINK #HORMO 🔗\n\n{link}\n\n📊 TU PROGRESO:\nMiembros: {contador}/200\nNivel: {nivel}\n\n🎯 PREMIOS ESCALONADOS:\n5 = 1 videito 🥵\n20 = 2-3 videitos 🔥\n50 = 4-10 videitos 😈\n100 = 10-20 videitos 🥵\n200 = +20 videitos + VIDEO FETICHE 👑🍑\n\n⚠️ REGLAS:\nSolo cuentan reales +24h en el canal\nBots = te baneo y no hay nada ❌\n\nSpamea tu link y me vas desnudando 😈🔥",
                reply_markup=get_volver()
            )

    # Botón RANKING PICANTE
    elif data == 'ranking':
        if not REFERIDOS:
            await query.edit_message_text("Aún no hay #HORMOS activos 😢 Sé el primero en mojarme con /milink", reply_markup=get_volver())
            return

        top = sorted(REFERIDOS.items(), key=lambda x: x[1]['contador'], reverse=True)[:10]
        texto = "🏆 TOP #HORMOS MÁS CALIENTES 🏆\n\n"
        for i, (uid, data_ref) in enumerate(top, 1):
            nivel = "👑 DIABLA" if data_ref['contador'] >= 200 else "🥵 INFIERNO" if data_ref['contador'] >= 100 else "😈 ARDIENDO" if data_ref['contador'] >= 50 else "🔥 CALIENTE" if data_ref['contador'] >= 20 else "🥵 TIBIO" if data_ref['contador'] >= 5 else "🥉 FRÍO"
            texto += f"{i}. {data_ref['username']} - {data_ref['contador']} miembros {nivel}\n"
        texto += "\n¿Vas a dejar que te ganen mi VIDEO FETICHE? Toca 🔗 MI LINK 😈🍑"
        await query.edit_message_text(texto, reply_markup=get_volver())

    elif data == 'volver':
        await query.edit_message_text("¿Qué se te antoja hoy? 👇", reply_markup=get_menu())

async def vip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id!= ADMIN_ID:
        return
    if not context.args:
        await update.message.reply_text("Uso: /vip ID_DEL_CLIENTE")
        return
    user_id = int(context.args[0])
    VIP_TEMPORAL[user_id] = datetime.now() + timedelta(minutes=15)
    await context.bot.send_message(user_id, "✅ CHAT VIP ACTIVADO 😊\n\nTienes 15 minutos de atención prioritaria\n\nPregúntame lo que quieras ✨")
    await update.message.reply_text(f"✅ VIP activado para {user_id}")

async def activar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id!= ADMIN_ID:
        return
    if not context.args:
        await update.message.reply_text("Uso: /activar ID_DEL_CLIENTE")
        return
    user_id = int(context.args[0])
    if user_id in PAGARON:
        PAGARON.remove(user_id)
        await context.bot.send_message(user_id, "😏 Bot reactivado. ¿En qué te ayudo?")
        await update.message.reply_text(f"✅ Bot reactivado para {user_id}")
    else:
        await update.message.reply_text(f"⚠️ El usuario {user_id} no estaba desactivado")

async def usuarios(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id!= ADMIN_ID:
        return
    if not USUARIOS:
        await update.message.reply_text("No hay usuarios aún")
        return
    texto = "📊 USUARIOS REGISTRADOS 📊\n\n"
    for uid, data in USUARIOS.items():
        estado = "💰 PAGÓ/DESACTIVADO" if data['pago'] else "🔥 VIP" if data['es_vip'] else "👀 NUEVO"
        refs = f" | {REFERIDOS[uid]['contador']} miembros" if uid in REFERIDOS else ""
        texto += f"👤 {data['nombre']} @{data['username']}\n🆔 {uid} | {estado}{refs}\n⏰ {data['ultimo_mensaje']}\n\n"
    texto += f"Total: {len(USUARIOS)} usuarios"
    await update.message.reply_text(texto)

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
    app.add_handler(CommandHandler('activar', activar))
    app.add_handler(CommandHandler('usuarios', usuarios))
    app.add_handler(CallbackQueryHandler(button))
    # ESTA LÍNEA ES LA CLAVE PARA QUE CUENTEN LOS REFERIDOS EN CANALES 👑
    app.add_handler(ChatMemberHandler(track_join, ChatMemberHandler.CHAT_MEMBER))
    app.add_handler(MessageHandler(filters.ALL, manejar_todo))
    app.add_error_handler(error_handler)
    logger.info("BOT PRENDIDO - MODO 24/7 ACTIVO ✅")
    # IMPORTANTE: allowed_updates para que Telegram mande los eventos de miembros
    app.run_polling(drop_pending_updates=True, allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
