import os, json, logging, unicodedata, asyncio, random, difflib, re
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto, Update
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, MessageHandler, ContextTypes, filters

logging.basicConfig(level=logging.INFO)
TOKEN = '8762577283:AAFVT7_WMpZ7njVnToIlZypUpCToF5LGcbA'
ADMIN_ID = 8783569348
LINK_CANAL = "https://t.me/+zt1RzGevdHBjMDgx"
LINK_PAYPAL = "https://www.paypal.com/qrcodes/p2pqrc/76RWY9FF7Q7RE"

USUARIOS = {}; INVITADOS = {}; REFERIDOS = {}; JOBS_FOLLOW = {}; DATA_FILE = "data.json"

# ========= CONFIG FACIL =========
DELAY_MIN, DELAY_MAX = 110, 140 # 2 min humano
FOLLOWUP_SEG = 300 # 5 min
MAX_FOLLOW = 3

MX_PRECIOS = """🛍 VIDEOS 🛒

🎂 BÁSICO: $ 100 MXN → 5 vds
🔥 TOP: $200 MXN ← MÁS VENDIDO → 12 vds
🏆 PREMIUM: $400 MXN → 20 vds + 1 personalizado + sexting

📼 VIDEOLLAMADAS 5min $400 / 10min $600
CLABE: 646180546711450910 Ref: yanae
Manda captura mor 🥰"""

PE_PRECIOS = """🛍 VIDEOS 🛒
🎂 BÁSICO: S/ 15 → 5 vds
🔥 TOP: S/ 30 → 12 vds
🏆 PREMIUM: S/ 60 → 20 vds + personalizado + sexting
VIDEOLLAMADAS S/60 5min / S/80 10min
YAPE/PLIN: 923553612 - Manda captura"""

USA_PRECIOS = f"""🛍 VIDEOS 🛒
BÁSICO $5 - 5 vds | TOP $9 - 12 vds | PREMIUM $20 - 20 vds + perso
VIDEOLLAMADAS $20 5min / $35 10min
PayPal: AbigailMaximoofO Link: {LINK_PAYPAL}"""

GRATIS_TEXTO="""(REGALITO) ✨ QUIERES HASTA 20 VIDEITOS GRATSS? ✨
1️⃣ Bio TikTok: Tg: yanabicitasa ✨
2️⃣ Sube fotito que te envié a tu story + frase hot 😋
3️⃣ Mándame captura + videito cuando cumplas
4️⃣ Confirma 100 vistas :3
5️⃣ Disfruta 20 videitos ❤️‍🔥

⚠️ Solo califico a compradores. Si promocionas a alguien más te bloqueo. Si me promocionas a mí te mando regalitos extra 🥺🎁
(Me avisas: ya cumpli con las 100 vistas)"""
MSG_GANAS="Si tienes muchas ganas de verme 🙈🔥\nhttps://t.me/YanaBiBot"
TEXTO_100="Las 100 vistas son solo para que veas lo fácil que es mor :3 Cuando llegues a 500-1000 me avisas y te suelto todo 🥵 Mándame video entrando a TikTok → tu perfil → tu story → likes, todo seguido sin cortar."
TEXTO_INTER="No hago intercambios mor 🥰 yo vendo, pero si cumples la promo te doy videitos al toque 😏"
TEXTO_GRATIS="tienes que cumplir con la promoción Mor 🥺"

