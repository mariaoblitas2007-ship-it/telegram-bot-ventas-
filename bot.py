import os, json, logging, unicodedata
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, MessageHandler, CallbackQueryHandler, CommandHandler, filters, ContextTypes, ChatMemberHandler
import pytesseract
from PIL import Image

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ===== CONFIG =====
TOKEN = '8762577283:AAFVT7_WMpZ7njVnToIlZypUpCToF5LGcbA'
ADMIN_ID = 8783569348
CANAL_ID = -1004327627898
LINK_CANAL = "https://t.me/+zt1RzGevdHBjMDgx"
LINK_PAYPAL = "https://www.paypal.com/qrcodes/p2pqrc/76RWY9FF7Q7RE"

USUARIOS, PAGARON, REFERIDOS, INVITADOS = {}, set(), {}, {}
VENTAS_ESTRELLAS, ESPERA_PAIS = [], {}
DATA_FILE = "data.json"

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

# ===== PRECIOS EXACTOS (no tocar) =====
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

USA_PRECIOS = """🛍 VIDEOS 🛒

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
""" + f"Link directo: {LINK_PAYPAL}" + """

Avísame cuando envíes con el comprobante 🥰
En cuanto caiga te mando tu pack 🔥

1. Pagas 2. Captura

Si no contesto envías cap del pago a : @YanaBiBot con estos precios."""
OTRO_PRECIOS = USA_PRECIOS

def get_menu(): return InlineKeyboardMarkup([
    [InlineKeyboardButton("💎 COMPRAR", callback_data='comprar')],
    [InlineKeyboardButton("🎁 GRATIS", callback_data='gratis')],
    [InlineKeyboardButton("🔗 MI LINK", callback_data='milink')],
    [InlineKeyboardButton("📊 RANKING", callback_data='ranking')],
    [InlineKeyboardButton("🔥 Canal", url=LINK_CANAL)]
])
def get_precios(): return InlineKeyboardMarkup([
    [InlineKeyboardButton("🇵🇪 Perú", callback_data='pe')],
    [InlineKeyboardButton("🇲🇽 México", callback_data='mx')],
    [InlineKeyboardButton("🇺🇸 EEUU/Otros", callback_data='usa')]
])
def normalizar(t): return unicodedata.normalize('NFKD', t or '').encode('ascii','ignore').decode().lower()
def es_precio(t): return "hola mor" in normalizar(t) and "precio" in normalizar(t)

async def analizar_foto(ctx, uid, user, fid):
    try:
        f = await ctx.bot.get_file(fid)
        p = f"/tmp/{fid}.jpg"
        await f.download_to_drive(p)
        txt = pytesseract.image_to_string(Image.open(p)).lower()
        if any(k in txt for k in ['yape','plin','paypal','banco','clabe','usd','s/','$']):
            tipo = "💰 PAGO"; PAGARON.add(uid); guardar_datos()
        elif any(k in txt for k in ['tiktok','story','yanabicitasa']):
            tipo = "📸 PROMO"
        else: tipo = "🔥 PACK"
        await ctx.bot.send_photo(ADMIN_ID, fid, caption=f"{tipo}\n@{user} ({uid})\nOCR:{txt[:120]}")
    except Exception as e: logger.error(e)

async def manejar_todo(upd, ctx):
    m = upd.message or upd.business_message
    if not m or m.from_user.is_bot: return
    uid = m.from_user.id
    USUARIOS[uid] = {'name':m.from_user.first_name}; guardar_datos()
    es_neg = upd.business_message is not None
    txt = normalizar(m.text)

    # --- NEGOCIO (@yanabicitasa) ---
    if es_neg:
        if uid == ADMIN_ID: return
        if 'calific' in txt: await m.reply_text("solo doy trato hot a compradores 🥵"); return
        if any(k in txt for k in ['fake','estafa']): await m.reply_text(f"¿Fake? mira mi canal {LINK_CANAL}"); return
        if txt=='ya' or 'ya cumpli' in txt: await m.reply_text("100 vistas ok, avísame a 500-1000. Video sin cortes.\n⚠️ SOLO @yanabicitasa"); return
        if any(k in txt for k in ['vistas','500','1000']): await m.reply_text("Comenta en #hormo: 'miren mi story' 🥵\n⚠️ Solo yo"); return
        if 'gratis' in txt: await m.reply_text("1.Bio Tg:yanabicitasa 2.Subir QR 3.Comentar 30-100 4.Captura\nDi 'ya'\n⚠️ SOLO YO"); return
        if m.text and es_precio(m.text): ESPERA_PAIS[uid]=True; await m.reply_text("¿De dónde eres?"); return
        if uid in ESPERA_PAIS:
            if 'peru' in txt: await m.reply_text(PE_PRECIOS)
            elif 'mex' in txt: await m.reply_text(MX_PRECIOS)
            else: await m.reply_text(USA_PRECIOS)
            del ESPERA_PAIS[uid]; return
        if m.photo: await analizar_foto(ctx,uid,m.from_user.username or '',m.photo[-1].file_id); return
        return # SILENCIO, no manda menú

    # --- BOT DIRECTO ---
    if m.chat.type == 'private':
        if m.photo: await analizar_foto(ctx,uid,m.from_user.username or '',m.photo[-1].file_id); return
        if m.text and m.text.startswith('/start'): await m.reply_text(f"Hola {m.from_user.first_name} 😏", reply_markup=get_menu()); return
        await m.reply_text("Elige:", reply_markup=get_menu())

async def botones(upd, ctx):
    q = upd.callback_query; await q.answer()
    if q.data == 'comprar': await q.edit_message_text("País:", reply_markup=get_precios())
    elif q.data == 'pe': await q.edit_message_text(PE_PRECIOS)
    elif q.data == 'mx': await q.edit_message_text(MX_PRECIOS)
    elif q.data == 'usa': await q.edit_message_text(USA_PRECIOS)
    elif q.data == 'gratis': await q.edit_message_text("Escribe 'gratis' a @yanabicitasa")
    elif q.data == 'milink':
        link = f"https://t.me/YanaBiBot?start={q.from_user.id}"
        REFERIDOS[q.from_user.id] = {'link':link}; guardar_datos()
        await q.edit_message_text(f"Tu link:\n{link}")
    elif q.data == 'ranking':
        top = sorted(REFERIDOS.items(), key=lambda x: INVITADOS.get(x[0],0), reverse=True)[:5]
        txt = "🏆 TOP:\n" + "\n".join([f"{i+1}. {USUARIOS.get(uid,{}).get('name','?')} - {INVITADOS.get(uid,0)}" for i,(uid,_) in enumerate(top)])
        await q.edit_message_text(txt)

async def nuevo_miembro(upd, ctx):
    for u in upd.chat_member.new_chat_members:
        if not u.is_bot:
            INVITADOS[upd.effective_user.id] = INVITADOS.get(upd.effective_user.id,0)+1; guardar_datos()

def main():
    cargar_datos()
    app = Application.builder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.ALL, manejar_todo))
    app.add_handler(CallbackQueryHandler(botones))
    app.add_handler(ChatMemberHandler(nuevo_miembro, ChatMemberHandler.CHAT_MEMBER))
    logger.info("BOT LISTO")
    app.run_polling()

if __name__ == '__main__': main()
