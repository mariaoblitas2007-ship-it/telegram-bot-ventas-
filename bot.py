import os, json, logging, unicodedata, asyncio, re
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from telegram.ext import Application, CallbackQueryHandler, CommandHandler, ChatMemberHandler, TypeHandler

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = '8762577283:AAFVT7_WMpZ7njVnToIlZypUpCToF5LGcbA'
ADMIN_ID = 8783569348
LINK_CANAL = "https://t.me/+zt1RzGevdHBjMDgx"
LINK_PAYPAL = "https://www.paypal.com/qrcodes/p2pqrc/76RWY9FF7Q7RE"

USUARIOS = {}; PAGARON = set(); REFERIDOS = {}; INVITADOS = {}; DATA_FILE = "data.json"

def cargar_datos():
    global USUARIOS, PAGARON, REFERIDOS, INVITADOS
    if os.path.exists(DATA_FILE):
        d = json.load(open(DATA_FILE))
        USUARIOS = {int(k):v for k,v in d.get('usuarios',{}).items()}
        PAGARON = set(d.get('pagaron',[]))
        REFERIDOS = {int(k):v for k,v in d.get('referidos',{}).items()}
        INVITADOS = {int(k):v for k,v in d.get('invitados',{}).items()}
def guardar_datos():
    json.dump({'usuarios':USUARIOS,'pagaron':list(PAGARON),'referidos':REFERIDOS,'invitados':INVITADOS}, open(DATA_FILE,'w'))

MX_PRECIOS = """🛍 VIDEOS 🛒

🎂 BÁSICO: $ 100 MXN
→ 5 vds | $20 c/u

🔥 TOP: $200 MXN ← MÁS VENDIDO
→ 12 vds | $16 c/u
→ Ahorras 50%

🏆 PREMIUM: $400 MXN
→ 1 personalizado + 20 vds
→ incluye sexting 🥰
→ Ahorras 80%

📼 VIDEOLLAMADAS 📼
$400 MXN: 5 min
$600 MXN: 10 min

🛍 PAGO MXN:
🏦 Banco: STP
🔢 CLABE:
646180546711450910
📝 Referencia/Concepto: yanae

🇲🇽 También acepto: Transfer / Astropay
→ Pídeme datos si usas otro método

Mándame captura cuando pagues bebé 🥰
En cuanto caiga te mando tu pack 🔥

1. Pagas 2. Captura

Si no contesto envías cap del pago a : @YanaBiBot con estos precios."""

PE_PRECIOS = """🛍 VIDEOS 🛒

🎂 BÁSICO: S/ 15
→ 5 vds | S/ 3 c/u

🔥 TOP: S/ 30 ← MÁS VENDIDO
→ 12 vds | S/ 2.50 c/u
→ Ahorras 50%

🏆 PREMIUM: S/ 60
→ 1 personalizado + 20 vds
→ incluye sexting 🥰
→ Ahorras 67%

📼 VIDEOLLAMADAS 📼
S/ 60: 5 min
S/ 80: 10 min

━━━━━━━━━━━━━━━━━━━━

923553612

YAPE/PLIN

CUENTO CON REFERENCIAS

1. Yapeas 2. Captura

Si no contesto envías cap del pago a : @YanaBiBot con estos precios."""

USA_PRECIOS = f"""🛍 VIDEOS 🛒

🎂 BÁSICO: $5 USD
→ 5 vds | $1 c/u

🔥 TOP: $9 USD ← MÁS VENDIDO
→ 12 vds | $0.75 c/u
→ Ahorras 50%

🏆 PREMIUM: $20 USD
→ 1 personalizado + 20 vds
→ incluye sexting 🥰
→ Ahorras 60%

📼 VIDEOLLAMADAS 📼
$20 USD: 5min
$35 USD: 10min

🪙 PAGO:
PayPal:
AbigailMaximoofO
/ USDT
Link: {LINK_PAYPAL}

Avísame cuando envíes con el comprobante 🥰
En cuanto caiga te mando tu pack 🔥

1. Pagas 2. Captura

Si no contesto envías cap del pago a : @YanaBiBot con estos precios."""

