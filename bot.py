import os, json, logging, unicodedata
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from telegram.ext import Application, MessageHandler, CallbackQueryHandler, filters, ContextTypes, ChatMemberHandler

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

COMENTA_TEXTO = "Busca videos con #hormo #hot #hormonal #amigoshormo y deja comentarios bien ricos 🥵\n\nEscribe cositas como: \"¿quién?\", \"¿alguno?\", \"miren mi story\", \"ando horm...\"\n\nEntre más caliente comentes, más gente entra a verte, bebé 😏"

# ✅ TU TEXTO DE EJEMPLO
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

def es_precio(t):
    return any(p in normalizar(t) for p in ['precio','precios','costo','cuanto','cuánto','vale','valor'])

def precio_por_pais(pais):
    if pais == 'pe': return PE_PRECIOS
    if pais == 'mx': return MX_PRECIOS
    return USA_PRECIOS

async def notificar_admin(tipo, uid, user, extra=""):
    username = f"@{user}" if user else "sin @"
    link = f"https://t.me/{user}" if user else f"tg://user?id={uid}"
    caption = f"{tipo}\n👤 {username}\n🆔 <code>{uid}</code>\n🔗 <a href='{link}'>ABRIR CHAT</a>\n{extra}"
    await app_bot.send_message(ADMIN_ID, caption, parse_mode='HTML')

async def analizar_foto(ctx, uid, user, fid):
    try:
        username = f"@{user}" if user else "sin @"
        link = f"https://t.me/{user}" if user else f"tg://user?id={uid}"
        caption = f"FOTO RECIBIDA\n👤 {username}\n🆔 <code>{uid}</code>\n🔗 <a href='{link}'>ABRIR CHAT</a>"
        await ctx.bot.send_photo(ADMIN_ID, fid, caption=caption, parse_mode='HTML')
        f = await ctx.bot.get_file(fid)
        p = f"/tmp/{fid}.jpg"
        await f.download_to_drive(p)
        txt = ""
        if HAS_OCR:
            try: txt = pytesseract.image_to_string(Image.open(p)).lower()
            except: pass
        if any(k in txt for k in ['yape','plin','paypal','banco','clabe','stp','abigail','maximoof','pago','comprobante']):
            PAGARON.add(uid); guardar_datos()
            await ctx.bot.send_message(ADMIN_ID, "💰 Posible PAGO detectado")
    except Exception as e:
        logger.error(e)

async def analizar_video(ctx, uid, user, fid):
    try:
        username = f"@{user}" if user else "sin @"
        link = f"https://t.me/{user}" if user else f"tg://user?id={uid}"
        caption = f"VIDEO RECIBIDO\n👤 {username}\n🆔 <code>{uid}</code>\n🔗 <a href='{link}'>ABRIR CHAT</a>"
        await ctx.bot.send_video(ADMIN_ID, fid, caption=caption, parse_mode='HTML')
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

