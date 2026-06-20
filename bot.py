import logging
import os
import csv
from datetime import datetime
from collections import defaultdict
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

TOKEN = "8751695788:AAFg5vFlt2EYvR5zOZ_tn29T0KZLYvTZs74"
TU_ID = 8783569348

user_pais = defaultdict(str)

PRECIOS_MX = """
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
$400 MXN: 10 min
$600 MXN: 20 min

🛍 PAGO MXN:
🇲🇽 Transfer/Astropay/
→ Escríbeme y te paso datos amor 💋

1. Pagas 2. Captura
"""

PRECIOS_USA = """
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
$20 USD: 10 min
$30 USD: 20 min

🪙 PAGO: 
PayPal: 
https://www.paypal.com/qrcodes/p2pqrc/76RWY9FF7Q7RE

🏦 Bank EEUU:
Community Federal Savings Bank
📍 Bank Address:
5 Penn Plaza, 14th Floor
New York, NY 10001, US
0️⃣ Account Number:
8338233469
0️⃣ Routing Number / ABA:
026073150
✍️ Account Type:
Checking

Avísame cuando envíes con el comprobante 🥰
En cuanto caiga te mando tu pack 🔥

1. Pagas 2. Captura
"""

PRECIOS_PE = """
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
S/ 60: 10 min
S/ 80: 20 min

\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\\

923553612
 
YAPE/PLIN

CUENTO CON REFERENCIAS 

1. Yapeas 2. Captura
"""

PRECIOS_OTROS = """
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
$20 USD: 10 min
$30 USD: 20 min

🛍 PAGO:
Escríbeme amor y te paso opciones de pago para tu país 💋

1. Pagas 2. Captura
"""

def registrar_venta(user_id, username, nombre, pais, monto, moneda):
    archivo = 'ventas.csv'
    if not os.path.exists(archivo):
        with open(archivo, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(['Fecha', 'User_ID', 'Username', 'Nombre', 'País', 'Monto', 'Moneda'])
    with open(archivo, 'a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow([datetime.now().strftime('%Y-%m-%d %H:%M'), user_id, username, nombre, pais, monto, moneda])

async def venta(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id!= TU_ID:
        return
    try:
        args = context.args
        username = args[0].replace('@', '')
        monto = args[1]
        moneda = args[2]
        registrar_venta(0, username, username, "manual", monto, moneda)
        await update.message.reply_text(f"✅ Venta registrada mi vida:\n@{username}\n{monto} {moneda} 💕")
    except:
        await update.message.reply_text("Usa así amor: /venta @usuario 20 USD")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_pais[user_id] == 'mx':
        await update.message.reply_text(PRECIOS_MX)
        return
    elif user_pais[user_id] == 'usa':
        await update.message.reply_text(PRECIOS_USA)
        return
    elif user_pais[user_id] == 'pe':
        await update.message.reply_text(PRECIOS_PE)
        return
    elif user_pais[user_id] == 'otros':
        await update.message.reply_text(PRECIOS_OTROS)
        return
    keyboard = [[InlineKeyboardButton("🇲🇽 México", callback_data='mx')], [InlineKeyboardButton("🇺🇸 USA", callback_data='usa')], [InlineKeyboardButton("🇵🇪 Perú", callback_data='pe')], [InlineKeyboardButton("🌎 Otro país", callback_data='otros')]]
    await update.message.reply_text("Hola amor 💋 ¿De qué país eres?", reply_markup=InlineKeyboardMarkup(keyboard))

async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer()
    if query.data in ['mx', 'usa', 'pe', 'otros']:
        user_pais[user_id] = query.data
    if query.data == 'mx':
        await query.edit_message_text(PRECIOS_MX)
    elif query.data == 'usa':
        await query.edit_message_text(PRECIOS_USA)
    elif query.data == 'pe':
        await query.edit_message_text(PRECIOS_PE)
    elif query.data == 'otros':
        await query.edit_message_text(PRECIOS_OTROS)

async def responder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if update.message.photo:
        await update.message.reply_text("Recibí tu captura amor 😘\n\nEn cuanto caiga el pago te mando tu pack 🔥")
        return
    texto = update.message.text.lower()
    
    if any(p in texto for p in ['gratis', 'free', 'muestra', 'prueba', 'regalo', 'demo', 'tienes gratis']):
        await update.message.reply_text("""
Ay amor 🥺 muestras gratis no manejo, pero...

Tengo un secretito pa ti 💋 Aquí te explico cómo puedes ganar videos gratis: https://t.me/+cBI1upnfsN1iYTgx

Entra ahí y sigue los pasitos mi vida 😘 Si tienes dudas me dices

Y si quieres algo más directo y rapidito, aquí tengo mis packs 👇💕
""")
        return
    
    if 'paypal' in texto:
        user_pais[user_id] = 'usa'
        await update.message.reply_text(PRECIOS_USA)
        return
    elif 'yape' in texto or 'plin' in texto:
        user_pais[user_id] = 'pe'
        await update.message.reply_text(PRECIOS_PE)
        return
    elif any(p in texto for p in ['precio', 'info', 'costo', 'cuanto', 'pack', 'video']):
        if user_pais[user_id] == 'mx': await update.message.reply_text(PRECIOS_MX)
        elif user_pais[user_id] == 'usa': await update.message.reply_text(PRECIOS_USA)
        elif user_pais[user_id] == 'pe': await update.message.reply_text(PRECIOS_PE)
        elif user_pais[user_id] == 'otros': await update.message.reply_text(PRECIOS_OTROS)
        else:
            keyboard = [[InlineKeyboardButton("🇲🇽 México", callback_data='mx')], [InlineKeyboardButton("🇺🇸 USA", callback_data='usa')], [InlineKeyboardButton("🇵🇪 Perú", callback_data='pe')], [InlineKeyboardButton("🌎 Otro país", callback_data='otros')]]
            await update.message.reply_text("¿De qué país eres? 😘", reply_markup=InlineKeyboardMarkup(keyboard))
        return
    else:
        await update.message.reply_text("Escribe 'precio', 'paypal' o 'yape' amor 😘💋")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("venta", venta))
    app.add_handler(CallbackQueryHandler(button))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, responder))
    app.add_handler(MessageHandler(filters.PHOTO, responder))
    print("Bot corriendo 🔥")
    app.run_polling()

if __name__ == '__main__':
    main()
