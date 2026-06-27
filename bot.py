import os, sys, asyncio, random, logging, unicodedata, signal, re
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, MessageHandler, CallbackQueryHandler, CommandHandler, filters, ContextTypes, ChatMemberHandler
from telegram.error import Forbidden

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

TOKEN = '8762577283:AAGyirGjyF6CkPFMzh-i4-2w1NpHz93fqIg'
ADMIN_ID = 8783569348
USERNAME_ADMIN = "@yanabicitasa"
CANAL_ID = -1004473732783

LINK_CANAL = "https://t.me/+ZWc0FAcw-hQ2MDZh"
LINK_PAYPAL = "https://www.paypal.com/qrcodes/p2pqrc/76RWY9FF7Q7RE"

VIP_TEMPORAL, DEMO_USADO, USUARIOS, PAGARON = {}, set(), {}, set()
ULTIMO_MENSAJE, FOLLOWUP_ENVIADO = {}, set()
REFERIDOS, INVITACIONES, INVITADOS = {}, {}, {}

FOTOS_GRATIS = ["fotitos1.JPG","fotitos2.JPG","fotitos3.JPG","fotitos4.JPG","fotitos5.JPG","fotitos6.JPG"]

# === PRECIOS ACTUALIZADOS ===
PE_PRECIOS = """
🛍 PACKS DISPONIBLES - PERÚ 🇵🇪😏

💦 PRUEBA: S/ 5
→ 3 fotitos
→ Para que me conozcas 🙈

🎂 BÁSICO: S/ 10
→ 6 unidades
→ +1 foto extra HOY

🔥 TOP: S/ 20 ← MÁS VENDIDO
→ 12 unidades
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
S/ 30: 5 min 😈
S/ 50: 10 min + 3 fotos

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
→ 3 fotitos
→ Para que me conozcas 🙈

🎂 BÁSICO: $90 MXN
→ 6 unidades
→ +1 foto extra HOY

🔥 TOP: $145 MXN ← MÁS VENDIDO
→ 12 unidades
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
$205 MXN: 5 min 😈
$320 MXN: 10 min + 3 fotos

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
→ 3 fotitos
→ Para que me pruebes 🙈

🎂 BÁSICO: $3.50 USD
→ 6 unidades
→ +1 foto extra HOY

🔥 TOP: $7 USD ← MÁS VENDIDO
→ 12 unidades
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
$10 USD: 5 min 😈
$20 USD: 10 min + 3 fotos

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
→ 3 fotitos
→ Para que me conozcas 🙈

🎂 BÁSICO: $3.50 USD
→ 6 unidades
→ +1 foto extra HOY

🔥 TOP: $7 USD ← MÁS VENDIDO
→ 12 unidades
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
$10 USD: 5 min 😈
$20 USD: 10 min + 3 fotos

🪙 PAGO:
PayPal: {LINK_PAYPAL}
/ USDT disponible

Avísame cuando envíes con el comprobante 😊
"""

TEXTO_GRATIS = """📸 GRATIS 🥺💋

✨ QUIERES HASTA 20 VIDEITOS GRATIS? ✨
Es por promocionarme en TikTok ✅

Pasitos súper fáciles uwu:
1️⃣ Ponte un nombrecito + fotito tierna <33
2️⃣ En tu bio pon: Tg: yanabicitasa ✨
3️⃣ Sube una fotito a tu story + frasita hot 😋
4️⃣ Comenta coshitas en videos hot, unos 30-100 👀
   Así generamos vistas juntos
5️⃣ Mándame captura + videito cuando termines
6️⃣ Disfruta de hasta 20 videitos :3 ❤️‍🔥

¿Te animas o ño? 🥺
(Me avisas cuando cumplas mi rey)"""

TEXTO_NIVELES = """🔥 VIDEOS GRATIS #HORMO - SÚBEME LA TEMP 🔥

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

Saca tu link en "🔗 MI LINK" y ponte a reclutar #HORMOS 😏"""

PREMIOS_REFERIDOS = {5:"1 videito pa calentar 🥵",20:"2-3 videitos... ya me mojo 🔥",50:"4-10 videitos 😈 te dejo sin aire",100:"10-20 videitos 🥵 ya soy tuya",200:"+20 videitos + VIDEO FETICHE 👑🍑"}

