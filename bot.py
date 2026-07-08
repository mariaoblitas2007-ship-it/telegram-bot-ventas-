import os, sys, asyncio, random, logging, unicodedata, signal, re, json
from datetime import datetime, timedelta, time
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, MessageHandler, CallbackQueryHandler, CommandHandler, filters, ContextTypes, ChatMemberHandler
from telegram.error import Forbidden, Conflict

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

TOKEN = '8762577283:AAFVT7_WMpZ7njVnToIlZypUpCToF5LGcbA'
ADMIN_ID = 8783569348
USERNAME_ADMIN = "@yanabicitasa"
CANAL_ID = -1004327627898

LINK_CANAL = "https://t.me/+zt1RzGevdHBjMDgx"
LINK_PAYPAL = "https://www.paypal.com/qrcodes/p2pqrc/76RWY9FF7Q7RE"

VIP_TEMPORAL, DEMO_USADO, USUARIOS, PAGARON = {}, set(), {}, set()
ULTIMO_MENSAJE, FOLLOWUP_ENVIADO = {}, set()
REFERIDOS, INVITACIONES, INVITADOS = {}, {}, {}
VENTAS_ESTRELLAS = []
ESPERA_PAIS = {}

FOTOS_GRATIS = ["fotitos1.JPG","fotitos2.JPG","fotitos3.JPG","fotitos4.JPG","fotitos5.JPG","fotitos6.JPG"]

DATA_FILE = "data.json"

def cargar_datos():
    global REFERIDOS, PAGARON, USUARIOS, INVITADOS, INVITACIONES, VENTAS_ESTRELLAS
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                d = json.load(f)
                REFERIDOS = {int(k): v for k,v in d.get('referidos', {}).items()}
                PAGARON = set(d.get('pagaron', []))
                USUARIOS = {int(k): v for k,v in d.get('usuarios', {}).items()}
                INVITADOS = {int(k): v for k,v in d.get('invitados', {}).items()}
                INVITACIONES = {v['link']: int(k) for k,v in REFERIDOS.items() if 'link' in v}
                VENTAS_ESTRELLAS = d.get('ventas_estrellas', [])
        except Exception as e:
            logger.error(f"Error cargando: {e}")

def guardar_datos():
    try:
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump({
                'referidos': REFERIDOS,
                'pagaron': list(PAGARON),
                'usuarios': USUARIOS,
                'invitados': INVITADOS,
                'ventas_estrellas': VENTAS_ESTRELLAS
            }, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"Error guardando: {e}")

PE_PRECIOS = """
🛍 VIDEOS 🛒

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

💳 PAGO: YAPE/PLIN: 923553612
CUENTO CON REFERENCIAS

Mándame captura cuando pagues bebé 🥰
En cuanto caiga te mando tu pack 🔥

1. Yapeas 2. Captura

Si no contesto envías cap del pago a : @YanaBiBot
"""

MX_PRECIOS = """
🛍 VIDEOS 🛒

🎂 BÁSICO: $100 MXN
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

Si no contesto envías cap del pago a : @YanaBiBot con estos precios.
"""

USA_PRECIOS = """
🛍 VIDEOS 🛒

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

Avísame cuando envíes con el comprobante 🥰
En cuanto caiga te mando tu pack 🔥

1. Pagas 2. Captura

Si no contesto envías cap del pago a : @YanaBiBot con estos precios.
"""

OTRO_PRECIOS = USA_PRECIOS

TEXTO_GRATIS = """📸 GRATIS 🥺💋..."""

TEXTO_NIVELES = """🔥 VIDEOS GRATIS #HORMO..."""

PREMIOS_REFERIDOS = {5:"1 videito pa calentar 🥵",20:"2-3 videitos... ya me mojo 🔥",50:"4-10 videitos 😈 te dejo sin aire",100:"10-20 videitos 🥵 ya soy tuya",200:"+20 videitos + VIDEO FETICHE 👑🍑"}

