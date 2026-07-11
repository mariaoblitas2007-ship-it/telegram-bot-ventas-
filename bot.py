import os, json, logging, unicodedata, asyncio, random, difflib, re
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto, Update
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, MessageHandler, ContextTypes, filters

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

MX_PRECIOS = """🛍 VIDEOS 🛒

🎂 BÁSICO: $ 100 MXN → 5 vds | $20 c/u
🔥 TOP: $200 MXN ← MÁS VENDIDO → 12 vds | $16 c/u
🏆 PREMIUM: $400 MXN → 1 personalizado + 20 vds + sexting

📼 VIDEOLLAMADAS $400 MXN 5min | $600 MXN 10min

PAGO:
🏦 STP CLABE: 646180546711450910
📝 Ref: yanae
1. Pagas 2. Captura"""

PE_PRECIOS = """🛍 VIDEOS 🛒
🎂 BÁSICO: S/ 15 → 5 vds
🔥 TOP: S/ 30 → 12 vds | S/2.50 c/u
🏆 PREMIUM: S/ 60 → 1 perso + 20 vds + sexting
📼 VIDEOLLAMADAS S/60 5min | S/80 10min
YAPE/PLIN: 923553612
1. Yapeas 2. Captura"""

USA_PRECIOS = f"""🛍 VIDEOS 🛒
BÁSICO $5 → 5 vds | TOP $9 → 12 vds | PREMIUM $20 → 20 vds + perso + sexting
VIDEOLLAMADAS $20 5min / $35 10min
PayPal: AbigailMaximoofO
Link: {LINK_PAYPAL}
1. Pagas 2. Captura"""

GRATIS_TEXTO="""✨ QUIERES HASTA 20 VIDEITOS GRATSS? ✨
1️⃣ Bio TikTok: Tg: yanabicitasa ✨
2️⃣ Sube fotito que te envié a tu story + frase hot 😋
3️⃣ Mándame captura + videito cuando cumplas
4️⃣ Confirma 100 vistas :3
5️⃣ Disfruta 20 videitos ❤️‍🔥

⚠️ Solo califico a compradores. Si promocionas a alguien más te bloqueo. Si me promocionas a mí te mando regalitos extra 🥺🎁
(Me avisas: ya cumpli con las 100 vistas)"""
TEXTO_100="Las 100 vistas son solo para que veas lo fácil que es mor :3 cuando llegues a 500-1000 me avisas y te suelto todo 🥵 mándame video sin cortar"
TEXTO_INTER="No hago intercambios mor 🥰 yo vendo, pero si cumples la promo te doy videitos al toque 😏"

