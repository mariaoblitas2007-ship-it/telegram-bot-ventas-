import os, json, logging, unicodedata, asyncio, re
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, ChatMemberHandler, TypeHandler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = '8762577283:AAFVT7_WMpZ7njVnToIlZypUpCToF5LGcbA'
ADMIN_ID = 8783569348
LINK_CANAL = "https://t.me/+zt1RzGevdHBjMDgx"
LINK_PAYPAL = "https://www.paypal.com/qrcodes/p2pqrc/76RWY9FF7Q7RE"

USUARIOS = {}; PAGARON = set(); REFERIDOS = {}; INVITADOS = {}; DATA_FILE = "data.json"

def cargar_datos():
    global USUARIOS, PAGARON, REFERIDOS, INVITADOS
    if os.path.exists(DATA_FILE):
        d=json.load(open(DATA_FILE))
        USUARIOS={int(k):v for k,v in d.get('usuarios',{}).items()}
        PAGARON=set(d.get('pagaron',[]))
        REFERIDOS={int(k):v for k,v in d.get('referidos',{}).items()}
        INVITADOS={int(k):v for k,v in d.get('invitados',{}).items()}
def guardar_datos():
    json.dump({'usuarios':USUARIOS,'pagaron':list(PAGARON),'referidos':REFERIDOS,'invitados':INVITADOS}, open(DATA_FILE,'w'))

MX_PRECIOS="""🛍 VIDEOS 🛒

🎂 BÁSICO: $ 100 MXN → 5 vds
🔥 TOP: $200 MXN ← MÁS VENDIDO → 12 vds
🏆 PREMIUM: $400 MXN → 1 personalizado + 20 vds + sexting

📼 VIDEOLLAMADAS: $400 MXN 5min / $600 MXN 10min
CLABE: 646180546711450910 | Ref: yanae
Mándame captura bebé 🥰"""

PE_PRECIOS="""🛍 VIDEOS 🛒

🎂 BÁSICO: S/ 15 → 5 vds
🔥 TOP: S/ 30 ← MÁS VENDIDO → 12 vds
🏆 PREMIUM: S/ 60 → 1 personalizado + 20 vds + sexting

📼 VIDEOLLAMADAS: S/ 60 5min / S/ 80 10min
YAPE/PLIN: 923553612
Mándame captura bebé 🥰"""

USA_PRECIOS=f"""🛍 VIDEOS 🛒

🎂 BÁSICO: $5 USD → 5 vds
🔥 TOP: $9 USD ← MÁS VENDIDO → 12 vds
🏆 PREMIUM: $20 USD → 1 personalizado + 20 vds + sexting

📼 VIDEOLLAMADAS: $20 USD 5min / $35 USD 10min
PayPal/USDT: {LINK_PAYPAL}
Mándame captura bebé 🥰"""

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

TEXTO_INTERCAMBIO="No hago intercambios mor 🥰 yo vendo, pero si me cumples la promo de los videitos gratis o me compras un pack te doy videitos al toque 😏"
TEXTO_PREMIUM_EXTRA="Si mandas el PREMIUM ahora te mando el DOBLE mor 😍 20 vids extra + 2 personalizados solo por hoy, ¿te lo aparto?"

def normalizar(t): return unicodedata.normalize('NFKD',t or '').encode('ascii','ignore').decode().lower()
def precio_por_pais(p): return PE_PRECIOS if p=='pe' else MX_PRECIOS if p=='mx' else USA_PRECIOS
def detectar_pais(t):
    t=normalizar(t)
    if 'peru' in t: return 'pe'
    if 'mex' in t: return 'mx'
    if any(x in t for x in ['usa','eeuu','colombia','argentina','chile','ecuador','venezuela','bolivia','espana']): return 'usa'
    return None
def es_intencion_compra(t):
    kws=['vendes','me vendes','vendés','vendes contenido','vendes?','cuanto vendes','quiero comprar','quiero pack','quiero adquirir','me interesa','cuanto cuesta','cuanto sale','cuanto es','precio','precios','info','cuanto cobras']
    return any(k in t for k in kws)
def es_intercambio(t): return any(k in t for k in ['intercamb','cambias','cambio por','intercambio'])
def es_100(t): return ('100' in t and 'vista' in t) or 'ya cumpli' in t
def es_pago(t): return any(k in t for k in ['yape','plin','ya te pague','te yapee','yapee','transferi','deposite','comprobante','pago realizado','ya quedo','te pague'])

async def notificar_admin(tipo,uid,user,extra=""):
    url=f"https://t.me/{user}" if user else f"tg://user?id={uid}"
    cap=f"{tipo}\n👤 @{user if user else 'sin @'}\n🆔 <code>{uid}</code>\n{extra}"
    kb=InlineKeyboardMarkup([[InlineKeyboardButton("🔗 ABRIR CHAT",url=url)]])
    try: await app_bot.send_message(ADMIN_ID,cap,reply_markup=kb,parse_mode='HTML')
    except: await app_bot.send_message(ADMIN_ID,cap,parse_mode='HTML')

