import os, json, logging, unicodedata
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, filters, ContextTypes, ChatMemberHandler, TypeHandler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ===== CONFIG =====
TOKEN = '8762577283:AAFVT7_WMpZ7njVnToIlZypUpCToF5LGcbA'
ADMIN_ID = 8783569348
LINK_CANAL = "https://t.me/+zt1RzGevdHBjMDgx"
LINK_PAYPAL = "https://www.paypal.com/qrcodes/p2pqrc/76RWY9FF7Q7RE"

USUARIOS = {}
PAGARON = set()
REFERIDOS = {}
INVITADOS = {}
ESPERA_PAIS = {}
DATA_FILE = "data.json"

try:
    import pytesseract
    from PIL import Image
    HAS_OCR = True
except:
    HAS_OCR = False

def cargar_datos():
    global USUARIOS, PAGARON, REFERIDOS, INVITADOS
    if os.path.exists(DATA_FILE):
        d = json.load(open(DATA_FILE))
        USUARIOS = {int(k):v for k,v in d.get('usuarios',{}).items()}
        PAGARON = set(d.get('pagaron',[]))
        REFERIDOS = {int(k):v for k,v in d.get('referidos',{}).items()}
        INVITADOS = {int(k):v for k,v in d.get('invitados',{}).items()}

def guardar_datos():
    json.dump({'usuarios':USUARIOS,'pagaron':list(PAGARON),'referidos':REFERIDOS,'invitados':INVITADOS}, open(DATA_FILE,'w'))

# ===== TEXTOS =====
MX_PRECIOS = """🛍 VIDEOS 🛒

🎂 BÁSICO: $ 100 MXN
→ 5 vds | $20 c/u

🔥 TOP: $200 MXN ← MÁS VENDIDO
→ 12 vds | $16 c/u
→ Ahorras 50%

🏆 PREMIUM: $400 MXN
→ 1 personalizado + 20 vds
→ incluye sexting 🥰
→ Ahorras 80%

📼 VIDEOLLAMADAS 📼
$400 MXN: 5 min
$600 MXN: 10 min

🛍 PAGO MXN:
🏦 Banco: STP
🔢 CLABE:
646180546711450910
📝 Referencia/Concepto: yanae

🇲🇽 También acepto: Transfer / Astropay
→ Pídeme datos si usas otro método

Mándame captura cuando pagues bebé 🥰
En cuanto caiga te mando tu pack 🔥

1. Pagas 2. Captura

Si no contesto envías cap del pago a : @YanaBiBot con estos precios."""

PE_PRECIOS = """🛍 VIDEOS 🛒

🎂 BÁSICO: S/ 15
→ 5 vds | S/ 3 c/u

🔥 TOP: S/ 30 ← MÁS VENDIDO
→ 12 vds | S/ 2.50 c/u
→ Ahorras 50%

🏆 PREMIUM: S/ 60
→ 1 personalizado + 20 vds
→ incluye sexting 🥰
→ Ahorras 67%

📼 VIDEOLLAMADAS 📼
S/ 60: 5 min
S/ 80: 10 min

━━━━━━━━━━━━━━━━━━━━

923553612

YAPE/PLIN

CUENTO CON REFERENCIAS

1. Yapeas 2. Captura

Si no contesto envías cap del pago a : @YanaBiBot con estos precios."""

USA_PRECIOS = f"""🛍 VIDEOS 🛒

🎂 BÁSICO: $5 USD
→ 5 vds | $1 c/u

🔥 TOP: $9 USD ← MÁS VENDIDO
→ 12 vds | $0.75 c/u
→ Ahorras 50%

🏆 PREMIUM: $20 USD
→ 1 personalizado + 20 vds
→ incluye sexting 🥰
→ Ahorras 60%

📼 VIDEOLLAMADAS 📼
$20 USD: 5min
$35 USD: 10min

🪙 PAGO:
PayPal:
AbigailMaximoofO
/ USDT
Link: {LINK_PAYPAL}

Avísame cuando envíes con el comprobante 🥰
En cuanto caiga te mando tu pack 🔥

1. Pagas 2. Captura

Si no contesto envías cap del pago a : @YanaBiBot con estos precios."""

