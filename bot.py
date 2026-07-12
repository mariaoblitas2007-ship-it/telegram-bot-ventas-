# ============================================================
# BOT YANABICITASA - VERSIÓN FINAL EXTENDIDA
# - Perú / México / 🌍 Otros
# - Gratis = 5 fotos QR + mensaje corto
# - Anti-spam = no repite mensajes al mismo chat
# - Falso/fake/estafa = manda al canal
# - Foto/Video Pago = se pausa y te avisa con razón + link directo
# - 100 vistas = te llega botón 📈 y tú envías el mensaje de 500
# - Mensaje 500 ya no dice 20, dice "para soltarte los videitos"
# ============================================================

import os, json, logging, unicodedata, random, re, difflib
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto, Update
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, MessageHandler, filters

logging.basicConfig(level=logging.INFO)

# --- CONFIG ---
TOKEN = '8762577283:AAFVT7_WMpZ7njVnToIlZypUpCToF5LGcbA'
ADMIN_ID = 8783569348
LINK_CANAL = "https://t.me/+zt1RzGevdHBjMDgx"
DATA_FILE = "data.json"

# Memoria en RAM
USUARIOS = {} # {uid: {flags, usados, follow}}
JOBS_FOLLOW = {} # {uid: job}
ESPERA_PAIS = {} # {uid: True} cuando espera que diga de donde es

# ============================================================
# TEXTOS
# ============================================================
SALUDO_NEGOCIO = f"""Wenas mor, ando grabando quieres verme? 🙈🔥

Mi canal donde subo de todo:
{LINK_CANAL}

¿Quieres gratis o comprar? dime mor :3"""

MX_PRECIOS = """🛍 <b>VIDEOS</b> 🛒

🎂 <b>BÁSICO: $100 MXN</b>
→ 5 videitos | $20 c/u
━━━━━━━━━━━━━━
🔥 <b>TOP: $200 MXN ← MÁS VENDIDO</b>
→ 12 videitos | $16 c/u
━━━━━━━━━━━━━━
🏆 <b>PREMIUM: $400 MXN</b>
→ 20 videitos + 1 perso + sexting
━━━━━━━━━━━━━━
📼 <b>VIDEOLLAMADAS</b> $400 5min | $600 10min

<b>PAGO MX - toca para copiar:</b>
🔢 CLABE: <code>646180546711450910</code>
📝 Ref: <code>yanae</code>"""

PE_PRECIOS = """🛍 <b>VIDEOS</b> 🛒

🎂 <b>BÁSICO: S/ 15</b>
→ 5 videitos
━━━━━━━━━━━━━━
🔥 <b>TOP: S/ 30</b>
→ 12 videitos
━━━━━━━━━━━━━━
🏆 <b>PREMIUM: S/ 60</b>
→ 20 videitos + 1 perso + sexting
━━━━━━━━━━━━━━
📼 <b>VIDEOLLAMADAS</b> S/60 5min | S/80 10min

<b>YAPE / PLIN toca para copiar:</b>
<code>923553612</code>"""

USA_PRECIOS = """🛍 <b>VIDEOS</b> 🛒

🎂 <b>BÁSICO: $5 USD</b>
→ 5 videitos
━━━━━━━━━━━━━━
🔥 <b>TOP: $9 USD</b>
→ 12 videitos
━━━━━━━━━━━━━━
🏆 <b>PREMIUM: $20 USD</b>
→ 20 videitos + 1 perso + sexting
━━━━━━━━━━━━━━
📼 <b>VIDEOLLAMADAS</b> $20 5min | $35 10min

<b>PAGO OTROS - toca para copiar:</b>
PayPal: <code>AbigailMaximoofO</code>
Link: <code>https://www.paypal.com/qrcodes/p2pqrc/76RWY9FF7Q7RE</code>"""

GRATIS_TODO = """✨ <b>¿Quieres hasta 20 gratis mor? :3</b> ✨

Solo haz esto mor:
1️⃣ Sube la foto de mi QR a tu story
2️⃣ Comenta cositas hormo en TikToks con #hormo #hot para que te lleguen vistas

Avísame cuando llegues a 100 vistas 🥵
Mándame captura + videito de que lo hiciste"""

