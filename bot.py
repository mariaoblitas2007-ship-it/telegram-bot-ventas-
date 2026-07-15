# FINAL - PRECIOS EXTENDIDOS CON VIDEOLLAMADAS + NEGOCIO SIN BOTONES + BOT CON BOTONES + 5 FOTOS + LINK APARTE
import time, unicodedata, re
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto, Update
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, MessageHandler, filters

TOKEN = '8762577283:AAFVT7_WMpZ7njVnToIlZypUpCToF5LGcbA'
ADMIN_ID = 8783569348
USUARIOS = {}; ESPERA_PAIS = {}

CANAL_LINK = "https://telegram.me/+lG8bEHr5J2QxMjhh"

GRATIS_TEXTO = """✨ QUIERES HASTA 20 VIDEITOS GRATSS? ✨

Pasitos súper fáciles uwu:
1️⃣ En tu bio de TikTok pon: Tg: yanabicitasa ✨
2️⃣ Sube una fotito de las que te envié a tu story 😋
3️⃣ Mándame captura + videito cuando cumplas con la promo
4️⃣ Me confirmas cuando llegue a 100 vistas(story) :3
5️⃣ Disfruta de hasta 20 videitos :3 ❤️‍🔥

¿Te animas o ño? 🥺
(Me avisas diciendo: ya cumpli con las 100 vistas )"""

GRATIS_RECORDATORIO = "ya te mande como conseguir mis videitos gratis mor 🥺💦"
PREGUNTA_PAIS = "De dónde eres Mor? 🥺"
OCUPADITA_MSG = "ando ocupadita en videollamada 👀 en un ratito te confirmo mor 🥰"

# ========= PRECIOS EXTENDIDOS CON VIDEOLLAMADAS =========
MX_PRECIOS = """🛍 <b>VIDEOS EXTENDIDOS</b> 🛒

🎂 <b>BÁSICO: $100 MXN</b> → 5 videitos | $20 c/u
━━━━━━━━━━━━━━
🔥 <b>TOP: $200 MXN ← MÁS VENDIDO</b> → 12 videitos | $16 c/u
━━━━━━━━━━━━━━
🏆 <b>PREMIUM: $400 MXN</b> → 20 videitos + 1 perso + sexting + sorpresita
━━━━━━━━━━━━━━
📼 <b>VIDEOLLAMADAS CALIENTES</b>
• 5 min - $400 MXN
• 10 min - $600 MXN
• Incluye dedito y juguetitos 😝
━━━━━━━━━━━━━━
<b>PAGO MX:</b>
CLABE: <code>646180546711450910</code>
Concepto: <code>yanae</code>"""

PE_PRECIOS = """🛍 <b>VIDEOS EXTENDIDOS</b> 🛒

🎂 <b>BÁSICO: S/ 15</b> → 5 videitos | S/ 3 c/u
━━━━━━━━━━━━━━
🔥 <b>TOP: S/ 30 ← MÁS VENDIDO</b> → 12 videitos | S/ 2.5 c/u
━━━━━━━━━━━━━━
🏆 <b>PREMIUM: S/ 60</b> → 20 videitos + 1 perso + sexting + sorpresita
━━━━━━━━━━━━━━
📼 <b>VIDEOLLAMADAS CALIENTES</b>
• 5 min - S/ 60
• 10 min - S/ 80
• Incluye dedito y juguetitos 😝
━━━━━━━━━━━━━━
<b>PAGO PE:</b>
<b>YAPE / PLIN:</b> <code>923553612</code>
A nombre de Yana"""

USA_PRECIOS = """🛍 <b>VIDEOS EXTENDIDOS</b> 🛒 🌍

🎂 <b>BÁSICO: $5 USD</b> → 5 videitos | $1 c/u
━━━━━━━━━━━━━━
🔥 <b>TOP: $9 USD ← MÁS VENDIDO</b> → 12 videitos | $0.75 c/u
━━━━━━━━━━━━━━
🏆 <b>PREMIUM: $20 USD</b> → 20 videitos + 1 perso + sexting + sorpresita
━━━━━━━━━━━━━━
📼 <b>VIDEOLLAMADAS CALIENTES</b>
• 5 min - $20 USD
• 10 min - $35 USD
• Incluye dedito y juguetitos 😝
━━━━━━━━━━━━━━
<b>PAGO MUNDIAL 🌍:</b>
🔗 <a href="https://www.paypal.com/qrcodes/p2pqrc/76RWY9FF7Q7RE">PayPal - Pagar aquí</a>"""

def normalizar(t):
    if not t: return ""
    t=unicodedata.normalize('NFKD',t).encode('ascii','ignore').decode().lower()
    return re.sub(r'[^\w\s]',' ',t)
def detectar_pais(t):
    t=normalizar(t)
    mx=['mexico','mx','cdmx','jalisco','guadalajara','monterrey','nuevo leon','puebla','cancun','veracruz','yucatan','tijuana','merida','queretaro']
    pe=['peru','pe','lima','arequipa','trujillo','chiclayo','lambayeque','piura','cusco','ica','tacna','puno','cajamarca','huancayo','iquitos']
    if any(x in t for x in mx): return 'mx'
    if any(x in t for x in pe): return 'pe'
    if len(t.strip())>=2: return 'usa'
    return None
