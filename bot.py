import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters

TOKEN = os.getenv("8751695788:AAENlUN4KTzaBmVNdbDf3AAr0kmro3pM6VI")
ADMIN_ID = 8783569348

# ===== PRECIOS =====
PRECIOS = {
    "peru": {
        "bandera": "🇵🇪",
        "nombre": "Perú",
        "basico": {"precio": "S/ 15", "detalle": "5 vds | S/ 3 c/u"},
        "top": {"precio": "S/ 30", "detalle": "12 vds | S/ 2.50 c/u", "tag": "MÁS VENDIDO", "ahorro": "Ahorras 50%"},
        "premium": {"precio": "S/ 60", "detalle": "1 personalizado + 20 vds\n→ incluye sexting 🥰", "ahorro": "Ahorras 67%"},
        "videollamada_10": "S/ 60: 10 min",
        "videollamada_20": "S/ 80: 20 min"
    },
    "mexico": {
        "bandera": "🇲🇽",
        "nombre": "México",
        "basico": {"precio": "$100 MXN", "detalle": "5 vds | $20 c/u"},
        "top": {"precio": "$200 MXN", "detalle": "12 vds | $16 c/u", "tag": "MÁS VENDIDO", "ahorro": "Ahorras 50%"},
        "premium": {"precio": "$400 MXN", "detalle": "1 personalizado + 20 vds\n→ incluye sexting 🥰", "ahorro": "Ahorras 80%"},
        "videollamada_10": "$400 MXN: 10 min",
        "videollamada_20": "$600 MXN: 20 min"
    },
    "eeuu": {
        "bandera": "🇺🇸",
        "nombre": "Estados Unidos",
        "basico": {"precio": "$5 USD", "detalle": "5 vds | $1 c/u"},
        "top": {"precio": "$9 USD", "detalle": "12 vds | $0.75 c/u", "tag": "MÁS VENDIDO", "ahorro": "Ahorras 50%"},
        "premium": {"precio": "$20 USD", "detalle": "1 personalizado + 20 vds\n→ incluye sexting 🥰", "ahorro": "Ahorras 60%"},
        "videollamada_10": "$20 USD: 10 min",
        "videollamada_20": "$30 USD: 20 min"
    },
    "mundial": {
        "bandera": "🌎",
        "nombre": "Todo el mundo",
        "basico": {"precio": "$5 USD", "detalle": "5 vds | $1 c/u"},
        "top": {"precio": "$9 USD", "detalle": "12 vds | $0.75 c/u", "tag": "MÁS VENDIDO", "ahorro": "Ahorras 50%"},
        "premium": {"precio": "$20 USD", "detalle": "1 personalizado + 20 vds\n→ incluye sexting 🥰", "ahorro": "Ahorras 60%"},
        "videollamada_10": "$20 USD: 10 min",
        "videollamada_20": "$30 USD: 20 min"
    }
}

# ===== PAGOS =====
PAGOS = {
    "peru": {
        "metodo": "YAPE/PLIN",
        "numero": "923553612",
        "instrucciones": "1. Yapeas 2. Captura\nCUENTO CON REFERENCIAS"
    },
    "mexico": {
        "banco": "STP",
        "clabe": "646180546711450910",
        "concepto": "yanae",
        "otros": "🇲🇽 También acepto: Transfer / Astropay\n→ Pídeme datos si usas otro método",
        "instrucciones": "1. Pagas 2. Captura\nMándame captura cuando pagues bebé 🥰\nEn cuanto caiga te mando tu pack 🔥"
    },
    "eeuu": {
        "paypal": "AbigailMaximoofO",
        "paypal_qr": "https://www.paypal.com/qrcodes/p2pqrc/76RWY9FF7Q7RE",
        "usdt": "Disponible",
        "banco_nombre": "Community Federal Savings Bank",
        "banco_direccion": "5 Penn Plaza, 14th Floor\nNew York, NY 10001, US",
        "cuenta": "8338233469",
        "routing": "026073150",
        "tipo_cuenta": "Checking",
        "instrucciones": "1. Pagas 2. Captura\nAvísame cuando envíes con el comprobante 🥰\nEn cuanto caiga te mando tu pack 🔥"
    },
    "mundial": {
        "paypal": "AbigailMaximoofO",
        "paypal_qr": "https://www.paypal.com/qrcodes/p2pqrc/76RWY9FF7Q7RE",
        "usdt": "Disponible",
        "instrucciones": "1. Pagas 2. Captura\nAvísame cuando envíes con el comprobante 🥰\nEn cuanto caiga te mando tu pack 🔥"
    }
}

# ===== VIDEOS GRATIS =====
COMO_GANAR_GRATIS = """
📸 *GRATIS* 🥺💋

✨ *QUIERES HASTA 20 VIDEITOS GRATIS?* ✨
Es por promocionarme en TikTok ✅

*Pasitos súper fáciles uwu:*
1️⃣ Ponte un nombrecito + fotito tierna <33
2️⃣ En tu bio pon: `Tg: yanabicitasa` ✨
3️⃣ Sube una fotito a tu story + frasita hot 😋
4️⃣ Comenta coshitas en videos hot, unos 30-100 👀
   Así generamos vistas juntos
5️⃣ Mándame captura + videito cuando termines
6️⃣ Disfruta de hasta 20 videitos :3 ❤️‍🔥

¿Te animas o ño? 🥺
(Me avisas cuando cumplas mi rey)
"""

FOTOS_GRATIS = [
    "fotitos1.JPG",
    "fotitos2.JPG", 
    "fotitos3.JPG",
    "fotitos4.JPG",
    "fotitos5.JPG",
    "fotitos6.JPG"
]

