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

USUARIOS, PAGARON, REFERIDOS, INVITADOS, ESPERA_PAIS = {}, set(), {}, {}, {}
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

# ===== 3 PRECIOS =====
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
        if any(k in txt for k in ['yape','plin','paypal','banco','clabe','stp','abigail','maximoof']):
            tipo = "💰 PAGO DETECTADO"; PAGARON.add(uid); guardar_datos()
        elif any(k in txt for k in ['tiktok','story','vistas']):
            tipo = "📸 PROMO"
        else:
            tipo = "📷 FOTO"
        username = f"@{user}" if user else "sin @"
        link_directo = f"https://t.me/{user}" if user else f"tg://user?id={uid}"
        caption = f"{tipo}\n👤 {username}\n🆔 <code>{uid}</code>\n🔗 <a href='{link_directo}'>ABRIR CHAT</a>"
        await ctx.bot.send_photo(ADMIN_ID, fid, caption=caption, parse_mode='HTML')
    except Exception as e:
        logger.error(e)

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
        if 'ya cumpli' in txt:
            await m.reply_text("Las 100 vistas son solo para que veas lo fácil que es, mor :3 💕\n\nCuando tu story llegue a 500-1000 me avisas y te suelto tus videitos al toque 🥵\n\nMándame videito entrando a TikTok → tu perfil → tu story → los likes, TODO seguido sin cortar. Si lo cortas se anula la promo, bebé 😘"); return
        if any(k in txt for k in ['vistas','500','1000']):
            await m.reply_text("Busca videos con #hormo #hot #hormonal #amigoshormo y deja comentarios bien ricos 🥵\n\nEscribe cositas como: \"¿quién?\", \"¿alguno?\", \"miren mi story\", \"ando horm...\" \n\nEntre más caliente comentes, más gente entra a verte, bebé 😏"); return
        if 'gratis' in txt:
            if uid in ESPERA_PAIS: del ESPERA_PAIS[uid]
            try:
                await m.reply_media_group([
                    InputMediaPhoto(open('fotitos1.JPG','rb')),
                    InputMediaPhoto(open('fotitos2.JPG','rb')),
                    InputMediaPhoto(open('fotitos3.JPG','rb')),
                    InputMediaPhoto(open('fotitos4.JPG','rb')),
                    InputMediaPhoto(open('fotitos5.JPG','rb'))
                ])
            except: pass
            await m.reply_text("✨ (REGALITO) QUIERES HASTA 20 VIDEITOS GRATSS? ✨\n\nhttps://t.me/YanaBiBot\n\nPasitos súper fáciles uwu:\n1️⃣ En tu bio de TikTok pon: Tg: yanabicitasa ✨\n2️⃣ Sube una fotito de las que te envié a tu story + Frase hot 😋\n3️⃣ Mándame captura + videito cuando cumplas\n4️⃣ Me confirmas cuando llegue a 100 vistas (story) :3\n5️⃣ Disfruta de hasta 20 videitos :3 ❤️\n\n¿Te animas o ño? 🥺\n(Me avisas cuando cumplas Mor)"); return
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
