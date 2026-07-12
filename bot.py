# FIX GRATIS NO ENVIABA - pausado_foto ya no bloquea gratis/precio + anti-spam corregido
import os, json, logging, time, unicodedata, re
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto, Update
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, MessageHandler, filters

logging.basicConfig(level=logging.INFO)
TOKEN = '8762577283:AAFVT7_WMpZ7njVnToIlZypUpCToF5LGcbA'
ADMIN_ID = 8783569348
DATA_FILE = "data.json"
USUARIOS = {}; ESPERA_PAIS = {}

GRATIS_TEXTO = """✨ ¿Quieres verme cogiendo y moviendo las ttas? 👀💕 ✨

Te lo regalo mor, es fácil:
1️⃣ Sube una de las 5 fotitos 🥺
2️⃣ Busca videitos hormonales y comenta cosas hormo como: alguien?, Revisa mi story, busco nv, yo si cumplo 🫣 y cositas así

Cuando llegues a 100 vistas mándame captura 🥵
Verifico y te suelto los videitos gratis :3"""

GRATIS_RECORDATORIO = "Ya te envié como ganarte los gratis mor 🥺 cumplan la promo para los videos gratis :3"
PREGUNTA_PAIS = "De dónde eres Mor?"
PREGUNTA_PAIS_AYUDA = "Dime de qué país eres mor? 🙈"
UPSELL_PICANTE = """Si pagas ahora mismo mor te mando extras bien ricos 😝🔥
dependiendo lo que elijas te sorprendo con más regalitos :3
solo si es ahora, después ya no"""
TEXTO_100_A_500 = """Cuando tu story llegue a 500-1000 me avisas y te suelto tus videitos al toque 🥵

Mándame videito entrando a TikTok → tu perfil → tu story → los likes, TODO seguido sin cortar. Si lo cortas se anula la promo, bebé 😘"""
OCUPADITA_MSG = "ando ocupadita en videollamada 👀 en un ratito te confirmo mor 🥰"

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
    if any(x in t for x in ['peru','lima','arequipa']): return 'pe'
    if any(x in t for x in ['mexico','mx']): return 'mx'
    if any(x in t for x in ['colombia','argentina','chile','venezuela','usa','eeuu','espana']): return 'usa'
    return None
def detectar_intencion(txt,cap=""):
    t=normalizar(f"{txt} {cap}")
    comprar_kw = ['vendes','vende','quiero conte','conte','contenido','pack','precio','precios','presio','cuanto','cuánto','q cuesta','valor','cuanto vale']
    if any(k in t for k in comprar_kw): return "comprar"
    if "500" in t or "1000" in t: return "vistas500"
    if "100" in t: return "vistas100"
    if any(x in t for x in ['ya cumpli','cumpli','prueba','vistas']): return "cumplido"
    if any(x in t for x in ['gratis','promo','gratiss','gratisss']): return "promo"
    return "otro"

# ANTI-SPAM CORREGIDO 100%
def puede_enviar(uid, tipo, cd):
    ahora=time.time()
    USUARIOS.setdefault(uid,{}); USUARIOS[uid].setdefault('antispam',{})
    if not isinstance(USUARIOS[uid]['antispam'], dict): USUARIOS[uid]['antispam']={}
    ultimo = USUARIOS[uid]['antispam'].get(tipo, 0)
    if ahora - ultimo < cd: return False
    USUARIOS[uid]['antispam'] = ahora
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
    await enviar_5_fotos(u.message); await u.message.reply_text(GRATIS_TEXTO, reply_markup=get_menu())