DUDAR_MSGS=["Entiendo mor piensalo tranqui 🥺 pero si me sorprendes con el pago ahora te pongo en prioridad 💖","Puedes pensarlo bebe las que pagan ahora las atiendo primero y con extra 😏","Tomate tu tiempo mor si me sorprendes hoy te dejo en VIP ✨","Vale mor piensalo si me sorprendes te mando algo que nadie tiene 🙈","Tranqui bebe si me sorprendes ahora te atiendo primero 💋"]
CALENTADA_MSGS=["Cuando compras te enseño todo sin censura mor completito para ti 🥵","Si compras te muestro todo lo que no subo a ningun lado 😏","Comprando ves mi lado mas atrevido sin tapujos 🙈✨","Cuando compres no me guardo nada todo es para ti 💖","Con el pack te enseño todo sin recortes bien cerquita 😘"]
COMPRA_MSGS=["TOP y PREMIUM son los mas pedidos 🔥 si mandas poquito mas te mando extras y te contesto al toque despues del pago :3","Si eliges TOP o PREMIUM y das extra te regalo videitos fuera de catalogo despues del pago 💋","TOP y PREMIUM vienen con sorpresita y si envias mas te mando exclusivos ✨","Con TOP o PREMIUM te consiento mas y te atiendo primero despues del pago 🥺","Elige PREMIUM y si mandas extra te mando doble + extras al instante 💖"]
VIDEOLLAMADA_MSGS=["Videollamadita solo virtual mor 🥰 5 y 10 min, si compras ahora te doy prioridad :3","Videollamada solo para mis premium que me consienten mor 😏","Hago videollamada bien coqueta solo virtual si me compras TOP o PREMIUM te dejo extra ✨","Videollamada solo virtual si me sorprendes con dinerito te doy mas tiempo 🙈","Videollamada con pago previo mor me compras y te contesto al instante 💋"]
VIDEITOS_MSGS=["Videitos tengo BÁSICO, TOP y PREMIUM mor 🔥 si compras ahora doble 🥵","Tengo packs de 5,12 y 20 videitos el PREMIUM con personalizado y extra 😏","Mis videitos son sin censura el TOP es el mas pedido y PREMIUM te enseño todo 💖","Dime de donde eres y te paso precios mor y si me sorprendes te doy extras ✨","Videitos al toque despues del pago :3 TOP o PREMIUM con regalitos 🙈"]
SALIR_MSGS=["Por ahora no hago saliditas mor 🙈 soy solo virtual pero bien atrevida si eres premium 💋","No hago presencial bebe pero virtual soy toda tuya si eres TOP o PREMIUM 😏","No salgo mor pero en virtual me porto super coqueta para mis premium ✨","No hago encuentros mi contenido es solo virtual y bien completito 🥰","Soy solo virtual mor si me consientes como premium te consiento al doble 💖"]
FOLLOW_MSGS=["Anais caliente si compras ahora te doy doble contenido aprovecha mor 🥵","Bebe solo hoy doble + extra si compras 😏","Mor me quede con ganas si compras ahora todo x2 🙈","Me dejas en visto? 🥺 5 videitos mas si compras","Solita y con ganas 🔥 doble si compras en 10 min","Te vi en linea 👀 precio especial y doble","No me dejes con ganas comprame pack y te sorprendo ✨","Si compras ahora audios + fotos que no subo 😈","Ultima promo paga 1 llevas 2 💋","Te espero 🥺 si compras te mando todo al toque"]

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
def get_menu(): return InlineKeyboardMarkup([[InlineKeyboardButton("💎 COMPRAR",callback_data='comprar')],[InlineKeyboardButton("🎁 GRATIS",callback_data='gratis')],[InlineKeyboardButton("🔗 MI LINK",callback_data='milink')],[InlineKeyboardButton("📊 RANKING",callback_data='ranking')]])
def get_precios(): return InlineKeyboardMarkup([[InlineKeyboardButton("🇵🇪 Perú",callback_data='pe')],[InlineKeyboardButton("🇲🇽 México",callback_data='mx')],[InlineKeyboardButton("🇺🇸 EEUU",callback_data='usa')]])
def normalizar(t):
    if not t: return ""
    t=unicodedata.normalize('NFKD',t).encode('ascii','ignore').decode().lower()
    return re.sub(r'[^\w\s]',' ',t)
def similar(a,b): return difflib.SequenceMatcher(None,a,b).ratio()
def fuzzy(texto, lista, umbral=0.72):
    if not texto: return False
    for w in texto.split():
        for p in lista:
            if p in w or w in p or similar(w,p)>=umbral: return True
    return False
def detectar_pais(t):
    t=normalizar(t)
    if 'peru' in t: return 'pe'
    if 'mex' in t: return 'mx'
    if any(x in t for x in ['usa','eeuu','colombia','argentina','chile','ecuador']): return 'usa'
    return None
def detectar_intencion(txt, cap=""):
    t=normalizar(f"{txt} {cap}")
    if fuzzy(t, ["videollamada","vdeollamada","llamada","en vivo"]): return "videollamada"
    if fuzzy(t, ["yape","plin","pague","comprobante","transfer"]): return "pago"
    if "100" in t and "vist" in t: return "vistas100"
    if fuzzy(t, ["intercambio","cambias"]): return "intercambio"
    if fuzzy(t, ["salir","vernos","encuentro","cita","hotel","presencial","salidas"]): return "salir"
    if fuzzy(t, ["pienso","pensarlo","luego","despues"]): return "dudar"
    if fuzzy(t, ["gratis","grtis","promo","regalo"]): return "promo"
    if fuzzy(t, ["videitos","vdeitos","videos","pack","contenido"]): return "videitos"
    if fuzzy(t, ["precio","presio","cuanto","qnto","comprar","kiero"]): return "comprar"
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
    await m.reply_text(GRATIS_TEXTO)
    await m.reply_text(LINK_CANAL)

