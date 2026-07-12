# DEFINITIVO - SIN SPAM - SIN REPETIR - SOLO PERU/MEX + OTROS
import os, json, logging, time, unicodedata, re
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto, Update
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, MessageHandler, filters

logging.basicConfig(level=logging.INFO)
TOKEN = '8762577283:AAFVT7_WMpZ7njVnToIlZypUpCToF5LGcbA'
ADMIN_ID = 8783569348
DATA_FILE = "data.json"
USUARIOS = {}; ESPERA_PAIS = {}

CANAL_LINK = "https://t.me/Yanabicitasa"

GRATIS_TEXTO = f"""✨ ¿Quieres verme cogiendo y moviendo las ttas? 👀💕 ✨

Te lo regalo mor, es fácil:

1️⃣ Sube una de las 5 fotitos a tu historia 🥺 (24h)

2️⃣ Ve a TikTok, busca videitos hormonales y comenta:
   alguien?, Revisa mi story, busco nv, yo si cumplo 🫣

3️⃣ Cuando llegues a 100 vistas mándame captura grabando seguido sin cortar 🥵

Verifico y te suelto los videitos gratis :3

📢 Mi canal:
{CANAL_LINK}"""

GRATIS_RECORDATORIO = "ya te mande como conseguir mis videitos gratis mor 🥺💦"
PREGUNTA_PAIS = "De dónde eres Mor?"
UPSELL_PICANTE = """Si pagas ahora mismo mor te mando extras bien ricos 😝🔥
dependiendo lo que elijas te sorprendo con más regalitos :3
solo si es ahora, después ya no"""
TEXTO_100_A_500 = """Cuando tu story llegue a 500-1000 me avisas y te suelto tus videitos al toque 🥵
Mándame videito entrando a TikTok → tu perfil → tu story → los likes, TODO seguido sin cortar. Si lo cortas se anula la promo, bebé 😘"""

MX_PRECIOS = """🛍 <b>VIDEOS</b> 🛒
🎂 <b>BÁSICO: $100 MXN</b> → 5 videitos | $20 c/u
━━━━━━━━━━━━━━
🔥 <b>TOP: $200 MXN ← MÁS VENDIDO</b> → 12 videitos | $16 c/u
━━━━━━━━━━━━━━
🏆 <b>PREMIUM: $400 MXN</b> → 20 videitos + 1 perso + sexting
━━━━━━━━━━━━━━
📼 <b>VIDEOLLAMADAS</b> $400 5min | $600 10min
<b>PAGO MX:</b> CLABE: <code>646180546711450910</code> Ref: <code>yanae</code>"""
PE_PRECIOS = """🛍 <b>VIDEOS</b> 🛒
🎂 <b>BÁSICO: S/ 15</b> → 5 videitos | S/ 3 c/u
━━━━━━━━━━━━━━
🔥 <b>TOP: S/ 30 ← MÁS VENDIDO</b> → 12 videitos | S/ 2.5 c/u
━━━━━━━━━━━━━━
🏆 <b>PREMIUM: S/ 60</b> → 20 videitos + 1 perso + sexting
━━━━━━━━━━━━━━
📼 <b>VIDEOLLAMADAS</b> S/60 5min | S/80 10min
<b>YAPE / PLIN:</b> <code>923553612</code>"""
USA_PRECIOS = """🛍 <b>VIDEOS</b> 🛒
🎂 <b>BÁSICO: $5 USD</b> → 5 videitos | $1 c/u
━━━━━━━━━━━━━━
🔥 <b>TOP: $9 USD ← MÁS VENDIDO</b> → 12 videitos | $0.75 c/u
━━━━━━━━━━━━━━
🏆 <b>PREMIUM: $20 USD</b> → 20 videitos + 1 perso + sexting
━━━━━━━━━━━━━━
📼 <b>VIDEOLLAMADAS</b> $20 5min | $35 10min
<b>PAGO OTROS:</b> 🔗 <a href="https://www.paypal.com/qrcodes/p2pqrc/76RWY9FF7Q7RE">Pagar aquí - PayPal</a>"""

def cargar_datos():
    global USUARIOS
    if os.path.exists(DATA_FILE):
        try: USUARIOS={int(k):v for k,v in json.load(open(DATA_FILE)).get('usuarios',{}).items()}
        except: pass
def normalizar(t):
    if not t: return ""
    t=unicodedata.normalize('NFKD',t).encode('ascii','ignore').decode().lower()
    return re.sub(r'[^\w\s]',' ',t)

def detectar_pais(t):
    t=normalizar(t)
    mx=['mexico','mx','cdmx','jalisco','guadalajara','monterrey','nuevo leon','puebla','cancun','quintana roo','veracruz','yucatan','merida','tijuana','sinaloa','sonora','chihuahua','oaxaca','chiapas','guanajuato','queretaro','aguascalientes','baja','toluca','culiacan']
    pe=['peru','pe','lima','arequipa','trujillo','chiclayo','lambayeque','piura','cusco','cuzco','ica','tacna','puno','ayacucho','cajamarca','chimbote','huancayo','junin','iquitos','loreto','huanuco','tarapoto','pucallpa','tumbes','moquegua','huacho']
    if any(x in t for x in mx): return 'mx'
    if any(x in t for x in pe): return 'pe'
    if len(t) >= 3: return 'usa' # Colombia, Chile, Argentina, etc = Otros
    return None