GRATIS_TEXTO = """(REGALITO)
✨ QUIERES HASTA 20 VIDEITOS GRATSS? ✨

https://t.me/YanaBiBot

Pasitos súper fáciles uwu:
1️⃣ En tu bio de TikTok pon: Tg: yanabicitasa ✨
2️⃣ Sube una fotito de las que te envié a tu story + Frase hot 😋
3️⃣ Mándame captura + videito cuando cumplas
4️⃣ Me confirmas cuando llegue a 100 vistas(story) :3
5️⃣ Disfruta de hasta 20 videitos :3 ❤️‍🔥

¿Te animas o ño? 🥺
(Me avisas diciendo: ya cumpli con las 100 vistas )
(Revisa mi perfil)"""

TEXTO_100_VISTAS = """Las 100 vistas son solo para que veas lo fácil que es, mor :3 💕

Cuando tu story llegue a 500-1000 me avisas y te suelto tus videitos al toque 🥵

Mándame videito entrando a TikTok → tu perfil → tu story → los likes, TODO seguido sin cortar. Si lo cortas se anula la promo, bebé 😘"""

def get_menu():
    return InlineKeyboardMarkup([[InlineKeyboardButton("💎 COMPRAR",callback_data='comprar')],[InlineKeyboardButton("🎁 GRATIS",callback_data='gratis')],[InlineKeyboardButton("🔗 MI LINK",callback_data='milink')],[InlineKeyboardButton("📊 RANKING",callback_data='ranking')],[InlineKeyboardButton("🔥 Canal",url=LINK_CANAL)]])
def get_precios():
    return InlineKeyboardMarkup([[InlineKeyboardButton("🇵🇪 Perú",callback_data='pe')],[InlineKeyboardButton("🇲🇽 México",callback_data='mx')],[InlineKeyboardButton("🇺🇸 EEUU",callback_data='usa')]])
def normalizar(t): return unicodedata.normalize('NFKD',t or '').encode('ascii','ignore').decode().lower()
def precio_por_pais(p): return PE_PRECIOS if p=='pe' else MX_PRECIOS if p=='mx' else USA_PRECIOS
def detectar_pais(t):
    t=normalizar(t)
    if any(x in t for x in ['peru']): return 'pe'
    if any(x in t for x in ['mex','mexico']): return 'mx'
    if any(x in t for x in ['usa','eeuu','estados unidos','united','colombia','argentina','chile','ecuador','venezuela','bolivia','espana','america']): return 'usa'
    return None
def es_hot(txt):
    kws = ['precio','precios','cuanto','cuesta','costo','pack','video','videos','videito','videitos','foto','fotos','desnuda','coger','cogiendo','masturbar','tetas','culito','quiero','manda','comprar','cuanto cobras']
    return any(k in txt for k in kws)
def es_100_vistas(txt):
    return ('100' in txt and 'vista' in txt) or ('cumpli' in txt and '100' in txt) or 'ya cumpli con las 100 vistas' in txt
def es_pago(txt):
    patrones=['yape','plin','ya te pague','te yapee','yapee','ya te transferi','transferi','deposite','comprobante','pago realizado','ya quedo','te pague']
    return any(p in txt for p in patrones)

async def notificar_admin(tipo, uid, user, extra=""):
    username = f"@{user}" if user else "sin @"
    url = f"https://t.me/{user}" if user else f"tg://user?id={uid}"
    caption = f"{tipo}\n👤 {username}\n🆔 <code>{uid}</code>\n{extra}"
    kb = InlineKeyboardMarkup([[InlineKeyboardButton("🔗 ABRIR CHAT", url=url)]])
    try: await app_bot.send_message(ADMIN_ID, caption, reply_markup=kb, parse_mode='HTML')
    except: await app_bot.send_message(ADMIN_ID, caption, parse_mode='HTML')

async def analizar_foto(ctx, uid, user, fid):
    try:
        url = f"https://t.me/{user}" if user else f"tg://user?id={uid}"
        kb = InlineKeyboardMarkup([[InlineKeyboardButton("🔗 ABRIR CHAT", url=url)]])
        await ctx.bot.send_photo(ADMIN_ID, fid, caption=f"FOTO RECIBIDA\n🆔 <code>{uid}</code>", reply_markup=kb, parse_mode='HTML')
    except Exception as e: logger.error(e)