# MENSAJE DE 500 - YA SIN DECIR 20
TEXTO_100_A_500 = """Sii mor ya vi que llegaste a 100 🥺✨ pero para soltarte los videitos son 500 vistas mor 🥵

Llegas rápido así mor:
1️⃣ Sigue comentando cositas hormo en TikToks con #hormo #hot (mientras más comentes más vistas te llegan)
2️⃣ Comenta en videos virales que están en Para Ti, ahí subes al toque
3️⃣ Deja tu story con mi QR y pide apoyo

Cuando llegues a 500 me mandas captura + videito sin cortar y te los suelto al toque 😏"""

CUMPLIDO_MSG = "ando algo ocupadita haciéndo videollamada 👀 en un ratito te confirmo mor 🥰"
PAGO_MSG = CUMPLIDO_MSG

# Mensajes con anti-spam (no se repiten)
REAL_MSGS = [
    f"Soy real mor revisa mi canal ahí ves todo sin censura 🥰\n{LINK_CANAL}",
    f"Si soy yo mor entra a mi canal y compruebas que no soy fake 🙈\n{LINK_CANAL}",
    f"Revisa mi canal mor ahí subo diario, verás que soy yo :3\n{LINK_CANAL}"
]
SALIR_MSGS = [
    "Si compras el premium lo pienso mor 🥺 por ahora solo hago virtual 🙈",
    "Lo puedo pensar si compras el premium mor 💖 si eres premium vemos que hacemos :3"
]
FALLBACK_MSGS = [
    "Dime mor quieres gratis o comprar? 🙈 tengo videitos y videollamada",
    "Entonces que dices mor, gratis con QR o comprita? :3",
    "Tu dime mor, ¿gratis de 100 vistas o comprita directa? 🥰"
]
VIDEOLLAMADA_MSGS = ["Videollamadita 🥰 5 y 10 min, si me compras ahora te doy prioridad :3"]

# ============================================================
# FUNCIONES BASE
# ============================================================
def cargar_datos():
    global USUARIOS
    if os.path.exists(DATA_FILE):
        try:
            d = json.load(open(DATA_FILE))
            USUARIOS = {int(k): v for k, v in d.get('usuarios', {}).items()}
        except: pass

def guardar_datos():
    json.dump({'usuarios': USUARIOS}, open(DATA_FILE, 'w'))

def get_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("💎 COMPRAR", callback_data='comprar')],
        [InlineKeyboardButton("🎁 GRATIS", callback_data='gratis')]
    ])

def get_precios():
    # Aquí están los 3 que pediste: Perú, México y Otros
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🇵🇪 Perú", callback_data='pe')],
        [InlineKeyboardButton("🇲🇽 México", callback_data='mx')],
        [InlineKeyboardButton("🌍 Otros", callback_data='usa')]
    ])

def normalizar(t):
    if not t: return ""
    t = unicodedata.normalize('NFKD', t).encode('ascii','ignore').decode().lower()
    return re.sub(r'[^\w\s]', ' ', t)

def detectar_pais(t):
    t = normalizar(t)
    if any(x in t for x in ['peru','pe']): return 'pe'
    if any(x in t for x in ['mexico','mx']): return 'mx'
    if any(x in t for x in ['usa','eeuu','colombia','argentina','chile','otros','dolar','espana']): return 'usa'
    return None

def detectar_intencion(txt, cap=""):
    """Detecta que quiere el cliente"""
    t = normalizar(f"{txt} {cap}")
    # Falso -> lo mandamos al canal (no al fallback)
    if any(x in t for x in ['falso','falsa','fake','estafa','mentira','no eres real','eres bot','robot']):
        return "real"
    if "500" in t and "vist" in t: return "vistas500"
    if "100" in t and "vist" in t: return "vistas100"
    if any(x in t for x in ['ya cumpli','cumpli','ya lo hice','ya esta','termine']): return "cumplido"
    if any(x in t for x in ['yape','plin','pague','pago','comprobante','transfer']): return "pago"
    if any(x in t for x in ['gratis','grtis','promo','regalo']): return "promo"
    if any(x in t for x in ['videollamada','vdeollamada']): return "videollamada"
    if any(x in t for x in ['videitos','precio','cuanto','comprar','pack']): return "comprar"
    if any(x in t for x in ['salidita','salimos','vernos','hotel','presencial','encuentro']): return "salir"
    if any(x in t for x in ['jaja','jeje','jiji','xd','lol']): return "risa"
    return "otro"

