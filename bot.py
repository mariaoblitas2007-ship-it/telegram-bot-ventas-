import os
import sys
import asyncio
import random
import logging
import unicodedata
import signal
import re
import sqlite3
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, MessageHandler, CallbackQueryHandler, CommandHandler, filters, ContextTypes, ChatMemberHandler
from telegram.error import Forbidden

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# === CONFIG SEGURA - usa variables de entorno en Render ===
TOKEN = os.getenv('TOKEN', '8762577283:AAGyirGjyF6CkPFMzh-i4-2w1NpHz93fqIg')
ADMIN_ID = int(os.getenv('ADMIN_ID', '8783569348'))
USERNAME_ADMIN = "@yanabicitasa"
CANAL_ID = int(os.getenv('CANAL_ID', '-1004473732783'))

LINK_CANAL = "https://t.me/+ZWc0FAcw-hQ2MDZh"
LINK_PAYPAL = "https://www.paypal.com/qrcodes/p2pqrc/76RWY9FF7Q7RE"

# === BASE DE DATOS PERSISTENTE ===
conn = sqlite3.connect('bot_data.db', check_same_thread=False)
conn.execute('''CREATE TABLE IF NOT EXISTS referidos (user_id INTEGER PRIMARY KEY, contador INTEGER, link TEXT, username TEXT)''')
conn.execute('''CREATE TABLE IF NOT EXISTS pagaron (user_id INTEGER PRIMARY KEY)''')
conn.execute('''CREATE TABLE IF NOT EXISTS invitados (invitado_id INTEGER PRIMARY KEY, referidor_id INTEGER)''')
conn.commit()

# Memoria rápida
VIP_TEMPORAL = {}
DEMO_USADO = set()
ULTIMO_MENSAJE = {}
VIO_PRECIOS = {}
ULTIMO_AVISO_INFO = {}

FOTOS_GRATIS = ["fotitos1.JPG", "fotitos2.JPG", "fotitos3.JPG", "fotitos4.JPG", "fotitos5.JPG", "fotitos6.JPG"]

def normalizar(texto):
    return unicodedata.normalize('NFKD', texto).encode('ascii', 'ignore').decode('ascii').lower()

def get_referido(user_id):
    cur = conn.execute('SELECT contador, link, username FROM referidos WHERE user_id=?', (user_id,))
    return cur.fetchone()

def set_referido(user_id, contador, link, username):
    conn.execute('INSERT OR REPLACE INTO referidos VALUES (?,?,?,?)', (user_id, contador, link, username))
    conn.commit()

def add_pagado(user_id):
    conn.execute('INSERT OR IGNORE INTO pagaron VALUES (?)', (user_id,))
    conn.commit()

def es_pagado(user_id):
    return conn.execute('SELECT 1 FROM pagaron WHERE user_id=?', (user_id,)).fetchone() is not None

def remove_pagado(user_id):
    conn.execute('DELETE FROM pagaron WHERE user_id=?', (user_id,))
    conn.commit()

#... [PE_PRECIOS, MX_PRECIOS, USA_PRECIOS, OTRO_PRECIOS, TEXTO_GRATIS igual que antes]...
PE_PRECIOS = """🛍 PACKS DISPONIBLES - PERÚ 🇵🇪😏\n\n💦 PRUEBA: S/ 5\n🎂 BÁSICO: S/ 10\n🔥 TOP: S/ 20 ← MÁS VENDIDO\n🏆 PREMIUM: S/ 35\n👑 VIP: S/ 50\n\n💳 YAPE/PLIN: 923553612"""
MX_PRECIOS = """🛍 MÉXICO 🇲🇽\nTOP: $145 MXN\nPREMIUM: $230 MXN\nVIP: $320 MXN"""
USA_PRECIOS = """🛍 USA 🇺🇸\nTOP: $7 USD\nPREMIUM: $12 USD\nVIP: $20 USD"""
OTRO_PRECIOS = f"""🛍 INTERNACIONAL 🌎\nTOP: $7 USD\nPayPal: {LINK_PAYPAL}"""
TEXTO_GRATIS = """🔥 VIDEOS GRATIS #HORMO\n5 = 1 videito\n20 = 2-3\n50 = 4-10\n100 = 10-20\n200 = +20 + FETICHE 👑"""