def get_menu(): return InlineKeyboardMarkup([[InlineKeyboardButton("💎 COMPRAR PACKS", callback_data='comprar')],[InlineKeyboardButton("🎁 GRATIS - Misiones", callback_data='gratis')],[InlineKeyboardButton("🔗 MI LINK - Referidos", callback_data='milink')],[InlineKeyboardButton("📊 RANKING", callback_data='ranking')],[InlineKeyboardButton("🔥 Canal Oficial", url=LINK_CANAL)]])
def get_precios_menu(): return InlineKeyboardMarkup([[InlineKeyboardButton("🇵🇪 Perú", callback_data='pe')],[InlineKeyboardButton("🇲🇽 México", callback_data='mx')],[InlineKeyboardButton("🇺🇸 USA/Otros", callback_data='usa')],[InlineKeyboardButton("🌎 Internacional", callback_data='otro')],[InlineKeyboardButton("⬅️ Volver", callback_data='volver')]])
def get_volver(): return InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Volver al Menú", callback_data='volver')]])
def normalizar(t): return unicodedata.normalize('NFKD', t).encode('ascii','ignore').decode('ascii').lower()

def es_trigger_precios(texto):
    if not texto: return False
    t = normalizar(texto)
    return "hola mor" in t and "precio" in t

def registrar_usuario(u):
    USUARIOS[u.id] = {'nombre': u.first_name, 'username': u.username or "sin_username"}
    guardar_datos()

async def avisar_pago(ctx, uid, user, nombre, fid):
    try: await ctx.bot.send_photo(ADMIN_ID, fid, caption=f"💰 PAGO\n👤 @{user}\n🆔 {uid}\n👉 tg://user?id={uid}")
    except: pass