async def analizar_video(ctx, uid, user, fid):
    try:
        url = f"https://t.me/{user}" if user else f"tg://user?id={uid}"
        kb = InlineKeyboardMarkup([[InlineKeyboardButton("🔗 ABRIR CHAT", url=url)]])
        await ctx.bot.send_video(ADMIN_ID, fid, caption=f"VIDEO RECIBIDO\n🆔 <code>{uid}</code>", reply_markup=kb, parse_mode='HTML')
    except Exception as e: logger.error(e)

async def enviar_bienvenida(m):
    try:
        await m.reply_media_group([
            InputMediaPhoto(open('fotitos1.JPG','rb')),
            InputMediaPhoto(open('fotitos2.JPG','rb')),
            InputMediaPhoto(open('fotitos3.JPG','rb')),
            InputMediaPhoto(open('fotitos4.JPG','rb')),
            InputMediaPhoto(open('fotitos5.JPG','rb'))
        ])
    except: pass
    await m.reply_text(GRATIS_TEXTO)
    await m.reply_text(f"🔥 Mi canal privado aquí mor 👇\n{LINK_CANAL}")

async def enviar_gratis(m):
    try:
        await m.reply_media_group([
            InputMediaPhoto(open('fotitos1.JPG','rb')),
            InputMediaPhoto(open('fotitos2.JPG','rb')),
            InputMediaPhoto(open('fotitos3.JPG','rb')),
            InputMediaPhoto(open('fotitos4.JPG','rb')),
            InputMediaPhoto(open('fotitos5.JPG','rb'))
        ])
    except: pass
    await m.reply_text(GRATIS_TEXTO)

async def start_cmd(upd, ctx): await upd.message.reply_text("Hola mor 🥵 bienvenido, elige:", reply_markup=get_menu())

async def recordar(context):
    uid=context.job.data['uid']; chat_id=context.job.data['chat_id']
    bc_id=context.job.data.get('business_connection_id')
    if uid in PAGARON or USUARIOS.get(uid,{}).get('respondio'): return
    try:
        if bc_id:
            await context.bot.send_message(chat_id, "sigues ahí? 🥹", business_connection_id=bc_id)
            await asyncio.sleep(1.5)
            await context.bot.send_message(chat_id, "Mor si mandas el PREMIUM hoy te doy el DOBLE de contenido 😍 20 vds extra + 2 personalizados solo por hoy, ¿te lo aparto?", business_connection_id=bc_id)
        else:
            await context.bot.send_message(chat_id, "sigues ahí? 🥹")
        USUARIOS[uid]['atendido']=True; guardar_datos()
    except: pass

