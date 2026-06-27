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

TOKEN = '8762577283:AAGyirGjyF6CkPFMzh-i4-2w1NpHz93fqIg'
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
INVITADOS = {}

FOTOS_GRATIS = [
    "fotitos1.JPG", "fotitos2.JPG", "fotitos3.JPG",
    "fotitos4.JPG", "fotitos5.JPG", "fotitos6.JPG"
]

def escape_md(text):
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
        caption = f"💰 PAGO RECIBIDO 💰\n\n👤 {username_display}\n🆔 {user_id}\n⏰ {datetime.now().strftime('%H:%M:%S')}\n\n👉 Escribirle al cliente: {link_chat}\n\nCliente enviado a tu privado ✅\n\nUsa /activar {user_id} para reactivar el bot en ese chat"
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

async def crear_link_referido(context, user_id, username):
    try:
        if user_id in REFERIDOS:
            return REFERIDOS[user_id]['link']
        link_name = f"ref-{username}" if username!= "sin_username" else f"ref-{user_id}"
        invite_link = await context.bot.create_chat_invite_link(chat_id=CANAL_ID, name=link_name, creates_join_request=False)
        REFERIDOS[user_id] = {'link': invite_link.invite_link, 'contador': 0, 'username': f"@{username}" if username!= "sin_username" else f"ID:{user_id}"}
        INVITACIONES[invite_link.invite_link] = user_id
        logger.info(f"Link creado para {username}: {invite_link.invite_link}")
        return invite_link.invite_link
    except Exception as e:
        logger.error(f"Error creando link para {username}: {e}")
        error_msg = "❌ No soy admin o me falta permiso 'Invitar usuarios'" if "not enough rights" in str(e).lower() else f"❌ Error: {str(e)}"
        await context.bot.send_message(chat_id=user_id, text=error_msg)
        return None

async def chequear_premio(context, user_id):
    if user_id not in REFERIDOS:
        return
    contador = REFERIDOS[user_id]['contador']
    for meta, premio in sorted(PREMIOS_REFERIDOS.items()):
        if contador == meta:
            username = REFERIDOS[user_id]['username']
            mensajes_meta = {
                5: f"🔥 NIVEL TIBIO DESBLOQUEADO 🔥\n\n{contador} #HORMOS metiste 😏\nPremio: {premio}",
                20: f"🔥 NIVEL CALIENTE DESBLOQUEADO 🔥\n\n{contador} #HORMOS 😈\nPremio: {premio}",
                50: f"😈 NIVEL ARDIENDO DESBLOQUEADO 😈\n\n{contador} #HORMOS 🔥\nPremio: {premio}",
                100: f"🥵 NIVEL INFIERNO DESBLOQUEADO 🥵\n\n{contador} #HORMOS 😈\nPremio: {premio}",
                200: f"👑 NIVEL DIABLA DESBLOQUEADO 👑\n\n{contador} #HORMOS 🍑\nPremio: {premio}"
            }
            try:
                await context.bot.send_message(chat_id=user_id, text=mensajes_meta.get(meta, f"🏆 META {meta} ALCANZADA 🏆\n\nPremio: {premio}"))
            except Forbidden:
                pass
            await context.bot.send_message(chat_id=ADMIN_ID, text=f"🔥 PREMIO DESBLOQUEADO 🔥\n\n👤 {username}\n🆔 {user_id}\n📊 {meta} miembros\n🎁 {premio}")

async def enviar_gratis(chat_id, context):
    await context.bot.send_message(chat_id=chat_id, text=TEXTO_GRATIS, reply_markup=get_volver())
    try:
        for foto in FOTOS_GRATIS:
            with open(foto, 'rb') as f:
                await context.bot.send_photo(chat_id=chat_id, photo=f)
            await asyncio.sleep(0.5)
    except:
        pass

async def track_join(update: Update, context: ContextTypes.DEFAULT_TYPE):
    result = update.chat_member
    if result.new_chat_member.status == "member" and result.old_chat_member.status in ["left", "kicked"]:
        user = result.new_chat_member.user
        if user.is_bot:
            return
        if result.invite_link and result.invite_link.invite_link in INVITACIONES:
            referidor_id = INVITACIONES[result.invite_link.invite_link]
            if referidor_id in REFERIDOS:
                REFERIDOS[referidor_id]['contador'] += 1
                INVITADOS[user.id] = referidor_id
                try:
                    await context.bot.send_message(chat_id=referidor_id, text=f"🔥 +1 #HORMO 🔥\n\n{user.first_name} cayó por tu link 😏\nTotal: {REFERIDOS[referidor_id]['contador']}/200")
                except:
                    pass
                await chequear_premio(context, referidor_id)
    elif result.new_chat_member.status in ["left", "kicked"] and result.old_chat_member.status == "member":
        user = result.new_chat_member.user
        if user.is_bot or user.id not in INVITADOS:
            return
        referidor_id = INVITADOS[user.id]
        if referidor_id in REFERIDOS and REFERIDOS[referidor_id]['contador'] > 0:
            REFERIDOS[referidor_id]['contador'] -= 1
            try:
                await context.bot.send_message(chat_id=referidor_id, text=f"💔 -1 #HORMO 💔\n\n{user.first_name} se salió 😢\nTotal: {REFERIDOS[referidor_id]['contador']}/200")
            except:
                pass
        del INVITADOS[user.id]

