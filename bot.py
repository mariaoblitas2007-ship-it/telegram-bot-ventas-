# ============================================================
# YANABICITASA - FINAL CORREGIDO
# Negocio = SOLO MENSAJES + 5 FOTOS (sin botones)
# @YanaBiBot = CON BOTONES + Volver + responde a todo
# ============================================================
import os, json, logging, time, unicodedata, random, re
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto, Update
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, MessageHandler, filters

logging.basicConfig(level=logging.INFO)
TOKEN = '8762577283:AAFVT7_WMpZ7njVnToIlZypUpCToF5LGcbA'
ADMIN_ID = 8783569348
LINK_CANAL = "https://t.me/+zt1RzGevdHBjMDgx"
DATA_FILE = "data.json"

USUARIOS = {}; JOBS_FOLLOW = {}; ESPERA_PAIS = {}

# TEXTOS
SALUDO_NEGOCIO_PROMO = f"""Wenas mor por aquí solo veo lo gratis 🙈

¿Quieres hasta 20 gratis mor? :3 ✨

Solo haz esto mor:
1️⃣ Sube la foto de mi QR a tu story
2️⃣ Comenta cositas hormo en TikToks con #hormo #hot para que te lleguen vistas

Avísame cuando llegues a 100 vistas 🥵
Mándame captura + videito de que lo hiciste"""

TEXTO_100_A_500 = """Sii mor ya vi que llegaste a 100 🥺✨ pero para soltarte los videitos son 500 vistas mor 🥵

Llegas rápido así:
1️⃣ Sigue comentando con #hormo #hot
2️⃣ Comenta en videos virales de Para Ti
3️⃣ Deja tu story con mi QR

Cuando llegues a 500 me mandas captura + videito sin cortar y te los suelto al toque 😏"""

MX_PRECIOS = """🛍 VIDEOS 🛒
🎂 BÁSICO: $100 MXN → 5 videitos | $20 c/u
━━━━━━━━━━━━━━
🔥 TOP: $200 MXN ← MÁS VENDIDO → 12 videitos | $16 c/u
━━━━━━━━━━━━━━
🏆 PREMIUM: $400 MXN → 20 videitos + 1 perso + sexting
━━━━━━━━━━━━━━
📼 VIDEOLLAMADAS $400 5min | $600 10min
CLABE: 646180546711450910 Ref: yanae"""

PE_PRECIOS = """🛍 VIDEOS 🛒
🎂 BÁSICO: S/ 15 → 5 videitos
━━━━━━━━━━━━━━
🔥 TOP: S/ 30 → 12 videitos
━━━━━━━━━━━━━━
🏆 PREMIUM: S/ 60 → 20 videitos + 1 perso + sexting
━━━━━━━━━━━━━━
📼 VIDEOLLAMADAS S/60 5min | S/80 10min
YAPE: 923553612"""

USA_PRECIOS = """🛍 VIDEOS 🛒
🎂 BÁSICO: $5 USD → 5 videitos
━━━━━━━━━━━━━━
🔥 TOP: $9 USD → 12 videitos
━━━━━━━━━━━━━━
🏆 PREMIUM: $20 USD → 20 videitos + 1 perso + sexting
━━━━━━━━━━━━━━
📼 VIDEOLLAMADAS $20 5min | $35 10min
PayPal: AbigailMaximoofO"""

CUMPLIDO_MSG = "ando algo ocupadita haciéndo videollamada 👀 en un ratito te confirmo mor 🥰"
REAL_MSGS = [f"Soy real mor revisa mi canal\n{LINK_CANAL}"]
FALLBACK_MSGS = ["Dime mor quieres gratis o comprar? 🙈"]

def cargar_datos():
    global USUARIOS
    if os.path.exists(DATA_FILE):
        try: USUARIOS={int(k):v for k,v in json.load(open(DATA_FILE)).get('usuarios',{}).items()}
        except: pass
def guardar_datos(): json.dump({'usuarios':USUARIOS}, open(DATA_FILE,'w'))
def normalizar(t):
    if not t: return ""
    t=unicodedata.normalize('NFKD',t).encode('ascii','ignore').decode().lower()
    return re.sub(r'[^\w\s]',' ',t)
def detectar_intencion(txt,cap=""):
    t=normalizar(f"{txt} {cap}")
    if any(x in t for x in ['falso','fake','estafa','eres bot']): return "real"
    if "500" in t and "vist" in t: return "vistas500"
    if "100" in t and "vist" in t: return "vistas100"
    if any(x in t for x in ['ya cumpli','cumpli']): return "cumplido"
    if any(x in t for x in ['yape','plin','pago','comprobante']): return "pago"
    if any(x in t for x in ['gratis','promo']): return "promo"
    if any(x in t for x in ['precio','comprar']): return "comprar"
    return "otro"