async def enviar_bienvenida(m):
    try:
        await m.reply_media_group([InputMediaPhoto(open(f'fotitos{i}.JPG','rb')) for i in range(1,6)])
    except: pass
    await m.reply_text(GRATIS_TEXTO)
    await m.reply_text(LINK_CANAL) # solo el link, sin texto

async def todo(upd,ctx):
    global app_bot; app_bot=ctx.bot
    m=upd.message or upd.business_message
    if not m or m.from_user.is_bot: return
    uid=m.from_user.id
    if uid not in USUARIOS: USUARIOS[uid]={}
    USUARIOS[uid].setdefault('flags',{})
    USUARIOS[uid]['n']=m.from_user.first_name; guardar_datos()
    es_neg=upd.business_message is not None
    txt=normalizar(m.text); raw=m.text or ""
    if es_neg and uid==ADMIN_ID: return

    # Si ya pago, solo reenvia a ti
    if uid in PAGARON and es_neg:
        if m.photo: await ctx.bot.send_photo(ADMIN_ID,m.photo[-1].file_id,caption=f"MEDIA DE PAGADOR {uid}")
        if m.video: await ctx.bot.send_video(ADMIN_ID,m.video[-1].file_id,caption=f"MEDIA DE PAGADOR {uid}")
        return

    if es_neg:
        # Foto/video -> solo te avisa, al cliente nada
        if m.photo or m.video:
            if m.photo: await ctx.bot.send_photo(ADMIN_ID,m.photo[-1].file_id,caption=f"FOTO {uid} @{m.from_user.username}")
            if m.video: await ctx.bot.send_video(ADMIN_ID,m.video[-1].file_id,caption=f"VIDEO {uid}")
            USUARIOS[uid]['flags']['media']=True; guardar_datos(); return

        # 100 vistas -> manda texto 500-1000 + te avisa en silencio
        if es_100(txt):
            if not USUARIOS[uid]['flags'].get('v100'):
                await m.reply_text(TEXTO_100)
                USUARIOS[uid]['flags']['v100']=True
            await notificar_admin("⚠️ DICE 100 VISTAS",uid,m.from_user.username,raw[:80])
            guardar_datos(); return

        # Pago -> solo te avisa, al cliente nada
        if es_pago(txt):
            await notificar_admin("💰 PAGO",uid,m.from_user.username,raw[:80])
            PAGARON.add(uid); USUARIOS[uid]['flags']['pago']=True; guardar_datos(); return

        # Intercambio
        if es_intercambio(txt):
            if not USUARIOS[uid]['flags'].get('inter'):
                await m.reply_text(TEXTO_INTERCAMBIO)
                USUARIOS[uid]['flags']['inter']=True; guardar_datos()
            return

        # Guarda pais si lo menciona, pero NO manda precios solo por pais
        pais_mencion=detectar_pais(txt)
        if pais_mencion:
            USUARIOS[uid]['pais']=pais_mencion; guardar_datos()
            # no return, sigue evaluando si además quiere comprar

        # Solo manda precios si pregunta si vendes / quiere comprar
        if es_intencion_compra(txt):
            if USUARIOS[uid]['flags'].get('precios'): return # anti-spam
            p=USUARIOS[uid].get('pais') or detectar_pais(txt) or 'usa'
            await m.reply_text(precio_por_pais(p))
            # Si menciona premium, manda extra
            if 'premium' in txt and not USUARIOS[uid]['flags'].get('prem_extra'):
                await m.reply_text(TEXTO_PREMIUM_EXTRA)
                USUARIOS[uid]['flags']['prem_extra']=True
            USUARIOS[uid]['flags']['precios']=True; guardar_datos()
            ctx.job_queue.run_once(lambda c: c.bot.send_message(c.job.data['cid'],"sigues ahí? 🥹 si mandas el PREMIUM ahora te doy el doble 😍",business_connection_id=c.job.data.get('bc')),300,data={'cid':m.chat.id,'bc':getattr(m,'business_connection_id',None)},name=f"rec_{uid}")
            return

        # Primer contacto
        if not USUARIOS[uid]['flags'].get('bienvenida'):
            await enviar_bienvenida(m)
            USUARIOS[uid]['flags']['bienvenida']=True; guardar_datos()
            return
        return

    if m.chat.type=='private': await m.reply_text("Escribe al privado de @yanabicitasa")

def main():
    cargar_datos()
    app=Application.builder().token(TOKEN).build()
    from telegram.ext import TypeHandler
    app.add_handler(TypeHandler(Update,todo))
    app.run_polling(allowed_updates=['message','business_message'])

if __name__=='__main__': main()
