# ============================================================
# SOLO PAÍS - Precios en dólares con mismo formato que Perú/México
# ============================================================
import os, json, logging, time, unicodedata, re
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto, Update
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, MessageHandler, filters

logging.basicConfig(level=logging.INFO)
TOKEN = '8762577283:AAFVT7_WMpZ7njVnToIlZypUpCToF5LGcbA'
ADMIN_ID = 8783569348
DATA_FILE = "data.json"

USUARIOS = {}; ESPERA_PAIS = {}

GRATIS_TEXTO = """✨ ¿Quieres verme cogiendo y moviendo las ttas? 👀💕 ✨

Solo haz esto mor:
1️⃣ Sube la foto de mi QR a tu story
2️⃣ Comenta cositas hormo en TikToks con #hormo #hot

Avísame cuando llegues a 100 vistas 🥵
Mándame pruebas que cumpliste con la promo :3"""
GRATIS_RECORDATORIO = "Ya te envié como ganarte los gratis mor 🥺 cumplan la promo para los videos gratis :3"
PREGUNTA_PAIS = "De dónde eres Mor?"
PREGUNTA_PAIS_AYUDA = "Dime de qué país eres mor? 🙈 Perú, México, Colombia, etc."
TEXTO_100_A_500 = "Sii mor ya vi que llegaste a 100 🥺✨ pero son 500 vistas mor 🥵 sigue comentando y cuando llegues a 500 me mandas pruebas que cumpliste con la promo :3"
OCUPADITA_MSG = "ando algo ocupadita haciéndo videollamada 👀 en un ratito te confirmo mor 🥰"
UPSELL_PICANTE = """Si pagas ahora mismo mor te mando regalitos extra bien puercos 😝🔥
te grabo moviendo las ttas y gimiendo tu nombre solo para ti 🥵💦
solo si es ahora, después ya no lo regalo"""

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

<b>PAGO MX:</b>
🔢 CLABE: <code>646180546711450910</code>
📝 Ref: <code>yanae</code>"""

PE_PRECIOS = """🛍 <b>VIDEOS</b> 🛒

🎂 <b>BÁSICO: S/ 15</b>
→ 5 videitos | S/ 3 c/u

━━━━━━━━━━━━━━
🔥 <b>TOP: S/ 30 ← MÁS VENDIDO</b>
→ 12 videitos | S/ 2.5 c/u

━━━━━━━━━━━━━━
🏆 <b>PREMIUM: S/ 60</b>
→ 20 videitos + 1 perso + sexting

━━━━━━━━━━━━━━
📼 <b>VIDEOLLAMADAS</b> S/60 5min | S/80 10min

<b>YAPE / PLIN:</b>
<code>923553612</code>"""

# MISMO FORMATO QUE LOS DEMÁS, CON LINK DIRECTO
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

<b>PAGO OTROS - link directo:</b>
🔗 <a href="https://www.paypal.com/qrcodes/p2pqrc/76RWY9FF7Q7RE">Pagar aquí - PayPal AbigailMaximoofO</a>"""

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
def detectar_pais(t):
    t=normalizar(t)
    if any(x in t for x in ['peru','lima','arequipa','cusco','trujillo','chiclayo','piura']): return 'pe'
    if any(x in t for x in ['mexico','mx','jalisco','guadalajara','monterrey','cancun','puebla']): return 'mx'
    if any(x in t for x in ['colombia','argentina','chile','venezuela','ecuador','bolivia','usa','eeuu','españa']): return 'usa'
    return None
def detectar_intencion(txt,cap=""):
    t=normalizar(f"{txt} {cap}")
    if "500" in t and "vist" in t: return "vistas500"
    if "100" in t and "vist" in t: return "vistas100"
    if any(x in t for x in ['ya cumpli','cumpli']): return "cumplido"
    if any(x in t for x in ['yape','plin','pago','comprobante']): return "pago"
    if any(x in t for x in ['gratis','promo']): return "promo"
    if any(x in t for x in ['precio','precios','cuanto','cuesta','comprar']): return "comprar"
    return "otro"