# Variantes sin spam
DUDAR_MSGS = [
    "Entiendo mor piensalo tranqui 🥺 pero si me sorprendes con el pago ahora te pongo en prioridad 💖",
    "Puedes pensarlo bebe, las que pagan ahora las atiendo primero y con extra 😏",
    "Tomate tu tiempo mor, si me sorprendes hoy te dejo en VIP y te contesto sin demora ✨",
    "Vale mor piensalo, si me sorprendes te mando algo que nadie tiene 🙈",
    "Tranqui bebe si me sorprendes ahora te atiendo primero y te consiento mas 💋"
]
CALENTADA_MSGS = [
    "Cuando compras te enseño todo sin censura mor completito para ti 🥵",
    "Si compras te muestro todo lo que no subo a ningun lado 😏",
    "Comprando ves mi lado mas atrevido te enseño todo sin tapujos 🙈✨",
    "Cuando compres no me guardo nada todo es para ti mor 💖",
    "Con el pack te enseño todo sin recortes y bien cerquita 😘"
]
COMPRA_MSGS = [
    "TOP y PREMIUM son los mas pedidos 🔥 si mandas poquito mas te mando extras y te contesto al toque despues del pago :3",
    "Si eliges TOP o PREMIUM y das extra te regalo videitos fuera de catalogo y respondo enseguida despues del pago 💋",
    "TOP y PREMIUM vienen con sorpresita y si envias mas te mando exclusivos te contesto justo despues del pago ✨",
    "Con TOP o PREMIUM te consiento mas y si me sorprendes con extra te mando especial y te atiendo primero 🥺",
    "Elige PREMIUM y si mandas poquito mas te mando doble + extras te contesto al instante 💖"
]
SALIR_MSGS = [
    "Por ahora no hago saliditas mor 🙈 soy solo virtual pero bien atrevida si eres premium 💋",
    "Saliditas presenciales no hago bebe pero virtual soy toda tuya si me eliges TOP o PREMIUM 😏",
    "No salgo mor pero en virtual me porto super coqueta para mis premium ✨",
    "No hago encuentros mor mi contenido es solo virtual y bien completito si eres premium 🥰",
    "Soy solo virtual mor pero si me consientes como premium yo te consiento al doble 💖"
]
FOLLOW_MSGS = [
    "Anais caliente si compras ahora te doy el doble de contenido aprovecha mor 🥵",
    "Bebe solo hoy si compras te mando doble + extra 😏",
    "Mor me quede con ganas de ti si compras ahora te lo doy todo x2 🙈",
    "Me dejas en visto? 🥺 si compras ahora te regalo 5 videitos mas",
    "Estoy solita y con ganas 🔥 aprovecha doble si compras en 10 min",
    "Te vi en linea 👀 si compras ahora precio especial y doble",
    "No me dejes con ganas bebe comprame pack y te sorprendo ✨",
    "Si compras ahora audios + fotos que no subo 😈",
    "Ultima promo del dia paga 1 llevas 2 te lo pierdes? 💋",
    "Te espero 🥺 si compras te mando todo al toque"
]

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
    t=re.sub(r'[^\w\s]', ' ', t); return t

def similar(a,b): return difflib.SequenceMatcher(None,a,b).ratio()
def fuzzy(texto, lista, umbral=0.73):
    if not texto: return False
    for w in texto.split():
        for p in lista:
            if p in w or w in p or similar(w,p)>=umbral or (len(w)>3 and w[:4]==p[:4]): return True
    return False

def detectar_intencion(txt, caption=""):
    t=normalizar(f"{txt} {caption}")
    if fuzzy(t, ["yape","plin","pague","pago","comprobante","transfer","captura pago"]): return "pago"
    if "100" in t and "vist" in t: return "vistas100"
    if fuzzy(t, ["pienso","pensarlo","luego","despues","nose","no se","pensar"]): return "dudar"
    if fuzzy(t, ["intercambio","cambias","cambio","inter","cambiamos"]): return "intercambio"
    if fuzzy(t, ["salir","vernos","encuentro","cita","hotel","presencial","salidas","vernos"]): return "salir"
    if fuzzy(t, ["precio","presio","prezio","cuanto","qnto","costo","comprar","kiero","quiero comprar","pack","costo"]): return "comprar"
    if fuzzy(t, ["gratis","grtis","promo","regalo","free","videito gratis"]): return "promo"
    if fuzzy(t, ["caliente","cachondo","paja","rico","ganas","quiero verte","hormonal"]): return "hormonal"
    return "otro"

def puede(uid,key): USUARIOS.setdefault(uid,{}); USUARIOS[uid].setdefault('flags',{}); return not USUARIOS[uid]['flags'].get(key)
def no_repite(uid, tipo, lista):
    USUARIOS[uid].setdefault('usados',{}); usados=USUARIOS[uid]['usados'].get(tipo,[])
    disp=[m for m in lista if m not in usados]
    if not disp: disp=lista; usados=[]
    choice=random.choice(disp); usados.append(choice)
    if len(usados)>4: usados=usados[-4:]
    USUARIOS[uid]['usados'][tipo]=usados; guardar_datos(); return choice

def link_directo(uid,username):
    url=f"https://t.me/{username}" if username!='None' else f"tg://user?id={uid}"
    return url

def teclado_admin(uid, username):
    url=link_directo(uid, username)
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("✅ Confirmar", callback_data=f"ok_{uid}"), InlineKeyboardButton("❌ Pedir prueba", callback_data=f"no_{uid}")],
        [InlineKeyboardButton("🚫 Ban", callback_data=f"ban_{uid}"), InlineKeyboardButton("🔗 Abrir chat", url=url)]
    ])

async def notificar_foto(bot, tipo, uid, username, file_id, is_video=False, caption=""):
    try:
        txt=f"{tipo}\n👤 @{username}\n🆔 <code>{uid}</code>\n📝 {caption[:80]}"
        if is_video: await bot.send_video(ADMIN_ID, file_id, caption=txt, reply_markup=teclado_admin(uid,username), parse_mode='HTML')
        else: await bot.send_photo(ADMIN_ID, file_id, caption=txt, reply_markup=teclado_admin(uid,username), parse_mode='HTML')
    except Exception as e: logging.error(e)