def no_repite(uid,tipo,lista):
    USUARIOS[uid].setdefault('usados',{}); usados=USUARIOS[uid]['usados'].get(tipo,[])
    disp=[m for m in lista if m not in usados]
    if not disp: disp=lista; usados=[]
    ch=random.choice(disp); usados.append(ch)
    if len(usados)>5: usados=usados[-5:]
    USUARIOS[uid]['usados']=usados; guardar_datos(); return ch
def link_directo(uid,un): return f"https://t.me/{un}" if un!="None" else f"tg://user?id={uid}"

# Botones SOLO para @YanaBiBot
def get_menu(): return InlineKeyboardMarkup([[InlineKeyboardButton("💎 COMPRAR",callback_data='comprar')],[InlineKeyboardButton("🎁 GRATIS",callback_data='gratis')]])
def get_precios(): return InlineKeyboardMarkup([[InlineKeyboardButton("🇵🇪 Perú",callback_data='pe')],[InlineKeyboardButton("🇲🇽 México",callback_data='mx')],[InlineKeyboardButton("🌍 Otros",callback_data='usa')],[InlineKeyboardButton("⬅️ Volver",callback_data='volver')]])
def get_volver(): return InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Volver al menú",callback_data='volver')]])
def teclado_admin(uid,un):
    url=link_directo(uid,un)
    return InlineKeyboardMarkup([[InlineKeyboardButton("✅ Confirmar",callback_data=f"ok_{uid}"),InlineKeyboardButton("❌ Pedir prueba",callback_data=f"no_{uid}")],[InlineKeyboardButton("📈 Enviar 500",callback_data=f"500_{uid}"),InlineKeyboardButton("🔗 Abrir",url=url)]])
def teclado_admin_100(uid,un):
    url=link_directo(uid,un)
    return InlineKeyboardMarkup([[InlineKeyboardButton("📈 Enviar mensaje 500",callback_data=f"500_{uid}")],[InlineKeyboardButton("✅ Ya tiene 500",callback_data=f"ok_{uid}")],[InlineKeyboardButton("🔗 Abrir",url=url)]])
def precio_por_pais(p): return PE_PRECIOS if p=='pe' else MX_PRECIOS if p=='mx' else USA_PRECIOS

# Promo SIN botones (para negocio) y CON botones (para bot)
async def promo_negocio_sin_botones(m):
    try: await m.reply_media_group([InputMediaPhoto(open(f'fotitos{i}.JPG','rb')) for i in range(1,6)])
    except:
        try: await m.reply_media_group([InputMediaPhoto(open(f'fotitos{i}.jpg','rb')) for i in range(1,6)])
        except: pass
    await m.reply_text(SALUDO_NEGOCIO_PROMO) # SIN botones

async def promo_bot_con_botones(m):
    try: await m.reply_media_group([InputMediaPhoto(open(f'fotitos{i}.JPG','rb')) for i in range(1,6)])
    except:
        try: await m.reply_media_group([InputMediaPhoto(open(f'fotitos{i}.jpg','rb')) for i in range(1,6)])
        except: pass
    await m.reply_text(SALUDO_NEGOCIO_PROMO, reply_markup=get_volver()) # CON botón volver

async def followup_job(c):
    uid=c.job.data['uid']
    if USUARIOS.get(uid,{}).get('flags',{}).get('pausado'): return
    try: await c.bot.send_message(c.job.data['chat_id'], no_repite(uid,'follow',FALLBACK_MSGS), reply_markup=get_menu())
    except: pass

def prog_follow(ctx,uid,cid):
    if uid in JOBS_FOLLOW:
        try: JOBS_FOLLOW[uid].schedule_removal()
        except: pass
    JOBS_FOLLOW[uid]=ctx.job_queue.run_once(followup_job,600,data={'uid':uid,'chat_id':cid})

async def btn(u,c):
    q=u.callback_query; await q.answer(); d=q.data
    if q.from_user.id==ADMIN_ID and "_" in d:
        acc,t=d.split("_",1); t=int(t)
        if acc=="ok": await c.bot.send_message(t,"Listo mor ya te confirmé 💖"); await q.edit_message_caption(caption=(q.message.caption or "")+"\n✅ CONFIRMADO"); USUARIOS.setdefault(t,{}).setdefault('flags',{})['pausado']=False
        elif acc=="no": await c.bot.send_message(t,"Mor mándame mejor la pruebita completa porfa 🥺"); await q.edit_message_caption(caption=(q.message.caption or "")+"\n❌ PEDIDA"); USUARIOS.setdefault(t,{}).setdefault('flags',{})['pausado']=False
        elif acc=="500": await c.bot.send_message(t,TEXTO_100_A_500); await q.edit_message_caption(caption=(q.message.caption or "")+"\n📈 MENSAJE 500 ENVIADO")
        guardar_datos(); return
    if d=='volver': await q.edit_message_text("¿Qué quieres mor? :3", reply_markup=get_menu())
    elif d=='comprar': await q.edit_message_text("De donde eres mor 👀✨", reply_markup=get_precios())
    elif d in ['pe','mx','usa']: await q.edit_message_text(precio_por_pais(d), parse_mode='HTML', reply_markup=get_volver())
    elif d=='gratis': await promo_bot_con_botones(q.message)

