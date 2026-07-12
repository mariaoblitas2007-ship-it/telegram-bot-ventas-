# ============================================================
# YANABICITASA - TEXTO NUEVO + SIN BOTONES PAÍSES
# ============================================================
import os, json, logging, time, unicodedata, random, re
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto, Update
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, MessageHandler, filters

logging.basicConfig(level=logging.INFO)
TOKEN = '8762577283:AAFVT7_WMpZ7njVnToIlZypUpCToF5LGcbA'
ADMIN_ID = 8783569348
LINK_CANAL = "https://t.me/+zt1RzGevdHBjMDgx"
DATA_FILE = "data.json"

USUARIOS = {}; JOBS_FOLLOW = {}; ESPERA_MONEDA = {}

# TEXTO NUEVO QUE PEDISTE
GRATIS_TEXTO = """✨ ¿Quieres verme cogiendo y moviendo las ttas? 👀💕 ✨

Solo haz esto mor:
1️⃣ Sube la foto de mi QR a tu story
2️⃣ Comenta cositas hormo en TikToks con #hormo #hot para que te lleguen vistas

Avísame cuando llegues a 100 vistas 🥵
Mándame pruebas que cumpliste con la promo :3"""

PREGUNTA_MONEDA = """De donde eres mor? que moneda usas? :3
dime si usas soles, pesos o dolares 🙈"""

TEXTO_100_A_500 = """Sii mor ya vi que llegaste a 100 🥺✨ pero para soltarte los videitos son 500 vistas mor 🥵
1️⃣ Sigue comentando con #hormo #hot
2️⃣ Comenta en videos virales de Para Ti
3️⃣ Deja tu story con mi QR
Cuando llegues a 500 me mandas pruebas que cumpliste con la promo :3 y te los suelto al toque 😏"""

OCUPADITA_MSG = "ando algo ocupadita haciéndo videollamada 👀 en un ratito te confirmo mor 🥰"
RECORDATORIO_CORTO = "Ya te dejé los pasitos arribita mor 👆 cuando llegues a 100 me mandas pruebas que cumpliste con la promo :3"
SOLO_GRATIS_AVISO = "Por aquí solo veo lo gratis mor 🙈\nSi quieres comprar ve a @YanaBiBot 💎"

MX_PRECIOS = """🛍 <b>VIDEOS</b> 🛒
🎂 <b>BÁSICO: $100 MXN</b> → 5 videitos | $20 c/u
━━━━━━━━━━━━━━
🔥 <b>TOP: $200 MXN</b> → 12 videitos | $16 c/u
━━━━━━━━━━━━━━
🏆 <b>PREMIUM: $400 MXN</b> → 20 videitos + 1 perso + sexting
━━━━━━━━━━━━━━
📼 <b>VIDEOLLAMADAS</b> $400 5min | $600 10min
CLABE: <code>646180546711450910</code> Ref: <code>yanae</code>"""

PE_PRECIOS = """🛍 <b>VIDEOS</b> 🛒
🎂 <b>BÁSICO: S/ 15</b> → 5 videitos
━━━━━━━━━━━━━━
🔥 <b>TOP: S/ 30</b> → 12 videitos
━━━━━━━━━━━━━━
🏆 <b>PREMIUM: S/ 60</b> → 20 videitos + 1 perso + sexting
━━━━━━━━━━━━━━
📼 <b>VIDEOLLAMADAS</b> S/60 5min | S/80 10min
YAPE: <code>923553612</code>"""

USA_PRECIOS = """🛍 <b>VIDEOS</b> 🛒
🎂 <b>BÁSICO: $5 USD</b> → 5 videitos
━━━━━━━━━━━━━━
🔥 <b>TOP: $9 USD</b> → 12 videitos
━━━━━━━━━━━━━━
🏆 <b>PREMIUM: $20 USD</b> → 20 videitos + 1 perso + sexting
━━━━━━━━━━━━━━
📼 <b>VIDEOLLAMADAS</b> $20 5min | $35 10min
PayPal: <code>AbigailMaximoofO</code>"""

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
def detectar_pais_moneda(t):
    t=normalizar(t)
    peru_lugares = ['peru','lima','arequipa','cusco','trujillo','chiclayo','piura','cajamarca','huancayo','ica','tacna','pucallpa','iquitos','huaraz','ayacucho','callao','loreto','lambayeque','juliaca','puno']
    peru_moneda = ['sol','soles','s/','yape','plin']
    mex_lugares = ['mexico','mx','cdmx','ciudad de mexico','edomex','jalisco','guadalajara','monterrey','nuevo leon','puebla','cancun','quintana roo','yucatan','tijuana','baja','chihuahua','veracruz']
    mex_moneda = ['peso mexicano','pesos mexicanos','mxn','clabe']
    usa_moneda = ['dolar','dolares','usd','dollar']
    if any(x in t for x in peru_moneda): return 'pe'
    if any(x in t for x in peru_lugares): return 'pe'
    if any(x in t for x in mex_moneda): return 'mx'
    if any(x in t for x in mex_lugares): return 'mx'
    if 'peso' in t or 'pesos' in t: return 'mx'
    if any(x in t for x in usa_moneda): return 'usa'
    return None