async def bienvenida(m):
    try: await m.reply_media_group([InputMediaPhoto(open(f'fotitos{i}.JPG','rb')) for i in range(1,6)])
    except: pass
    await m.reply_text(GRATIS_TEXTO); await m.reply_text(MSG_GANAS); await m.reply_text(LINK_CANAL)

# followup
async def followup_job(context):
    uid=context.job.data['uid']; chat_id=context.job.data['chat_id']
    USUARIOS.setdefault(uid,{}); c=USUARIOS[uid].get('follow',0)
    if c>=MAX_FOLLOW: return
    msg=no_repite(uid,'follow',FOLLOW_MSGS)
    try: await context.bot.send_message(chat_id, msg); USUARIOS[uid]['follow']=c+1; guardar_datos()
    except: pass
def programar_follow(context, uid, chat_id):
    if uid in JOBS_FOLLOW:
        try: JOBS_FOLLOW[uid].schedule_removal()
        except: pass
    JOBS_FOLLOW[uid]=context.job_queue.run_once(followup_job, FOLLOWUP_SEG, data={'uid':uid,'chat_id':chat_id})

# comandos admin faciles
async def stats_cmd(u,c):
    if u.effective_user.id!=ADMIN_ID: return
    total=len(USUARIOS); pagos=sum(1 for v in USUARIOS.values() if v.get('flags',{}).get('pago') )
    await u.message.reply_text(f"📊 STATS\nUsuarios: {total}\nPagos detectados: {pagos}\nReferidos totales: {sum(INVITADOS.values())}\nFollow activos: {len(JOBS_FOLLOW)}")

async def start_cmd(u,c):
    uid=u.effective_user.id; USUARIOS.setdefault(uid,{}); USUARIOS[uid]['n']=u.effective_user.username or "?"
    if c.args and c.args[0].isdigit():
        ref=int(c.args[0])
        if ref!=uid and 'ref' not in USUARIOS[uid]:
            USUARIOS[uid]['ref']=ref; INVITADOS[ref]=INVITADOS.get(ref,0)+1; guardar_datos()
            try: await c.bot.send_message(ref,f"🎉 Nuevo referido! Total: {INVITADOS[ref]}")
            except: pass
    await u.message.reply_text("Hola mor 🥵 acá consultas precios y la que te cumple es @yanabicitasa", reply_markup=get_menu())

async def btn(u,c):
    q=u.callback_query; await q.answer(); data=q.data; uid=q.from_user.id
    # acciones admin
    if uid==ADMIN_ID and "_" in data:
        try:
            acc, target = data.split("_"); target=int(target)
            if acc=="ok": await c.bot.send_message(target, "Gracias mor ya confirme tu pruebita 💖 te mando en un ratito :3"); await q.edit_message_caption(caption=q.message.caption+"\n✅ CONFIRMADO")
            elif acc=="no": await c.bot.send_message(target, "Mor mándame mejor la pruebita completa porfa 🥺 video entrando a tu perfil y a la story sin cortar"); await q.edit_message_caption(caption=q.message.caption+"\n❌ PEDIDA MEJOR PRUEBA")
            elif acc=="ban": USUARIOS.setdefault(target,{}).setdefault('flags',{})['ban']=True; guardar_datos(); await q.edit_message_caption(caption=q.message.caption+"\n🚫 BANEADO")
            return
        except: pass
    if data=='comprar': await q.edit_message_text("Elige tu país:", reply_markup=get_precios())
    elif data=='pe': await q.edit_message_text(PE_PRECIOS)
    elif data=='mx': await q.edit_message_text(MX_PRECIOS)
    elif data=='usa': await q.edit_message_text(USA_PRECIOS)
    elif data=='gratis': await q.edit_message_text(GRATIS_TEXTO + "\n\n" + MSG_GANAS)
    elif data=='milink':
        link=f"https://t.me/YanaBiBot?start={q.from_user.id}"; REFERIDOS[q.from_user.id]={'link':link}; guardar_datos()
        await q.edit_message_text(f"🔗 Tu link:\n{link}\n\nInvita y subes ranking. Si me promocionas te mando regalitos 🎁")
    elif data=='ranking':
        top=sorted(INVITADOS.items(),key=lambda x:x[1],reverse=True)[:10]
        txt="\n".join([f"{i+1}. @{USUARIOS.get(u,{}).get('n','?')} - {c}" for i,(u,c) in enumerate(top)]) if top else "Aún nadie"
        await q.edit_message_text(f"📊 RANKING\n{txt}")