async def todo(upd, ctx):
    global app_bot; app_bot = ctx.bot
    m = upd.message or upd.business_message
    if not m or m.from_user.is_bot: return
    uid = m.from_user.id
    if uid not in USUARIOS: USUARIOS[uid] = {}
    USUARIOS[uid]['n'] = m.from_user.first_name
    guardar_datos()
    es_neg = upd.business_message is not None
    txt = normalizar(m.text)
    raw = m.text or ""

    if es_neg:
        if uid == ADMIN_ID: return

        if uid in ESPERA_PAIS:
            if 'peru' in txt or '🇵🇪' in raw: pais='pe'
            elif 'mex' in txt or '🇲🇽' in raw: pais='mx'
            else: pais='usa'
            USUARIOS[uid]['pais']=pais; guardar_datos()
            await m.reply_text(precio_por_pais(pais))
            del ESPERA_PAIS[uid]; return

        pais_detectado = None
        if 'peru' in txt or '🇵🇪' in raw: pais_detectado = 'pe'
        elif 'mex' in txt or 'mexico' in txt or '🇲🇽' in raw: pais_detectado = 'mx'
        elif any(p in txt for p in ['usa','eeuu','estados','chile','colombia','argentina','ecuador','venezuela','bolivia']) or '🇺🇸' in raw: pais_detectado = 'usa'
        if pais_detectado:
            USUARIOS[uid]['pais'] = pais_detectado
            guardar_datos()
            await m.reply_text(precio_por_pais(pais_detectado))
            return

        if any(k in txt for k in ['ya lo hice','ya lo hise','ya te mande','te mande la cap','mira tengo','ya tengo una','jakajs','jajs','jajajs']):
            await notificar_admin("PRUEBA ENVIADA", uid, m.from_user.username, f"💬 {raw}")
            await m.reply_text("Ya lo vi mor, ahora mándame el videito entrando a tu perfil para verificar y te suelto los videos 🥰")
            return

        if any(k in txt for k in ['no tengo seguidores','no tengo muchos seguidores','no llega a 100','no va a llegar','seguidores y no va']):
            await m.reply_text(COMENTA_TEXTO); return

        if 'pasame tus precios' in txt or 'pasame precios' in txt or 'pásame tus precios' in txt:
            pais = USUARIOS[uid].get('pais')
            if pais: await m.reply_text(precio_por_pais(pais))
            else: ESPERA_PAIS[uid]=True; await m.reply_text("¿De dónde eres? 🇵🇪 🇲🇽 🇺🇸")
            return

        if 'mejor hay que hablar' in txt:
            await m.reply_text("Hablemos pues mor 🥵 dime, ¿quieres precios o la promo gratis?"); return

        if 'lo se hacer' in txt or 'lo sé hacer' in txt:
            await m.reply_text("Perfecto mor, si ya sabes mándame captura + videito de tu story y te suelto los videos al toque 🥰"); return

        if txt.strip() == 'cumplo' or txt.startswith('cumplo'):
            await m.reply_text("Dale mor, mándame la prueba (captura + video entrando a tu perfil) y te mando todo 🥵"); return

        if txt.strip() == 'dame':
            await m.reply_text("¿Qué quieres que te dé mor? ¿Precios o la promo?"); return

        if 'quieres ver bb' in txt or 'quieres ver' in txt:
            await m.reply_text("Claro que quiero verte mor 😏 pero primero agarra un pack y te muestro todo, ¿te paso precios?"); return

        if any(k in txt for k in ['ya pague','pague','pagué','te pague','comprobante','transferi','deposite','pago realizado']):
            PAGARON.add(uid); guardar_datos()
            await notificar_admin("PAGO (TEXTO)", uid, m.from_user.username, f"💬 {raw[:50]}")
            await m.reply_text("Gracias mor 🥰 ya vi tu pago, en un ratito te mando todo"); return

        # ✅ NUEVOS: jajaja y pn
        if any(k in txt for k in ['jajaja','jaja','jeje','xd','lol']):
            await m.reply_text("Jajaja mor 🥵 ¿te paso precios o quieres la promo gratis?")
            return
        if any(k in txt for k in ['quisieras ver','quisiera ver','ver mi pn','mi pn','pn?','ver mi pene']):
            await m.reply_text("Jajaja guarda eso, yo no recibo ftpn 😏 si quieres ver lo mío agarra el PREMIUM, ¿de dónde eres? 🇵🇪 🇲🇽 🇺🇸")
            ESPERA_PAIS[uid]=True; return

        # ✅ TU EJEMPLO para "que contienen"
        if any(k in txt for k in ['que contienen','que contiene','que tienen','que incluyen','que hay en']):
            await m.reply_text(EJEMPLO_TEXTO)
            return

        # ✅ Sexting
        if 'sexting' in txt:
            await m.reply_text("Sexting es chat caliente mor 🥵 nos escribimos cochinadas, te mando audios gimiendo, fotos al momento y te hago venir con palabras. Va incluido en el PREMIUM, ¿lo quieres?")
            return

        # ✅ Una foto
        if txt.strip() in ['una foto','una fotito','mandame una foto','pasa foto']:
            await m.reply_text("Para probadita haz la promo gratis mor, te mando hasta 20. ¿Te paso los pasitos?")
            await enviar_gratis(m); return

        # ✅ Sigue conversación si dice sí
        if any(k in txt for k in ['si','si quiero','dale','va','ok','quiero precios','pasamelos']):
            pais = USUARIOS[uid].get('pais')
            if pais: await m.reply_text(precio_por_pais(pais))
            else: ESPERA_PAIS[uid]=True; await m.reply_text("¿De dónde eres? 🇵🇪 🇲🇽 🇺🇸")
            return

        # ✅ SALUDO CON TU EJEMPLO
        saludos = ['hola','hola bb','hey','buenas','ola','buenos dias','buenas tardes','buenas noches','holis','hello','que tal','jola','wenas']
        if (txt in saludos or any(txt.startswith(s+' ') for s in saludos)) and len(txt) < 25:
            await m.reply_text(EJEMPLO_TEXTO); return

        if any(k in txt for k in ['cual es la promo','que es la promo','promo','promocion']):
            await enviar_gratis(m); return
        if 'premium' in txt or txt == 'el premium':
            pais = USUARIOS[uid].get('pais')
            if pais: await m.reply_text(precio_por_pais(pais))
            else: ESPERA_PAIS[uid]=True; await m.reply_text("¿De dónde eres? 🇵🇪 🇲🇽 🇺🇸")
            return

        if any(k in txt for k in ['intercambio','intercambios','intercambiabas','cambio de fotos','cambiamos','intercambiamos']):
            await m.reply_text("No hago intercambios mor 🥺 solo vendo packs o te doy gratis si haces la promo, ¿quieres los pasitos?")
            await enviar_gratis(m); return

        if m.photo: await analizar_foto(ctx, uid, m.from_user.username or '', m.photo[-1].file_id); return
        if m.video: await analizar_video(ctx, uid, m.from_user.username or '', m.video.file_id); return
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
    app.add_handler(MessageHandler(filters.ALL, todo))
    app.add_handler(CallbackQueryHandler(btn))
    app.add_handler(ChatMemberHandler(nuevo, ChatMemberHandler.CHAT_MEMBER))
    app.run_polling()

if __name__ == '__main__':
    main()