async def btn(u,c):
    q=u.callback_query; await q.answer(); d=q.data; uid=q.from_user.id
    USUARIOS.setdefault(uid,{}).setdefault('flags',{})
    if q.from_user.id==ADMIN_ID and "_" in d:
        acc,t=d.split("_",1); t=int(t)
        if acc=="ok": await c.bot.send_message(t,"Listo mor ya te confirmé 💖")
        elif acc=="no": await c.bot.send_message(t,"Mor mándame mejor la pruebita completa porfa 🥺")
        elif acc=="500": await c.bot.send_message(t,TEXTO_100_A_500)
        return
    if d=='volver':
        if not puede_enviar(uid,'volver',2): return
        await q.edit_message_text("¿Qué quieres mor? :3", reply_markup=get_menu())
    elif d=='comprar':
        if USUARIOS[uid].get('pais_guardado'):
            await q.edit_message_text(precio_por_pais(USUARIOS[uid]['pais_guardado']), parse_mode='HTML', disable_web_page_preview=False, reply_markup=get_volver())
            return
        await q.edit_message_text("De donde eres mor 👀✨", reply_markup=get_precios())
    elif d in ['pe','mx','usa']:
        USUARIOS[uid]['pais_guardado']=d
        await q.edit_message_text(precio_por_pais(d), parse_mode='HTML', disable_web_page_preview=False, reply_markup=get_volver())
        if not USUARIOS[uid]['flags'].get('upsell'):
            await q.message.reply_text(UPSELL_PICANTE, reply_markup=get_volver())
            USUARIOS[uid]['flags']['upsell']=True
    elif d=='gratis':
        if not USUARIOS[uid]['flags'].get('gratis_enviado'):
            await enviar_5_fotos(q.message); await q.message.reply_text(GRATIS_TEXTO, reply_markup=get_volver())
            USUARIOS[uid]['flags']['gratis_enviado']=True
        else:
            if puede_enviar(uid,'gratis_aviso',10):
                await q.message.reply_text(GRATIS_RECORDATORIO, reply_markup=get_volver())