async def handle_all(update,context):
    m=update.business_message or update.message
    if not m or not m.from_user or m.from_user.is_bot: return
    uid=m.from_user.id; username=m.from_user.username or "None"; raw=m.text or ""; caption=getattr(m,'caption','') or ""; es_neg=update.business_message is not None
    if es_neg and uid==ADMIN_ID: return
    USUARIOS.setdefault(uid,{})
    if USUARIOS[uid].get('flags',{}).get('ban'): return

    if uid in JOBS_FOLLOW:
        try: JOBS_FOLLOW[uid].schedule_removal(); del JOBS_FOLLOW[uid]
        except: pass

    if es_neg:
        # FOTOS / VIDEOS = interpreta que es
        if m.photo or m.video:
            is_vid=bool(m.video); file_id=m.video.file_id if is_vid else m.photo[-1].file_id
            cap=normalizar(caption)
            tipo="📸 PRUEBA"
            if fuzzy(cap, ["yape","plin","pago"]): tipo="💰 CAPTURA DE PAGO"
            elif fuzzy(cap, ["vista","100","500","story","tiktok"]): tipo="🎁 PRUEBA PROMO 100 VISTAS"
            elif fuzzy(cap, ["promo","gratis"]): tipo="🎁 PRUEBA PROMO"
            await notificar_foto(context.bot, tipo, uid, username, file_id, is_vid, caption or raw)
            # auto respuesta suave sin spam
            if puede(uid,'foto_thx'): await m.reply_text("Gracias mor ya reviso tu pruebita 🥺💖"); USUARIOS[uid].setdefault('flags',{})['foto_thx']=True; guardar_datos()
            return

        intent=detectar_intencion(raw, caption)
        try: await context.bot.send_chat_action(m.chat.id, "typing")
        except: pass
        await asyncio.sleep(random.randint(DELAY_MIN, DELAY_MAX))

        if intent=="vistas100":
            if puede(uid,'v100'): await m.reply_text(TEXTO_100); USUARIOS[uid].setdefault('flags',{})['v100']=True
            await context.bot.send_message(ADMIN_ID,f"🎁 100 VISTAS @{username} {uid}\n{raw[:100]}", reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔗 Abrir", url=link_directo(uid,username))]]))
        elif intent=="intercambio":
            if puede(uid,'inter'): await m.reply_text(TEXTO_INTER); USUARIOS[uid].setdefault('flags',{})['inter']=True
        elif intent=="salir": await m.reply_text(no_repite(uid,'salir',SALIR_MSGS))
        elif intent=="dudar": await m.reply_text(no_repite(uid,'dudar',DUDAR_MSGS))
        elif intent=="hormonal": await m.reply_text(no_repite(uid,'calentada',CALENTADA_MSGS))
        elif intent=="comprar": await m.reply_text(no_repite(uid,'compra',COMPRA_MSGS))
        elif intent=="pago":
            await m.reply_text(no_repite(uid,'compra',COMPRA_MSGS)); USUARIOS[uid].setdefault('flags',{})['pago']=True
            await context.bot.send_message(ADMIN_ID,f"💰 PAGO DETECTADO @{username} {uid}\n{raw}", reply_markup=teclado_admin(uid,username))
        else:
            if puede(uid,'bienvenida'): await bienvenida(m); USUARIOS[uid].setdefault('flags',{})['bienvenida']=True
            else:
                if puede(uid,'rec'): await m.reply_text(TEXTO_GRATIS); USUARIOS[uid].setdefault('flags',{})['rec']=True
        guardar_datos(); programar_follow(context, uid, m.chat.id); return
    else:
        if m.chat.type=='private':
            if m.from_user.id==ADMIN_ID and raw.startswith('/'): return
            if puede(uid,'menu'): await m.reply_text("Hola mor 🥵 acá consultas precios y la que te cumple es @yanabicitasa", reply_markup=get_menu()); USUARIOS[uid].setdefault('flags',{})['menu']=True; guardar_datos()
            programar_follow(context, uid, m.chat.id)

def main():
    cargar_datos()
    app=Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start",start_cmd))
    app.add_handler(CommandHandler("stats",stats_cmd))
    app.add_handler(CallbackQueryHandler(btn))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_all))
    app.add_handler(MessageHandler(filters.UpdateType.BUSINESS_MESSAGE, handle_all))
    app.add_handler(MessageHandler(filters.PHOTO | filters.VIDEO, handle_all))
    app.add_handler(MessageHandler(filters.UpdateType.BUSINESS_MESSAGE & (filters.PHOTO | filters.VIDEO), handle_all))
    # caption con foto en negocio
    app.add_handler(MessageHandler(filters.CAPTION & filters.UpdateType.BUSINESS_MESSAGE, handle_all))
    print("Bot completo iniciado - promo + ventas + fotos + admin facil")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__=='__main__': main()