def no_repite(uid, tipo, lista):
    """Evita que el bot mande el mismo mensaje 2 veces al mismo chat"""
    USUARIOS[uid].setdefault('usados', {})
    usados = USUARIOS[uid]['usados'].get(tipo, [])
    disp = [m for m in lista if m not in usados]
    if not disp: # si ya los usó todos, resetea
        disp = lista; usados = []
    ch = random.choice(disp)
    usados.append(ch)
    if len(usados) > 5: usados = usados[-5:]
    USUARIOS[uid]['usados'][tipo] = usados
    guardar_datos()
    return ch

def link_directo(uid, un):
    return f"https://t.me/{un}" if un!= "None" else f"tg://user?id={uid}"

def teclado_admin(uid, un):
    url = link_directo(uid, un)
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ Confirmar", callback_data=f"ok_{uid}"),
         InlineKeyboardButton("❌ Pedir prueba", callback_data=f"no_{uid}")],
        [InlineKeyboardButton("🚫 Ban", callback_data=f"ban_{uid}"),
         InlineKeyboardButton("🔗 Abrir Chat", url=url)]
    ])

def teclado_admin_100(uid, un):
    """Teclado especial cuando llega a 100 - con botón para enviar mensaje 500"""
    url = link_directo(uid, un)
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📈 Enviar mensaje 500", callback_data=f"500_{uid}")],
        [InlineKeyboardButton("✅ Ya tiene 500", callback_data=f"ok_{uid}"),
         InlineKeyboardButton("❌ Pedir mejor prueba", callback_data=f"no_{uid}")],
        [InlineKeyboardButton("🚫 Ban", callback_data=f"ban_{uid}"),
         InlineKeyboardButton("🔗 Abrir Chat", url=url)]
    ])

def precio_por_pais(p):
    return PE_PRECIOS if p == 'pe' else MX_PRECIOS if p == 'mx' else USA_PRECIOS

# ============================================================
# ENVÍO DE PROMO CON 5 FOTOS
# ============================================================
async def bienvenida_promo(m):
    try:
        await m.reply_media_group([InputMediaPhoto(open(f'fotitos{i}.JPG','rb')) for i in range(1,6)])
    except:
        try: await m.reply_media_group([InputMediaPhoto(open(f'fotitos{i}.jpg','rb')) for i in range(1,6)])
        except: pass
    await m.reply_text(GRATIS_TODO, parse_mode='HTML')

# ============================================================
# FOLLOW UP (no spamea)
# ============================================================
async def followup_job(c):
    uid = c.job.data['uid']
    if USUARIOS.get(uid,{}).get('flags',{}).get('pausado'): return
    if USUARIOS.get(uid,{}).get('follow',0) >= 2: return
    try:
        await c.bot.send_message(c.job.data['chat_id'], no_repite(uid,'follow',FALLBACK_MSGS))
        USUARIOS[uid]['follow'] = USUARIOS[uid].get('follow',0)+1
        guardar_datos()
    except: pass

JOBS_FOLLOW = {}
def prog_follow(ctx, uid, cid):
    if uid in JOBS_FOLLOW:
        try: JOBS_FOLLOW[uid].schedule_removal()
        except: pass
    JOBS_FOLLOW[uid] = ctx.job_queue.run_once(followup_job, 600, data={'uid':uid,'chat_id':cid})

# ============================================================
# BOTONES
# ============================================================
async def start_cmd(u,c):
    await u.message.reply_text("Hola mor 🥵", reply_markup=get_menu())