def detectar_intencion(txt,cap=""):
    t=normalizar(f"{txt} {cap}")
    if any(x in t for x in ['falso','fake','estafa','eres bot']): return "real"
    if "500" in t and "vist" in t: return "vistas500"
    if "100" in t and "vist" in t: return "vistas100"
    if any(x in t for x in ['ya cumpli','cumpli']): return "cumplido"
    if any(x in t for x in ['yape','plin','pago','comprobante']): return "pago"
    if any(x in t for x in ['gratis','promo']): return "promo"
    if any(x in t for x in ['precio','precios','cuanto','cuesta','comprar','pack']): return "comprar"
    if any(x in t for x in ['videollamada']): return "videollamada"
    return "otro"
def no_repite(uid,tipo,lista):
    USUARIOS[uid].setdefault('usados',{}); u=USUARIOS[uid]['usados'].get(tipo,[])
    d=[m for m in lista if m not in u]
    if not d: d=lista; u=[]
    ch=random.choice(d); u.append(ch)
    if len(u)>5: u=u[-5:]
    USUARIOS[uid]['usados']=u; guardar_datos(); return ch
def link_directo(uid,un): return f"https://t.me/{un}" if un!="None" else f"tg://user?id={uid}"
def get_menu(): return InlineKeyboardMarkup([[InlineKeyboardButton("💎 COMPRAR",callback_data='comprar')],[InlineKeyboardButton("🎁 GRATIS",callback_data='gratis')]])
def get_volver(): return InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Volver al menú",callback_data='volver')]])
def teclado_admin(uid,un):
    url=link_directo(uid,un)
    return InlineKeyboardMarkup([[InlineKeyboardButton("✅ Confirmar",callback_data=f"ok_{uid}"),InlineKeyboardButton("❌ Pedir prueba",callback_data=f"no_{uid}")],[InlineKeyboardButton("📈 Enviar 500",callback_data=f"500_{uid}"),InlineKeyboardButton("🔗 Abrir",url=url)]])
def teclado_admin_100(uid,un):
    url=link_directo(uid,un)
    return InlineKeyboardMarkup([[InlineKeyboardButton("📈 Enviar mensaje 500",callback_data=f"500_{uid}")],[InlineKeyboardButton("✅ Ya tiene 500",callback_data=f"ok_{uid}")],[InlineKeyboardButton("🔗 Abrir",url=url)]])
def precio_por_pais(p): return PE_PRECIOS if p=='pe' else MX_PRECIOS if p=='mx' else USA_PRECIOS
async def enviar_5_fotos(m):
    try: await m.reply_media_group([InputMediaPhoto(open(f'fotitos{i}.JPG','rb')) for i in range(1,6)])
    except:
        try: await m.reply_media_group([InputMediaPhoto(open(f'fotitos{i}.jpg','rb')) for i in range(1,6)])
        except: pass
async def despedida_ocupadita(m, es_neg, uid):
    if es_neg: await m.reply_text(OCUPADITA_MSG)
    else: await m.reply_text(OCUPADITA_MSG, reply_markup=get_volver())
    USUARIOS.setdefault(uid,{}).setdefault('flags',{})['pausado']=True; guardar_datos()
async def followup_job(c):
    uid=c.job.data['uid']
    if USUARIOS.get(uid,{}).get('flags',{}).get('pausado'): return
    if USUARIOS.get(uid,{}).get('follow',0) >= 2:
        try: await c.bot.send_message(c.job.data['chat_id'], OCUPADITA_MSG, reply_markup=get_menu())
        except: pass
        USUARIOS[uid].setdefault('flags',{})['pausado']=True; guardar_datos(); return
    try:
        await c.bot.send_message(c.job.data['chat_id'], no_repite(uid,'follow',["Dime mor quieres gratis o comprar? 🙈"]), reply_markup=get_menu())
        USUARIOS[uid]['follow']=USUARIOS[uid].get('follow',0)+1; guardar_datos()
    except: pass