CANAL_TELEGRAM = "https://t.me/+ZWc0FAcw-hQ2MDZh"

# ===== FUNCIONES DEL BOT =====
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("💰 Precios", callback_data='menu_precios')],
        [InlineKeyboardButton("🎁 Videos Gratis", callback_data='gratis')],
        [InlineKeyboardButton("📺 Canal VIP", url=CANAL_TELEGRAM)]
    ]
    await update.message.reply_text(
        "Hola bebé 🥺💋 ¿Qué quieres ver hoy?\n\nCuando pagues mándame captura + monto aquí mismo",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def menu_precios(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = [
        [InlineKeyboardButton("🇵🇪 Perú", callback_data='precio_peru')],
        [InlineKeyboardButton("🇲🇽 México", callback_data='precio_mexico')],
        [InlineKeyboardButton("🇺🇸 EEUU", callback_data='precio_eeuu')],
        [InlineKeyboardButton("🌎 Todo el mundo", callback_data='precio_mundial')],
        [InlineKeyboardButton("⬅️ Volver", callback_data='volver')]
    ]
    await query.edit_message_text(
        "Elige tu país para ver precios y métodos de pago:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def mostrar_precio(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    pais = query.data.split('_')[1]
    p = PRECIOS[pais]
    pg = PAGOS[pais]

    texto = f"🛍 *VIDEOS* 🛒\n\n"
    texto += f"{p['bandera']} *{p['nombre']}*\n\n"
    texto += f"🎂 *BÁSICO: {p['basico']['precio']}*\n→ {p['basico']['detalle']}\n\n"
    texto += f"🔥 *TOP: {p['top']['precio']}* ← {p['top']['tag']}\n→ {p['top']['detalle']}\n→ {p['top']['ahorro']}\n\n"
    texto += f"🏆 *PREMIUM: {p['premium']['precio']}*\n→ {p['premium']['detalle']}\n→ {p['premium']['ahorro']}\n\n"
    texto += f"📼 *VIDEOLLAMADAS* 📼\n{p['videollamada_10']}\n{p['videollamada_20']}\n\n"
    texto += "\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\n\n"

    if pais == "peru":
        texto += f"{pg['numero']}\n\n{pg['metodo']}\n\n{pg['instrucciones']}\n"
    elif pais == "mexico":
        texto += f"🛍 *PAGO MXN:*\n🏦 Banco: {pg['banco']}\n🔢 CLABE:\n{pg['clabe']}\n📝 Referencia/Concepto: {pg['concepto']}\n\n{pg['otros']}\n\n{pg['instrucciones']}"
    elif pais == "eeuu":
        texto += f"🪙 *PAGO:*\nPayPal:\n{pg['paypal']}\n\n🏦 *Bank EEUU:*\n{pg['banco_nombre']}\n📍 Bank Address:\n{pg['banco_direccion']}\n0️⃣ Account Number:\n{pg['cuenta']}\n0️⃣ Routing Number / ABA:\n{pg['routing']}\n✍️ Account Type:\n{pg['tipo_cuenta']}\n\n{pg['instrucciones']}"
    elif pais == "mundial":
        texto += f"🪙 *PAGO:*\nPayPal:\n{pg['paypal']}\n\n{pg['paypal_qr']}\n\n/ USDT\n\n{pg['instrucciones']}"

    keyboard = [[InlineKeyboardButton("⬅️ Volver", callback_data='menu_precios')]]
    await query.edit_message_text(
        texto,
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup(keyboard),
        disable_web_page_preview=True
    )

async def videos_gratis(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    media_group = []
    for foto in FOTOS_GRATIS:
        media_group.append(InputMediaPhoto(open(foto, 'rb')))
    await query.message.reply_media_group(media=media_group)

    keyboard = [[InlineKeyboardButton("⬅️ Volver", callback_data='volver')]]
    await query.message.reply_text(
        COMO_GANAR_GRATIS,
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    await query.delete_message()

async def volver(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    keyboard = [
        [InlineKeyboardButton("💰 Precios", callback_data='menu_precios')],
        [InlineKeyboardButton("🎁 Videos Gratis", callback_data='gratis')],
        [InlineKeyboardButton("📺 Canal VIP", url=CANAL_TELEGRAM)]
    ]
    await query.edit_message_text(
        "Hola bebé 🥺💋 ¿Qué quieres ver hoy?\n\nCuando pagues mándame captura + monto aquí mismo",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def recibir_comprobante(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    caption = update.message.caption or "Sin descripción"

    await context.bot.send_photo(
        chat_id=ADMIN_ID,
        photo=update.message.photo[-1].file_id,
        caption=f"💸 *NUEVO PAGO RECIBIDO*\n\n"
                f"👤 Cliente: @{user.username or 'Sin username'}\n"
                f"🆔 ID: `{user.id}`\n"
                f"📝 Nombre: {user.first_name}\n"
                f"💬 Mensaje: {caption}\n\n"
                f"Responde a este mensaje para contactarlo.",
        parse_mode='Markdown'
    )

    await update.message.reply_text(
        "Amor, recibí tu captura 🥺❤️‍🔥\n"
        "Déjame verificar y en un ratito te mando tu pack\n"
        "Gracias por tu compra 😘"
    )

def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(menu_precios, pattern='^menu_precios$'))
    app.add_handler(CallbackQueryHandler(mostrar_precio, pattern='^precio_'))
    app.add_handler(CallbackQueryHandler(videos_gratis, pattern='^gratis$'))
    app.add_handler(CallbackQueryHandler(volver, pattern='^volver$'))
    app.add_handler(MessageHandler(filters.PHOTO, recibir_comprobante))

    print("Bot iniciado...")
    app.run_polling()

if __name__ == '__main__':
    main()
