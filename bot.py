import os, json, logging, unicodedata
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, ChatMemberHandler, TypeHandler

logging.basicConfig(level=logging.INFO)
TOKEN = '8762577283:AAFVT7_WMpZ7njVnToIlZypUpCToF5LGcbA'
ADMIN_ID = 8783569348
LINK_CANAL = "https://t.me/+zt1RzGevdHBjMDgx"
LINK_PAYPAL = "https://www.paypal.com/qrcodes/p2pqrc/76RWY9FF7Q7RE"

USUARIOS = {}; PAGARON = set(); REFERIDOS = {}; INVITADOS = {}; ESPERA_PAIS = {}; DATA_FILE = "data.json"

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
PayPal: AbigailMaximoofO / USDT
Link: {LINK_PAYPAL}

Avísame cuando envíes con el comprobante 🥰
En cuanto caiga te mando tu pack 🔥
1. Pagas 2. Captura
Si no contesto envías cap del pago a : @YanaBiBot con estos precios."""

# --- NUEVO TEXTO CON ACLARACIÓN ---
GRATIS_TEXTO="""(REGALITO)
✨ QUIERES HASTA 20 VIDEITOS GRATSS? ✨

Pasitos súper fáciles uwu:
1️⃣ En tu bio de TikTok pon: Tg: yanabicitasa ✨
2️⃣ Sube una fotito de las que te envié a tu story + Frase hot 😋
3️⃣ Mándame captura + videito cuando cumplas
4️⃣ Me confirmas cuando llegue a 100 vistas(story) :3
5️⃣ Disfruta de hasta 20 videitos :3 ❤️‍🔥

⚠️ Ojo mor: solo califico a compradores. Si promocionas a alguien más te bloqueo. Si me promocionas a mí te mando regalitos extra 🥺🎁

¿Te animas o ño? 🥺
(Me avisas diciendo: ya cumpli con las 100 vistas )
(Revisa mi perfil)"""

MSG_GANAS="""Si tienes muchas ganas de verme 🙈🔥
https://t.me/YanaBiBot"""

TEXTO_100="""Las 100 vistas son solo para que veas lo fácil que es, mor :3 💕

Cuando tu story llegue a 500-1000 me avisas y te suelto tus videitos al toque 🥵

Mándame videito entrando a TikTok → tu perfil → tu story → los likes, TODO seguido sin cortar. Si lo cortas se anula la promo, bebé 😘"""
TEXTO_INTER="No hago intercambios mor 🥰 yo vendo, pero si me cumples la promo de los videitos gratis o me compras un pack te doy videitos al toque 😏"
TEXTO_GRATIS="tienes que cumplir con la promoción Mor 🥺"

def get_menu():
    return InlineKeyboardMarkup([[InlineKeyboardButton("💎 COMPRAR",callback_data='comprar')],[InlineKeyboardButton("🎁 GRATIS",callback_data='gratis')],[InlineKeyboardButton("🔗 MI LINK",callback_data='milink')],[InlineKeyboardButton("📊 RANKING",callback_data='ranking')],[InlineKeyboardButton("🔥 Canal",url=LINK_CANAL)]])
def get_precios():
    return InlineKeyboardMarkup([[InlineKeyboardButton("🇵🇪 Perú",callback_data='pe')],[InlineKeyboardButton("🇲🇽 México",callback_data='mx')],[InlineKeyboardButton("🇺🇸 EEUU",callback_data='usa')]])

def normalizar(t): return unicodedata.normalize('NFKD',t or '').encode('ascii','ignore').decode().lower()
def precio_por_pais(p): return PE_PRECIOS if p=='pe' else MX_PRECIOS if p=='mx' else USA_PRECIOS
def detectar_pais(t):
    t=normalizar(t)
    if 'peru' in t: return 'pe'
    if 'mex' in t: return 'mx'
    if any(x in t for x in ['usa','eeuu','colombia','argentina','chile','ecuador','venezuela','bolivia','espana']): return 'usa'
    return None
def es_compra(t): return any(k in t for k in ['vendes','me vendes','precio','precios','cuanto cuesta','pasame'])
def es_gratis(t): return any(k in t for k in ['video gratis','videos gratis','videito gratis','regalame','gratis'])
def es_100(t): return ('100' in t and 'vista' in t) or 'ya cumpli' in t
def es_pago(t): return any(k in t for k in ['yape','plin','ya te pague','te yapee','comprobante','te pague'])
def puede(uid,key):
    USUARIOS[uid].setdefault('flags',{})
    return not USUARIOS[uid]['flags'].get(key)
def link_directo(uid,username):
    url=f"https://t.me/{username}" if username and username!='None' else f"tg://user?id={uid}"
    return InlineKeyboardMarkup([[InlineKeyboardButton("🔗 ABRIR CHAT DIRECTO", url=url)]])
async def notificar_admin(tipo,uid,username,texto=""):
    msg=f"{tipo}\n👤 @{username}\n🆔 <code>{uid}</code>\n💬 {texto[:120]}"
    try: await app_bot.send_message(ADMIN_ID,msg,reply_markup=link_directo(uid,username),parse_mode='HTML')
    except: pass
async def bienvenida(m):
    try: await m.reply_media_group([InputMediaPhoto(open(f'fotitos{i}.JPG','rb')) for i in range(1,6)])
    except: pass
    await m.reply_text(GRATIS_TEXTO)
    await m.reply_text(MSG_GANAS)
    await m.reply_text(LINK_CANAL)

