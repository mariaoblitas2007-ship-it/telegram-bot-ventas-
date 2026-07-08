import os, sys, asyncio, random, logging, unicodedata, signal, re, json
from datetime import datetime, timedelta, time
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, MessageHandler, CallbackQueryHandler, CommandHandler, filters, ContextTypes, ChatMemberHandler
from telegram.error import Forbidden, Conflict

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

TOKEN = '8762577283:AAFVT7_WMpZ7njVnToIlZypUpCToF5LGcbA'
ADMIN_ID = 8783569348
USERNAME_ADMIN = "@yanabicitasa"
CANAL_ID = -1004327627898

LINK_CANAL = "https://t.me/+zt1RzGevdHBjMDgx"
LINK_PAYPAL = "https://www.paypal.com/qrcodes/p2pqrc/76RWY9FF7Q7RE"

VIP_TEMPORAL, DEMO_USADO, USUARIOS, PAGARON = {}, set(), {}, set()
ULTIMO_MENSAJE, FOLLOWUP_ENVIADO = {}, set()
REFERIDOS, INVITACIONES, INVITADOS = {}, {}, {}
VENTAS_ESTRELLAS = []
ESPERA_PAIS = {}

FOTOS_GRATIS = ["fotitos1.JPG","fotitos2.JPG","fotitos3.JPG","fotitos4.JPG","fotitos5.JPG","fotitos6.JPG"]

DATA_FILE = "data.json"

def cargar_datos():
    global REFERIDOS, PAGARON, USUARIOS, INVITADOS, INVITACIONES, VENTAS_ESTRELLAS
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                d = json.load(f)
                REFERIDOS = {int(k): v for k,v in d.get('referidos', {}).items()}
                PAGARON = set(d.get('pagaron', []))
                USUARIOS = {int(k): v for k,v in d.get('usuarios', {}).items()}
                INVITADOS = {int(k): v for k,v in d.get('invitados', {}).items()}
                INVITACIONES = {v['link']: int(k) for k,v in REFERIDOS.items() if 'link' in v}
                VENTAS_ESTRELLAS = d.get('ventas_estrellas', [])
        except Exception as e:
            logger.error(f"Error cargando: {e}")

def guardar_datos():
    try:
        with open(DATA_FILE, 'w', encoding='utf-8') as f:
            json.dump({
                'referidos': REFERIDOS,
                'pagaron': list(PAGARON),
                'usuarios': USUARIOS,
                'invitados': INVITADOS,
                'ventas_estrellas': VENTAS_ESTRELLAS
            }, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"Error guardando: {e}")

PE_PRECIOS = """
🛍 VIDEOS 🛒

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

💳 PAGO: YAPE/PLIN: 923553612
CUENTO CON REFERENCIAS

Mándame captura cuando pagues bebé 🥰
En cuanto caiga te mando tu pack 🔥

1. Yapeas 2. Captura

Si no contesto envías cap del pago a : @YanaBiBot
"""

MX_PRECIOS = """
🛍 VIDEOS 🛒

🎂 BÁSICO: $100 MXN
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

Si no contesto envías cap del pago a : @YanaBiBot con estos precios.
"""

USA_PRECIOS = """
🛍 VIDEOS 🛒

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

Avísame cuando envíes con el comprobante 🥰
En cuanto caiga te mando tu pack 🔥

1. Pagas 2. Captura

Si no contesto envías cap del pago a : @YanaBiBot con estos precios.
"""

OTRO_PRECIOS = USA_PRECIOS

TEXTO_GRATIS = """📸 GRATIS 🥺💋

✨ QUIERES HASTA 20 VIDEITOS GRATIS? ✨
Es por promocionarme en TikTok ✅

Pasitos súper fáciles uwu:
1️⃣ Ponte un nombrecito + fotito tierna <33
2️⃣ En tu bio pon: Tg: yanabicitasa ✨
3️⃣ Sube una fotito a tu story + frasita hot 😋
4️⃣ Comenta coshitas en videos hot, unos 30-100 👀
   Así generamos vistas juntos
5️⃣ Mándame captura + videito cuando termines
6️⃣ Disfruta de hasta 20 videitos :3 ❤️‍🔥

¿Te animas o ño? 🥺
(Me avisas cuando cumplas mi rey)"""