async def manejar_todo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message or update.business_message
    if not message or not message.from_user or message.from_user.is_bot:
        return
    user = message.from_user
    user_id = user.id
    if user_id in PAGARON and user_id!= ADMIN_ID:
        return
    username = user.username or "sin_username"
    registrar_usuario(user)
    nombre = user.first_name

    if message.text and message.text.lower() == '/start':
        DEMO_USADO.add(user_id)
        await message.reply_text(f"Mmmm {nombre}... 😏✨ llegaste justo cuando te pensaba 🙈")
        await message.reply_text("¿Qué se te antoja hoy? 👇", reply_markup=get_menu())
        return

    if message.text and message.text.lower() == '/milink':
        link = await crear_link_referido(context, user_id, username)
        if link:
            contador = REFERIDOS[user_id]['contador'] if user_id in REFERIDOS else 0
            await message.reply_text(f"🔗 TU LINK: {link}\n\nMiembros: {contador}/200", reply_markup=get_volver())
        return

    if message.photo:
        if user_id == ADMIN_ID:
            return
        caption = message.caption or ""
        es_comprobante = any(x in normalizar(caption) for x in ['pago', 'yape', 'plin', 'comprobante', 'paypal', 'usdt', 'transfer'])
        if es_comprobante or not caption:
            PAGARON.add(user_id)
            foto_id = message.photo[-1].file_id
            await avisar_pago(context, user_id, username, nombre, foto_id)
            await message.reply_text(f"✅ PAGO RECIBIDO 😊\n\nGracias {nombre}, escríbeme al privado 👉 {USERNAME_ADMIN}")
        else:
            await message.reply_text("Que linda foto bebé 😏 ¿Quieres comprar? Elige tu pack 👇", reply_markup=get_precios_menu())
        return

    if not message.text:
        return
    texto = message.text.strip()
    if ULTIMO_MENSAJE.get(user_id) == texto.lower():
        return
    ULTIMO_MENSAJE[user_id] = texto.lower()

    # AVISO AL ADMIN CUANDO PIDEN INFO
    palabras_info = ['info', 'informacion', 'información', 'precio', 'cuanto', 'cuesta', 'como', 'cómo', 'ayuda', 'duda']
    if any(x in normalizar(texto) for x in palabras_info) and user_id!= ADMIN_ID:
        try:
            await context.bot.send_message(chat_id=ADMIN_ID, text=f"🔔 CLIENTE PIDIENDO INFO 🔔\n\n👤 {nombre} @{username}\n🆔 {user_id}\n💬 {texto}\n\n👉 tg://user?id={user_id}")
        except:
            pass

    if any(x in normalizar(texto) for x in ['gratis', 'free', 'regalo']):
        await enviar_gratis(user_id, context)
        return
    if any(x in normalizar(texto) for x in ['comprar', 'quiero', 'pago']):
        await message.reply_text(f"¡Así me gusta {nombre}! 😍🔥", reply_markup=get_precios_menu())
        return
    if 'peru' in normalizar(texto) or 'soles' in normalizar(texto):
        asyncio.create_task(follow_up_task(context.application, user_id, username))
        await message.reply_text(PE_PRECIOS, reply_markup=get_volver())
        return
    await message.reply_text("Elige una opción 😏👇", reply_markup=get_menu())

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    user_id = query.from_user.id
    if data == 'comprar':
        await query.edit_message_text("💎 ELIGE TU PAÍS 💎", reply_markup=get_precios_menu())
    elif data == 'pe':
        await query.edit_message_text(PE_PRECIOS, reply_markup=get_volver())
    elif data == 'mx':
        await query.edit_message_text(MX_PRECIOS, reply_markup=get_volver())
    elif data == 'usa':
        await query.edit_message_text(USA_PRECIOS, reply_markup=get_volver())
    elif data == 'otro':
        await query.edit_message_text(OTRO_PRECIOS, reply_markup=get_volver())
    elif data == 'gratis':
        await query.edit_message_text(TEXTO_GRATIS, reply_markup=get_volver())
        await enviar_gratis(user_id, context)
    elif data == 'milink':
        link = await crear_link_referido(context, user_id, query.from_user.username or "sin_username")
        if link:
            await query.edit_message_text(f"🔗 TU LINK: {link}", reply_markup=get_volver())
    elif data == 'volver':
        await query.edit_message_text("¿Qué se te antoja hoy? 👇", reply_markup=get_menu())

async def vip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id!= ADMIN_ID:
        return
    user_id = int(context.args[0])
    VIP_TEMPORAL[user_id] = datetime.now() + timedelta(minutes=15)
    await context.bot.send_message(user_id, "✅ VIP ACTIVADO")
    await update.message.reply_text(f"✅ VIP para {user_id}")

async def activar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id!= ADMIN_ID:
        return
    user_id = int(context.args[0])
    if user_id in PAGARON:
        PAGARON.remove(user_id)
        await context.bot.send_message(user_id, "😏 Bot reactivado")
        await update.message.reply_text(f"✅ Reactivado {user_id}")

async def usuarios(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id!= ADMIN_ID:
        return
    texto = f"📊 Total: {len(USUARIOS)} usuarios"
    await update.message.reply_text(texto)

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f"Error: {context.error}")

def shutdown_handler(signum, frame):
    sys.exit(0)

signal.signal(signal.SIGINT, shutdown_handler)
signal.signal(signal.SIGTERM, shutdown_handler)

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler('vip', vip))
    app.add_handler(CommandHandler('activar', activar))
    app.add_handler(CommandHandler('usuarios', usuarios))
    app.add_handler(CallbackQueryHandler(button))
    app.add_handler(ChatMemberHandler(track_join, ChatMemberHandler.CHAT_MEMBER))
    app.add_handler(MessageHandler(filters.ALL, manejar_todo))
    app.add_error_handler(error_handler)
    logger.info("BOT PRENDIDO ✅")
    app.run_polling(drop_pending_updates=True, allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