def get_menu(): return InlineKeyboardMarkup([[InlineKeyboardButton("💎 COMPRAR PACKS", callback_data='comprar')],[InlineKeyboardButton("🎁 GRATIS - Misiones", callback_data='gratis')],[InlineKeyboardButton("🔗 MI LINK - Referidos", callback_data='milink')],[InlineKeyboardButton("📊 RANKING", callback_data='ranking')],[InlineKeyboardButton("🔥 Canal Oficial", url=LINK_CANAL)]])
def get_precios_menu(): return InlineKeyboardMarkup([[InlineKeyboardButton("🇵🇪 Perú", callback_data='pe')],[InlineKeyboardButton("🇲🇽 México", callback_data='mx')],[InlineKeyboardButton("🇺🇸 USA/Otros", callback_data='usa')],[InlineKeyboardButton("🌎 Internacional", callback_data='otro')],[InlineKeyboardButton("⬅️ Volver", callback_data='volver')]])
def get_volver(): return InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Volver al Menú", callback_data='volver')]])
def normalizar(t): return unicodedata.normalize('NFKD', t).encode('ascii','ignore').decode('ascii').lower()
def registrar_usuario(u): USUARIOS[u.id] = {'nombre': u.first_name, 'username': u.username or "sin_username"}

async def avisar_pago(ctx, uid, user, nombre, fid):
    try: await ctx.bot.send_photo(ADMIN_ID, fid, caption=f"💰 PAGO\n👤 @{user}\n🆔 {uid}\n👉 tg://user?id={uid}")
    except: pass

async def follow_up(ctx: ContextTypes.DEFAULT_TYPE):
    uid = ctx.job.data['uid']
    if uid in PAGARON or uid in FOLLOWUP_ENVIADO: return
    FOLLOWUP_ENVIADO.add(uid)
    try: await ctx.bot.send_message(uid, "Oye 😏 ¿sigues ahí? TOP con 2 extras 🎁", reply_markup=get_menu())
    except: pass

async def crear_link_referido(ctx, uid, username):
    try:
        if uid in REFERIDOS: return REFERIDOS[uid]['link']
        inv = await ctx.bot.create_chat_invite_link(CANAL_ID, name=f"ref{uid}", creates_join_request=False)
        REFERIDOS[uid] = {'link': inv.invite_link, 'contador': 0, 'username': f"@{username}"}
        INVITACIONES[inv.invite_link] = uid
        return inv.invite_link
    except Exception as e:
        logger.error(e)
        try: await ctx.bot.send_message(ADMIN_ID, f"⚠️ Error link @{username}: {e}")
        except: pass
        return None

async def chequear_premio(ctx, uid):
    if uid not in REFERIDOS: return
    c = REFERIDOS[uid]['contador']
    if c in PREMIOS_REFERIDOS:
        try: await ctx.bot.send_message(uid, f"🏆 Meta {c}!\nPremio: {PREMIOS_REFERIDOS[c]}")
        except: pass
        await ctx.bot.send_message(ADMIN_ID, f"Premio {c} para {REFERIDOS[uid]['username']}")

async def enviar_gratis(cid, ctx):
    await ctx.bot.send_message(cid, TEXTO_GRATIS, reply_markup=get_volver())
    await asyncio.sleep(0.5)
    for f in FOTOS_GRATIS:
        try:
            with open(f, 'rb') as ph: await ctx.bot.send_photo(cid, ph)
            await asyncio.sleep(0.4)
        except: continue

async def track_join(upd: Update, ctx: ContextTypes.DEFAULT_TYPE):
    r = upd.chat_member
    if r.new_chat_member.status == "member" and r.invite_link and r.invite_link.invite_link in INVITACIONES:
        ref = INVITACIONES[r.invite_link.invite_link]
        if ref in REFERIDOS:
            REFERIDOS[ref]['contador'] += 1
            INVITADOS[r.new_chat_member.user.id] = ref
            try: await ctx.bot.send_message(ref, f"🔥 +1 | Total: {REFERIDOS[ref]['contador']}/200")
            except: pass
            await chequear_premio(ctx, ref)
    elif r.new_chat_member.status in ["left","kicked"]:
        u = r.new_chat_member.user
        if u.id in INVITADOS:
            ref = INVITADOS[u.id]
            if ref in REFERIDOS and REFERIDOS[ref]['contador']>0: REFERIDOS[ref]['contador'] -= 1
            del INVITADOS[u.id]