TEXTO_NIVELES = """🔥 VIDEOS GRATIS #HORMO - SÚBEME LA TEMP 🔥

¿Sin plata bebé? 😏 Trabaja por mí y te mojo...

🥉 NIVEL TIBIO - 5 MIEMBROS:
1 videito pa que me pruebes 🥵

🔥 NIVEL CALIENTE - 20 MIEMBROS:
2-3 videitos... ya me pones nerviosa 😈

😈 NIVEL ARDIENDO - 50 MIEMBROS:
4-10 videitos 🥵 Te voy a dejar sin aire

🥵 NIVEL INFIERNO - 100 MIEMBROS:
10-20 videitos 🔥 Ya soy toda tuya

👑 NIVEL DIABLA - 200 MIEMBROS:
+20 videitos + VIDEO FETICHE solo para ti 😈🍑
Aquí me entrego completa...

¿Caliente y con prisa? Toca "💎 COMPRAR" y te atiendo YA 🔥

Saca tu link en "🔗 MI LINK" y ponte a reclutar #HORMOS 😏"""

PREMIOS_REFERIDOS = {5:"1 videito pa calentar 🥵",20:"2-3 videitos... ya me mojo 🔥",50:"4-10 videitos 😈 te dejo sin aire",100:"10-20 videitos 🥵 ya soy tuya",200:"+20 videitos + VIDEO FETICHE 👑🍑"}

def get_menu(): return InlineKeyboardMarkup([[InlineKeyboardButton("💎 COMPRAR PACKS", callback_data='comprar')],[InlineKeyboardButton("🎁 GRATIS - Misiones", callback_data='gratis')],[InlineKeyboardButton("🔗 MI LINK - Referidos", callback_data='milink')],[InlineKeyboardButton("📊 RANKING", callback_data='ranking')],[InlineKeyboardButton("🔥 Canal Oficial", url=LINK_CANAL)]])
def get_precios_menu(): return InlineKeyboardMarkup([[InlineKeyboardButton("🇵🇪 Perú", callback_data='pe')],[InlineKeyboardButton("🇲🇽 México", callback_data='mx')],[InlineKeyboardButton("🇺🇸 USA/Otros", callback_data='usa')],[InlineKeyboardButton("🌎 Internacional", callback_data='otro')],[InlineKeyboardButton("⬅️ Volver", callback_data='volver')]])
def get_volver(): return InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Volver al Menú", callback_data='volver')]])
def normalizar(t): return unicodedata.normalize('NFKD', t).encode('ascii','ignore').decode('ascii').lower()

def es_trigger_precios(texto):
    if not texto: return False
    t = normalizar(texto)
    return "hola mor" in t and "precio" in t

def registrar_usuario(u):
    USUARIOS[u.id] = {'nombre': u.first_name, 'username': u.username or "sin_username"}
    guardar_datos()

async def avisar_pago(ctx, uid, user, nombre, fid):
    try: await ctx.bot.send_photo(ADMIN_ID, fid, caption=f"💰 PAGO\n👤 @{user}\n🆔 {uid}\n👉 tg://user?id={uid}")
    except: pass