def puede_enviar(uid, tipo, cd):
    ahora=time.time(); USUARIOS[uid].setdefault('antispam',{})
    if ahora - USUARIOS[uid]['antispam'].get(tipo,0) < cd: return False
    USUARIOS[uid]['antispam']=ahora; return True
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
    uid=u.effective_user.id; USUARIOS.setdefault(uid,{}).setdefault('flags',{}); USUARIOS[uid]['flags']['gratis_enviado']=True; guardar_datos()
    await enviar_5_fotos(u.message); await u.message.reply_text(GRATIS_TEXTO, reply_markup=get_menu())
async def btn(u,c):
    q=u.callback_query; await q.answer(); d=q.data; uid=q.from_user.id
    USUARIOS.setdefault(uid,{}).setdefault('flags',{})
    if q.from_user.id==ADMIN_ID and "_" in d:
        acc,t=d.split("_",1); t=int(t)
        if acc=="ok": await c.bot.send_message(t,"Listo mor ya te confirmé 💖"); await q.edit_message_caption(caption=(q.message.caption or "")+"\n✅ CONFIRMADO"); USUARIOS.setdefault(t,{}).setdefault('flags',{})['pausado']=False
        elif acc=="no": await c.bot.send_message(t,"Mor mándame mejor la pruebita completa porfa 🥺"); await q.edit_message_caption(caption=(q.message.caption or "")+"\n❌ PEDIDA"); USUARIOS.setdefault(t,{}).setdefault('flags',{})['pausado']=False
        elif acc=="500": await c.bot.send_message(t,TEXTO_100_A_500); await q.edit_message_caption(caption=(q.message.caption or "")+"\n📈 MENSAJE 500 ENVIADO")
        guardar_datos(); return
    if d=='volver':
        if not puede_enviar(uid,'volver',4): return
        await q.edit_message_text("¿Qué quieres mor? :3", reply_markup=get_menu())
    elif d=='comprar':
        if not puede_enviar(uid,'comprar',4): return
        await q.edit_message_text("De donde eres mor 👀✨", reply_markup=get_precios())
    elif d in ['pe','mx','usa']:
        if not puede_enviar(uid,f'precio_{d}',8): return
        await q.edit_message_text(precio_por_pais(d), parse_mode='HTML', disable_web_page_preview=False, reply_markup=get_volver())
        if not USUARIOS[uid]['flags'].get('upsell'):
            await q.message.reply_text(UPSELL_PICANTE, reply_markup=get_volver())
            USUARIOS[uid]['flags']['upsell']=True; guardar_datos()
    elif d=='gratis':
        if not USUARIOS[uid]['flags'].get('gratis_enviado'):
            await enviar_5_fotos(q.message); await q.message.reply_text(GRATIS_TEXTO, reply_markup=get_volver())
            USUARIOS[uid]['flags']['gratis_enviado']=True; guardar_datos()
        else:
            if not USUARIOS[uid]['flags'].get('gratis_aviso') and puede_enviar(uid,'gratis_aviso',3600):
                await q.message.reply_text(GRATIS_RECORDATORIO, reply_markup=get_volver())
                USUARIOS[uid]['flags']['gratis_aviso']=True; guardar_datos()