GRATIS_TEXTO = "✨ (REGALITO) QUIERES HASTA 20 VIDEITOS GRATSS? ✨\n\nhttps://t.me/YanaBiBot\n\nPasitos súper fáciles uwu:\n1️⃣ En tu bio de TikTok pon: Tg: yanabicitasa ✨\n2️⃣ Sube una fotito de las que te envié a tu story + Frase hot 😋\n3️⃣ Mándame captura + videito cuando cumplas\n4️⃣ Me confirmas cuando llegue a 100 vistas (story) :3\n5️⃣ Disfruta de hasta 20 videitos :3 ❤️\n\n¿Te animas o ño? 🥺\n(Me avisas cuando cumplas Mor)"

EJEMPLO_TEXTO = "Wenas Mor, tengo varios videitos cogiendo, masturbándome, con juguetitos y mis deditos, también tengo manoseándome las tetas, y puedo cumplir fetiche dependiendo lo que envíes :3 🥵\n\n¿Quieres que te pase precios?"

def get_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("💎 COMPRAR",callback_data='comprar')],
        [InlineKeyboardButton("🎁 GRATIS",callback_data='gratis')],
        [InlineKeyboardButton("🔗 MI LINK",callback_data='milink')],
        [InlineKeyboardButton("📊 RANKING",callback_data='ranking')],
        [InlineKeyboardButton("🔥 Canal",url=LINK_CANAL)]
    ])

def get_precios():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🇵🇪 Perú",callback_data='pe')],
        [InlineKeyboardButton("🇲🇽 México",callback_data='mx')],
        [InlineKeyboardButton("🇺🇸 EEUU",callback_data='usa')]
    ])

def normalizar(t):
    return unicodedata.normalize('NFKD',t or '').encode('ascii','ignore').decode().lower()

def precio_por_pais(pais):
    if pais == 'pe': return PE_PRECIOS
    if pais == 'mx': return MX_PRECIOS
    return USA_PRECIOS

def detectar_pais(t):
    t = normalizar(t)
    if any(x in t for x in ['peru','perú']): return 'pe'
    if any(x in t for x in ['mex','mexico','méxico']): return 'mx'
    if any(x in t for x in ['usa','eeuu','ee uu','estados unidos','united','america']): return 'usa'
    if any(x in t for x in ['colombia','argentina','chile','ecuador','venezuela','bolivia','españa','spain']): return 'usa'
    return None

async def notificar_admin(tipo, uid, user, extra=""):
    username = f"@{user}" if user else "sin @"
    url = f"https://t.me/{user}" if user else f"tg://user?id={uid}"
    caption = f"{tipo}\n👤 {username}\n🆔 <code>{uid}</code>\n{extra}"
    kb = InlineKeyboardMarkup([[InlineKeyboardButton("🔗 ABRIR CHAT", url=url)]])
    try:
        await app_bot.send_message(ADMIN_ID, caption, reply_markup=kb, parse_mode='HTML')
    except:
        await app_bot.send_message(ADMIN_ID, caption, parse_mode='HTML')

async def analizar_foto(ctx, uid, user, fid):
    try:
        username = f"@{user}" if user else "sin @"
        url = f"https://t.me/{user}" if user else f"tg://user?id={uid}"
        caption = f"FOTO RECIBIDA\n👤 {username}\n🆔 <code>{uid}</code>"
        kb = InlineKeyboardMarkup([[InlineKeyboardButton("🔗 ABRIR CHAT", url=url)]])
        await ctx.bot.send_photo(ADMIN_ID, fid, caption=caption, reply_markup=kb, parse_mode='HTML')
        f = await ctx.bot.get_file(fid)
        p = f"/tmp/{fid}.jpg"
        await f.download_to_drive(p)
        txt = ""
        if HAS_OCR:
            try: txt = pytesseract.image_to_string(Image.open(p)).lower()
            except: pass
        if any(k in txt for k in ['yape','plin','paypal','banco','clabe','stp','abigail','maximoof','pago','comprobante']):
            if uid not in PAGARON:
                PAGARON.add(uid); guardar_datos()
                await ctx.bot.send_message(ADMIN_ID, "💰 Posible PAGO detectado")
    except Exception as e:
        logger.error(e)