async def detectar_estrellas(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.effective_message
    if not msg or not msg.paid_media_purchased: return
    compra = msg.paid_media_purchased
    user = compra.from_user
    uid = user.id
    estrellas = 0
    post_id = 0
    if msg.reply_to_message:
        post_id = msg.reply_to_message.message_id
        if msg.reply_to_message.paid_media:
            estrellas = msg.reply_to_message.paid_media.star_count
    canal_id_str = str(CANAL_ID).replace("-100", "")
    link_post = f"https://t.me/c/{canal_id_str}/{post_id}"
    venta = {'uid': uid, 'nombre': user.first_name, 'username': user.username or '', 'estrellas': estrellas, 'post': link_post, 'fecha': datetime.now().isoformat(), 'dia': datetime.now().strftime('%Y-%m-%d')}
    VENTAS_ESTRELLAS.append(venta)
    guardar_datos()
    total_persona = sum(v['estrellas'] for v in VENTAS_ESTRELLAS if v['uid'] == uid)
    await context.bot.send_message(ADMIN_ID, f"⭐ {estrellas} ESTRELLAS\n👤 {user.first_name} @{user.username or 'sin_user'}\n👉 PERFIL: tg://user?id={uid}\n🎬 COMPRÓ: {link_post}\n💰 Total de él/ella: {total_persona}⭐", disable_web_page_preview=True)

async def resumen_estrellas(context: ContextTypes.DEFAULT_TYPE):
    hoy = datetime.now().strftime('%Y-%m-%d')
    hoy_ventas = [v for v in VENTAS_ESTRELLAS if v['dia'] == hoy]
    if not hoy_ventas: return
    total = sum(v['estrellas'] for v in hoy_ventas)
    conteo = {}
    for v in hoy_ventas:
        conteo[v['estrellas']] = conteo.get(v['estrellas'], 0) + 1
    top = max(conteo.items(), key=lambda x: x[1])
    texto = f"📊 ESTRELLAS HOY {hoy}\n\n💎 Total: {total}⭐ en {len(hoy_ventas)} ventas\n\n"
    for e, c in sorted(conteo.items(), key=lambda x: -x[1]):
        texto += f"• {e}⭐: {c} veces\n"
    texto += f"\n🥇 MÁS VENDIDO: {top[0]}⭐ ({top[1]} ventas)"
    await context.bot.send_message(ADMIN_ID, texto)

async def follow_up(ctx: ContextTypes.DEFAULT_TYPE):
    uid = ctx.job.data['uid']
    if uid in PAGARON or uid in FOLLOWUP_ENVIADO: return
    FOLLOWUP_ENVIADO.add(uid)
    try: await ctx.bot.send_message(uid, "Oye 😏 ¿sigues ahí? TOP con 2 extras 🎁", reply_markup=get_menu())
    except: pass

async def crear_link_referido(ctx, uid, username):
    try:
        if uid in REFERIDOS: return REFERIDOS[uid]['link']
        inv = await ctx.bot.create_chat_invite_link(CANAL_ID, name=f"ref{uid}", creates_join_request=False)
        REFERIDOS[uid] = {'link': inv.invite_link, 'contador': 0, 'username': f"@{username}"}
        INVITACIONES[inv.invite_link] = uid
        guardar_datos()
        return inv.invite_link
    except Exception as e:
        logger.error(e)
        return None

async def chequear_premio(ctx, uid):
    if uid not in REFERIDOS: return
    c = REFERIDOS[uid]['contador']
    if c in PREMIOS_REFERIDOS:
        try: await ctx.bot.send_message(uid, f"🏆 Meta {c}!\nPremio: {PREMIOS_REFERIDOS[c]}")
        except: pass
        await ctx.bot.send_message(ADMIN_ID, f"Premio {c} para {REFERIDOS[uid]['username']}")

async def enviar_gratis(cid, ctx):
    await ctx.bot.send_message(cid, TEXTO_GRATIS, reply_markup=get_volver())
    await asyncio.sleep(0.5)
    for f in FOTOS_GRATIS:
        try:
            with open(f, 'rb') as ph: await ctx.bot.send_photo(cid, ph)
            await asyncio.sleep(0.4)
        except: continue

async def track_join(upd: Update, ctx: ContextTypes.DEFAULT_TYPE):
    r = upd.chat_member
    if r.new_chat_member.status == "member" and r.invite_link and r.invite_link.invite_link in INVITACIONES:
        ref = INVITACIONES[r.invite_link.invite_link]
        if ref in REFERIDOS:
            REFERIDOS[ref]['contador'] += 1
            INVITADOS[r.new_chat_member.user.id] = ref
            guardar_datos()
            try: await ctx.bot.send_message(ref, f"🔥 +1 | Total: {REFERIDOS[ref]['contador']}/200")
            except: pass
            await chequear_premio(ctx, ref)
    elif r.new_chat_member.status in ["left","kicked"]:
        u = r.new_chat_member.user
        if u.id in INVITADOS:
            ref = INVITADOS[u.id]
            if ref in REFERIDOS and REFERIDOS[ref]['contador']>0:
                REFERIDOS[ref]['contador'] -= 1
            del INVITADOS[u.id]
            guardar_datos()

async def manejar_todo(upd: Update, ctx: ContextTypes.DEFAULT_TYPE):
    m = upd.message or upd.business_message
    if not m or not m.from_user or m.from_user.is_bot: return

    if getattr(m, 'paid_media_purchased', None):
        await detectar_estrellas(upd, ctx)
        return

    uid = m.from_user.id
    registrar_usuario(m.from_user)
    name = m.from_user.first_name
    user = m.from_user.username or "x"

    es_negocio = upd.business_message is not None

    # ===== 1. CHAT DE NEGOCIO (@yanabicitasa) =====
    if es_negocio:
        # IGNORA TUS PROPIOS MENSAJES - AQUÍ ESTABA EL BUG
        if uid == ADMIN_ID: return

        if m.text and es_trigger_precios(m.text):
            ESPERA_PAIS[uid] = True
            await m.reply_text("hola mi amor 🫣🔥\n¿de dónde eres tú, bebé? 🥺💋")
            return
        if uid in ESPERA_PAIS and m.text:
            txt = normalizar(m.text)
            if any(k in txt for k in ['peru','pe','lima']): await m.reply_text(PE_PRECIOS)
            elif any(k in txt for k in ['mexico','mx']): await m.reply_text(MX_PRECIOS)
            elif any(k in txt for k in ['eeuu','usa']): await m.reply_text(USA_PRECIOS)
            else: await m.reply_text(OTRO_PRECIOS)
            del ESPERA_PAIS[uid]
            return
        if m.photo:
            PAGARON.add(uid); guardar_datos()
            await avisar_pago(ctx, uid, user, name, m.photo[-1].file_id)
            await m.reply_text(f"✅ Pago recibido. Escríbeme {USERNAME_ADMIN}")
            return
        return # IGNORA TODO LO DEMÁS EN NEGOCIO

    # ===== 2. CHAT DIRECTO CON @YanaBiBot =====
    if m.chat.type == 'private':
        if m.text and es_trigger_precios(m.text):
            ESPERA_PAIS[uid] = True
            await m.reply_text("hola mi amor 🫣🔥\n¿de dónde eres tú, bebé? 🥺💋")
            return
        if uid in ESPERA_PAIS and m.text:
            txt = normalizar(m.text)
            if any(k in txt for k in ['peru','pe','lima']): await m.reply_text(PE_PRECIOS, reply_markup=get_menu())
            elif any(k in txt for k in ['mexico','mx']): await m.reply_text(MX_PRECIOS, reply_markup=get_menu())
            elif any(k in txt for k in ['eeuu','usa']): await m.reply_text(USA_PRECIOS, reply_markup=get_menu())
            else: await m.reply_text(OTRO_PRECIOS, reply_markup=get_menu())
            del ESPERA_PAIS[uid]
            return
        if m.photo:
            PAGARON.add(uid); guardar_datos()
            await avisar_pago(ctx, uid, user, name, m.photo[-1].file_id)
            await m.reply_text(f"✅ Pago recibido. Escríbeme {USERNAME_ADMIN}")
            return
        if m.text and m.text.lower() == '/start':
            await m.reply_text(f"Mmmm {name}... 😏✨", reply_markup=get_menu())
            return
        if m.text and any(x in normalizar(m.text) for x in ['gratis','free','regalo']):
            await enviar_gratis(uid, ctx); return
        if m.text and any(x in m.text.lower() for x in ['comprar','quiero','pago','precio']):
            await m.reply_text("Elige país:", reply_markup=get_precios_menu()); return
        await m.reply_text("¿Qué se te antoja? 👇", reply_markup=get_menu())
        return

    # ===== 3. GRUPOS =====
    if m.text and m.text.lower() == '/start':
        await m.reply_text(f"Mmmm {name}... 😏✨", reply_markup=get_menu())
        return
    if m.text and '/milink' in m.text.lower():
        link = await crear_link_referido(ctx, uid, user)
        if link:
            c = REFERIDOS[uid]['contador']
            await m.reply_text(f"{TEXTO_NIVELES}\n\n🔗 TU LINK:\n{link}\n\n📊 Llevas: {c}/200", reply_markup=get_volver())
        else: await m.reply_text("😏 Preparando link...", reply_markup=get_volver())
        return
    if m.photo:
        if uid == ADMIN_ID: return
        PAGARON.add(uid)
        guardar_datos()
        await avisar_pago(ctx, uid, user, name, m.photo[-1].file_id)
        await m.reply_text(f"✅ Pago recibido. Escríbeme {USERNAME_ADMIN}")
        return

async def button(upd: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = upd.callback_query; await q.answer()
    uid = q.from_user.id; d = q.data
    if d == 'comprar': await q.edit_message_text("💎 ELIGE TU PAÍS 💎", reply_markup=get_precios_menu())
    elif d == 'pe': await q.edit_message_text(PE_PRECIOS, reply_markup=get_volver()); ctx.job_queue.run_once(follow_up, 1800, data={'uid':uid})
    elif d == 'mx': await q.edit_message_text(MX_PRECIOS, reply_markup=get_volver())
    elif d == 'usa': await q.edit_message_text(USA_PRECIOS, reply_markup=get_volver())
    elif d == 'otro': await q.edit_message_text(OTRO_PRECIOS, reply_markup=get_volver())
    elif d == 'gratis':
        await q.edit_message_text("Cargando misiones...", reply_markup=get_volver())
        await enviar_gratis(uid, ctx)
    elif d == 'milink':
        link = await crear_link_referido(ctx, uid, q.from_user.username or "x")
        if link:
            c = REFERIDOS[uid]['contador']
            await q.edit_message_text(f"{TEXTO_NIVELES}\n\n🔗 TU LINK:\n{link}\n\n📊 Llevas: {c}/200", reply_markup=get_volver())
        else: await q.edit_message_text("😏 Preparando link...", reply_markup=get_volver())
    elif d == 'ranking':
        if not REFERIDOS: await q.edit_message_text("Aún no hay referidos", reply_markup=get_volver())
        else:
            top = sorted(REFERIDOS.items(), key=lambda x: x[1]['contador'], reverse=True)[:10]
            txt = "🏆 TOP REFERIDOS\n\n" + "\n".join([f"{i+1}. {d['username']} - {d['contador']}" for i,(u,d) in enumerate(top)])
            await q.edit_message_text(txt, reply_markup=get_volver())
    elif d == 'volver': await q.edit_message_text("¿Qué se te antoja? 👇", reply_markup=get_menu())

async def vip(u,c):
    if u.effective_user.id!= ADMIN_ID: return
    uid=int(c.args[0]); VIP_TEMPORAL[uid]=datetime.now()+timedelta(minutes=15)
    await c.bot.send_message(uid,"✅ VIP"); await u.message.reply_text("OK")

async def activar(u,c):
    if u.effective_user.id!= ADMIN_ID: return
    uid=int(c.args[0])
    if uid in PAGARON:
        PAGARON.remove(uid)
        guardar_datos()
    await c.bot.send_message(uid,"Bot reactivado"); await u.message.reply_text("OK")

def main():
    cargar_datos()
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler('vip', vip))
    app.add_handler(CommandHandler('activar', activar))
    app.add_handler(CallbackQueryHandler(button))
    app.add_handler(ChatMemberHandler(track_join, ChatMemberHandler.CHAT_MEMBER))
    app.add_handler(MessageHandler(filters.ALL, manejar_todo))
    if app.job_queue:
        app.job_queue.run_daily(resumen_estrellas, time=time(4, 58))
    logger.info("BOT PRENDIDO ✅")
    try:
        app.run_polling(drop_pending_updates=True, allowed_updates=Update.ALL_TYPES)
    except Conflict:
        logger.error("Otra instancia corriendo")
        sys.exit(0)

if __name__ == '__main__': main()