def detectar_intencion(txt,cap=""):
    t=normalizar(f"{txt} {cap}")
    if any(x in t for x in ['videos gratis','gratis','promo','20 videitos']): return "promo"
    if any(x in t for x in ['yape','plin','pago','comprobante','paypal','clabe','transfer']): return "pago"
    if "100" in t or "ya cumpli" in t: return "vistas100"
    if any(x in t for x in ['precio','precios','pasame tus precios','pasa precios','cuanto cuesta','cuanto valen','pack','contenido']): return "comprar"
    return "otro"

def puede_enviar(uid,tipo,cd):
    ahora=time.time(); USUARIOS.setdefault(uid,{}).setdefault('antispam',{})
    if not isinstance(USUARIOS[uid]['antispam'],dict): USUARIOS[uid]['antispam']={}
    if ahora-USUARIOS[uid]['antispam'].get(tipo,0) < cd: return False
    USUARIOS[uid]['antispam'] = ahora
    return True
async def enviar_unico(m,uid,tipo,texto,**kw):
    USUARIOS[uid].setdefault('historial',[])
    if texto in USUARIOS[uid]['historial']: return False
    if not puede_enviar(uid,tipo,kw.pop('cd',999999)): return False
    await m.reply_text(texto,**kw); USUARIOS[uid]['historial'].append(texto); USUARIOS[uid]['historial']=USUARIOS[uid]['historial'][-20:]; return True

def link_cliente(uid,un): return f"https://t.me/{un}" if un!="None" else f"tg://user?id={uid}"
def get_menu(): return InlineKeyboardMarkup([[InlineKeyboardButton("💎 COMPRAR",callback_data='comprar')],[InlineKeyboardButton("🎁 GRATIS",callback_data='gratis')]])
def get_precios(): return InlineKeyboardMarkup([[InlineKeyboardButton("🇵🇪 Perú",callback_data='pe')],[InlineKeyboardButton("🇲🇽 México",callback_data='mx')],[InlineKeyboardButton("🌍 Otros",callback_data='usa')]])
def get_volver(): return InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Volver",callback_data='volver')]])
def precio_por_pais(p): return PE_PRECIOS if p=='pe' else MX_PRECIOS if p=='mx' else USA_PRECIOS

async def enviar_5_fotos(m):
    try: await m.reply_media_group([InputMediaPhoto(open(f'fotitos{i}.JPG','rb')) for i in range(1,6)])
    except:
        try: await m.reply_media_group([InputMediaPhoto(open(f'fotitos{i}.jpg','rb')) for i in range(1,6)])
        except: pass

async def enviar_gratis_completo(m, con_botones=False):
    await enviar_5_fotos(m)
    if con_botones: await m.reply_text(GRATIS_TEXTO, reply_markup=get_menu())
    else: await m.reply_text(GRATIS_TEXTO)
    await m.reply_text(CANAL_LINK, disable_web_page_preview=False)

async def start_cmd(u,c):
    uid=u.effective_user.id; USUARIOS.setdefault(uid,{}).setdefault('flags',{})['gratis_enviado']=True
    await enviar_gratis_completo(u.message, True)
async def btn(u,c):
    q=u.callback_query; await q.answer(); d=q.data; uid=q.from_user.id
    if d=='volver': await q.edit_message_text("¿Qué quieres mor? :3",reply_markup=get_menu()); return
    if d=='comprar':
        if USUARIOS.get(uid,{}).get('pais_guardado'): await q.edit_message_text(precio_por_pais(USUARIOS[uid]['pais_guardado']),parse_mode='HTML',disable_web_page_preview=False,reply_markup=get_volver()); return
        await q.edit_message_text("De dónde eres Mor? 👀✨",reply_markup=get_precios()); return
    if d in ['pe','mx','usa']:
        USUARIOS.setdefault(uid,{})['pais_guardado']=d; await q.edit_message_text(precio_por_pais(d),parse_mode='HTML',disable_web_page_preview=False,reply_markup=get_volver())
        await q.message.reply_text("Si pagas ahora mismo mor te mando extras bien ricos 😝🔥",reply_markup=get_volver()); return
    if d=='gratis':
        if not USUARIOS.get(uid,{}).get('flags',{}).get('gratis_enviado'): await enviar_gratis_completo(q.message, True); USUARIOS.setdefault(uid,{}).setdefault('flags',{})['gratis_enviado']=True
        else: await enviar_unico(q.message,uid,"gratis_recordatorio",GRATIS_RECORDATORIO,cd=999999,reply_markup=get_volver())