async def manejar_todo(upd: Update, ctx: ContextTypes.DEFAULT_TYPE):
    m = upd.message or upd.business_message
    if not m or not m.from_user or m.from_user.is_bot: return
    uid = m.from_user.id
    if uid in PAGARON and uid!= ADMIN_ID: return
    registrar_usuario(m.from_user)
    name = m.from_user.first_name
    user = m.from_user.username or "x"

    if m.text and m.text.lower() == '/start':
        await m.reply_text(f"Mmmm {name}... 😏✨", reply_markup=get_menu())
        return
    if m.text and '/milink' in m.text.lower():
        link = await crear_link_referido(ctx, uid, user)
        if link:
            c = REFERIDOS[uid]['contador']
            await m.reply_text(f"{TEXTO_NIVELES}\n\n🔗 TU LINK:\n{link}\n\n📊 Llevas: {c}/200", reply_markup=get_volver())
        else: await m.reply_text("😏 Preparando link...", reply_markup=get_volver())
        return
    if m.photo:
        if uid == ADMIN_ID: return
        PAGARON.add(uid)
        await avisar_pago(ctx, uid, user, name, m.photo[-1].file_id)
        await m.reply_text(f"✅ Pago recibido. Escríbeme {USERNAME_ADMIN}")
        return
    if not m.text: return
    txt = m.text.lower()
    if ULTIMO_MENSAJE.get(uid) == txt: return
    ULTIMO_MENSAJE[uid] = txt

    if any(x in normalizar(txt) for x in ['gratis','free','regalo']):
        await enviar_gratis(uid, ctx); return
    if any(x in txt for x in ['comprar','quiero','pago']):
        await m.reply_text("Elige país:", reply_markup=get_precios_menu()); return
    if 'peru' in normalizar(txt) or 'soles' in txt:
        ctx.job_queue.run_once(follow_up, 1800, data={'uid':uid})
        await m.reply_text(PE_PRECIOS, reply_markup=get_volver()); return
    await m.reply_text("Elige:", reply_markup=get_menu())

async def button(upd: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = upd.callback_query; await q.answer()
    uid = q.from_user.id; d = q.data
    if d == 'comprar': await q.edit_message_text("💎 ELIGE TU PAÍS 💎", reply_markup=get_precios_menu())
    elif d == 'pe': await q.edit_message_text(PE_PRECIOS, reply_markup=get_volver()); ctx.job_queue.run_once(follow_up, 1800, data={'uid':uid})
    elif d == 'mx': await q.edit_message_text(MX_PRECIOS, reply_markup=get_volver())
    elif d == 'usa': await q.edit_message_text(USA_PRECIOS, reply_markup=get_volver())
    elif d == 'otro': await q.edit_message_text(OTRO_PRECIOS, reply_markup=get_volver())
    elif d == 'gratis':
        await q.edit_message_text("Cargando misiones...", reply_markup=get_volver())
        await enviar_gratis(uid, ctx)
    elif d == 'milink':
        link = await crear_link_referido(ctx, uid, q.from_user.username or "x")
        if link:
            c = REFERIDOS[uid]['contador']
            await q.edit_message_text(f"{TEXTO_NIVELES}\n\n🔗 TU LINK:\n{link}\n\n📊 Llevas: {c}/200", reply_markup=get_volver())
        else: await q.edit_message_text("😏 Preparando link...", reply_markup=get_volver())
    elif d == 'ranking':
        if not REFERIDOS: await q.edit_message_text("Aún no hay referidos", reply_markup=get_volver())
        else:
            top = sorted(REFERIDOS.items(), key=lambda x: x[1]['contador'], reverse=True)[:10]
            txt = "🏆 TOP REFERIDOS\n\n" + "\n".join([f"{i+1}. {d['username']} - {d['contador']}" for i,(u,d) in enumerate(top)])
            await q.edit_message_text(txt, reply_markup=get_volver())
    elif d == 'volver': await q.edit_message_text("¿Qué se te antoja? 👇", reply_markup=get_menu())

async def vip(u,c):
    if u.effective_user.id!= ADMIN_ID: return
    uid=int(c.args[0]); VIP_TEMPORAL[uid]=datetime.now()+timedelta(minutes=15)
    await c.bot.send_message(uid,"✅ VIP"); await u.message.reply_text("OK")

async def activar(u,c):
    if u.effective_user.id!= ADMIN_ID: return
    uid=int(c.args[0])
    if uid in PAGARON: PAGARON.remove(uid)
    await c.bot.send_message(uid,"Bot reactivado"); await u.message.reply_text("OK")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler('vip', vip))
    app.add_handler(CommandHandler('activar', activar))
    app.add_handler(CallbackQueryHandler(button))
    app.add_handler(ChatMemberHandler(track_join, ChatMemberHandler.CHAT_MEMBER))
    app.add_handler(MessageHandler(filters.ALL, manejar_todo))
    logger.info("BOT PRENDIDO ✅")
    app.run_polling(drop_pending_updates=True, allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__': main()
