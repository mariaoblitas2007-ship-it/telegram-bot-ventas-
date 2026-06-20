import logging
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

# ✅ TOKEN SE LEE DE RENDER - NO LO PONGAS AQUÍ
TOKEN = os.environ.get('TOKEN')

# 👜 EDITA TU CATÁLOGO AQUÍ - BORRA ESTE Y PON TUS PRODUCTOS REALES
CATALOGO = """
👜 *YANABICITASA - Chiclayo* 📍

✨ *PRODUCTOS DISPONIBLES:*

1️⃣ *Producto 1* - S/ 00
   Descripción corta
   
2️⃣ *Producto 2* - S/ 00
   Descripción corta
   
3️⃣ *Producto 3* - S/ 00
   Descripción corta

🚚 *Envíos a todo Perú*
💳 *Pagos:* Yape, Plin, Transferencia BCP

Escríbeme para tu pedido amor 💋
"""

PAGOS = """
💵 *MÉTODOS DE PAGO YANABICITASA* 🇵🇪

1️⃣ *Yape/Plin:* 923553612
   Nombre: MARIA [TU APELLIDO]
   
2️⃣ *Transferencia BCP:*
   Cuenta: [TU CUENTA BCP]
   CCI: [TU CCI]

3️⃣ *Contraentrega Chiclayo*
   Pagas cuando te entrego 🛵

*PASOS:*
1. Yapeas/Transfieres el monto
2. Mándame captura aquí
3. Coordino tu envío 🔥
"""

ENVIOS = """
🚚 *ENVÍOS YANABICITASA*

📍 *Chiclayo:* S/ 5 - Entrega mismo día
📍 *Lambayeque/Ferreñafe:* S/ 10 - 24hrs
📍 *Todo Perú:* S/ 15 vía Olva/Shalom - 2-3 días

*ENVÍO GRATIS* en compras mayores a S/ 200 🎁
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
    