async def start_cmd(upd,ctx):
    uid=upd.message.from_user.id
    USUARIOS.setdefault(uid,{}); USUARIOS[uid].setdefault('flags',{})
    if puede(uid,'menu_normal'):
        await upd.message.reply_text("Hola mor 🥵 acá consultas precios y la que te cumple es @yanabicitasa", reply_markup=get_menu())
        USUARIOS[uid]['flags']['menu_normal']=True; guardar_datos()

async def btn(upd,ctx):
    q=upd.callback_query; await q.answer()
    if q.data=='comprar': await q.edit_message_text("Elige tu país:", reply_markup=get_precios())
    elif q.data=='pe': await q.edit_message_text(PE_PRECIOS)
    elif q.data=='mx': await q.edit_message_text(MX_PRECIOS)
    elif q.data=='usa': await q.edit_message_text(USA_PRECIOS)
    elif q.data=='gratis': await q.edit_message_text(GRATIS_TEXTO + "\n\n" + MSG_GANAS)
    elif q.data=='milink':
        link=f"https://t.me/YanaBiBot?start={q.from_user.id}"; REFERIDOS[q.from_user.id]={'link':link}; guardar_datos()
        await q.edit_message_text(f"Tu link:\n{link}")
    elif q.data=='ranking':
        top=sorted(INVITADOS.items(),key=lambda x:x[1],reverse=True)[:5]
        txt="TOP:\n"+"\n".join([f"{i+1}. {USUARIOS.get(u,{}).get('n','?')} - {c}" for i,(u,c) in enumerate(top)]) or "Aún nadie"
        await q.edit_message_text(txt)

async def todo(upd,ctx):
    global app_bot; app_bot=ctx.bot
    m=upd.message or upd.business_message
    if not m or m.from_user.is_bot: return
    uid=m.from_user.id; username=m.from_user.username or "None"
    USUARIOS.setdefault(uid,{}); USUARIOS[uid].setdefault('flags',{})
    txt=normalizar(m.text); raw=m.text or ""
    es_neg=upd.business_message is not None
    if es_neg and uid==ADMIN_ID: return

    if es_neg:
        if m.photo: await ctx.bot.send_photo(ADMIN_ID,m.photo[-1].file_id,caption=f"📸 @{username} {uid}",reply_markup=link_directo(uid,username)); return
        if m.video: await ctx.bot.send_video(ADMIN_ID,m.video[-1].file_id,caption=f"🎥 @{username} {uid}",reply_markup=link_directo(uid,username)); return
        if es_pago(txt): await notificar_admin("💰 PAGO",uid,username,raw); PAGARON.add(uid); guardar_datos(); return
        if es_100(txt):
            if puede(uid,'v100'): await m.reply_text(TEXTO_100); USUARIOS[uid]['flags']['v100']=True
            await notificar_admin("🎁 PROMO - 100 VISTAS",uid,username,raw); guardar_datos(); return
        if 'intercamb' in txt or 'cambias' in txt:
            if puede(uid,'inter'): await m.reply_text(TEXTO_INTER); USUARIOS[uid]['flags']['inter']=True; guardar_datos()
            return
        if es_gratis(txt):
            if puede(uid,'bienvenida'): await bienvenida(m); USUARIOS[uid]['flags']['bienvenida']=True
            else:
                if puede(uid,'rec_gratis'): await m.reply_text(TEXTO_GRATIS); USUARIOS[uid]['flags']['rec_gratis']=True
            guardar_datos(); return
        p_det=detectar_pais(txt)
        if p_det: USUARIOS[uid]['pais']=p_det; guardar_datos()
        if uid in ESPERA_PAIS:
            p=detectar_pais(txt) or USUARIOS[uid].get('pais')
            if p and puede(uid,'precios'): await m.reply_text(precio_por_pais(p)); USUARIOS[uid]['flags']['precios']=True; del ESPERA_PAIS[uid]; guardar_datos()
            return
        if es_compra(txt):
            p=USUARIOS[uid].get('pais') or p_det
            if p:
                if puede(uid,'precios'): await m.reply_text(precio_por_pais(p)); USUARIOS[uid]['flags']['precios']=True; guardar_datos()
                return
            else:
                if puede(uid,'preg_pais'): await m.reply_text("de donde eres mor?:3"); USUARIOS[uid]['flags']['preg_pais']=True; ESPERA_PAIS[uid]=True; guardar_datos()
                return
        if puede(uid,'bienvenida'): await bienvenida(m); USUARIOS[uid]['flags']['bienvenida']=True; guardar_datos()
        return
    else:
        if m.chat.type=='private':
            if puede(uid,'menu_normal'):
                await m.reply_text("Hola mor 🥵 acá consultas precios y la que te cumple es @yanabicitasa", reply_markup=get_menu())
                USUARIOS[uid]['flags']['menu_normal']=True; guardar_datos()
            return

async def nuevo(upd,ctx):
    cm=upd.chat_member
    if cm.old_chat_member.status in ['left','kicked'] and cm.new_chat_member.status=='member':
        if not cm.new_chat_member.user.is_bot: INVITADOS[cm.from_user.id]=INVITADOS.get(cm.from_user.id,0)+1; guardar_datos()

def main():
    cargar_datos()
    app=Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start",start_cmd))
    app.add_handler(CallbackQueryHandler(btn))
    app.add_handler(TypeHandler(Update,todo))
    app.add_handler(ChatMemberHandler(nuevo, ChatMemberHandler.CHAT_MEMBER))
    app.run_polling(allowed_updates=['message','business_message','callback_query','chat_member'])

if __name__=='__main__': main()