def detectar_intencion(txt,cap=""):
    t=normalizar(f"{txt} {cap}")
    if any(k in t for k in ['vendes','vende','quiero conte','conte','contenido','pack','precio','precios','presio','cuanto']): return "comprar"
    if "500" in t or "1000" in t: return "vistas500"
    if "100" in t: return "vistas100"
    if any(x in t for x in ['prueba','vistas','cumpli']): return "prueba"
    if any(x in t for x in ['gratis','promo']): return "promo"
    return "otro"

# FIX REAL ANTI-SPAM
def puede_enviar(uid, tipo, cd):
    ahora=time.time()
    USUARIOS.setdefault(uid,{}).setdefault('antispam',{})
    if not isinstance(USUARIOS[uid]['antispam'], dict): USUARIOS[uid]['antispam']={}
    ultimo = USUARIOS[uid]['antispam'].get(tipo, 0)
    if ahora - ultimo < cd: return False
    USUARIOS[uid]['antispam'][tipo] = ahora # FIX: antes borraba el dict
    return True

async def reply_once(m, uid, tipo, texto, **kwargs):
    # NUNCA repite el mismo texto en el mismo chat
    USUARIOS[uid].setdefault('historial_textos', [])
    if texto in USUARIOS[uid]['historial_textos']:
        return False
    cd = kwargs.pop('cd', 600)
    if not puede_enviar(uid, tipo, cd):
        return False
    await m.reply_text(texto, **kwargs)
    USUARIOS[uid]['historial_textos'].append(texto)
    if len(USUARIOS[uid]['historial_textos']) > 15:
        USUARIOS[uid]['historial_textos'] = USUARIOS[uid]['historial_textos'][-15:]
    return True

def link_directo(uid,un): return f"https://t.me/{un}" if un!="None" else f"tg://user?id={uid}"
def get_menu(): return InlineKeyboardMarkup([[InlineKeyboardButton("💎 COMPRAR",callback_data='comprar')],[InlineKeyboardButton("🎁 GRATIS",callback_data='gratis')]])
def get_precios(): return InlineKeyboardMarkup([[InlineKeyboardButton("🇵🇪 Perú",callback_data='pe')],[InlineKeyboardButton("🇲🇽 México",callback_data='mx')],[InlineKeyboardButton("🌍 Otros países",callback_data='usa')],[InlineKeyboardButton("⬅️ Volver",callback_data='volver')]])
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
async def start_cmd(u,c):
    uid=u.effective_user.id; USUARIOS.setdefault(uid,{}).setdefault('flags',{}); USUARIOS[uid]['flags']['gratis_enviado']=True
    await enviar_5_fotos(u.message); await u.message.reply_text(GRATIS_TEXTO, reply_markup=get_menu(), disable_web_page_preview=False)
async def btn(u,c):
    q=u.callback_query; await q.answer(); d=q.data; uid=q.from_user.id
    USUARIOS.setdefault(uid,{}).setdefault('flags',{})
    if q.from_user.id==ADMIN_ID and "_" in d:
        acc,t=d.split("_",1); t=int(t)
        if acc=="ok": await c.bot.send_message(t,"Listo mor ya te confirmé 💖")
        elif acc=="no": await c.bot.send_message(t,"Mor mándame mejor la pruebita completa porfa 🥺")
        elif acc=="500": await c.bot.send_message(t,TEXTO_100_A_500)
        return
    if d=='volver': await q.edit_message_text("¿Qué quieres mor? :3", reply_markup=get_menu())
    elif d=='comprar':
        if USUARIOS[uid].get('pais_guardado'):
            await q.edit_message_text(precio_por_pais(USUARIOS[uid]['pais_guardado']), parse_mode='HTML', disable_web_page_preview=False, reply_markup=get_volver()); return
        await q.edit_message_text("De donde eres mor 👀✨", reply_markup=get_precios())
    elif d in ['pe','mx','usa']:
        USUARIOS[uid]['pais_guardado']=d
        await q.edit_message_text(precio_por_pais(d), parse_mode='HTML', disable_web_page_preview=False, reply_markup=get_volver())
        if not USUARIOS[uid]['flags'].get('upsell'):
            await q.message.reply_text(UPSELL_PICANTE, reply_markup=get_volver()); USUARIOS[uid]['flags']['upsell']=True
    elif d=='gratis':
        if not USUARIOS[uid]['flags'].get('gratis_enviado'):
            await enviar_5_fotos(q.message); await q.message.reply_text(GRATIS_TEXTO, reply_markup=get_volver(), disable_web_page_preview=False)
            USUARIOS[uid]['flags']['gratis_enviado']=True
        else:
            await reply_once(q.message, uid, "gratis_recordatorio", GRATIS_RECORDATORIO, cd=999, reply_markup=get_volver())