PREMIOS_REFERIDOS = {5:"1 videito 🥵",20:"2-3 videitos 🔥",50:"4-10 videitos 😈",100:"10-20 videitos 🥵",200:"+20 + FETICHE 👑🍑"}

def get_menu():
    return InlineKeyboardMarkup([[InlineKeyboardButton("💎 COMPRAR", callback_data='comprar')],
        [InlineKeyboardButton("🎁 GRATIS", callback_data='gratis')],
        [InlineKeyboardButton("🔗 MI LINK", callback_data='milink')],
        [InlineKeyboardButton("📊 RANKING", callback_data='ranking')],
        [InlineKeyboardButton("🔥 Canal", url=LINK_CANAL)]])

def get_precios_menu():
    return InlineKeyboardMarkup([[InlineKeyboardButton("🇵🇪 Perú", callback_data='pe')],
        [InlineKeyboardButton("🇲🇽 México", callback_data='mx')],
        [InlineKeyboardButton("🇺🇸 USA", callback_data='usa')],
        [InlineKeyboardButton("🌎 Otro", callback_data='otro')],
        [InlineKeyboardButton("⬅️ Volver", callback_data='volver')]])

def get_volver():
    return InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Volver", callback_data='volver')]])

async def avisar_pago(context, user_id, username, nombre, foto_id):
    try:
        await context.bot.send_photo(chat_id=ADMIN_ID, photo=foto_id,
            caption=f"💰 PAGO\n👤 @{username}\n🆔 {user_id}\n⏰ {datetime.now().strftime('%H:%M')}\n\n👉 tg://user?id={user_id}")
    except Exception as e:
        logger.error(e)

async def follow_up_callback(context: ContextTypes.DEFAULT_TYPE):
    job = context.job
    user_id = job.data['user_id']
    if es_pagado(user_id):
        return
    try:
        await context.bot.send_message(chat_id=user_id, text="Oye 😏 ¿sigues ahí? TOP con 2 fotos extra 🎁", reply_markup=get_menu())
    except:
        pass

async def crear_link_referido(context, user_id, username):
    ref = get_referido(user_id)
    if ref:
        return ref[1]
    try:
        link = await context.bot.create_chat_invite_link(chat_id=CANAL_ID, name=f"ref-{user_id}", creates_join_request=False)
        set_referido(user_id, 0, link.invite_link, f"@{username}")
        return link.invite_link
    except Exception as e:
        await context.bot.send_message(user_id, f"❌ Error: {e}")
        return None

async def track_join(update: Update, context: ContextTypes.DEFAULT_TYPE):
    m = update.chat_member
    if m.new_chat_member.status == "member" and m.old_chat_member.status in ["left","kicked"]:
        user = m.new_chat_member.user
        if user.is_bot or not m.invite_link:
            return
        # buscar referidor por link
        cur = conn.execute('SELECT user_id, contador FROM referidos WHERE link=?', (m.invite_link.invite_link,))
        row = cur.fetchone()
        if row:
            ref_id, cont = row
            nuevo = cont + 1
            conn.execute('UPDATE referidos SET contador=? WHERE user_id=?', (nuevo, ref_id))
            conn.execute('INSERT OR REPLACE INTO invitados VALUES (?,?)', (user.id, ref_id))
            conn.commit()
            try:
                await context.bot.send_message(ref_id, f"🔥 +1 | Total: {nuevo}/200")
            except: pass
            if nuevo in PREMIOS_REFERIDOS:
                await context.bot.send_message(ref_id, f"🏆 Premio desbloqueado: {PREMIOS_REFERIDOS[nuevo]}")
                await context.bot.send_message(ADMIN_ID, f"Premio {nuevo} para {ref_id}")
    elif m.new_chat_member.status in ["left","kicked"]:
        user = m.new_chat_member.user
        cur = conn.execute('SELECT referidor_id FROM invitados WHERE invitado_id=?', (user.id,))
        row = cur.fetchone()
        if row:
            ref_id = row[0]
            cur2 = conn.execute('SELECT contador FROM referidos WHERE user_id=?', (ref_id,))
            cont = cur2.fetchone()[0]
            if cont > 0:
                conn.execute('UPDATE referidos SET contador=? WHERE user_id=?', (cont-1, ref_id))
                conn.commit()
                try: await context.bot.send_message(ref_id, f"💔 -1 | Total: {cont-1}/200")
                except: pass
            conn.execute('DELETE FROM invitados WHERE invitado_id=?', (user.id,))
            conn.commit()

