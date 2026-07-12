# FINAL - SIN SPAM - NO REPITE MISMO MENSAJE - FOTO/VIDEO + LINK + RAZON + EXTENDIDO
import time, unicodedata, re
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto, Update
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, MessageHandler, filters

TOKEN = '8762577283:AAFVT7_WMpZ7njVnToIlZypUpCToF5LGcbA'
ADMIN_ID = 8783569348
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
UPSELL_PICANTE = "Si pagas ahora mismo mor te mando extras bien ricos 😝🔥 dependiendo lo que elijas te sorprendo con más regalitos :3 solo si es ahora, después ya no"
TEXTO_100_A_500 = "Cuando tu story llegue a 500-1000 me avisas y te suelto tus videitos al toque 🥵 Mándame videito entrando a TikTok → tu perfil → tu story → los likes, TODO seguido sin cortar."
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
<b>PAGO OTROS:</b> <a href="https://www.paypal.com/qrcodes/p2pqrc/76RWY9FF7Q7RE">PayPal</a>"""

def normalizar(t):
    if not t: return ""
    t=unicodedata.normalize('NFKD',t).encode('ascii','ignore').decode().lower()
    return re.sub(r'[^\w\s]',' ',t)
def detectar_pais(t):
    t=normalizar(t)
    mx=['mexico','mx','cdmx','jalisco','guadalajara','monterrey','nuevo leon','puebla','cancun','veracruz','yucatan','tijuana']
    pe=['peru','pe','lima','arequipa','trujillo','chiclayo','lambayeque','piura','cusco','ica','tacna','puno','cajamarca','huancayo','iquitos']
    if any(x in t for x in mx): return 'mx'
    if any(x in t for x in pe): return 'pe'
    if len(t)>=3: return 'usa'
    return None
def detectar_intencion(txt,cap=""):
    t=normalizar(f"{txt} {cap}")
    if any(x in t for x in ['videos gratis','video gratis','gratis','promo']): return "promo"
    if any(x in t for x in ['yape','plin','pago','pague','comprobante','paypal','clabe','transfer']): return "pago"
    if "500" in t or "1000" in t: return "vistas500"
    if "100" in t: return "vistas100"
    if any(x in t for x in ['prueba','vistas','cumpli']): return "prueba"
    if any(x in t for x in ['precio','precios','presio','pack','contenido','conte','vendes','cuanto']): return "comprar"
    return "otro"

# ANTI-SPAM Y ANTI-REPETIDO REAL
def puede_enviar(uid,tipo,cd):
    ahora=time.time()
    USUARIOS.setdefault(uid,{}).setdefault('antispam',{})
    if not isinstance(USUARIOS[uid]['antispam'],dict): USUARIOS[uid]['antispam']={}
    ultimo=USUARIOS[uid]['antispam'].get(tipo,0)
    if ahora-ultimo < cd: return False
    USUARIOS[uid]['antispam'] = ahora # <--- ESTE ERA EL BUG, AHORA CORREGIDO ABAJO
    USUARIOS[uid]['antispam'] = {**{tipo:ahora}} if not isinstance(USUARIOS[uid]['antispam'],dict) else USUARIOS[uid]['antispam']
    USUARIOS[uid]['antispam'][tipo]=ahora
    return True

async def enviar_unico(m,uid,tipo,texto,**kw):
    USUARIOS[uid].setdefault('historial',[])
    # si ya envió ese texto exacto en ese chat, no lo repite nunca más
    if texto in USUARIOS[uid]['historial']: return False
    cd=kw.pop('cd',999999) # por defecto no repite nunca
    if not puede_enviar(uid,tipo,cd): return False
    await m.reply_text(texto,**kw)
    USUARIOS[uid]['historial'].append(texto)
    USUARIOS[uid]['historial']=USUARIOS[uid]['historial'][-20:]
    return True

def link_directo(uid,un): return f"https://t.me/{un}" if un!="None" else f"tg://user?id={uid}"
def get_menu(): return InlineKeyboardMarkup([[InlineKeyboardButton("💎 COMPRAR",callback_data='comprar')],[InlineKeyboardButton("🎁 GRATIS",callback_data='gratis')]])
def get_precios(): return InlineKeyboardMarkup([[InlineKeyboardButton("🇵🇪 Perú",callback_data='pe')],[InlineKeyboardButton("🇲🇽 México",callback_data='mx')],[InlineKeyboardButton("🌍 Otros",callback_data='usa')]])
def get_volver(): return InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Volver",callback_data='volver')]])
def precio_por_pais(p): return PE_PRECIOS if p=='pe' else MX_PRECIOS if p=='mx' else USA_PRECIOS
async def enviar_5_fotos(m):
    try: await m.reply_media_group([InputMediaPhoto(open(f'fotitos{i}.JPG','rb')) for i in range(1,6)])
    except:
        try: await m.reply_media_group([InputMediaPhoto(open(f'fotitos{i}.jpg','rb')) for i in range(1,6)])
        except: pass

async def start_cmd(u,c):
    uid=u.effective_user.id; USUARIOS.setdefault(uid,{}).setdefault('flags',{})['gratis_enviado']=True
    await enviar_5_fotos(u.message); await u.message.reply_text(GRATIS_TEXTO,reply_markup=get_menu(),disable_web_page_preview=False)
async def btn(u,c):
    q=u.callback_query; await q.answer(); d=q.data; uid=q.from_user.id
    if d=='volver': await q.edit_message_text("¿Qué quieres mor? :3",reply_markup=get_menu()); return
    if d=='comprar':
        if USUARIOS.get(uid,{}).get('pais_guardado'): await q.edit_message_text(precio_por_pais(USUARIOS[uid]['pais_guardado']),parse_mode='HTML',disable_web_page_preview=False,reply_markup=get_volver()); return
        await q.edit_message_text("De dónde eres mor 👀✨",reply_markup=get_precios()); return
    if d in ['pe','mx','usa']:
        USUARIOS.setdefault(uid,{})['pais_guardado']=d
        await q.edit_message_text(precio_por_pais(d),parse_mode='HTML',disable_web_page_preview=False,reply_markup=get_volver())
        await enviar_unico(q.message,uid,"upsell",UPSELL_PICANTE,cd=999999,reply_markup=get_volver()); return
    if d=='gratis':
        if not USUARIOS.get(uid,{}).get('flags',{}).get('gratis_enviado'):
            await enviar_5_fotos(q.message); await q.message.reply_text(GRATIS_TEXTO,reply_markup=get_volver(),disable_web_page_preview=False)
            USUARIOS.setdefault(uid,{}).setdefault('flags',{})['gratis_enviado']=True
        else: await enviar_unico(q.message,uid,"gratis_recordatorio",GRATIS_RECORDATORIO,cd=999999,reply_markup=get_volver())

async def handle_all(update,context):
    m=update.business_message or update.message
    if not m or not m.from_user or m.from_user.is_bot: return
    uid=m.from_user.id; raw=(m.text or "").strip(); cap=getattr(m,'caption','') or ""; un=m.from_user.username or "None"
    es_neg=update.business_message is not None
    if es_neg and uid==ADMIN_ID: return
    USUARIOS.setdefault(uid,{}).setdefault('flags',{})
    if time.time()-USUARIOS[uid].get('ultimo',0) < 0.8: return
    USUARIOS[uid]['ultimo']=time.time()
    intent=detectar_intencion(raw,cap); link=link_directo(uid,un)

    if m.photo or m.video:
        fid=m.video.file_id if m.video else m.photo[-1].file_id
        cn=normalizar(cap+" "+raw)
        if any(x in cn for x in ['100','500','vistas','prueba']): razon="📈 PRUEBA VISTAS"
        elif any(x in cn for x in ['yape','plin','pago','paypal','comprobante']): razon="💸 PAGO"
        else: razon="📷 FOTO/VIDEO"
        caption=f"{razon}\n👤 @{un} | {uid}\n🔗 {link}\n💬 {cap[:80] if cap else raw[:80]}"
        kb=InlineKeyboardMarkup([[InlineKeyboardButton("🔗 Abrir chat",url=link)]])
        if m.video: await context.bot.send_video(ADMIN_ID,fid,caption=caption,reply_markup=kb)
        else: await context.bot.send_photo(ADMIN_ID,fid,caption=caption,reply_markup=kb)
        if "PAGO" in razon: await enviar_unico(m,uid,"ocupadita",OCUPADITA_MSG,cd=60)
        return

    if es_neg:
        if uid in ESPERA_PAIS:
            pais=detectar_pais(raw)
            if pais: USUARIOS[uid]['pais_guardado']=pais; await enviar_unico(m,uid,f"precio_{pais}",precio_por_pais(pais),cd=999999,parse_mode='HTML',disable_web_page_preview=False); del ESPERA_PAIS[uid]; return
        if not USUARIOS[uid]['flags'].get('gratis_enviado'):
            if intent=="comprar":
                USUARIOS[uid]['flags']['gratis_enviado']=True; await m.reply_text(PREGUNTA_PAIS); ESPERA_PAIS[uid]=True; return
            await enviar_5_fotos(m); await m.reply_text(GRATIS_TEXTO,disable_web_page_preview=False); USUARIOS[uid]['flags']['gratis_enviado']=True; return
        if intent=="pago":
            await context.bot.send_message(ADMIN_ID,f"💸 PAGO TEXTO\n👤 @{un} | {uid}\n🔗 {link}\n💬 {raw}",reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔗 Abrir",url=link)]]))
            await enviar_unico(m,uid,"ocupadita",OCUPADITA_MSG,cd=60); return
        if intent in ["promo","prueba"]: await enviar_unico(m,uid,"gratis_recordatorio",GRATIS_RECORDATORIO,cd=999999); return
        if intent=="comprar":
            if USUARIOS[uid].get('pais_guardado'): await enviar_unico(m,uid,f"precio_{USUARIOS[uid]['pais_guardado']}",precio_por_pais(USUARIOS[uid]['pais_guardado']),cd=999999,parse_mode='HTML',disable_web_page_preview=False); return
            await m.reply_text(PREGUNTA_PAIS); ESPERA_PAIS[uid]=True; return
        if intent=="otro": await enviar_unico(m,uid,"vivo","Aquí estoy mor 🙈 dime si quieres los gratis o precios? 👀",cd=999999); return

def main():
    app=Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start",start_cmd))
    app.add_handler(CallbackQueryHandler(btn))
    app.add_handler(MessageHandler(filters.UpdateType.BUSINESS_MESSAGE,handle_all))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND,handle_all))
    app.add_handler(MessageHandler(filters.PHOTO | filters.VIDEO,handle_all))
    print("SIN SPAM - NO REPITE - ACTIVO")
    app.run_polling(allowed_updates=Update.ALL_TYPES)
if __name__=='__main__': main()