async def analizar_video(ctx, uid, user, fid):
    try:
        username = f"@{user}" if user else "sin @"
        url = f"https://t.me/{user}" if user else f"tg://user?id={uid}"
        caption = f"VIDEO RECIBIDO\n👤 {username}\n🆔 <code>{uid}</code>"
        kb = InlineKeyboardMarkup([[InlineKeyboardButton("🔗 ABRIR CHAT", url=url)]])
        await ctx.bot.send_video(ADMIN_ID, fid, caption=caption, reply_markup=kb, parse_mode='HTML')
    except Exception as e:
        logger.error(e)

async def enviar_gratis(m):
    try:
        await m.reply_media_group([
            InputMediaPhoto(open('fotitos1.JPG','rb')),
            InputMediaPhoto(open('fotitos2.JPG','rb')),
            InputMediaPhoto(open('fotitos3.JPG','rb')),
            InputMediaPhoto(open('fotitos4.JPG','rb')),
            InputMediaPhoto(open('fotitos5.JPG','rb'))
        ])
    except: pass
    await m.reply_text(GRATIS_TEXTO)

async def start_cmd(upd, ctx):
    await upd.message.reply_text("Hola mor 🥵 bienvenido, elige:", reply_markup=get_menu())

async def recordar(context):
    job = context.job
    uid = job.data['uid']
    chat_id = job.data['chat_id']
    if uid in PAGARON: return
    if USUARIOS.get(uid,{}).get('respondio'): return
    try:
        await context.bot.send_message(chat_id, "Mor ¿sigues ahí? 👀 el PREMIUM está con descuento hoy, ¿te lo paso?")
    except: pass

async def todo(upd, ctx):
    global app_bot; app_bot = ctx.bot
    m = upd.message or upd.business_message
    if not m or m.from_user.is_bot: return
    uid = m.from_user.id
    if uid not in USUARIOS: USUARIOS[uid] = {}
    USUARIOS[uid]['n'] = m.from_user.first_name
    USUARIOS[uid]['respondio'] = True
    guardar_datos()
    es_neg = upd.business_message is not None
    txt = normalizar(m.text)
    raw = m.text or ""
    def tiene(lista): return any(p in txt for p in lista)

    PRECIOS = ['precio','precios','costo','cuanto','cuánto','vale','valor','tarifa','cuesta','info','porfa','cumpli','cumplii','oyee','video','vidy','publicidad']
    PROMO = ['promo','promocion','promoción','gratis','free','regalo']
    PREMIUM = ['premium','premiun']
    PAGO = ['ya pague','pague','pagué','comprobante','transferi','deposite','pago realizado','ya quedo','listo','pagado']
    ENCUENTRO = ['encuentro','encuentros','cita','citas','salida','salidas','en persona','presencial','vernos','conocernos']

    if es_neg:
        if uid == ADMIN_ID: return
        if uid in PAGARON:
            if m.photo: await analizar_foto(ctx, uid, m.from_user.username or '', m.photo[-1].file_id)
            if m.video: await analizar_video(ctx, uid, m.from_user.username or '', m.video.file_id)
            return
        if uid in ESPERA_PAIS:
            pais = detectar_pais(txt) or 'usa'
            USUARIOS[uid]['pais'] = pais
            await m.reply_text(f"Perfecto mor 🥰 estos son para {'Perú' if pais=='pe' else 'México' if pais=='mx' else 'EEUU'}:")
            await m.reply_text(precio_por_pais(pais))
            if not USUARIOS[uid].get('canal'):
                await m.reply_text(f"Únete a mi canal privado aquí mor 🔥 {LINK_CANAL}"); USUARIOS[uid]['canal']=True
            USUARIOS[uid]['atendido']=True; USUARIOS[uid]['respondio']=False; USUARIOS[uid]['saludo_enviado']=True
            guardar_datos()
            ctx.job_queue.run_once(recordar, 180, data={'uid':uid,'chat_id':m.chat.id}, name=f"rec_{uid}")
            del ESPERA_PAIS[uid]; return

        pais_directo = detectar_pais(txt)
        if pais_directo and not USUARIOS[uid].get('pais'):
            USUARIOS[uid]['pais'] = pais_directo; guardar_datos()

        if tiene(PAGO):
            PAGARON.add(uid); guardar_datos()
            await notificar_admin("💰 PAGO", uid, m.from_user.username, f"💬 {raw[:50]}")
            return

        # >>> NUEVO: FOTO/VIDEO = reenvía y bloquea para siempre
        if m.photo:
            await analizar_foto(ctx, uid, m.from_user.username or '', m.photo[-1].file_id)
            USUARIOS[uid]['atendido'] = True
            USUARIOS[uid]['saludo_enviado'] = True
            guardar_datos()
            return
        if m.video:
            await analizar_video(ctx, uid, m.from_user.username or '', m.video.file_id)
            USUARIOS[uid]['atendido'] = True
            USUARIOS[uid]['saludo_enviado'] = True
            guardar_datos()
            return

        if tiene(ENCUENTRO):
            await m.reply_text("Los encuentros son SOLO con PREMIUM mor 😏 incluye videollamada + personalizado. ¿Te paso el PREMIUM?"); return
        if tiene(PROMO): await enviar_gratis(m); return
        if 'sexting' in txt: await m.reply_text("Sexting va en el PREMIUM mor 🥵 ¿lo quieres?"); return

        if USUARIOS[uid].get('atendido'): return

        if not USUARIOS[uid].get('saludo_enviado'):
            await m.reply_text(EJEMPLO_TEXTO)
            USUARIOS[uid]['saludo_enviado'] = True; guardar_datos()
            ESPERA_PAIS[uid] = True
            await m.reply_text("Dime de dónde eres mor?\n🇵🇪 Perú\n🇲🇽 México\n🇺🇸 Otro país")
            return

        pais = USUARIOS[uid].get('pais')
        if not pais:
            ESPERA_PAIS[uid] = True
            await m.reply_text("Claro mor 🥵 primero dime ¿de dónde eres?\n🇵🇪 Perú\n🇲🇽 México\n🇺🇸 Otro país")
            return
        await m.reply_text(precio_por_pais(pais))
        USUARIOS[uid]['atendido']=True; USUARIOS[uid]['respondio']=False; guardar_datos()
        ctx.job_queue.run_once(recordar, 180, data={'uid':uid,'chat_id':m.chat.id}, name=f"rec_{uid}")
        return

    if m.chat.type == 'private':
        await m.reply_text("Elige:", reply_markup=get_menu())