async def handle_all(update, context):
    m = update.business_message or update.message
    if not m or not m.from_user or m.from_user.is_bot: return
    uid=m.from_user.id; raw=(m.text or "").strip(); cap=getattr(m,'caption','') or ""
    es_neg = update.business_message is not None
    if es_neg and uid==ADMIN_ID: return
    USUARIOS.setdefault(uid,{}); USUARIOS[uid].setdefault('flags',{})
    if time.time()-USUARIOS[uid].get('ultimo',0) < 1: return
    USUARIOS[uid]['ultimo']=time.time()
    if USUARIOS[uid]['flags'].get('pausado'): return
    if USUARIOS[uid]['flags'].get('pausado_foto'):
        if not any(x in normalizar(raw+" "+cap) for x in ['100','500','vistas','prueba','gratis','precio']): return
        USUARIOS[uid]['flags']['pausado_foto']=False
    intent=detectar_intencion(raw,cap)
    if es_neg:
        if uid in ESPERA_PAIS:
            pais=detectar_pais(raw)
            if pais:
                USUARIOS[uid]['pais_guardado']=pais
                await m.reply_text(precio_por_pais(pais), parse_mode='HTML', disable_web_page_preview=False)
                if not USUARIOS[uid]['flags'].get('upsell_n'):
                    await m.reply_text(UPSELL_PICANTE); USUARIOS[uid]['flags']['upsell_n']=True
                del ESPERA_PAIS[uid]; return
            else: return
        if m.photo or m.video:
            cn=normalizar(cap+" "+raw); fid=m.video.file_id if m.video else m.photo[-1].file_id
            if any(x in cn for x in ['100','500','1000','vistas','prueba','cumpli']):
                txt=f"📈 PRUEBA @{m.from_user.username or uid}"
                if m.video: await context.bot.send_video(ADMIN_ID,fid,caption=txt,reply_markup=teclado_admin_100(uid,m.from_user.username or "None"))
                else: await context.bot.send_photo(ADMIN_ID,fid,caption=txt,reply_markup=teclado_admin_100(uid,m.from_user.username or "None"))
                return
            else:
                USUARIOS[uid]['flags']['pausado_foto']=True; return
        if not USUARIOS[uid]['flags'].get('gratis_enviado'):
            if intent=="comprar":
                USUARIOS[uid]['flags']['gratis_enviado']=True
                if USUARIOS[uid].get('pais_guardado'):
                    await m.reply_text(precio_por_pais(USUARIOS[uid]['pais_guardado']), parse_mode='HTML', disable_web_page_preview=False); return
                await m.reply_text(PREGUNTA_PAIS); ESPERA_PAIS[uid]={'intentos':0}; return
            await enviar_5_fotos(m); await m.reply_text(GRATIS_TEXTO, disable_web_page_preview=False)
            USUARIOS[uid]['flags']['gratis_enviado']=True; return
        if intent in ["promo","prueba"]:
            await reply_once(m, uid, "gratis_recordatorio", GRATIS_RECORDATORIO, cd=999999); return
        if intent=="comprar":
            if USUARIOS[uid].get('pais_guardado'):
                await reply_once(m, uid, "precio_directo", precio_por_pais(USUARIOS[uid]['pais_guardado']), cd=999999, parse_mode='HTML', disable_web_page_preview=False); return
            if uid not in ESPERA_PAIS:
                await m.reply_text(PREGUNTA_PAIS); ESPERA_PAIS[uid]={'intentos':0}
            return
        if intent=="otro":
            await reply_once(m, uid, "vivo", "Aquí estoy mor 🙈 dime si quieres los gratis o precios? 👀", cd=600); return
    else:
        if not USUARIOS[uid]['flags'].get('gratis_enviado'):
            if intent=="comprar":
                USUARIOS[uid]['flags']['gratis_enviado']=True
                await m.reply_text("De donde eres mor 👀✨", reply_markup=get_precios()); return
            await enviar_5_fotos(m); await m.reply_text(GRATIS_TEXTO, reply_markup=get_menu(), disable_web_page_preview=False)
            USUARIOS[uid]['flags']['gratis_enviado']=True; return
        if intent in ["promo","prueba"]:
            await reply_once(m, uid, "gratis_recordatorio", GRATIS_RECORDATORIO, cd=999999, reply_markup=get_volver()); return

def main():
    cargar_datos()
    app=Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start_cmd))
    app.add_handler(CallbackQueryHandler(btn))
    app.add_handler(MessageHandler(filters.UpdateType.BUSINESS_MESSAGE, handle_all))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_all))
    app.add_handler(MessageHandler(filters.PHOTO | filters.VIDEO, handle_all))
    print("Bot sin spam - sin repetir mensajes - activo")
    app.run_polling(allowed_updates=Update.ALL_TYPES)
if __name__=='__main__': main()
