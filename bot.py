import os, json, logging, unicodedata, random, difflib, re
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto, Update
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, MessageHandler, filters

logging.basicConfig(level=logging.INFO)
TOKEN = '8762577283:AAFVT7_WMpZ7njVnToIlZypUpCToF5LGcbA'
ADMIN_ID = 8783569348
LINK_CANAL = "https://t.me/+zt1RzGevdHBjMDgx"
LINK_PAYPAL = "https://www.paypal.com/qrcodes/p2pqrc/76RWY9FF7Q7RE"

USUARIOS = {}; INVITADOS = {}; REFERIDOS = {}; JOBS_FOLLOW = {}; ESPERA_PAIS = {}; DATA_FILE = "data.json"

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
📝 Ref: <code>yanae</code>
1. Pagas 2. Captura"""

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
<code>923553612</code>
1. Yapeas 2. Captura"""

USA_PRECIOS = """🛍 <b>VIDEOS</b> 🛒

🎂 <b>BÁSICO: $5 USD</b>
→ 5 videitos | $1 c/u

━━━━━━━━━━━━━━
🔥 <b>TOP: $9 USD ← MÁS VENDIDO</b>
→ 12 videitos | $0.75 c/u

━━━━━━━━━━━━━━
🏆 <b>PREMIUM: $20 USD</b>
→ 20 videitos + 1 perso + sexting

━━━━━━━━━━━━━━
📼 <b>VIDEOLLAMADAS</b> $20 5min | $35 10min

<b>PAGO USA - toca para copiar:</b>
🔗 PayPal: <code>AbigailMaximoofO</code>
🌐 Link: <code>https://www.paypal.com/qrcodes/p2pqrc/76RWY9FF7Q7RE</code>
1. Pagas 2. Captura"""

GRATIS_TODO = """✨ <b>¿QUIERES GANAR HASTA 20 VIDEITOS GRATIS? :3</b> ✨

Te explico todo juntito mor, es súper fácil y te ayudo con truquito 🥺💖

🌸 <b>Tip que funciona mejor mor:</b>
Créate una cuentita nueva en TikTok, ponte una fotito tierna y un nombrecito lindo :3 tipo “karla19” “sofihot” así la gente entra más rápido a verte.

1️⃣ En tu bio pon: <code>Tg: yanabicitasa</code> ✨
2️⃣ Sube una fotito de las que te envié a tu story + una frase hot 😋
3️⃣ Mándame captura + videito de que lo hiciste
4️⃣ Me avisas cuando llegue a 100 vistas y luego a 500-1000
5️⃣ Disfruta de <b>HASTA 20 videitos</b> bien ricos ❤️‍🔥 :3

⚠️ Ojo mor: solo califico a compradores. Si promocionas a alguien más te bloqueo, si me promocionas a mí te mando regalitos extra 🎁

¿Le entras mor? dime: <i>ya cumplí con las 100 vistas</i>

💋 <b>Para conseguir vistas rápido mor:</b>
Busca videos con #hormo #hot #hormonal #amigoshormo y deja comentarios bien ricos 🥵

Escribe cositas como: “¿quién?” “¿alguno?” “miren mi story” “ando horm...”

Entre más caliente comentes, más gente entra a verte, mor 😏"""

TEXTO_100="Sii mor las 100 vistas son solo para que veas lo fácil que es :3 cuando llegues a 500-1000 me avisas y te suelto tus videitos al toque 🥵 mándame videito sin cortar"
TEXTO_INTER="No hago intercambios mor 🥰 yo vendo, pero si cumples la promo te doy videitos al toque 😏"

# MENSAJE CORREGIDO - YA NO PIDE MÁS DINERO
CUMPLIDO_MSG = "ando algo ocupadita haciéndo videollamada 👀 en un ratito te confirmo mor 🥰"
PAGO_MSG = "ando algo ocupadita haciéndo videollamada 👀 en un ratito te confirmo mor 🥰"

