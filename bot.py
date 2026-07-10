import os, json, logging, unicodedata, time
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from telegram.ext import Application, TypeHandler

logging.basicConfig(level=logging.INFO)
TOKEN = '8762577283:AAFVT7_WMpZ7njVnToIlZypUpCToF5LGcbA'
ADMIN_ID = 8783569348
LINK_CANAL = "https://t.me/+zt1RzGevdHBjMDgx"
LINK_PAYPAL = "https://www.paypal.com/qrcodes/p2pqrc/76RWY9FF7Q7RE"

USUARIOS = {}; PAGARON = set(); ESPERA_PAIS = {}; DATA_FILE = "data.json"

def cargar_datos():
    global USUARIOS, PAGARON
    if os.path.exists(DATA_FILE):
        d=json.load(open(DATA_FILE))
        USUARIOS={int(k):v for k,v in d.get('usuarios',{}).items()}
        PAGARON=set(d.get('pagaron',[]))
def guardar_datos():
    json.dump({'usuarios':USUARIOS,'pagaron':list(PAGARON)}, open(DATA_FILE,'w'))

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

Mándame captura cuando pagues bebé 🥰
1. Pagas 2. Captura
Si no contesto envías cap a : @YanaBiBot con estos precios."""

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
923553612 YAPE/PLIN
1. Yapeas 2. Captura
Si no contesto envías cap a : @YanaBiBot con estos precios."""

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
PayPal: AbigailMaximoofO / USDT
Link: {LINK_PAYPAL}
Avísame con comprobante 🥰
Si no contesto envías cap a : @YanaBiBot con estos precios."""

GRATIS_TEXTO="""(REGALITO)
✨ QUIERES HASTA 20 VIDEITOS GRATSS? ✨

https://t.me/YanaBiBot

Pasitos súper fáciles uwu:
1️⃣ En tu bio de TikTok pon: Tg: yanabicitasa ✨
2️⃣ Sube una fotito de las que te envié a tu story + Frase hot 😋
3️⃣ Mándame captura + videito cuando cumplas
4️⃣ Me confirmas cuando llegue a 100 vistas(story) :3
5️⃣ Disfruta de hasta 20 videitos :3 ❤️‍🔥

¿Te animas o ño? 🥺
(Me avisas diciendo: ya cumpli con las 100 vistas )
(Revisa mi perfil)"""

TEXTO_100="""Las 100 vistas son solo para que veas lo fácil que es, mor :3 💕
Cuando tu story llegue a 500-1000 me avisas y te suelto tus videitos al toque 🥵
Mándame videito entrando a TikTok → tu perfil → tu story → los likes, TODO seguido sin cortar. Si lo cortas se anula la promo, bebé 😘"""
TEXTO_INTER="No hago intercambios mor 🥰 yo vendo, pero si me cumples la promo de los videitos gratis o me compras un pack te doy videitos al toque 😏"

def normalizar(t): return unicodedata.normalize('NFKD',t or '').encode('ascii','ignore').decode().lower()
def precio_por_pais(p): return PE_PRECIOS if p=='pe' else MX_PRECIOS if p=='mx' else USA_PRECIOS
def detectar_pais(t):
    t=normalizar(t)
    if 'peru' in t: return 'pe'
    if 'mex' in t: return 'mx'
    if any(x in t for x in ['usa','eeuu','colombia','argentina','chile','ecuador','venezuela','bolivia','espana']): return 'usa'
    return None
def es_compra(t): return any(k in t for k in ['vendes','me vendes','precio','precios','cuanto cuesta','cuanto es','pasame'])
def es_100(t): return ('100' in t and 'vista' in t) or 'ya cumpli' in t
def es_pago(t): return any(k in t for k in ['yape','plin','ya te pague','te yapee','comprobante','te pague'])
def puede_enviar(uid, key, cooldown=999999):
    # anti-spam: si ya se envió una vez, no volver a enviar nunca
    flags=USUARIOS[uid].setdefault('flags',{})
    if flags.get(key): return False
    return True

async def notificar(tipo,uid,user,extra=""):
    try: await app_bot.send_message(ADMIN_ID,f"{tipo} {uid} @{user} {extra}")
    except: pass

async def bienvenida(m):
    try: await m.reply_media_group([InputMediaPhoto(open(f'fotitos{i}.JPG','rb')) for i in range(1,6)])
    except: pass
    await m.reply_text(GRATIS_TEXTO)
    await m.reply_text(LINK_CANAL)

async def todo(upd,ctx):
    global app_bot; app_bot=ctx.bot
    m=upd.message or upd.business_message
    if not m or m.from_user.is_bot: return
    uid=m.from_user.id
    USUARIOS.setdefault(uid,{}); USUARIOS[uid].setdefault('flags',{})
    txt=normalizar(m.text); raw=m.text or ""
    es_neg=upd.business_message is not None
    if es_neg and uid==ADMIN_ID: return
    guardar_datos()

    if es_neg:
        if m.photo or m.video:
            if m.photo: await ctx.bot.send_photo(ADMIN_ID,m.photo[-1].file_id,caption=f"{uid}")
            if m.video: await ctx.bot.send_video(ADMIN_ID,m.video[-1].file_id,caption=f"{uid}")
            return
        if es_pago(txt):
            await notificar("💰 PAGO",uid,m.from_user.username,raw); PAGARON.add(uid); guardar_datos(); return
        if es_100(txt):
            if puede_enviar(uid,'v100'): await m.reply_text(TEXTO_100); USUARIOS[uid]['flags']['v100']=True
            await notificar("100 VISTAS",uid,m.from_user.username,raw); guardar_datos(); return
        if 'intercamb' in txt or 'cambias' in txt:
            if puede_enviar(uid,'inter'): await m.reply_text(TEXTO_INTER); USUARIOS[uid]['flags']['inter']=True; guardar_datos()
            return

        p_det=detectar_pais(txt)
        if p_det: USUARIOS[uid]['pais']=p_det; guardar_datos()

        if uid in ESPERA_PAIS:
            p=detectar_pais(txt) or USUARIOS[uid].get('pais')
            if p and puede_enviar(uid,'precios'):
                await m.reply_text(precio_por_pais(p)); USUARIOS[uid]['flags']['precios']=True; del ESPERA_PAIS[uid]; guardar_datos()
            return

        if es_compra(txt):
            p=USUARIOS[uid].get('pais') or p_det
            if p:
                if puede_enviar(uid,'precios'):
                    await m.reply_text(precio_por_pais(p)); USUARIOS[uid]['flags']['precios']=True; guardar_datos()
                return
            else:
                if puede_enviar(uid,'preg_pais'):
                    await m.reply_text("de donde eres mor?:3"); USUARIOS[uid]['flags']['preg_pais']=True; ESPERA_PAIS[uid]=True; guardar_datos()
                return

        if puede_enviar(uid,'bienvenida'):
            await bienvenida(m); USUARIOS[uid]['flags']['bienvenida']=True; guardar_datos()
            return

def main():
    cargar_datos()
    app=Application.builder().token(TOKEN).build()
    app.add_handler(TypeHandler(Update,todo))
    app.run_polling(allowed_updates=['message','business_message'])

if __name__=='__main__': main()