def prog_follow(ctx,uid,cid):
    if uid in JOBS_FOLLOW:
        try: JOBS_FOLLOW[uid].schedule_removal()
        except: pass
    JOBS_FOLLOW[uid]=ctx.job_queue.run_once(followup_job,600,data={'uid':uid,'chat_id':cid})
async def start_cmd(u,c):
    uid=u.effective_user.id; USUARIOS.setdefault(uid,{}).setdefault('flags',{})['saludo_bot']=True; USUARIOS[uid]['ultimo']=time.time(); guardar_datos()
    await enviar_5_fotos(u.message); await u.message.reply_text(GRATIS_TEXTO, reply_markup=get_menu())
async def btn(u,c):
    q=u.callback_query; await q.answer(); d=q.data
    if q.from_user.id==ADMIN_ID and "_" in d:
        acc,t=d.split("_",1); t=int(t)
        if acc=="ok": await c.bot.send_message(t,"Listo mor ya te confirmé 💖"); await q.edit_message_caption(caption=(q.message.caption or "")+"\n✅ CONFIRMADO"); USUARIOS.setdefault(t,{}).setdefault('flags',{})['pausado']=False
        elif acc=="no": await c.bot.send_message(t,"Mor mándame mejor la pruebita completa porfa 🥺"); await q.edit_message_caption(caption=(q.message.caption or "")+"\n❌ PEDIDA"); USUARIOS.setdefault(t,{}).setdefault('flags',{})['pausado']=False
        elif acc=="500": await c.bot.send_message(t,TEXTO_100_A_500); await q.edit_message_caption(caption=(q.message.caption or "")+"\n📈 MENSAJE 500 ENVIADO")
        guardar_datos(); return
    if d=='volver': await q.edit_message_text("¿Qué quieres mor? :3", reply_markup=get_menu())
    elif d=='comprar': await q.edit_message_text(PREGUNTA_MONEDA, reply_markup=get_volver()); ESPERA_MONEDA[q.from_user.id]=True
    elif d=='gratis':
        await enviar_5_fotos(q.message); await q.message.reply_text(GRATIS_TEXTO, reply_markup=get_volver())