async def followup_job(c):
    uid=c.job.data['uid']; chat_id=c.job.data['chat_id']
    USUARIOS.setdefault(uid,{}); co=USUARIOS[uid].get('follow',0)
    if co>=3: return
    try: await c.bot.send_message(chat_id,no_repite(uid,'follow',FOLLOW_MSGS)); USUARIOS[uid]['follow']=co+1; guardar_datos()
    except: pass
JOBS_FOLLOW={}
def prog_follow(ctx,uid,cid):
    if uid in JOBS_FOLLOW:
        try: JOBS_FOLLOW[uid].schedule_removal()
        except: pass
    JOBS_FOLLOW[uid]=ctx.job_queue.run_once(followup_job,300,data={'uid':uid,'chat_id':cid})

async def start_cmd(u,c):
    uid=u.effective_user.id; USUARIOS.setdefault(uid,{}); USUARIOS[uid]['n']=u.effective_user.username or "?"
    if c.args and c.args[0].isdigit():
        ref=int(c.args[0])
        if ref!=uid and 'ref' not in USUARIOS[uid]:
            USUARIOS[uid]['ref']=ref; INVITADOS[ref]=INVITADOS.get(ref,0)+1; guardar_datos()
    await u.message.reply_text("Hola mor 🥵 acá consultas precios",reply_markup=get_menu())

async def btn(u,c):
    q=u.callback_query; await q.answer(); d=q.data
    if q.from_user.id==ADMIN_ID and "_" in d:
        try:
            acc,t=d.split("_"); t=int(t)
            if acc=="ok": await c.bot.send_message(t,"Gracias mor ya confirme tu pruebita 💖"); await q.edit_message_caption(caption=(q.message.caption or "")+"\n✅ CONFIRMADO")
            elif acc=="no": await c.bot.send_message(t,"Mor mándame mejor la pruebita completa porfa 🥺"); await q.edit_message_caption(caption=(q.message.caption or "")+"\n❌ PEDIDA PRUEBA")
            elif acc=="ban": USUARIOS.setdefault(t,{}).setdefault('flags',{})['ban']=True; guardar_datos(); await q.edit_message_caption(caption=(q.message.caption or "")+"\n🚫 BANEADO")
            return
        except: pass
    if d=='comprar': await q.edit_message_text("Elige tu país:",reply_markup=get_precios())
    elif d=='pe': await q.edit_message_text(PE_PRECIOS)
    elif d=='mx': await q.edit_message_text(MX_PRECIOS)
    elif d=='usa': await q.edit_message_text(USA_PRECIOS)
    elif d=='gratis': await q.edit_message_text(GRATIS_TEXTO)
    elif d=='milink':
        link=f"https://t.me/YanaBiBot?start={q.from_user.id}"; REFERIDOS[q.from_user.id]={'link':link}; guardar_datos()
        await q.edit_message_text(f"🔗 Tu link:\n{link}")
    elif d=='ranking':
        top=sorted(INVITADOS.items(),key=lambda x:x[1],reverse=True)[:10]
        txt="\n".join([f"{i+1}. @{USUARIOS.get(u,{}).get('n','?')} - {c}" for i,(u,c) in enumerate(top)]) if top else "Aún nadie"
        await q.edit_message_text(f"📊 RANKING\n{txt}")