async def btn(upd, ctx):
    q = upd.callback_query; await q.answer()
    if q.data == 'comprar': await q.edit_message_text("Elige tu país:", reply_markup=get_precios())
    elif q.data == 'pe': await q.edit_message_text(PE_PRECIOS)
    elif q.data == 'mx': await q.edit_message_text(MX_PRECIOS)
    elif q.data == 'usa': await q.edit_message_text(USA_PRECIOS)
    elif q.data == 'gratis': await q.edit_message_text("Escribe 'gratis' a @yanabicitasa")
    elif q.data == 'milink':
        link = f"https://t.me/YanaBiBot?start={q.from_user.id}"
        REFERIDOS[q.from_user.id] = {'link': link}; guardar_datos()
        await q.edit_message_text(f"Tu link:\n{link}")
    elif q.data == 'ranking':
        top = sorted(INVITADOS.items(), key=lambda x: x[1], reverse=True)[:5]
        txt = "TOP:\n" + "\n".join([f"{i+1}. {USUARIOS.get(u,{}).get('n','?')} - {c}" for i,(u,c) in enumerate(top)])
        await q.edit_message_text(txt)

async def nuevo(upd, ctx):
    cm = upd.chat_member
    if cm.old_chat_member.status in ['left','kicked'] and cm.new_chat_member.status == 'member':
        if not cm.new_chat_member.user.is_bot:
            inviter = cm.from_user.id
            INVITADOS[inviter] = INVITADOS.get(inviter, 0) + 1
            guardar_datos()

def main():
    cargar_datos()
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start_cmd))
    app.add_handler(TypeHandler(Update, todo))
    app.add_handler(CallbackQueryHandler(btn))
    app.add_handler(ChatMemberHandler(nuevo, ChatMemberHandler.CHAT_MEMBER))
    app.run_polling(allowed_updates=['message','business_message','callback_query','chat_member'])

if __name__ == '__main__':
    main()
