import logging
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

# ✅ USA VARIABLE DE ENTORNO PARA RENDER
TOKEN = os.environ.get('TOKEN')

# 👜 CATÁLOGO YANABICITASA - EDITA AQUÍ
CATALOGO = """
👜 *YANABICITASA - Chiclayo* 📍

✨ *CARTERAS DISPONIBLES:*

1️⃣ *Bandolera Cuero Premium* - S/ 89
   Colores: Negro, Marrón, Beige
   
2️⃣ *Tote Bag Grande* - S/ 120
   Ideal para trabajo/universidad
   
3️⃣ *Mini Bag Elegante* - S/ 65
   Para salidas y fiestas
   
4️⃣ *Mochila Urbana* - S/ 95
   Impermeable, varios compartimientos

🚚 *Envíos a todo Perú*
💳 *Pagos:* Yape, Plin, Transferencia BCP
"""

PAGOS = """
💵 *MÉTODOS DE PAGO YANABICITASA* 🇵🇪

1️⃣ *Yape/Plin:* 923553612
   Nombre: [PON TU NOMBRE AQUÍ]
   
2️⃣ *Transferencia BCP:*
   Cuenta: [PON TU CUENTA AQUÍ]
   CCI: [PON TU CCI AQUÍ]

3️⃣ *Contraentrega Chiclayo*
   Pagas cuando te entrego 🛵

*PASOS:*
1. Yapeas/Transfieres
2. Mándame captura aquí
3. Coordino tu envío 🔥
"""

ENVIOS = """
🚚 *ENVÍOS YANABICITASA*

📍 *Chiclayo:* S/ 5 - Entrega mismo día
📍 *Lambayeque/Ferreñafe:* S/ 10 - 24hrs
📍 *Todo Perú:* S/ 15 vía Olva/Shalom - 2-3 días

*GRATIS* en compras mayores a S/ 200 🎁
"""

# 🔘 MENÚ PRINCIPAL
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("👜 Ver Catálogo", callback_data='catalogo')],
        [InlineKeyboardButton("💵 Métodos de Pago", callback_data='pagos')],
        [InlineKeyboardButton("🚚 Envíos", callback_data='envios')],
        [InlineKeyboardButton("📞 Hablar con Yana", callback_data='dudas')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    text = "Hola reina 💋 Bienvenida a *YANABICITASA*\n\n¿En qué te ayudo hoy?"
    
    if update.message:
        await update.message.reply_text(text, reply_markup=reply_markup, parse_mode='Markdown')
    else:
        await update.callback_query.edit_message_text(text, reply_markup=reply_markup, parse_mode='Markdown')

# 🔘 BOTONES - AQUÍ ESTABA EL ERROR, YA LO ARREGLÉ
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    # 🔥 BOTÓN VOLVER QUE FALTABA
    boton_volver = [[InlineKeyboardButton("⬅️ Volver al Menú", callback_data='volver')]]
    reply_markup_volver = InlineKeyboardMarkup(boton_volver)
    
    if query.data == 'catalogo':
        await query.edit_message_text(CATALOGO, reply_markup=reply_markup_volver, parse_mode='Markdown')
    elif query.data == 'pagos':
        await query.edit_message_text(PAGOS, reply_markup=reply_markup_volver, parse_mode='Markdown')
    elif query.data == 'envios':
        await query.edit_message_text(ENVIOS, reply_markup=reply_markup_volver, parse_mode='Markdown')
    elif query.data == 'dudas':
        await query.edit_message_text(
            "Escríbeme tu consulta por aquí amor 😘\n\nTe respondo al toque 💋",
            reply_markup=reply_markup_volver
        )
    elif query.data == 'volver':
        await start(update, context)

# 🤖 AUTO-RESPUESTA - TAMBIÉN CON BOTÓN VOLVER
async def responder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    boton_volver = [[InlineKeyboardButton("⬅️ Volver al Menú", callback_data='volver')]]
    reply_markup_volver = InlineKeyboardMarkup(boton_volver)
    
    if update.message.photo:
        await update.message.reply_text(
            "Recibí tu captura reina 😘\n\nYa reviso tu pago y coordino tu envío 🔥",
            reply_markup=reply_markup_volver
        )
        return
    
    texto = update.message.text.lower()
    
    if any(palabra in texto for palabra in ['precio', 'catalogo', 'cartera', 'bolso', 'cuanto', 'costo']):
        await update.message.reply_text(CATALOGO, reply_markup=reply_markup_volver, parse_mode='Markdown')
    
    elif any(palabra in texto for palabra in ['pago', 'pagar', 'yape', 'plin', 'cuenta']):
        await update.message.reply_text(PAGOS, reply_markup=reply_markup_volver, parse_mode='Markdown')
    
    elif any(palabra in texto for palabra in ['envio', 'envían', 'delivery', 'chiclayo']):
        await update.message.reply_text(ENVIOS, reply_markup=reply_markup_volver, parse_mode='Markdown')
    
    else:
        await update.message.reply_text(
            "No entendí amor 😅\n\nUsa el menú para ver