async def handle_all(update, context):
    m = update.business_message or update.message
    if not m or not m.from_user or m.from_user.is_bot: return
    uid=m.from_user.id; un=m.from_user.username or "None"; raw=m.text or ""; cap=getattr(m,'caption','') or ""
    es_neg = update.business_message is not None
    if es_neg and uid==ADMIN_ID: return
    USUARIOS.setdefault(uid,{}); USUARIOS[uid].setdefault('flags',{})
    ahora=time.time()
    if ahora-USUARIOS[uid].get('ultimo',0) < 2.2: return
    USUARIOS[uid]['ultimo']=ahora
    if USUARIOS[uid]['flags'].get('pausado'): return
    if es_neg:
        if uid in ESPERA_PAIS:
            pais = detectar_pais(raw)
            if pais:
                if puede_enviar(uid,'precio_negocio',8):
                    await m.reply_text(precio_por_pais(pais), parse_mode='HTML', disable_web_page_preview=False)
                    if not USUARIOS[uid]['flags'].get('upsell_negocio'):
                        await m.reply_text(UPSELL_PICANTE)
                        USUARIOS[uid]['flags']['upsell_negocio']=True
                del ESPERA_PAIS[uid]; guardar_datos(); return
            else:
                intentos=ESPERA_PAIS[uid].get('intentos',0)
                if intentos==0 and puede_enviar(uid,'pais_ayuda',20):
                    await m.reply_text(PREGUNTA_PAIS_AYUDA)
                    ESPERA_PAIS[uid]['intentos']=1; guardar_datos(); return
                else: return
        if m.photo or m.video:
            is_v=bool(m.video); fid=m.video.file_id if is_v else m.photo[-1].file_id
            cn=normalizar(cap+" "+raw); es_100="100" in cn; es_500="500" in cn
            link=f"https://t.me/{un}" if un!="None" else f"tg://user?id={uid}"
            if es_100 and not es_500:
                if not puede_enviar(uid,'notif_100',25): return
                txt=f"📈 NEGOCIO 100\n@{un} {uid}\n{link}"
                if is_v: await context.bot.send_video(ADMIN_ID,fid,caption=txt,reply_markup=teclado_admin_100(uid,un))
                else: await context.bot.send_photo(ADMIN_ID,fid,caption=txt,reply_markup=teclado_admin_100(uid,un))
                return
            if es_500:
                txt=f"✅ NEGOCIO 500\n@{un} {uid}\n{link}"
                if is_v: await context.bot.send_video(ADMIN_ID,fid,caption=txt,reply_markup=teclado_admin(uid,un))
                else: await context.bot.send_photo(ADMIN_ID,fid,caption=txt,reply_markup=teclado_admin(uid,un))
                await m.reply_text(OCUPADITA_MSG); USUARIOS[uid]['flags']['pausado']=True; guardar_datos(); return
            return
        if not USUARIOS[uid]['flags'].get('gratis_enviado'):
            await enviar_5_fotos(m); await m.reply_text(GRATIS_TEXTO)
            USUARIOS[uid]['flags']['gratis_enviado']=True; guardar_datos(); return
        intent=detectar_intencion(raw,cap)
        if intent in ["vistas100","cumplido"]:
            if not puede_enviar(uid,'notif_100_txt',25): return
            link=f"https://t.me/{un}" if un!="None" else f"tg://user?id={uid}"
            await context.bot.send_message(ADMIN_ID,f"📈 NEGOCIO 100 @{un} {uid}\n{raw}\n{link}",reply_markup=teclado_admin_100(uid,un)); return
        if intent=="comprar":
            if not puede_enviar(uid,'pregunta_pais',45): return
            await m.reply_text(PREGUNTA_PAIS)
            ESPERA_PAIS[uid]={'intentos':0}; guardar_datos(); return
        if intent=="promo":
            if not USUARIOS[uid]['flags'].get('gratis_aviso') and puede_enviar(uid,'gratis_aviso_n',3600):
                await m.reply_text(GRATIS_RECORDATORIO)
                USUARIOS[uid]['flags']['gratis_aviso']=True; guardar_datos()
            return
        return
    else:
        intent=detectar_intencion(raw,cap)
        if intent=="otro": return
        if not USUARIOS[uid]['flags'].get('gratis_enviado'):
            await enviar_5_fotos(m); await m.reply_text(GRATIS_TEXTO, reply_markup=get_menu())
            USUARIOS[uid]['flags']['gratis_enviado']=True; guardar_datos(); return
        if intent=="comprar":
            if not puede_enviar(uid,'comprar',5): return
            await m.reply_text("De donde eres mor 👀✨", reply_markup=get_precios()); return
        if intent=="promo":
            if not USUARIOS[uid]['flags'].get('gratis_aviso') and puede_enviar(uid,'gratis_aviso_b',3600):
                await m.reply_text(GRATIS_RECORDATORIO, reply_markup=get_volver())
                USUARIOS[uid]['flags']['gratis_aviso']=True; guardar_datos()
            return

def main():
    cargar_datos()
    app=Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start_cmd))
    app.add_handler(CallbackQueryHandler(btn))
    app.add_handler(MessageHandler(filters.UpdateType.BUSINESS_MESSAGE, handle_all))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_all))
    app.add_handler(MessageHandler(filters.PHOTO | filters.VIDEO, handle_all))
    print("Solo país + dólares mismo formato listo")
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__=='__main__': main()