REAL_MSGS = [
    f"Sii soy yo mor 🥰 revisa mi canal ahí subo todo sin censura, verás que soy real :3\n{LINK_CANAL}",
    f"Soy real mor, entra a mi canal y ves mis videitos nuevos bien ricos 🙈✨\n{LINK_CANAL}",
    f"Claro que soy yo mor 🥺 en mi canal me ves completita, ahí estoy grabando ahora\n{LINK_CANAL}"
]
VIDEOLLAMADA_MSGS = [
    "Videollamadita 🥰 5 y 10 min, si me compras ahora te doy prioridad :3",
    "Hago videollamadita solo virtual mor 5 y 10 min 🥰 si me compras ahora te consiento mucho 😏"
]
DUDAR_MSGS=["Entiendo mor piensalo tranqui 🥺 pero si me compras ahora te pongo en prioridad 💖","Puedes pensarlo bebe las que pagan ahora las atiendo primero y con extra 😏"]
CALENTADA_MSGS=["Cuando compras te enseño todo sin censura mor completito para ti 🥵","Si compras te muestro todo lo que no subo a ningun lado 😏"]
COMPRA_MSGS=["TOP y PREMIUM son los mas pedidos mor 🔥 te contesto al toque despues del pago :3","Si eliges TOP o PREMIUM te mando extras bien ricos 💋"]
VIDEITOS_MSGS=["Videitos tengo BÁSICO, TOP y PREMIUM mor 🔥","Mis videitos son sin censura el TOP es el mas pedido y PREMIUM te enseño todo 💖"]
SALIR_MSGS=["Por ahora no hago saliditas mor 🙈 soy solo virtual pero bien atrevida si eres premium 💋","No hago presencial bebe pero virtual soy toda tuya si eres TOP o PREMIUM 😏"]
FOLLOW_MSGS=["Anais caliente si compras ahora y me sorprendes te doy doble mor 🥵","Bebe solo hoy doble + extra si me compras 😏","Mor me quede con ganas si compras ahora te lo doy todo x2 🙈"]

def cargar_datos():
    global USUARIOS, INVITADOS, REFERIDOS
    if os.path.exists(DATA_FILE):
        try:
            d=json.load(open(DATA_FILE))
            USUARIOS={int(k):v for k,v in d.get('usuarios',{}).items()}
            INVITADOS={int(k):v for k,v in d.get('invitados',{}).items()}
            REFERIDOS={int(k):v for k,v in d.get('referidos',{}).items()}
        except: pass
def guardar_datos(): json.dump({'usuarios':USUARIOS,'invitados':INVITADOS,'referidos':REFERIDOS}, open(DATA_FILE,'w'))
def get_menu(): return InlineKeyboardMarkup([[InlineKeyboardButton("💎 COMPRAR",callback_data='comprar')],[InlineKeyboardButton("🎁 GRATIS",callback_data='gratis')]])
def get_precios():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🇵🇪 Perú", callback_data='pe')],
        [InlineKeyboardButton("🇲🇽 México", callback_data='mx')],
        [InlineKeyboardButton("🌍 Otros", callback_data='usa')]
    ])
def normalizar(t):
    if not t: return ""
    t=unicodedata.normalize('NFKD',t).encode('ascii','ignore').decode().lower()
    return re.sub(r'[^\w\s]',' ',t)
def similar(a,b): return difflib.SequenceMatcher(None,a,b).ratio()
def fuzzy(texto, lista, umbral=0.68):
    if not texto: return False
    for w in texto.split():
        for p in lista:
            if p in w or w in p or similar(w,p)>=umbral: return True
    return False
def detectar_pais(t):
    t=normalizar(t)
    if any(x in t for x in ['peru','pe']): return 'pe'
    if any(x in t for x in ['mexico','mx']): return 'mx'
    if any(x in t for x in ['usa','eeuu','colombia','argentina','chile','otros','mundo','dolar']): return 'usa'
    return None
def detectar_intencion(txt, cap=""):
    t=normalizar(f"{txt} {cap}")
    if any(x in t for x in ['eres real','eres bot','eres un bot','robot','fake','no eres real','prueba que eres','asegurarme que eres','ver que eres real','eres tu','video para asegurarme']):
        return "real"
    if any(x in t for x in ['no entendi','no entiendo','como es','explica','como funciona']): return "no_entendi"
    if any(x in t for x in ['ya cumpli','ya cumplí','cumpli','ya esta','termine promo','ya lo hice','ya lo subi']): return "cumplido"
    if fuzzy(t, ["videollamada","vdeollamada","llamada","en vivo"]): return "videollamada"
    if fuzzy(t, ["yape","plin","pague","pago","comprobante","transfer","capture"]): return "pago"
    if "100" in t and "vist" in t: return "vistas100"
    if fuzzy(t, ["intercambio","cambias"]): return "intercambio"
    if fuzzy(t, ["salir","vernos","encuentro","hotel","presencial"]): return "salir"
    if fuzzy(t, ["pienso","pensarlo","luego"]): return "dudar"
    if fuzzy(t, ["gratis","grtis","promo","regalo"]): return "promo"
    if fuzzy(t, ["videitos","vdeitos","videos","pack"]): return "videitos"
    if fuzzy(t, ["precio","presio","cuanto","qnto","comprar","costo"]): return "comprar"
    if fuzzy(t, ["caliente","cachondo","ganas"]): return "hormonal"
    return "otro"