async def btn(u,c):
    q = u.callback_query; await q.answer(); d = q.data

    # --- BOTONES DE ADMIN ---
    if q.from_user.id == ADMIN_ID and "_" in d:
        try:
            acc, t = d.split("_", 1); t = int(t)
            if acc == "ok":
                await c.bot.send_message(t, "Listo mor ya te confirmé 💖")
                await q.edit_message_caption(caption=(q.message.caption or "") + "\n✅ CONFIRMADO")
                USUARIOS.setdefault(t,{}).setdefault('flags',{})['pausado'] = False
            elif acc == "no":
                await c.bot.send_message(t, "Mor mándame mejor la pruebita completa porfa 🥺")
                await q.edit_message_caption(caption=(q.message.caption or "") + "\n❌ PEDIDA PRUEBA")
                USUARIOS.setdefault(t,{}).setdefault('flags',{})['pausado'] = False
            elif acc == "500":
                # BOTÓN QUE TÚ PEDISTE: envía el mensaje de 500 al cliente
                await c.bot.send_message(t, TEXTO_100_A_500)
                await q.edit_message_caption(caption=(q.message.caption or "") + f"\n📈 MENSAJE 500 ENVIADO a {t}")
            elif acc == "ban":
                USUARIOS.setdefault(t,{}).setdefault('flags',{})['ban'] = True
                await q.edit_message_caption(caption=(q.message.caption or "") + "\n🚫 BANEADO")
            guardar_datos(); return
        except Exception as e:
            print(f"Error admin btn: {e}"); return

    # --- BOTONES DE CLIENTE ---
    if d == 'comprar':
        await q.edit_message_text("De donde eres mor 👀✨", reply_markup=get_precios())
    elif d in ['pe','mx','usa']:
        await q.edit_message_text(precio_por_pais(d), parse_mode='HTML')
    elif d == 'gratis':
        try: await q.message.reply_media_group([InputMediaPhoto(open(f'fotitos{i}.JPG','rb')) for i in range(1,6)])
        except:
            try: await q.message.reply_media_group([InputMediaPhoto(open(f'fotitos{i}.jpg','rb')) for i in range(1,6)])
            except: pass
        await q.message.reply_text(GRATIS_TODO, parse_mode='HTML')