async def handle_all(update, context):
    m = update.business_message or update.message
    if not m or not m.from_user or m.from_user.is_bot: return
    uid=m.from_user.id; un=m.from_user.username or "None"; raw=m.text or ""; cap=getattr(m,'caption','') or ""
    es_neg = update.business_message is not None
    if es_neg and uid==ADMIN_ID: return
    USUARIOS.setdefault(uid,{})
    ahora=time.time()
    if ahora-USUARIOS[uid].get('ultimo',0) < 2.5: return
    USUARIOS[uid]['ultimo']=ahora
    if USUARIOS[uid].get('flags',{}).get('ban') or USUARIOS[uid].get('flags',{}).get('pausado'): return
    if es_neg:
        if m.photo or m.video:
            is_v=bool(m.video); fid=m.video.file_id if is_v else m.photo[-1].file_id
            cap_norm=normalizar(cap+" "+raw); es_100="100" in cap_norm; es_500="500" in cap_norm
            link=f"https://t.me/{un}" if un!="None" else f"tg://user?id={uid}"
            if es_100 and not es_500:
                txt=f"📈 NEGOCIO 100\n@{un} {uid}\n{link}"
                if is_v: await context.bot.send_video(ADMIN_ID,fid,caption=txt,reply_markup=teclado_admin_100(uid,un))
                else: await context.bot.send_photo(ADMIN_ID,fid,caption=txt,reply_markup=teclado_admin_100(uid,un))
                return
            if es_500:
                txt=f"✅ NEGOCIO 500\n@{un} {uid}\n{link}"
                if is_v: await context.bot.send_video(ADMIN_ID,fid,caption=txt,reply_markup=teclado_admin(uid,un))
                else: await context.bot.send_photo(ADMIN_ID,fid,caption=txt,reply_markup=teclado_admin(uid,un))
                await despedida_ocupadita(m, True, uid); return
            return
        if not USUARIOS[uid].get('flags',{}).get('saludo_negocio'):
            await enviar_5_fotos(m); await m.reply_text(GRATIS_TEXTO)
            USUARIOS[uid].setdefault('flags',{})['saludo_negocio']=True; USUARIOS[uid]['ultimo_promo']=ahora; USUARIOS[uid]['contador_msg']=0; guardar_datos(); return
        intent=detectar_intencion(raw,cap); USUARIOS[uid]['contador_msg']=USUARIOS[uid].get('contador_msg',0)+1
        if intent in ["vistas100","cumplido"]:
            link=f"https://t.me/{un}" if un!="None" else f"tg://user?id={uid}"
            await context.bot.send_message(ADMIN_ID,f"📈 NEGOCIO PIDE 100 @{un} {uid}\n{raw}\n{link}",reply_markup=teclado_admin_100(uid,un)); return
        if intent in ["comprar","pago"]:
            if ahora-USUARIOS[uid].get('ultimo_aviso_compra',0) > 300:
                await m.reply_text(SOLO_GRATIS_AVISO); USUARIOS[uid]['ultimo_aviso_compra']=ahora; guardar_datos()
            return
        if USUARIOS[uid]['contador_msg'] >= 4: await despedida_ocupadita(m, True, uid); return
        if ahora-USUARIOS[uid].get('ultimo_promo',0) > 120:
            await m.reply_text(RECORDATORIO_CORTO); USUARIOS[uid]['ultimo_promo']=ahora; guardar_datos()
        return
    else:
        if uid in ESPERA_MONEDA:
            pais_detectado = detectar_pais_moneda(raw)
            if pais_detectado: await m.reply_text(precio_por_pais(pais_detectado), parse_mode='HTML', reply_markup=get_volver())
            else: await m.reply_text(precio_por_pais('usa'), parse_mode='HTML', reply_markup=get_volver())
            del ESPERA_MONEDA[uid]; guardar_datos(); prog_follow(context,uid,m.chat.id); return
        if not USUARIOS[uid].get('flags',{}).get('saludo_bot'):
            await enviar_5_fotos(m); await m.reply_text(GRATIS_TEXTO, reply_markup=get_menu())
            USUARIOS[uid].setdefault('flags',{})['saludo_bot']=True; USUARIOS[uid]['ultimo_promo']=ahora; USUARIOS[uid]['contador_msg']=0; guardar_datos()
            prog_follow(context,uid,m.chat.id); return
        intent=detectar_intencion(raw,cap); USUARIOS[uid]['contador_msg']=USUARIOS[uid].get('contador_msg',0)+1
        if intent=="comprar":
            pais_directo = detectar_pais_moneda(raw)
            if pais_directo: await m.reply_text(precio_por_pais(pais_directo), parse_mode='HTML', reply_markup=get_volver()); guardar_datos(); return
            else: await m.reply_text(PREGUNTA_MONEDA, reply_markup=get_volver()); ESPERA_MONEDA[uid]=True; guardar_datos(); return
        if intent=="pago":
            await m.reply_text(OCUPADITA_MSG, reply_markup=get_volver())
            await context.bot.send_message(ADMIN_ID,f"💰 PAGO BOT @{un} {uid}\n{raw}",reply_markup=teclado_admin(uid,un))
            USUARIOS[uid].setdefault('flags',{})['pausado']=True; guardar_datos(); return
        if intent=="promo": await enviar_5_fotos(m); await m.reply_text(GRATIS_TEXTO, reply_markup=get_volver()); return
        if intent=="real": await m.reply_text(no_repite(uid,'real',[f"Soy real mor revisa mi canal\n{LINK_CANAL}"]), reply_markup=get_volver()); return
        if USUARIOS[uid]['contador_msg'] >= 6: await despedida_ocupadita(m, False, uid); return
        await m.reply_text(f"Wenas mor 🙈\n\nMi canal: {LINK_CANAL}", reply_markup=get_menu())
        guardar_datos(); prog_follow(context,uid,m.chat.id); return

def main():
    cargar_datos()
    app=Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start_cmd))
    app.add_handler(CallbackQueryHandler(btn))
    app.add_handler(MessageHandler(filters.UpdateType.BUSINESS_MESSAGE, handle_all))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_all))
    app.add_handler(MessageHandler(filters.PHOTO | filters.VIDEO, handle_all))
    print("Listo: texto nuevo + pregunta moneda")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__=='__main__': main()