def puede(uid,k): USUARIOS.setdefault(uid,{}); USUARIOS[uid].setdefault('flags',{}); return not USUARIOS[uid]['flags'].get(k)
def no_repite(uid,tipo,lista):
    USUARIOS[uid].setdefault('usados',{}); usados=USUARIOS[uid]['usados'].get(tipo,[])
    disp=[m for m in lista if m not in usados]
    if not disp: disp=lista; usados=[]
    ch=random.choice(disp); usados.append(ch)
    if len(usados)>4: usados=usados[-4:]
    USUARIOS[uid]['usados']=usados; guardar_datos(); return ch
def link_directo(uid,un): return f"https://t.me/{un}" if un!='None' else f"tg://user?id={uid}"
def teclado_admin(uid,un):
    url=link_directo(uid,un)
    return InlineKeyboardMarkup([[InlineKeyboardButton("✅ Confirmar",callback_data=f"ok_{uid}"),InlineKeyboardButton("❌ Pedir prueba",callback_data=f"no_{uid}")],[InlineKeyboardButton("🚫 Ban",callback_data=f"ban_{uid}"),InlineKeyboardButton("🔗 Abrir",url=url)]])
def precio_por_pais(p): return PE_PRECIOS if p=='pe' else MX_PRECIOS if p=='mx' else USA_PRECIOS

async def bienvenida_promo(m):
    try: await m.reply_media_group([InputMediaPhoto(open(f'fotitos{i}.JPG','rb')) for i in range(1,6)])
    except: pass
    await m.reply_text(GRATIS_TODO, parse_mode='HTML')

async def followup_job(c):
    uid=c.job.data['uid']; chat_id=c.job.data['chat_id']
    USUARIOS.setdefault(uid,{})
    if USUARIOS[uid].get('flags',{}).get('pausado'): return
    co=USUARIOS[uid].get('follow',0)
    if co>=3: return
    try: await c.bot.send_message(chat_id,no_repite(uid,'follow',FOLLOW_MSGS)); USUARIOS[uid]['follow']=co+1; guardar_datos()
    except: pass
JOBS_FOLLOW={}
def prog_follow(ctx,uid,cid):
    if uid in JOBS_FOLLOW:
        try: JOBS_FOLLOW[uid].schedule_removal()
        except: pass
    JOBS_FOLLOW[uid]=ctx.job_queue.run_once(followup_job,300,data={'uid':uid,'chat_id':cid})

async def start_cmd(u,c): await u.message.reply_text("Hola mor 🥵",reply_markup=get_menu())

async def btn(u,c):
    q=u.callback_query; await q.answer(); d=q.data
    if q.from_user.id==ADMIN_ID and "_" in d:
        try:
            acc,t=d.split("_"); t=int(t)
            if acc=="ok": await c.bot.send_message(t,"Listo mor ya te confirmé 💖"); await q.edit_message_caption(caption=(q.message.caption or "")+"\n✅ CONFIRMADO"); USUARIOS.setdefault(t,{}).setdefault('flags',{})['pausado']=False
            elif acc=="no": await c.bot.send_message(t,"Mor mándame mejor la pruebita completa porfa 🥺"); await q.edit_message_caption(caption=(q.message.caption or "")+"\n❌ PEDIDA PRUEBA"); USUARIOS.setdefault(t,{}).setdefault('flags',{})['pausado']=False
            elif acc=="ban": USUARIOS.setdefault(t,{}).setdefault('flags',{})['ban']=True
            guardar_datos(); return
        except: pass
    if d=='comprar': await q.edit_message_text("De donde eres mor 👀✨", reply_markup=get_precios())
    elif d=='pe': await q.edit_message_text(PE_PRECIOS, parse_mode='HTML')
    elif d=='mx': await q.edit_message_text(MX_PRECIOS, parse_mode='HTML')
    elif d=='usa': await q.edit_message_text(USA_PRECIOS, parse_mode='HTML')
    elif d=='gratis': await q.edit_message_text(GRATIS_TODO, parse_mode='HTML')