async def handle_all(update,context):
    m=update.business_message or update.message
    if not m or not m.from_user or m.from_user.is_bot: return
    uid=m.from_user.id; raw=(m.text or "").strip(); cap=getattr(m,'caption','') or ""; un=m.from_user.username or "None"
    es_negocio=update.business_message is not None
    if es_negocio and uid==ADMIN_ID: return
    USUARIOS.setdefault(uid,{}).setdefault('flags',{})
    if time.time()-USUARIOS[uid].get('ultimo',0) < 0.6: return
    USUARIOS[uid]['ultimo']=time.time(); intent=detectar_intencion(raw,cap); link_cli=link_cliente(uid,un)

    if m.sticker: await context.bot.send_sticker(ADMIN_ID,m.sticker.file_id); await context.bot.send_message(ADMIN_ID,f"🎭 STICKER\n👤 @{un} | {uid}\n🔗 {link_cli}"); return
    if m.photo or m.video:
        fid=m.video.file_id if m.video else m.photo[-1].file_id; cn=normalizar(cap+" "+raw)
        razon="📈 PRUEBA VISTAS" if any(x in cn for x in ['100','ya cumpli']) else "💸 PAGO" if any(x in cn for x in ['yape','plin','pago']) else "📷 FOTO/VIDEO"
        caption=f"{razon}\n👤 @{un} | {uid}\n🔗 {link_cli}"; kb=InlineKeyboardMarkup([[InlineKeyboardButton("🔗 Abrir chat",url=link_cli)]])
        if m.video: await context.bot.send_video(ADMIN_ID,fid,caption=caption,reply_markup=kb)
        else: await context.bot.send_photo(ADMIN_ID,fid,caption=caption,reply_markup=kb)
        if "PAGO" in razon: await enviar_unico(m,uid,"ocupadita",OCUPADITA_MSG,cd=60)
        return

    if es_negocio:
        if uid in ESPERA_PAIS:
            pais = detectar_pais(raw) or 'usa'
            USUARIOS[uid]['pais_guardado']=pais
            await m.reply_text(precio_por_pais(pais), parse_mode='HTML', disable_web_page_preview=False)
            del ESPERA_PAIS[uid]; return
        if not USUARIOS[uid]['flags'].get('gratis_enviado'):
            if intent=="comprar":
                pais_directo = detectar_pais(raw)
                if pais_directo in ['mx','pe','usa']:
                    USUARIOS[uid]['flags']['gratis_enviado']=True; USUARIOS[uid]['pais_guardado']=pais_directo
                    await m.reply_text(precio_por_pais(pais_directo), parse_mode='HTML', disable_web_page_preview=False); return
                USUARIOS[uid]['flags']['gratis_enviado']=True; await m.reply_text(PREGUNTA_PAIS); ESPERA_PAIS[uid]=True; return
            await enviar_gratis_completo(m, False); USUARIOS[uid]['flags']['gratis_enviado']=True; return
        if intent=="comprar":
            pais_directo = detectar_pais(raw)
            if pais_directo in ['mx','pe']:
                USUARIOS[uid]['pais_guardado']=pais_directo; await enviar_unico(m,uid,f"precio_{pais_directo}",precio_por_pais(pais_directo),cd=999999,parse_mode='HTML',disable_web_page_preview=False); return
            if USUARIOS[uid].get('pais_guardado'): await enviar_unico(m,uid,"precio_guardado",precio_por_pais(USUARIOS[uid]['pais_guardado']),cd=999999,parse_mode='HTML',disable_web_page_preview=False); return
            await m.reply_text(PREGUNTA_PAIS); ESPERA_PAIS[uid]=True; return
        if intent=="pago": await context.bot.send_message(ADMIN_ID,f"💸 PAGO\n👤 @{un} | {uid}\n🔗 {link_cli}"); await enviar_unico(m,uid,"pago",OCUPADITA_MSG,cd=60); return
        if intent in ["promo","vistas100"]: await enviar_unico(m,uid,"gratis_recordatorio",GRATIS_RECORDATORIO,cd=999999); return
        return
    else:
        if not USUARIOS[uid]['flags'].get('gratis_enviado'):
            if intent=="comprar": USUARIOS[uid]['flags']['gratis_enviado']=True; await m.reply_text("De dónde eres Mor? 👀✨", reply_markup=get_precios()); return
            await enviar_gratis_completo(m, True); USUARIOS[uid]['flags']['gratis_enviado']=True; return
        if intent=="comprar":
            if USUARIOS[uid].get('pais_guardado'): await m.reply_text(precio_por_pais(USUARIOS[uid]['pais_guardado']),parse_mode='HTML',reply_markup=get_volver()); return
            await m.reply_text("De dónde eres Mor? 👀✨", reply_markup=get_precios()); return

def main():
    app=Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start",start_cmd)); app.add_handler(CallbackQueryHandler(btn))
    app.add_handler(MessageHandler(filters.UpdateType.BUSINESS_MESSAGE,handle_all))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND,handle_all))
    app.add_handler(MessageHandler(filters.PHOTO | filters.VIDEO | filters.Sticker.ALL,handle_all))
    print("Extendidos + videollamadas activo")
    app.run_polling(allowed_updates=Update.ALL_TYPES)
if __name__=='__main__': main()