async def handle_all(update, context):
    m = update.business_message or update.message
    if not m or not m.from_user or m.from_user.is_bot: return
    uid=m.from_user.id; raw=(m.text or "").strip(); cap=getattr(m,'caption','') or ""
    es_neg = update.business_message is not None
    if es_neg and uid==ADMIN_ID: return
    USUARIOS.setdefault(uid,{}); USUARIOS[uid].setdefault('flags',{})
    if time.time()-USUARIOS[uid].get('ultimo',0) < 0.8: return
    USUARIOS[uid]['ultimo']=time.time()
    if USUARIOS[uid]['flags'].get('pausado'): return

    intent=detectar_intencion(raw,cap)

    # FIX: pausado_foto ya NO bloquea gratis/precio
    if USUARIOS[uid]['flags'].get('pausado_foto'):
        if intent in ["promo","comprar","vistas100","vistas500","cumplido"]:
            USUARIOS[uid]['flags']['pausado_foto']=False
        else:
            cn=normalizar(raw+" "+cap)
            if not any(x in cn for x in ['100','500','1000','vistas','prueba','cumpli','gratis','precio','presio']):
                return
            USUARIOS[uid]['flags']['pausado_foto']=False

    if es_neg:
        if uid in ESPERA_PAIS:
            pais=detectar_pais(raw)
            if pais:
                USUARIOS[uid]['pais_guardado']=pais
                await m.reply_text(precio_por_pais(pais), parse_mode='HTML', disable_web_page_preview=False)
                if not USUARIOS[uid]['flags'].get('upsell_n'):
                    await m.reply_text(UPSELL_PICANTE)
                    USUARIOS[uid]['flags']['upsell_n']=True
                del ESPERA_PAIS[uid]; return
            else:
                if ESPERA_PAIS[uid].get('intentos',0)==0 and puede_enviar(uid,'pais_ayuda',15):
                    await m.reply_text(PREGUNTA_PAIS_AYUDA)
                    ESPERA_PAIS[uid]['intentos']=1; return
                else: return

        if m.photo or m.video:
            cn=normalizar(cap+" "+raw)
            fid=m.video.file_id if m.video else m.photo[-1].file_id
            es_prueba = any(x in cn for x in ['100','500','1000','vistas','prueba','cumpli'])
            if es_prueba:
                txt=f"📈 PRUEBA {cn[:30]}\n@{m.from_user.username or uid} {uid}"
                if m.video: await context.bot.send_video(ADMIN_ID,fid,caption=txt,reply_markup=teclado_admin_100(uid,m.from_user.username or "None"))
                else: await context.bot.send_photo(ADMIN_ID,fid,caption=txt,reply_markup=teclado_admin_100(uid,m.from_user.username or "None"))
                return
            else:
                txt=f"📷 FOTO SIN PRUEBA\n@{m.from_user.username or uid} {uid} - pausado"
                if m.video: await context.bot.send_video(ADMIN_ID,fid,caption=txt)
                else: await context.bot.send_photo(ADMIN_ID,fid,caption=txt)
                USUARIOS[uid]['flags']['pausado_foto']=True
                return

        if not USUARIOS[uid]['flags'].get('gratis_enviado'):
            if intent=="comprar":
                USUARIOS[uid]['flags']['gratis_enviado']=True
                if USUARIOS[uid].get('pais_guardado'):
                    await m.reply_text(precio_por_pais(USUARIOS[uid]['pais_guardado']), parse_mode='HTML', disable_web_page_preview=False)
                    return
                await m.reply_text(PREGUNTA_PAIS)
                ESPERA_PAIS[uid]={'intentos':0}; return
            # Si pide gratis o es primer hola -> manda gratis
            await enviar_5_fotos(m); await m.reply_text(GRATIS_TEXTO)
            USUARIOS[uid]['flags']['gratis_enviado']=True; return

        if intent=="comprar":
            if USUARIOS[uid].get('pais_guardado'):
                if puede_enviar(uid,'precio_directo',5):
                    await m.reply_text(precio_por_pais(USUARIOS[uid]['pais_guardado']), parse_mode='HTML', disable_web_page_preview=False)
                return
            if uid in ESPERA_PAIS: return
            if puede_enviar(uid,'pregunta_pais',15):
                await m.reply_text(PREGUNTA_PAIS)
                ESPERA_PAIS[uid]={'intentos':0}
            return
        if intent=="promo":
            if puede_enviar(uid,'gratis_recordatorio',20):
                await m.reply_text(GRATIS_RECORDATORIO)
            return
        if intent in ["vistas100","vistas500","cumplido"]:
            if puede_enviar(uid,'prueba_txt',10):
                await context.bot.send_message(ADMIN_ID,f"📩 PRUEBA TEXTO @{m.from_user.username or uid} {uid}\n{raw}",reply_markup=teclado_admin_100(uid,m.from_user.username or "None"))
            return
        if intent=="otro":
            if puede_enviar(uid,'vivo_otro',300):
                await m.reply_text("Aquí estoy mor 🙈 dime si quieres los gratis o precios? 👀")
            return
    else:
        if not USUARIOS[uid]['flags'].get('gratis_enviado'):
            if intent=="comprar":
                USUARIOS[uid]['flags']['gratis_enviado']=True
                await m.reply_text("De donde eres mor 👀✨", reply_markup=get_precios())
                return
            await enviar_5_fotos(m); await m.reply_text(GRATIS_TEXTO, reply_markup=get_menu())
            USUARIOS[uid]['flags']['gratis_enviado']=True; return
        if intent=="comprar":
            if USUARIOS[uid].get('pais_guardado'):
                if puede_enviar(uid,'precio_directo_b',5):
                    await m.reply_text(precio_por_pais(USUARIOS[uid]['pais_guardado']), parse_mode='HTML', reply_markup=get_volver())
                return
            if puede_enviar(uid,'comprar_b',3):
                await m.reply_text("De donde eres mor 👀✨", reply_markup=get_precios())
            return
        if intent=="promo" or intent in ["vistas100","vistas500","cumplido"]:
            if puede_enviar(uid,'promo_b',15):
                await m.reply_text(GRATIS_RECORDATORIO, reply_markup=get_volver())
            return
        if intent=="otro":
            if puede_enviar(uid,'otro_bot',300):
                await m.reply_text("Wenas mor 🙈 ¿gratis o precios?", reply_markup=get_menu())
            return

def main():
    cargar_datos()
    app=Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start_cmd))
    app.add_handler(CallbackQueryHandler(btn))
    app.add_handler(MessageHandler(filters.UpdateType.BUSINESS_MESSAGE, handle_all))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_all))
    app.add_handler(MessageHandler(filters.PHOTO | filters.VIDEO, handle_all))
    print("Fix gratis ya envía + no bloquea por foto")
    app.run_polling(allowed_updates=Update.ALL_TYPES)
if __name__=='__main__': main()