async def handle_all(update,context):
    m=update.business_message or update.message
    if not m or not m.from_user or m.from_user.is_bot: return
    uid=m.from_user.id; un=m.from_user.username or "None"; raw=m.text or ""; cap=getattr(m,'caption','') or ""; es_neg=update.business_message is not None
    if es_neg and uid==ADMIN_ID: return
    USUARIOS.setdefault(uid,{})
    if USUARIOS[uid].get('flags',{}).get('ban') or USUARIOS[uid].get('flags',{}).get('pausado'): return
    if uid in JOBS_FOLLOW:
        try: JOBS_FOLLOW[uid].schedule_removal(); del JOBS_FOLLOW[uid]
        except: pass
    if es_neg:
        if m.photo or m.video:
            is_v=bool(m.video); fid=m.video.file_id if is_v else m.photo[-1].file_id
            tipo="💰 CAPTURA PAGO" if fuzzy(normalizar(cap),["yape","plin","pago"]) else "📸 PRUEBA PROMO"
            try:
                if is_v: await context.bot.send_video(ADMIN_ID,fid,caption=f"{tipo}\n@{un} {uid}",reply_markup=teclado_admin(uid,un))
                else: await context.bot.send_photo(ADMIN_ID,fid,caption=f"{tipo}\n@{un} {uid}",reply_markup=teclado_admin(uid,un))
            except: pass
            await m.reply_text(CUMPLIDO_MSG); USUARIOS[uid].setdefault('flags',{})['pausado']=True; guardar_datos(); return

        intent=detectar_intencion(raw,cap); pais=detectar_pais(raw)
        if not USUARIOS[uid].get('flags',{}).get('saludo'):
            await m.reply_text(SALUDO_NEGOCIO); USUARIOS[uid].setdefault('flags',{})['saludo']=True; guardar_datos(); prog_follow(context,uid,m.chat.id); return
        if uid in ESPERA_PAIS and pais:
            await m.reply_text(precio_por_pais(pais), parse_mode='HTML'); del ESPERA_PAIS[uid]; guardar_datos(); prog_follow(context,uid,m.chat.id); return

        if intent=="cumplido":
            await m.reply_text(CUMPLIDO_MSG); await context.bot.send_message(ADMIN_ID,f"✅ CUMPLIÓ PROMO @{un} {uid}\n{raw}",reply_markup=teclado_admin(uid,un)); USUARIOS[uid].setdefault('flags',{})['pausado']=True; guardar_datos(); return
        if intent=="pago":
            await m.reply_text(PAGO_MSG); await context.bot.send_message(ADMIN_ID,f"💰 PAGÓ @{un} {uid}\n{raw}",reply_markup=teclado_admin(uid,un)); USUARIOS[uid].setdefault('flags',{})['pausado']=True; guardar_datos(); return

        if intent=="real": await m.reply_text(no_repite(uid,'real',REAL_MSGS)); guardar_datos(); prog_follow(context,uid,m.chat.id); return
        if intent=="no_entendi":
            await m.reply_text("Tranqui mor te explico facilito 🥺👇\nTengo videitos y videollamada, todo virtual 🙈"); await m.reply_text("De donde eres mor 👀✨", reply_markup=get_precios()); ESPERA_PAIS[uid]=True; guardar_datos(); prog_follow(context,uid,m.chat.id); return

        if intent=="vistas100":
            if puede(uid,'v100'): await m.reply_text(TEXTO_100); USUARIOS[uid].setdefault('flags',{})['v100']=True
        elif intent=="promo": await bienvenida_promo(m)
        elif intent=="videollamada":
            await m.reply_text(no_repite(uid,'vdll',VIDEOLLAMADA_MSGS)); await m.reply_text("De donde eres mor 👀✨", reply_markup=get_precios()); ESPERA_PAIS[uid]=True
        elif intent in ["videitos","comprar"]:
            await m.reply_text(no_repite(uid,'compra',COMPRA_MSGS)); await m.reply_text("De donde eres mor 👀✨", reply_markup=get_precios()); ESPERA_PAIS[uid]=True
        elif intent=="dudar": await m.reply_text(no_repite(uid,'dudar',DUDAR_MSGS))
        elif intent=="hormonal": await m.reply_text(no_repite(uid,'calentada',CALENTADA_MSGS))
        elif intent=="intercambio":
            if puede(uid,'inter'): await m.reply_text(TEXTO_INTER); USUARIOS[uid].setdefault('flags',{})['inter']=True
        elif intent=="salir": await m.reply_text(no_repite(uid,'salir',SALIR_MSGS))
        else: await m.reply_text("Dime mor quieres gratis o comprar? 🙈 tengo videitos y videollamada, mor 😏")
        guardar_datos(); prog_follow(context,uid,m.chat.id); return

def main():
    cargar_datos()
    app=Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start",start_cmd))
    app.add_handler(CallbackQueryHandler(btn))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_all))
    app.add_handler(MessageHandler(filters.UpdateType.BUSINESS_MESSAGE, handle_all))
    app.add_handler(MessageHandler(filters.PHOTO | filters.VIDEO, handle_all))
    app.add_handler(MessageHandler(filters.UpdateType.BUSINESS_MESSAGE & (filters.PHOTO | filters.VIDEO), handle_all))
    app.add_handler(MessageHandler(filters.CAPTION & filters.UpdateType.BUSINESS_MESSAGE, handle_all))
    print("Bot final - ocupadita en videollamada listo")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__=='__main__': main()
