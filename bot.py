import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputMediaPhoto
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters
from precios import PRECIOS
from pagos import PAGOS
from videos_gratis import COMO_GANAR_GRATIS, FOTOS_GRATIS
from canal import CANAL_TELEGRAM

TOKEN = os.getenv("8751695788:AAENlUN4KTzaBmVNdbDf3AAr0kmro3pM6VI")
ADMIN_ID = 8783569348 # Tu ID para recibir notificaciones

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
    p = PRECIOS
    pg = PAGOS

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

    # 1. Manda las 6 fotos como álbum
    media_group = []
    for foto in FOTOS_GRATIS:
        media_group.append(InputMediaPhoto(open(foto, 'rb')))
    await query.message.reply_media_group(media=media_group)

    # 2. Manda el texto con las instrucciones
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

# NUEVO: Captura pagos y te notifica
async def recibir_comprobante(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    caption = update.message.caption or "Sin descripción"

    # 1. Reenvía la foto + caption a tu ID
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

    # 2. Responde al cliente
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

    # Handler para recibir fotos/capturas de pago
    app.add_handler(MessageHandler(filters.PHOTO, recibir_comprobante))

    print("Bot iniciado...")
    app.run_polling()

if __name__ == '__main__':
    main()