async def manejar_todo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message or update.business_message
    if not msg or not msg.from_user or msg.from_user.is_bot:
        return
    user = msg.from_user
    uid = user.id
    if es_pagado(uid) and uid!= ADMIN_ID:
        return
    nombre = user.first_name
    username = user.username or "sin_username"

    if msg.text and msg.text.lower() == '/start':
        await msg.reply_text(f"Hola {nombre} 😏", reply_markup=get_menu())
        return

    if msg.photo:
        if uid == ADMIN_ID: # TÚ mandas foto → no es pago, la reenvía al canal si quieres
            return
        caption = msg.caption or ""
        es_comp = any(x in normalizar(caption) for x in ['pago','yape','plin','comprobante','paypal'])
        if es_comp or not caption:
            add_pagado(uid)
            await avisar_pago(context, uid, username, nombre, msg.photo[-1].file_id)
            await msg.reply_text(f"✅ Pago recibido. Escríbeme al privado {USERNAME_ADMIN}")
        else:
            await msg.reply_text("Linda foto 😏 ¿Quieres comprar?", reply_markup=get_precios_menu())
        return

    if not msg.text:
        return
    texto = msg.text.strip()
    if ULTIMO_MENSAJE.get(uid) == texto.lower():
        return
    ULTIMO_MENSAJE[uid] = texto.lower()

    # AVISO INFO con cooldown 10 min
    if any(x in normalizar(texto) for x in ['info','precio','cuanto','ayuda']) and uid!= ADMIN_ID:
        ahora = datetime.now()
        if uid not in ULTIMO_AVISO_INFO or (ahora - ULTIMO_AVISO_INFO[uid]).seconds > 600:
            await context.bot.send_message(ADMIN_ID, f"🔔 {nombre} (@{username}): {texto}\n👉 tg://user?id={uid}")
            ULTIMO_AVISO_INFO[uid] = ahora

    if 'gratis' in normalizar(texto):
        await msg.reply_text(TEXTO_GRATIS, reply_markup=get_volver())
        return
    if any(x in normalizar(texto) for x in ['comprar','quiero']):
        await msg.reply_text("Elige país 👇", reply_markup=get_precios_menu())
        return
    if 'peru' in normalizar(texto):
        context.job_queue.run_once(follow_up_callback, 1800, data={'user_id': uid}, name=f'fu_{uid}')
        await msg.reply_text(PE_PRECIOS, reply_markup=get_volver())
        return

    await msg.reply_text("Elige opción 👇", reply_markup=get_menu())

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    uid = q.from_user.id
    if q.data == 'comprar':
        await q.edit_message_text("Elige país", reply_markup=get_precios_menu())
    elif q.data == 'pe':
        await q.edit_message_text(PE_PRECIOS, reply_markup=get_volver())
        context.job_queue.run_once(follow_up_callback, 1800, data={'user_id': uid}, name=f'fu_{uid}')
    elif q.data == 'milink':
        link = await crear_link_referido(context, uid, q.from_user.username or "x")
        ref = get_referido(uid)
        cont = ref[0] if ref else 0
        await q.edit_message_text(f"Tu link:\n{link}\n\nLlevas: {cont}/200", reply_markup=get_volver())
    elif q.data == 'ranking':
        cur = conn.execute('SELECT username, contador FROM referidos ORDER BY contador DESC LIMIT 10')
        txt = "🏆 TOP\n" + "\n".join([f"{i+1}. {u} - {c}" for i,(u,c) in enumerate(cur.fetchall())])
        await q.edit_message_text(txt, reply_markup=get_volver())
    elif q.data == 'volver':
        await q.edit_message_text("Menú", reply_markup=get_menu())

async def activar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id!= ADMIN_ID:
        return
    uid = int(context.args[0])
    remove_pagado(uid)
    await update.message.reply_text(f"Reactivado {uid}")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler('activar', activar))
    app.add_handler(CallbackQueryHandler(button))
    app.add_handler(ChatMemberHandler(track_join, ChatMemberHandler.CHAT_MEMBER))
    app.add_handler(MessageHandler(filters.ALL, manejar_todo))
    logger.info("BOT v2 con DB ✅")
    app.run_polling(drop_pending_updates=True, allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