async def handle_all(update, context):
    m = update.business_message or update.message
    if not m or not m.from_user or m.from_user.is_bot: return
    uid=m.from_user.id; un=m.from_user.username or "None"; raw=m.text or ""; cap=getattr(m,'caption','') or ""
    es_neg = update.business_message is not None
    if es_neg and uid==ADMIN_ID: return
    USUARIOS.setdefault(uid,{})
    if time.time()-USUARIOS[uid].get('ultimo',0) < 1.8: return
    USUARIOS[uid]['ultimo']=time.time()
    if USUARIOS[uid].get('flags',{}).get('ban') or USUARIOS[uid].get('flags',{}).get('pausado'): return

    # ===== NEGOCIO = SOLO MENSAJES + 5 FOTOS =====
    if es_neg:
        if m.photo or m.video:
            is_v=bool(m.video); fid=m.video.file_id if is_v else m.photo[-1].file_id
            cap_norm=normalizar(cap+" "+raw)
            es_100="100" in cap_norm; es_500="500" in cap_norm
            link=f"https://t.me/{un}" if un!="None" else f"tg://user?id={uid}"
            if es_100 and not es_500:
                txt=f"📈 NEGOCIO 100\n@{un} {uid}\n{link}\nPresiona para enviar 500"
                if is_v: await context.bot.send_video(ADMIN_ID,fid,caption=txt,reply_markup=teclado_admin_100(uid,un))
                else: await context.bot.send_photo(ADMIN_ID,fid,caption=txt,reply_markup=teclado_admin_100(uid,un))
                return
            if es_500:
                txt=f"✅ NEGOCIO 500\n@{un} {uid}\n{link}"
                if is_v: await context.bot.send_video(ADMIN_ID,fid,caption=txt,reply_markup=teclado_admin(uid,un))
                else: await context.bot.send_photo(ADMIN_ID,fid,caption=txt,reply_markup=teclado_admin(uid,un))
                await m.reply_text(CUMPLIDO_MSG); USUARIOS[uid].setdefault('flags',{})['pausado']=True; guardar_datos(); return
            return
        if not USUARIOS[uid].get('flags',{}).get('saludo_negocio'):
            await promo_negocio_sin_botones(m) # 5 fotos + texto SIN botones
            USUARIOS[uid].setdefault('flags',{})['saludo_negocio']=True; guardar_datos(); return
        intent=detectar_intencion(raw,cap)
        if intent in ["vistas100","cumplido","promo"]:
            link=f"https://t.me/{un}" if un!="None" else f"tg://user?id={uid}"
            await context.bot.send_message(ADMIN_ID,f"📈 NEGOCIO PIDE GRATIS @{un} {uid}\n{raw}\n{link}",reply_markup=teclado_admin_100(uid,un))
            return
        else:
            await m.reply_text(SALUDO_NEGOCIO_PROMO) # puro mensaje sin botón
            return

    # ===== @YanaBiBot = CON BOTONES =====
    else:
        intent=detectar_intencion(raw,cap)
        if intent=="comprar": await m.reply_text("De donde eres mor 👀✨", reply_markup=get_precios()); return
        if intent=="promo": await promo_bot_con_botones(m); return
        if intent=="pago": await m.reply_text(CUMPLIDO_MSG, reply_markup=get_volver()); await context.bot.send_message(ADMIN_ID,f"💰 PAGO BOT @{un} {uid}",reply_markup=teclado_admin(uid,un)); USUARIOS[uid].setdefault('flags',{})['pausado']=True; guardar_datos(); return
        # Cualquier mensaje responde con menú de botones
        await m.reply_text(f"Wenas mor 🙈 ¿qué quieres hacer?\n\nMi canal: {LINK_CANAL}", reply_markup=get_menu())

def main():
    cargar_datos()
    app=Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", lambda u,c: u.message.reply_text("Hola mor 🥵", reply_markup=get_menu())))
    app.add_handler(CallbackQueryHandler(btn))
    app.add_handler(MessageHandler(filters.UpdateType.BUSINESS_MESSAGE, handle_all))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_all))
    app.add_handler(MessageHandler(filters.PHOTO | filters.VIDEO, handle_all))
    print("Bot listo: Negocio=solo mensajes+5 fotos / Bot=con botones")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__=='__main__': main()