async def detectar_estrellas(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.effective_message
    if not msg or not msg.paid_media_purchased: return
    compra = msg.paid_media_purchased
    user = compra.from_user
    uid = user.id
    estrellas = 0
    post_id = 0
    if msg.reply_to_message:
        post_id = msg.reply_to_message.message_id
        if msg.reply_to_message.paid_media:
            estrellas = msg.reply_to_message.paid_media.star_count
    canal_id_str = str(CANAL_ID).replace("-100", "")
    link_post = f"https://t.me/c/{canal_id_str}/{post_id}"
    venta = {'uid': uid, 'nombre': user.first_name, 'username': user.username or '', 'estrellas': estrellas, 'post': link_post, 'fecha': datetime.now().isoformat(), 'dia': datetime.now().strftime('%Y-%m-%d')}
    VENTAS_ESTRELLAS.append(venta)
    guardar_datos()
    total_persona = sum(v['estrellas'] for v in VENTAS_ESTRELLAS if v['uid'] == uid)
    await context.bot.send_message(ADMIN_ID, f"⭐ {estrellas} ESTRELLAS\n👤 {user.first_name} @{user.username or 'sin_user'}\n👉 PERFIL: tg://user?id={uid}\n🎬 COMPRÓ: {link_post}\n💰 Total de él/ella: {total_persona}⭐", disable_web_page_preview=True)

async def manejar_todo(upd: Update, ctx: ContextTypes.DEFAULT_TYPE):
    m = upd.message or upd.business_message
    if not m or not m.from_user or m.from_user.is_bot: return

    if getattr(m, 'paid_media_purchased', None):
        await detectar_estrellas(upd, ctx)
        return

    uid = m.from_user.id
    registrar_usuario(m.from_user)
    name = m.from_user.first_name
    user = m.from_user.username or "x"
    es_negocio = upd.business_message is not None

    # ===== 1. CHAT DE NEGOCIO =====
    if es_negocio:
        if uid == ADMIN_ID: return
        txt = normalizar(m.text) if m.text else ""

        if 'calific' in txt:
            await m.reply_text("solo doy trato hot a mis compradores del sexting 🥵")
            return

        if txt == 'ya' or 'ya cumpli' in txt or 'ya esta' in txt or 'listo' in txt or 'termine' in txt:
            await m.reply_text(
                "100 vistas es para que veas que es fácil :3 me confirmas cuando tenga 500-1000 vistas la story, y te envío lo videos\n"
                "Me envías video entrando al TikTok, entrando al estado, entrando a los likes,\n"
                "cualquier corte en el video anula la promoción de videos\n\n"
                "⚠️ REGLA DE ORO: solo puedes promocionarme a MÍ (@yanabicitasa). Si promocionas a alguien más, se anulan TODAS tus recompensas."
            )
            return

        if any(k in txt for k in ['como llego','como consigo','como tengo','mas vistas','más vistas','no sube','ayuda vistas','500','1000']):
            await m.reply_text(
                "mmm quieres que te vean rico, ¿verdad? 🥵🔥\n\n"
                "Haz esto y vas a explotar tu story:\n"
                "1️⃣ Busca en TikTok videos con #hormo #hot #hormonal #amigoshormo\n"
                "2️⃣ Comenta bien puerco:\n"
                "• '¿quién se anima conmigo? 😏'\n"
                "• '¿alguno caliente por aquí? 🥵'\n"
                "• 'miren mi story, los espero mojaditos...'\n"
                "• 'tengo algo hot en mi perfil, entren 😈'\n\n"
                "Entre más morboso, más hormos caen. En 2h tienes tus 500-1000.\n\n"
                "⚠️ OJO: solo me promocionas a mí. Si metes otra cuenta, pierdes todo."
            )
            return

        if any(k in txt for k in ['gratis','free','mision','promocion','regalo']):
            await m.reply_text(
                "¿Quieres hasta 20 videitos gratis? 🥺💋\n\n"
                "1. Ponte nombre + foto hot\n"
                "2. En tu bio pon: Tg: yanabicitasa\n"
                "3. Sube mi QR a tu story\n"
                "4. Comenta en 30-100 videos hot\n"
                "5. Mándame captura\n\n"
                "Cuando termines dime 'ya'\n\n"
                "⚠️ SOLO YO: prohibido promocionar a otra persona. Si lo haces, se cancelan tus videos."
            )
            return

        if m.text and es_trigger_precios(m.text):
            ESPERA_PAIS[uid] = True
            await m.reply_text("hola mi amor 🫣🔥\n¿de dónde eres tú, bebé? 🥺💋")
            return

        if uid in ESPERA_PAIS and m.text:
            if any(k in txt for k in ['peru','pe','lima']): await m.reply_text(PE_PRECIOS)
            elif any(k in txt for k in ['mexico','mx']): await m.reply_text(MX_PRECIOS)
            elif any(k in txt for k in ['eeuu','usa']): await m.reply_text(USA_PRECIOS)
            else: await m.reply_text(OTRO_PRECIOS)
            del ESPERA_PAIS[uid]
            return

        if m.photo:
            PAGARON.add(uid); guardar_datos()
            await avisar_pago(ctx, uid, user, name, m.photo[-1].file_id)
            return

        if m.text:
            await m.reply_text("mmm dime bebé... ¿vienes por los 20 videitos gratis o quieres comprar un pack bien hot? 🥵\nEscribe 'gratis' o 'precios'")
            return

    # ===== 2. DIRECTO @YanaBiBot =====
    if m.chat.type == 'private':
        if m.text and es_trigger_precios(m.text):
            ESPERA_PAIS[uid] = True
            await m.reply_text("hola mi amor 🫣🔥\n¿de dónde eres tú, bebé? 🥺💋")
            return
        if uid in ESPERA_PAIS and m.text:
            txt = normalizar(m.text)
            if any(k in txt for k in ['peru','pe','lima']): await m.reply_text(PE_PRECIOS, reply_markup=get_menu())
            elif any(k in txt for k in ['mexico','mx']): await m.reply_text(MX_PRECIOS, reply_markup=get_menu())
            elif any(k in txt for k in ['eeuu','usa']): await m.reply_text(USA_PRECIOS, reply_markup=get_menu())
            else: await m.reply_text(OTRO_PRECIOS, reply_markup=get_menu())
            del ESPERA_PAIS[uid]
            return
        if m.photo:
            PAGARON.add(uid); guardar_datos()
            await avisar_pago(ctx, uid, user, name, m.photo[-1].file_id)
            return
        if m.text and m.text.lower() == '/start':
            await m.reply_text(f"Mmmm {name}... 😏✨", reply_markup=get_menu())
            return
        await m.reply_text("¿Qué se te antoja? 👇", reply_markup=get_menu())
        return

#... resto de handlers igual...
def main():
    cargar_datos()
    app = Application.builder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.ALL, manejar_todo))
    logger.info("BOT PRENDIDO ✅")
    app.run_polling(drop_pending_updates=True, allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__': main()
