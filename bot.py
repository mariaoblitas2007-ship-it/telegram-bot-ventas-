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

PREMIUM_SALUDO = "Hola mor 🥺💕 ¿cómo estás? Si quieres lo mejor, agarra mi PACK PREMIUM: 1 personalizado + 20 videitos + sexting y te mando hasta el DOBLE de contenido 🥵\n\n¿De dónde eres? 🇵🇪 🇲🇽 🇺🇸"

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

async def analizar_foto(ctx, uid, user, fid):
    try:
        f = await ctx.bot.get_file(fid)
        p = f"/tmp/{fid}.jpg"
        await f.download_to_drive(p)
        txt = ""
        if HAS_OCR:
            try: txt = pytesseract.image_to_string(Image.open(p)).lower()
            except: pass
        username = f"@{user}" if user else "sin @"
        if txt and all(k in txt for k in ['basico','top','premium']):
            await ctx.bot.send_message(ADMIN_ID, f"📦 {username} envió foto de PACKS")
            return
        if any(k in txt for k in ['yape','plin','paypal','banco','clabe','stp','abigail','maximoof']):
            tipo = "💰 PAGO DETECTADO"; PAGARON.add(uid); guardar_datos()
        elif any(k in txt for k in ['tiktok','story','vistas','hormonal','alguno para jugar']):
            tipo = "📸 PROMO"
        else:
            tipo = "📷 FOTO"
        link_directo = f"https://t.me/{user}" if user else f"tg://user?id={uid}"
        caption = f"{tipo}\n👤 {username}\n🆔 <code>{uid}</code>\n🔗 <a href='{link_directo}'>ABRIR CHAT</a>"
        await ctx.bot.send_photo(ADMIN_ID, fid, caption=caption, parse_mode='HTML')
        if tipo == "📸 PROMO":
            await ctx.bot.send_message(uid, COMENTA_TEXTO)
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
    m = upd.message or upd.business_message
    if not m or m.from_user.is_bot: return
    uid = m.from_user.id
    USUARIOS[uid] = {'n': m.from_user.first_name}; guardar_datos()
    es_neg = upd.business_message is not None
    txt = normalizar(m.text)
    raw = m.text or ""

    if es_neg:
        if uid == ADMIN_ID: return
        if 'calific' in txt:
            await m.reply_text("solo trato hot a compradores 🥵"); return
        if any(k in txt for k in ['fake','estafa']):
            await m.reply_text(f"¿Fake? mira {LINK_CANAL}"); return
        if any(k in txt for k in ['ganas','caliente','quitar','quito']):
            await m.reply_text(PREMIUM_SALUDO); ESPERA_PAIS[uid]=True; return
        if txt.strip() in ['hola','hola bb','hey','buenas','ola','buenos dias','buenas tardes','buenas noches']:
            await enviar_gratis(m); return
        if any(k in txt for k in ['hermosa','linda','preciosa','guapa','bella','rica','diosa','te amo','me encantas']):
            await m.reply_text("Aww gracias mor 🥺💕 si quieres ver más, cómprame un pack y te mando hasta el doble de contenido, ¿te paso precios? 🥵"); return
        if any(k in txt for k in ['encuentro','encuentros','sales','cita','citas','nos vemos','te veo','en persona','salir']):
            await m.reply_text("Solo puedo pensarlo si compras el paquete más grande, sorpréndeme con la cap del pago 🫣"); return
        if any(k in txt for k in ['ayuda','ayudas','me ayudas','apoyame','ayudame']):
            await m.reply_text("Claro mor, si agarras el PREMIUM te mando hasta el doble de contenido 🥵 ¿quieres ver precios?"); return
        if any(k in txt for k in ['enseña','enseñas','muestra','muestrame','prueba','sample','videito','probadita','adelanto']):
            if uid in PAGARON:
                await m.reply_text("Ya pagaste mi amor 🥰 en un ratito te mando todo"); return
            else:
                if uid in ESPERA_PAIS: del ESPERA_PAIS[uid]
                await enviar_gratis(m); return
        if any(k in txt for k in ['videollamada','video llamada','videocall','llamada']):
            ESPERA_PAIS[uid]=True
            await m.reply_text("Tengo videollamadas mor 🥵 ¿de dónde eres? 🇵🇪 🇲🇽 🇺🇸"); return
        if any(k in txt for k in ['no tengo','sin plata','sin dinero','no puedo comprar','no tengo pa']):
            await m.reply_text("Mor, si no puedes comprar, haz la promo gratis y te mando hasta 20, ¿te paso los pasitos?"); await enviar_gratis(m); return
        if any(k in txt for k in ['primeros 5','primeros cinco','primeros5','de los primeros']):
            await m.reply_text("Amor, los primeros 5 solo es para la reacción, para los videos tienes que hacer la story y llegar a 100 vistas, ¿te mando los pasos?"); await enviar_gratis(m); return
        if any(k in txt for k in ['pasas el rato','como estas','como estás','que haces','nada por prv','prvv','prv']):
            await m.reply_text("Aquí chambeando para mis mors 🥵 ¿quieres ver mi pack PREMIUM o te mando el gratis?"); return
        if any(k in txt for k in ['te enseño','como me corro','como me vengo','me corro','me vengo','te muestro como']):
            await m.reply_text("Jajaja guarda eso para cuando compres el PREMIUM, ahí sí te muestro todo 🫣 ¿de dónde eres? 🇵🇪 🇲🇽 🇺🇸"); ESPERA_PAIS[uid]=True; return
        if any(k in txt for k in ['intercambio','intercambios','cambio de fotos','cambiamos','intercambiamos']):
            await m.reply_text("No hago intercambios, mor 🥺 solo vendo packs o te doy gratis si haces la promo, ¿quieres los pasitos?"); await enviar_gratis(m); return
        if any(k in txt for k in ['ftpn','pene','pito','verga','mando ftpn','la tengo parada','bien parada','quieres ver mi']):
            await m.reply_text("Jajaja guarda eso, yo no recibo ftpn 😏 si quieres ver lo mío agarra el PREMIUM, ¿de dónde eres? 🇵🇪 🇲🇽 🇺🇸"); ESPERA_PAIS[uid]=True; return
        if any(k in txt for k in ['wooo','woow','comoo','no entiendo','que es esto']):
            await m.reply_text("Te explico de nuevo mor 🥺"); await enviar_gratis(m); return
        if 'ya cumpli' in txt:
            await m.reply_text("Las 100 vistas son solo para que veas lo fácil que es, mor :3 💕\n\nCuando tu story llegue a 500-1000 me avisas y te suelto tus videitos al toque 🥵\n\nMándame videito entrando a TikTok → tu perfil → tu story → los likes, TODO seguido sin cortar. Si lo cortas se anula la promo, bebé 😘"); return
        if any(k in txt for k in ['vistas','500','1000']):
            await m.reply_text(COMENTA_TEXTO); return
        if 'gratis' in txt:
            if uid in ESPERA_PAIS: del ESPERA_PAIS[uid]
            await enviar_gratis(m); return
        if m.text and es_precio(m.text):
            ESPERA_PAIS[uid] = True
            await m.reply_text("¿De dónde eres? 🇵🇪 🇲🇽 🇺🇸"); return
        if uid in ESPERA_PAIS:
            if 'peru' in txt or '🇵🇪' in raw:
                await m.reply_text(PE_PRECIOS)
            elif 'mex' in txt or '🇲🇽' in raw:
                await m.reply_text(MX_PRECIOS)
            elif 'usa' in txt or 'eeuu' in txt or 'estados' in txt or '🇺🇸' in raw or '🇺🇲' in raw:
                await m.reply_text(USA_PRECIOS)
            else:
                await m.reply_text(USA_PRECIOS)
            del ESPERA_PAIS[uid]; return
        if m.photo:
            await analizar_foto(ctx, uid, m.from_user.username or '', m.photo[-1].file_id); return
        return

    if m.chat.type == 'private':
        if m.photo:
            await analizar_foto(ctx, uid, m.from_user.username or '', m.photo[-1].file_id); return
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