# ============================================================
# MANEJADOR PRINCIPAL
# ============================================================
async def handle_all(update, context):
    m = update.business_message or update.message
    if not m or not m.from_user or m.from_user.is_bot: return
    uid = m.from_user.id; un = m.from_user.username or "None"
    raw = m.text or ""; cap = getattr(m,'caption','') or ""
    es_neg = update.business_message is not None

    if es_neg and uid == ADMIN_ID: return
    USUARIOS.setdefault(uid, {})

    if USUARIOS[uid].get('flags',{}).get('ban') or USUARIOS[uid].get('flags',{}).get('pausado'):
        return

    if uid in JOBS_FOLLOW:
        try: JOBS_FOLLOW[uid].schedule_removal(); del JOBS_FOLLOW[uid]
        except: pass

    if es_neg:
        # ============ FOTOS / VIDEOS ============
        if m.photo or m.video:
            is_v = bool(m.video); fid = m.video.file_id if is_v else m.photo[-1].file_id
            cap_norm = normalizar(cap + " " + raw)
            es_pago = any(x in cap_norm for x in ['yape','plin','pago','comprobante','transfer'])
            es_100 = "100" in cap_norm
            es_500 = "500" in cap_norm
            link_chat = f"https://t.me/{un}" if un!= "None" else f"tg://user?id={uid}"

            if es_pago:
                txt = f"💰 CAPTURA DE PAGO\n👤 @{un} ID:<code>{uid}</code>\n📝 Razón: Envió comprobante de pago\n🔗 Link: {link_chat}\n💬 {cap or raw}"
                if is_v: await context.bot.send_video(ADMIN_ID, fid, caption=txt, parse_mode='HTML', reply_markup=teclado_admin(uid,un))
                else: await context.bot.send_photo(ADMIN_ID, fid, caption=txt, parse_mode='HTML', reply_markup=teclado_admin(uid,un))
                await m.reply_text(PAGO_MSG)
                USUARIOS[uid].setdefault('flags',{})['pausado'] = True; guardar_datos(); return

            if es_100 and not es_500:
                txt = f"📈 LLEGÓ A 100 VISTAS\n👤 @{un} ID:<code>{uid}</code>\n📝 Razón: Dice que llegó a 100, presiona para enviar mensaje de 500\n🔗 {link_chat}"
                if is_v: await context.bot.send_video(ADMIN_ID, fid, caption=txt, parse_mode='HTML', reply_markup=teclado_admin_100(uid,un))
                else: await context.bot.send_photo(ADMIN_ID, fid, caption=txt, parse_mode='HTML', reply_markup=teclado_admin_100(uid,un))
                # No se pausa, tú decides con el botón
                guardar_datos(); prog_follow(context, uid, m.chat.id); return

            if es_500:
                txt = f"✅ LLEGÓ A 500 VISTAS - ENTREGAR PREMIO\n👤 @{un} ID:<code>{uid}</code>\n🔗 {link_chat}"
                if is_v: await context.bot.send_video(ADMIN_ID, fid, caption=txt, parse_mode='HTML', reply_markup=teclado_admin(uid,un))
                else: await context.bot.send_photo(ADMIN_ID, fid, caption=txt, parse_mode='HTML', reply_markup=teclado_admin(uid,un))
                await m.reply_text(CUMPLIDO_MSG)
                USUARIOS[uid].setdefault('flags',{})['pausado'] = True; guardar_datos(); return

        # ============ TEXTO ============
        intent = detectar_intencion(raw, cap)
        pais = detectar_pais(raw)

        if not USUARIOS[uid].get('flags',{}).get('saludo'):
            await m.reply_text(SALUDO_NEGOCIO)
            USUARIOS[uid].setdefault('flags',{})['saludo'] = True
            guardar_datos(); prog_follow(context, uid, m.chat.id); return

        if uid in ESPERA_PAIS and pais:
            await m.reply_text(precio_por_pais(pais), parse_mode='HTML')
            del ESPERA_PAIS[uid]; guardar_datos(); prog_follow(context, uid, m.chat.id); return

        if intent in ["vistas100","cumplido"]:
            link_chat = f"https://t.me/{un}" if un!= "None" else f"tg://user?id={uid}"
            txt = f"📈 DICE QUE LLEGÓ A 100\n👤 @{un} ID:<code>{uid}</code>\n💬 {raw}\n🔗 {link_chat}\n👉 Presiona para enviar explicación de 500"
            await context.bot.send_message(ADMIN_ID, txt, parse_mode='HTML', reply_markup=teclado_admin_100(uid,un))
            guardar_datos(); return

        if intent == "vistas500":
            await m.reply_text(CUMPLIDO_MSG)
            await context.bot.send_message(ADMIN_ID, f"✅ DICE 500 @{un} {uid}", reply_markup=teclado_admin(uid,un))
            USUARIOS[uid].setdefault('flags',{})['pausado'] = True; guardar_datos(); return

        if intent == "pago":
            await m.reply_text(PAGO_MSG)
            await context.bot.send_message(ADMIN_ID, f"💰 DICE QUE PAGÓ @{un} {uid}\n{raw}", reply_markup=teclado_admin(uid,un))
            USUARIOS[uid].setdefault('flags',{})['pausado'] = True; guardar_datos(); return

        if intent == "real":
            await m.reply_text(no_repite(uid,'real',REAL_MSGS)); guardar_datos(); prog_follow(context,uid,m.chat.id); return
        if intent == "risa":
            await m.reply_text(no_repite(uid,'risa',["jajaja mor 😏 revisa mi canal y verás que no soy fake","😏 entra a mi canal mor ahí estoy subiendo todo"])); guardar_datos(); return
        if intent == "promo": await bienvenida_promo(m)
        elif intent in ["comprar","videollamada"]:
            await m.reply_text("De donde eres mor 👀✨", reply_markup=get_precios()); ESPERA_PAIS[uid]=True
        elif intent == "salir": await m.reply_text(no_repite(uid,'salir',SALIR_MSGS))
        else: await m.reply_text(no_repite(uid,'fallback',FALLBACK_MSGS))

        guardar_datos()
        if intent not in ["risa","real"]: prog_follow(context, uid, m.chat.id)
        return

def main():
    cargar_datos()
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start_cmd))
    app.add_handler(CallbackQueryHandler(btn))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_all))
    app.add_handler(MessageHandler(filters.UpdateType.BUSINESS_MESSAGE, handle_all))
    app.add_handler(MessageHandler(filters.PHOTO | filters.VIDEO, handle_all))
    app.add_handler(MessageHandler(filters.UpdateType.BUSINESS_MESSAGE & (filters.PHOTO | filters.VIDEO), handle_all))
    app.add_handler(MessageHandler(filters.CAPTION & filters.UpdateType.BUSINESS_MESSAGE, handle_all))
    print("Bot final extendido listo: 3 países + 5 fotos + botón 500 + anti-spam + link directo")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__': main()