async def todo(upd, ctx):
    global app_bot; app_bot=ctx.bot
    m=upd.message or upd.business_message
    if not m or m.from_user.is_bot: return
    uid=m.from_user.id
    if uid not in USUARIOS: USUARIOS[uid]={}
    USUARIOS[uid]['n']=m.from_user.first_name; USUARIOS[uid]['respondio']=True; guardar_datos()
    es_neg=upd.business_message is not None
    txt=normalizar(m.text); raw=m.text or ""
    def tiene(l): return any(p in txt for p in l)
    PROMO=['promo','promocion','free']; ENCUENTRO=['encuentro','cita','en persona','vernos']
    bc_id = getattr(m, 'business_connection_id', None)

    if es_neg:
        if uid==ADMIN_ID: return
        if uid in PAGARON:
            if m.photo: await analizar_foto(ctx,uid,m.from_user.username or '',m.photo[-1].file_id)
            if m.video: await analizar_video(ctx,uid,m.from_user.username or '',m.video.file_id)
            return

        if m.photo:
            await analizar_foto(ctx,uid,m.from_user.username or '',m.photo[-1].file_id)
            USUARIOS[uid]['atendido']=True; guardar_datos(); return
        if m.video:
            await analizar_video(ctx,uid,m.from_user.username or '',m.video.file_id)
            USUARIOS[uid]['atendido']=True; guardar_datos(); return

        if es_100_vistas(txt):
            await m.reply_text(TEXTO_100_VISTAS)
            USUARIOS[uid]['atendido']=True; guardar_datos(); return

        if es_pago(txt):
            await notificar_admin("💰 PAGO", uid, m.from_user.username, f"💬 {raw[:80]}")
            PAGARON.add(uid); USUARIOS[uid]['atendido']=True; guardar_datos(); return

        if tiene(ENCUENTRO): await m.reply_text("Los encuentros son SOLO con PREMIUM mor 😏 incluye videollamada + personalizado. ¿Te paso el PREMIUM?"); return
        if tiene(PROMO): await enviar_gratis(m); return
        if 'sexting' in txt: await m.reply_text("Sexting va en el PREMIUM mor 🥵 ¿lo quieres?"); return

        # Detecta pais si lo dice voluntariamente
        pais = detectar_pais(txt)
        if pais:
            USUARIOS[uid]['pais']=pais
            await m.reply_text(precio_por_pais(pais))
            USUARIOS[uid]['atendido']=True; USUARIOS[uid]['respondio']=False; guardar_datos()
            ctx.job_queue.run_once(recordar, 300, data={'uid':uid,'chat_id':m.chat.id,'business_connection_id':bc_id}, name=f"rec_{uid}")
            return

        # Solo si muestra interés en comprar
        if es_hot(txt):
            pais_def = USUARIOS[uid].get('pais') or 'usa'
            await m.reply_text(precio_por_pais(pais_def))
            USUARIOS[uid]['atendido']=True; USUARIOS[uid]['respondio']=False; guardar_datos()
            ctx.job_queue.run_once(recordar, 300, data={'uid':uid,'chat_id':m.chat.id,'business_connection_id':bc_id}, name=f"rec_{uid}")
            return

        if USUARIOS[uid].get('atendido'): return

        if not USUARIOS[uid].get('saludo_enviado'):
            await enviar_bienvenida(m)
            USUARIOS[uid]['saludo_enviado']=True; USUARIOS[uid]['canal']=True; guardar_datos()
            return
        return

    if m.chat.type=='private': await m.reply_text("Elige:", reply_markup=get_menu())

async def btn(upd, ctx):
    q=upd.callback_query; await q.answer()
    if q.data=='comprar': await q.edit_message_text("Elige tu país:", reply_markup=get_precios())
    elif q.data=='pe': await q.edit_message_text(PE_PRECIOS)
    elif q.data=='mx': await q.edit_message_text(MX_PRECIOS)
    elif q.data=='usa': await q.edit_message_text(USA_PRECIOS)
    elif q.data=='gratis': await q.edit_message_text(GRATIS_TEXTO)
    elif q.data=='milink':
        link=f"https://t.me/YanaBiBot?start={q.from_user.id}"; REFERIDOS[q.from_user.id]={'link':link}; guardar_datos(); await q.edit_message_text(f"Tu link:\n{link}")
    elif q.data=='ranking':
        top=sorted(INVITADOS.items(), key=lambda x:x[1], reverse=True)[:5]
        await q.edit_message_text("TOP:\n"+"\n".join([f"{i+1}. {USUARIOS.get(u,{}).get('n','?')} - {c}" for i,(u,c) in enumerate(top)]))

async def nuevo(upd, ctx):
    cm=upd.chat_member
    if cm.old_chat_member.status in ['left','kicked'] and cm.new_chat_member.status=='member':
        if not cm.new_chat_member.user.is_bot: INVITADOS[cm.from_user.id]=INVITADOS.get(cm.from_user.id,0)+1; guardar_datos()

def main():
    cargar_datos()
    app=Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start_cmd))
    app.add_handler(TypeHandler(Update, todo))
    app.add_handler(CallbackQueryHandler(btn))
    app.add_handler(ChatMemberHandler(nuevo, ChatMemberHandler.CHAT_MEMBER))
    app.run_polling(allowed_updates=['message','business_message','callback_query','chat_member'])

if __name__=='__main__': main()
