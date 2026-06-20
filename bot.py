import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes
from telegram.constants import ParseMode

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

TOKEN = os.environ.get('TOKEN')
if not TOKEN:
    logger.error("FATAL: No se encontró TOKEN en Environment Variables")
    raise ValueError("Falta TOKEN en Render")

def get_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🛍 PERÚ 🇵🇪", callback_data='pe')],
        [InlineKeyboardButton("🛍 MÉXICO 🇲🇽", callback_data='mx')],
        [InlineKeyboardButton("🛍 USA 🇺🇸", callback_data='usd')],
        [InlineKeyboardButton("🌍 OTRO PAÍS / INTERNATIONAL", callback_data='intl')],
        [InlineKeyboardButton("🎁 REGALITOS", callback_data='regalitos')],
        [InlineKeyboardButton("🔥 MI CANAL VIP", callback_data='canal')]
    ])

def get_volver():
    return InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Volver al Menú Principal", callback_data='volver')]])

PE_PRECIOS = """
🛍 *VIDEOS \- PERÚ* 🇵🇪

🎂 *BÁSICO: S/ 15*
→ 5 videos \| S/ 3 c/u

🔥 *TOP: S/ 30* ← MÁS VENDIDO
→ 12 videos \| S/ 2\.50 c/u
→ Ahorras 50%

🏆 *PREMIUM: S/ 60*
→ 1 personalizado \+ 20 videos
→ incluye sexting 🥰
→ Ahorras 67%

━━━━━━━━━━━━━━━
📼 *VIDEOLLAMADAS \- PERÚ* 📼

S/ 60: 10 min
S/ 80: 20 min

━━━━━━━━━━━━━━━
💳 *PAGO:*
*YAPE/PLIN:* `923553612`

*CUENTO CON REFERENCIAS*

1\. Yapeas 2\. Captura
"""

MX_PRECIOS = """
🛍 *VIDEOS \- MÉXICO* 🇲🇽

🎂 *BÁSICO: $100 MXN*
→ 5 videos \| $20 c/u

🔥 *TOP: $200 MXN* ← MÁS VENDIDO
→ 12 videos \| $16 c/u
→ Ahorras 50%

🏆 *PREMIUM: $400 MXN*
→ 1 personalizado \+ 20 videos
→ incluye sexting 🥰
→ Ahorras 80%

━━━━━━━━━━━━━━━
📼 *VIDEOLLAMADAS \- MÉXICO* 📼

$400 MXN: 10 min
$600 MXN: 20 min

━━━━━━━━━━━━━━━
🛍 *PAGO MXN:*
🇲🇽 Transfer/Astropay
→ *Pídeme datos por aquí*

1\. Pagas 2\. Captura
"""

# 🌍 USD/INTERNACIONAL - LINK PAYPAL CORRECTO ✅
USD_PRECIOS = """
🛍 *VIDEOS \- USD/INTERNACIONAL* 🌍

🎂 *BÁSICO: $5 USD*
→ 5 videos \| $1 c/u

🔥 *TOP: $9 USD* ← MÁS VENDIDO
→ 12 videos \| $0\.75 c/u
→ Ahorras 50%

🏆 *PREMIUM: $20 USD*
→ 1 personalizado \+ 20 videos
→ incluye sexting 🥰
→ Ahorras 60%

━━━━━━━━━━━━━━━
📼 *VIDEOLLAMADAS \- INTERNACIONAL* 📼

$20 USD: 10 min
$30 USD: 20 min

━━━━━━━━━━━━━━━
🪙 *PAGO PAYPAL:* 
👉 https://www\.paypal\.com/qrcodes/p2pqrc/76RWY9FF7Q7RE

Avísame cuando envíes con el comprobante 🥰
En cuanto caiga te mando tu pack 🔥

1\. Pagas 2\. Captura
"""

REGALITOS = """
🎁 *REGALITOS PARA TI* 🔥

Aquí tienes contenido gratis amor:

👉 https://t\.me/\+cBI1upnfsN1iYTgx

Entra y disfruta 😘
"""

CANAL_VIP = """
🔥 *MI CANAL VIP EXCLUSIVO* 💋

Todo mi contenido más caliente está aquí:

👉 https://t\.me/\+ZWc0FAcw\-hQ2MDZh

*Solo para mis reyes* 👑
"""

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = "Hola amor 💋 Bienvenido a *YANABICITASA*\n\nElige tu país para ver precios:"
    try:
        if update.message:
            await