async def handle_all(update,context):
    m=update.business_message or update.message
    if not m or not m.from_user or m.from_user.is_bot: return
    uid=m.from_user.id; un=m.from_user.username or "None"; raw=m.text or ""; cap=getattr(m,'caption','') or ""; es_neg=update.business_message is not None
    if es_neg and uid==ADMIN_ID: return
    USUARIOS.setdefault(uid,{})
    if USUARIOS[uid].get('flags',{}).get('ban'): return
    if uid in JOBS_FOLLOW:
        try: JOBS_FOLLOW[uid].schedule_removal(); del JOBS_FOLLOW[uid]
        except: pass
    if es_neg:
        if m.photo or m.video:
            is_v=bool(m.video); fid=m.video.file_id if is_v else m.photo[-1].file_id
            tipo="📸 PRUEBA"
            if fuzzy(normalizar(cap),["yape","plin","pago"]): tipo="💰 CAPTURA PAGO"
            elif fuzzy(normalizar(cap),["100","vista"]): tipo="🎁 PRUEBA 100 VISTAS"
            try:
                if is_v: await context.bot.send_video(ADMIN_ID,fid,caption=f"{tipo}\n@{un} {uid}",reply_markup=teclado_admin(uid,un))
                else: await context.bot.send_photo(ADMIN_ID,fid,caption=f"{tipo}\n@{un} {uid}",reply_markup=teclado_admin(uid,un))
            except: pass
            return
        intent=detectar_intencion(raw,cap); pais=detectar_pais(raw)
        # INMEDIATO - sin sleep de 2 min
        if not USUARIOS[uid].get('flags',{}).get('saludo'):
            await m.reply_text(SALUDO_NEGOCIO); USUARIOS[uid].setdefault('flags',{})['saludo']=True; guardar_datos(); prog_follow(context,uid,m.chat.id); return
        if uid in ESPERA_PAIS and pais:
            await m.reply_text(precio_por_pais(pais)); del ESPERA_PAIS[uid]; guardar_datos(); prog_follow(context,uid,m.chat.id); return
        if intent=="vistas100":
            if puede(uid,'v100'): await m.reply_text(TEXTO_100); USUARIOS[uid].setdefault('flags',{})['v100']=True
        elif intent=="promo": await bienvenida_promo(m)
        elif intent=="videollamada":
            await m.reply_text(no_repite(uid,'vdll',VIDEOLLAMADA_MSGS)); await m.reply_text("De donde eres mor? 🥺",reply_markup=get_precios()); ESPERA_PAIS[uid]=True
        elif intent=="videitos":
            await m.reply_text(no_repite(uid,'vds',VIDEITOS_MSGS)); await m.reply_text("De donde eres mor? 🥺",reply_markup=get_precios()); ESPERA_PAIS[uid]=True
        elif intent=="comprar":
            await m.reply_text(no_repite(uid,'compra',COMPRA_MSGS)); await m.reply_text("De donde eres mor? 🥺",reply_markup=get_precios()); ESPERA_PAIS[uid]=True
        elif intent=="dudar": await m.reply_text(no_repite(uid,'dudar',DUDAR_MSGS))
        elif intent=="hormonal": await m.reply_text(no_repite(uid,'calentada',CALENTADA_MSGS))
        elif intent=="intercambio":
            if puede(uid,'inter'): await m.reply_text(TEXTO_INTER); USUARIOS[uid].setdefault('flags',{})['inter']=True
        elif intent=="salir": await m.reply_text(no_repite(uid,'salir',SALIR_MSGS))
        elif intent=="pago":
            await m.reply_text(no_repite(uid,'compra',COMPRA_MSGS)); await context.bot.send_message(ADMIN_ID,f"💰 PAGO @{un} {uid}\n{raw}",reply_markup=teclado_admin(uid,un))
        else: await m.reply_text("Dime mor quieres gratis o comprar? 🙈 tengo videitos y videollamada 😏")
        guardar_datos(); prog_follow(context,uid,m.chat.id); return
    else:
        if m.chat.type=='private' and not raw.startswith('/'):
            if puede(uid,'menu'): await m.reply_text("Hola mor 🥵",reply_markup=get_menu()); USUARIOS[uid].setdefault('flags',{})['menu']=True; guardar_datos()

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
    print("Bot inmediato sin @YanaBiBot - listo")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__=='__main__': main()
