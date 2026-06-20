import asyncio
import logging
import random
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, ContextTypes, filters

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = 'TU_TOKEN_AQUI'
ADMIN_ID = 123456789 # CAMBIA POR TU ID

PAGO_MOVIL = {'banco': 'Banco Ejemplo', 'cedula': '12345678', 'telefono': '999999999'}
PRECIOS_CRIPTO = {'bs': 0.005, 'usdt': 0.20}

USUARIOS_REGISTRADOS = set()
PAIS_USUARIO = {}
DEMO_USADO = set()
VIP_TEMPORAL = {}
DEMO_HOT = {}

PAISES = {
    '1': 'Perú', '2': 'México', '3': 'Colombia', '4': 'Argentina',
    '5': 'Chile', '6': 'Venezuela', '7': 'Ecuador', '8': 'España'
}

async def send_fluid(message, textos):
    """Manda varios mensajes cortos con delay natural como chat real"""
    for i, texto in enumerate(textos):
        if i > 0:
            await asyncio.sleep(random.uniform(0.8, 1.5))
        try:
            await message.reply_text(texto)
        except Exception as e:
            logger.error(f"Error enviando mensaje: {e}")
            break

def get_menu():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("💎 Comprar Premium", callback_data="comprar")],
        [InlineKeyboardButton("📸 Ver Packs", callback_data="packs")],
        [InlineKeyboardButton("💋 Chat Hot", callback_data="chat")]
    ])

def get_volver():
    return InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Volver", callback_data="menu")]])

async def auto_tease_demo(context: ContextTypes.DEFAULT_TYPE):
    job = context.job
    user_id = job.data['user_id']

    # VERIFICA QUE EL DEMO SIGA ACTIVO
    if user_id not in DEMO_HOT or DEMO_HOT[user_id] < datetime.now():
        return

    teases_fluidos = [
        ["oye...", "Xd no dejo de pensar en ti 😳"],
        ["papi", "me distraje en clase x tu culpa 😈", "JSKSKS"],
        ["toy aburrida...", "qué haces? 💦 uwu"],
        ["me puse a verme al espejo y...", "🙈 JSKSKSSKS"],
        ["ay no sé xq te cuento esto pero...", "Xd"],
        ["tengo calor 😰", "o eres tú? uwu"],
        ["weno...", "me voy a tener que... ya sabes 💦"],
        ["toy solita y con ganas 😈", "JSKSKS lastima q se acaba pronto"],
        ["si tuviera más tiempo te...", "🙈 pero ya casi me voy Xd"],
        ["me grabaría algo pero...", "no me da tiempo 😢 uwu"],
        ["JSKSKSSKS", "toy pensando coshitas 🥺"]
    ]

    try:
        mensajes = random.choice(teases_fluidos)
        for i, texto in enumerate(mensajes):
            if i > 0:
                await asyncio.sleep(1.2)
            await context.bot.send_message(chat_id=user_id, text=texto)
    except Exception as e:
        logger.error(f"Error en auto-tease: {e}")

async def auto_tease_vip(context: ContextTypes.DEFAULT_TYPE):
    job = context.job
    user_id = job.data['user_id']

    # VERIFICA QUE EL VIP SIGA ACTIVO
    if user_id not in VIP_TEMPORAL or VIP_TEMPORAL[user_id] < datetime.now():
        return

    mensajes_vip = [
        ["oye se me hace q", "ya me tengo que ir 😢"],
        ["toy que me muero de ganas", "y se acaba 😭"],
        ["no quiero q se corte pero...", "🥺"],
        ["me quedé con ganas de más contigo", "JSKSKS"],
        ["si sigo me quedo sin tiempo pa ti 😢"],
        ["ay no...", "ya casi 😭", "qué hacemos?"]
    ]

    try:
        mensajes = random.choice(mensajes_vip)
        for i, texto in enumerate(mensajes):
            if i > 0:
                await asyncio.sleep(1.2)
            await context.bot.send_message(chat_id=user_id, text=texto)
        await context.bot.send_message(chat_id=user_id, text="¿Otro PREMIUM? 😈", reply_markup=get_menu())
    except Exception as e:
        logger.error(f"Error en auto-tease vip: {e}")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    es_nuevo = user_id not in USUARIOS_REGISTRADOS

    if es_nuevo:
        USUARIOS_REGISTRADOS.add(user_id)
        DEMO_HOT[user_id] = datetime.now() + timedelta(minutes=10)
        DEMO_USADO.add(user_id)

        saludo = random.choice([
            ["olaaa mi rey 😘", "Bienvenido a *YANABICITASA*", "tengo *18 añitos* y ando bien caliente 🔥", "*Te regalo 10 min de chat hot conmigo*", "es tu única vez gratis, aprovecha 💦", "Elige tu país bebé:"],
            ["heyy bebé 💋", "Bienvenido a *YANABICITASA* uwu", "tengo *18* y toy con ganas 😈", "*10 min hot gratis pa ti*", "solo esta vez Xd", "De dónde eres? 🔥"]
        ])
        await send_fluid(update.message, saludo)

        context.job_queue.run_once(auto_tease_demo, 180, data={'user_id': user_id}, name=f"tease1_{user_id}")
        context.job_queue.run_once(auto_tease_demo, 420, data={'user_id': user_id}, name=f"tease2_{user_id}")
    else:
        saludo_vuelta = random.choice([
            ["ola de nuevo mi rey 😘", "ya tienes tu demo usada Xd", "pero puedes comprar *PREMIUM* y seguimos 💋"],
            ["heyy bebé 💋", "uwu ya gastaste tu demo", "pero PREMIUM y te doy *15 min VIP* 🔥"]
        ])
        await send_fluid(update.message, saludo_vuelta)

    botones = [[InlineKeyboardButton(f"{v}", callback_data=f"pais_{k}")] for k, v in PAISES.items()]
    await update.message.reply_text("🌎 *Selecciona tu país:*", reply_markup=InlineKeyboardMarkup(botones))

async def responder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    texto = update.message.text.lower()
    ahora = datetime.now()

    es_vip = user_id in VIP_TEMPORAL and VIP_TEMPORAL[user_id] > ahora
    es_demo = user_id in DEMO_HOT and DEMO_HOT[user_id] > ahora

    if es_vip or es_demo:
        tiempo_restante = (VIP_TEMPORAL[user_id] - ahora).seconds // 60 if es_vip else (DEMO_HOT[user_id] - ahora).seconds // 60

        if not es_vip and tiempo_restante <= 2:
            await update.message.reply_text("Ay papi se me va a acabar el tiempo 😢\n\n*Si quieres seguir caliente conmigo...*\n\nCompra *PREMIUM* y seguimos sin corte 🔥\n\n¿Me dejas ir o me compras? 😈", reply_markup=get_menu())
            return

        if any(x in texto for x in ['mas tiempo', 'más tiempo', 'otro', 'renovar', 'extender', 'seguir', 'mas', 'más', 'otra vez']):
            await update.message.reply_text("Bebé se me está acabando 😢\n\nSi quieres seguir calientito...\n*PREMIUM y seguimos* sin corte 🔥\n\n¿Me mantienes prendida? 😈", reply_markup=get_menu())
            return

        elif es_vip and tiempo_restante <= 5:
            await send_fluid(update.message, ["Ay no papi", "ya me voy a tener que ir 😢", "Aprovecha rápido", "Qué quieres que haga antes? 💋", "*Otro PREMIUM = seguimos más* 🔥"])
            return

        elif any(x in texto for x in ['hola', 'ola', 'buenas', 'hey', 'wenas']):
            saludos_fluidos = [
                ["olaaa 😘", "cómo estás weno?"],
                ["heyy bebé 💋", "q tal tu día? Xd"],
                ["oliii JSKSKSKS", "todo bien?", "en q te ayudo uwu"],
                ["hola papi 😘", "qué buscas hoy? Xd"],
                ["olaa hermoso 🔥", "cómo amaneciste?"],
                ["heyy mi amor 💋", "q se te ofrece uwu"]
            ]
            await send_fluid(update.message, random.choice(saludos_fluidos))
            return

        elif any(x in texto for x in ['como estas', 'cómo estás', 'que tal', 'k tal']):
            estados_fluidos = [
                ["bien mi rey 😘", "gracias x preguntar Xd", "y tú cómo andas? 💋"],
                ["super bien bebé 🔥", "uwu tú q tal?"],
                ["bien amor 😏", "acá atendiéndote JSKSKS", "en q te ayudo weno?"],
                ["todo bien mi vida 💕", "uwu y tú?"],
                ["bien papi 😘", "un poco ocupada pero", "siempre pa ti Xd", "qué necesitas?"]
            ]
            await send_fluid(update.message, random.choice(estados_fluidos))
            return

        elif any(x in texto for x in ['que haces', 'qué haces', 'q haces']):
            quehaces_fluidos = [
                ["nada acá 🙈", "pensando en ti Xd", "y tú?"],
                ["toy echada aburrida...", "y tú? uwu"],
                ["acabo de salir de bañarme 😳", "JSKSKS y tú q haces?"],
                ["nada viendo tik tok...", "me hablas? 😏 Xd"],
                ["ando de ganas la vdd 💦", "uwu y tú qué? JSKSKSSKS"],
                ["weno nada...", "te estaba esperando 🙈", "q haces?"]
            ]
            await send_fluid(update.message, random.choice(quehaces_fluidos))
            return

        elif any(x in texto for x in ['estas sola', 'estás sola', 'sola']):
            sola_fluidos = [
                ["sip solita 😈", "xq?"],
                ["sola y aburrida...", "me haces compañía? Xd"],
                ["solita en mi cuarto 🙈", "y tú? uwu"],
                ["sii por?", "quieres que haga algo? 😏 JSKSKS"],
                ["sola y con calor 😰", "tú? Xd"]
            ]
            await send_fluid(update.message, random.choice(sola_fluidos))
            return

        elif any(x in texto for x in ['que tienes puesto', 'que llevas', 'ropa', 'vestida', 'desnuda', 'calata', 'sin ropa']):
            ropa_fluidos = [
                ["mmm nada papi 😏", "solo mi collar...", "te gusta así?", "o me pongo algo pa ti? 💋"],
                ["uff acabo de salir de bañarme 🔥", "ando con toalla nada más...", "la dejo caer? 😈"],
                ["bebé ando en ropa interior 😏", "negra de encaje...", "quieres que me la quite? 💦"],
                ["papi estoy en tanga nomás 🥵", "te muestro?", "o me visto? 😈"],
                ["ando de ganas y sin nada 😈", "aprovechas? 💦"]
            ]
            await send_fluid(update.message, random.choice(ropa_fluidos))
            return

        elif any(x in texto for x in ['tocate', 'tócate', 'toca', 'masturba', 'dedos', 'dedéate', 'metete', 'juega']):
            tocar_fluidos = [
                ["ufff ya me estoy tocando papi 💦", "pensando en ti...", "sigo o te grabo? 😈"],
                ["mmm me metí los dedos 🥵", "x tu culpa", "estoy que me vengo...", "quieres escuchar? 💋"],
                ["bebé no sabes cómo me tienes 🔥", "ya estoy mojada...", "te muestro en video? 😏 Xd"],
                ["ay papi me estoy masturbando 🥵", "solo x ti", "qué más quieres que haga? 💦"],
                ["ando de ganas tocándome 😈", "te unes?", "o me grabo sola? 💋 uwu"]
            ]
            await send_fluid(update.message, random.choice(tocar_fluidos))
            return

        elif any(x in texto for x in ['muestra', 'muestrame', 'enseña', 'ver', 'foto', 'video', 'pic']):
            mostrar_fluidos = [
                ["mmm quieres verme? 🥵", "dime EXACTO qué quieres ver", "y te lo hago 💦"],
                ["bebé si me pagas te muestro TODO 🔥", "pero si me dices qué quieres ver", "te doy precio especial 😏"],
                ["papi te mando foto si me dices qué quieres 😈", "tetas?", "culo?", "todo? 💦"],
                ["ando de ganas de mostrarme 💋", "qué parte quieres ver primero? 😏 Xd"]
            ]
            await send_fluid(update.message, random.choice(mostrar_fluidos))
            return

        elif any(x in texto for x in ['ganas', 'caliente', 'cachonda', 'excitada', 'mojada', 'arrecha']):
            ganas_fluidos = [
                ["ay papi estoy que ardo 🥵", "toda mojada...", "qué me haces? 💦"],
                ["bebé no sabes cómo me tienes 😈", "necesito que me calmes...", "cómo? 🔥 Xd"],
                ["uff estoy bien cachonda 💦", "me ayudas?", "o me grabo sola? 😏"],
                ["papi estoy hirviendo 🥵", "necesito venirme...", "me ayudas? 💋 uwu"],
                ["ando de ganas bebé 🔥", "mal...", "qué me haces? 😈 JSKSKS"],
                ["uff ando de ganas bien mal 💦", "me calmas?", "o me grabo? 😏 Xd"]
            ]
            await send_fluid(update.message, random.choice(ganas_fluidos))
            return

        elif any(x in texto for x in ['pene', 'verga', 'pito', 'pinga', 'p']):
            pene_fluidos = [
                ["uff papi me gustan los p... 😏", "cómo tienes el tuyo?", "cuéntame 💦 Xd"],
                ["bebé me vuelven loca los p... 🥵", "grande?", "grueso?", "dime todo 🔥"],
                ["mi rey me encantan los p... 😈", "quiero saber del tuyo...", "me cuentas? 💋"],
                ["corazón me gustan mucho los p... 💦", "el tuyo cómo es?", "me mojo solo de pensar 😏 uwu"],
                ["ando de ganas de un p... 🥺", "me hablas del tuyo? 💋 JSKSKS"]
            ]
            await send_fluid(update.message, random.choice(pene_fluidos))
            return

        elif any(x in texto for x in ['tamaño', 'grande', 'chico', 'cm', 'centímetros', 'mide', 'largo', 'grueso']):
            tamaño_fluidos = [
                ["mmm me gustan grandes papi 😏", "cuántos cm tienes?", "dime y te digo si me entra 💦"],
                ["bebé el tamaño sí importa 🥵", "cuántos cm?", "si me gusta te grabo algo especial 🔥"],
                ["mi rey mientras me llene estoy feliz 😈", "dime cuánto mides...", "me aguanto todo? 💋"],
                ["corazón más de 15cm y me vuelvo loca 💦", "cuánto tienes tú? 😏 Xd"]
            ]
            await send_fluid(update.message, random.choice(tamaño_fluidos))
            return

        elif any(x in texto for x in ['gemir', 'gemido', 'grito', 'sonido', 'escuchar', 'ahh', 'mmm']):
            gemidos_fluidos = [
                ["ahhh papi síii 💦", "te gusta cómo gimo?", "te grabo audio si quieres 😈"],
                ["mmm ahh mmm 😏", "así sueno cuando me toco...", "quieres escuchar más? 🔥"],
                ["bebé gimo bien rico 🥵", "PREMIUM y te mando nota de voz", "gimiendo tu nombre 💋"],
                ["ahhh ayy síii 💦", "te grabo gimiendo?", "o prefieres video? 😈 Xd"]
            ]
            await send_fluid(update.message, random.choice(gemidos_fluidos))
            return

        elif any(x in texto for x in ['posición', 'pose', 'perrito', 'misionero', 'vaquera', 'cuatro']):
            posicion_fluidos = [
                ["uff perrito es mi favorita 😏", "te grabo así?", "dime qué posición te prende 💦"],
                ["papi en vaquera me vengo rico 🥵", "quieres video en esa pose? 🔥"],
                ["bebé me gusta en cuatro 😈", "dime tu pose favorita", "y te la hago en video 💋"],
                ["mi rey misionero es rico también 💦", "cuál quieres ver?", "te cobro barato 😏 Xd"]
            ]
            await send_fluid(update.message, random.choice(posicion_fluidos))
            return

        elif any(x in texto for x in ['oral', 'chupar', 'mamar', 'mamada', 'boca', 'lengua', 'lamer']):
            oral_fluidos = [
                ["mmm chupo rico papi 😏", "quieres video chupando?", "te lo hago 💦"],
                ["bebé me encanta mamar 🥵", "toda la noche si quieres...", "me pagas PREMIUM? 🔥"],
                ["mi rey con mi boca te vuelvo loco 😈", "quieres verme chupando?", "dime qué 💋"],
                ["corazón mi lengua es mágica 💦", "te grabo mamando si me convences 😏 Xd"]
            ]
            await send_fluid(update.message, random.choice(oral_fluidos))
            return

        elif any(x in texto for x in ['coger', 'follar', 'singar', 'culiar', 'tirar', 'sexo', 'sex']):
            coger_fluidos = [
                ["uff papi quiero que me cojas rico 😏", "fuerte o suave?", "te grabo como quieras 💦"],
                ["bebé me urge que me folles 🥵", "estoy que ardo...", "cómo me vas a dar? 🔥"],
                ["mi rey cógeme como perra 😈", "te grabo todo si me pagas PREMIUM 💋"],
                ["corazón quiero sexo contigo 💦", "dime cómo me vas a hacer venir 😏"],
                ["ando de ganas de coger 🔥", "cómo me vas a dar? 💋 Xd"]
            ]
            await send_fluid(update.message, random.choice(coger_fluidos))
            return

        elif any(x in texto for x in ['amor', 'bebe', 'bebé', 'mi rey', 'papi', 'cielo', 'hermosa', 'vida', 'corazón']):
            cariño_fluidos = [
                ["ay mi amor tú también me encantas 😘", "qué quieres que te haga? 💦"],
                ["bebé me derrites cuando me hablas así 🥺", "te grabo algo bonito? 🔥"],
                ["papi me pones mal con tus palabras 😈", "ven", "dime qué quieres de mí 💋"],
                ["mi rey me tienes loca 😏", "qué te hago para ponerte feliz? 💦 Xd"],
                ["corazón me encantas 😘", "te dedico mi próximo video? 🔥"],
                ["mi cielo me pones bien mal 🥺", "toda mojada x ti...", "qué hago? 💋 uwu"]
            ]
            await send_fluid(update.message, random.choice(cariño_fluidos))
            return

        elif any(x in texto for x in ['jaja', 'xd', 'jiji', 'jsjs', 'jsksks']):
            risas_fluidas = [
                ["JSKSKSSKS 😘", "de q te ríes bebé?"],
                ["Xd me haces reír 🔥", "qué pasó uwu"],
                ["jsksksksk amor 😏", "eres chistoso"],
                ["jeje 💕", "uwu me gusta tu risa", "JSKSKS"],
                ["JSKSKSKS papi 😘", "Xd qué es tan gracioso?"],
                ["xd XDDD", "me contagias la risa uwu"],
                ["JSKSKSSKSK", "ay me hiciste reír 🔥"]
            ]
            await send_fluid(update.message, random.choice(risas_fluidas))
            return

        elif any(x in texto for x in ['linda', 'bonita', 'hermosa', 'preciosa', 'guapa', 'sexy', 'cute']):
            coshita_fluidos = [
                ["aww coshita 🥺", "gracias mi rey"],
                ["JSKSKSKS coshita linda 😘", "uwu tú también"],
                ["ay coshita 💕", "me sonrojaste Xd"],
                ["uwu gracias bebé...", "tú eres un coshito 🔥"],
                ["JSKSKSSKS que coshita 🥺", "me dices cosas lindas"],
                ["aww Xd coshita 🥰", "me haces sentir bien"]
            ]
            await send_fluid(update.message, random.choice(coshita_fluidos))
            return

        elif any(x in texto for x in ['gracias', 'ok', 'vale', 'bueno', 'dale', 'perfecto', 'weno', 'okaa']):
            cierre_fluidos = [
                ["de nada mi rey 😘", "Xd cualquier coshita me avisas 💋"],
                ["a ti bebé 🔥", "uwu acá toy si necesitas algo"],
                ["weno amor 😏", "JSKSKS me hablas cuando quieras"],
                ["dale papi 💕", "uwu cuídate mucho Xd"],
                ["ya sabes mi rey 😘", "acá toy 24/7 uwu"],
                ["weno weno 😘", "Xd me avisas cualquier coshita 💋"]
            ]
            await send_fluid(update.message, random.choice(cierre_fluidos))
            return

        else:
            provoca_fluidos = [
                ["uff mi rey", "justo me agarraste cambiando 😏", "me acompañas o q? 💋"],
                ["papi llegaste rico 🔥", "ando bien prendida...", "quieres ver? 😈"],
                ["bebé me encanta tu timing 💦", "en un rato me voy a grabar", "te lo dedico? 🥵"],
                ["mi amor me cachaste sin nada puesto 😈", "aprovechas?", "o te lo pierdes? 🔥"],
                ["rey justo iba a portarme mal en cámara 🥵", "quieres ser mi cómplice? 💋"],
                ["mmm me tienes pensando cosas 🥺", "te cuento?", "o mejor te muestro? 😏"],
                ["ando de ganas bebé 🔥", "qué hacemos? 💦 Xd"],
                ["uff ando de ganas mal 😈", "me calmas tú?", "o me grabo? 💋"],
                ["bebé ando de ganas contigo 🥵", "dime qué quieres 💦 JSKSKS"]
            ]
            await send_fluid(update.message, random.choice(provoca_fluidos))
            return

    if user_id in PAIS_USUARIO:
        pais = PAIS_USUARIO[user_id]
        precio = PRECIOS_CRIPTO['bs'] if pais == 'Venezuela' else PRECIOS_CRIPTO['usdt']
        moneda = 'Bs' if pais == 'Venezuela' else 'USDT'

        if pais == 'Venezuela':
            await update.message.reply_text(
                f"💋 *Para {pais}:*\n\n"
                f"📱 *Pago Móvil:*\n"
                f"Banco: {PAGO_MOVIL['banco']}\n"
                f"Cédula: {PAGO_MOVIL['cedula']}\n"
                f"Teléfono: {PAGO_MOVIL['telefono']}\n"
                f"Monto: {precio} {moneda}\n\n"
                f"🔥 *Cripto:*\n"
                f"USDT: `{PRECIOS_CRIPTO['usdt']}`\n\n"
                f"Envía comprobante y te activo *VIP 15 min* 😈",
                reply_markup=get_volver()
            )
        else:
            await update.message.reply_text(
                f"💋 *Para {pais}:*\n\n"
                f"💎 *USDT:* `{precio}`\n\n"
                f"Envía hash y te activo *VIP 15 min* 😈",
                reply_markup=get_volver()
            )
    else:
        await update.message.reply_text("Primero elige tu país mi rey 😘", reply_markup=get_menu())

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "menu":
        await query.edit_message_text("💋 *YANABICITASA* 💋\n\n¿Qué quieres hacer mi rey?", reply_markup=get_menu())

    elif data.startswith("pais_"):
        pais_id = data.split("_")[1]
        PAIS_USUARIO[query.from_user.id] = PAISES[pais_id]
        await query.edit_message_text(f"Perfecto bebé 💋\n\nPaís: *{PAISES[pais_id]}*\n\n¿Qué quieres hacer?", reply_markup=get_menu())

    elif data == "comprar":
        user_id = query.from_user.id
        if user_id not in PAIS_USUARIO:
            await query.edit_message_text("Primero elige tu país mi rey 😘", reply_markup=get_menu())
            return

        pais = PAIS_USUARIO[user_id]
        precio = PRECIOS_CRIPTO['bs'] if pais == 'Venezuela' else PRECIOS_CRIPTO['usdt']
        moneda = 'Bs' if pais == 'Venezuela' else 'USDT'

        if pais == 'Venezuela':
            text = f"💎 *PREMIUM - {pais}*\n\n📱 *Pago Móvil:*\nBanco: {PAGO_MOVIL['banco']}\nCédula: {PAGO_MOVIL['cedula']}\nTeléfono: {PAGO_MOVIL['telefono']}\nMonto: {precio} {moneda}\n\n🔥 *Cripto:*\nUSDT: `{PRECIOS_CRIPTO['usdt']}`\n\nEnvía comprobante y te doy *15 min VIP* 😈"
        else:
            text = f"💎 *PREMIUM - {pais}*\n\n💰 *USDT:* `{precio}`\n\nEnvía hash y te activo *15 min VIP* 😈"

        await query.edit_message_text(text, reply_markup=get_volver())

    elif data == "packs":
        await query.edit_message_text("📸 *Packs disponibles:*\n\n🔥 Pack Básico - 5 USDT\n💦 Pack Premium - 10 USDT\n😈 Pack VIP - 20 USDT\n\nCompra PREMIUM primero y te paso catálogo completo 💋", reply_markup=get_volver())

    elif data == "chat":
        await query.edit_message_text("💋 *Chat Hot*\n\nCon PREMIUM tienes *15 min VIP* conmigo 😈\n\n¿Qué quieres que hagamos? 💦", reply_markup=get_volver())

async def activar_vip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id!= ADMIN_ID:
        return

    try:
        user_id = int(context.args[0])
        VIP_TEMPORAL[user_id] = datetime.now() + timedelta(minutes=15)
        DEMO_HOT.pop(user_id, None)

        current_jobs = context.job_queue.get_jobs_by_name(f"tease1_{user_id}") + context.job_queue.get_jobs_by_name(f"tease2_{user_id}")
        for job in current_jobs:
            job.schedule_removal()

        context.job_queue.run_once(auto_tease_vip, 600, data={'user_id': user_id}, name=f"tease_vip_{user_id}")

        await context.bot.send_message(user_id, "✅ *VIP ACTIVADO* 😈\n\nTienes *15 minutos* conmigo bebé\n\nHáblame rico 🔥")
        await update.message.reply_text(f"✅ VIP activado para {user_id}")
    except:
        await update.message.reply_text("Uso: /vip ID_DEL_CLIENTE")

async def quitar_vip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id!= ADMIN_ID:
        return
    try:
        user_id = int(context.args[0])
        VIP_TEMPORAL.pop(user_id, None)
        DEMO_HOT.pop(user_id, None)

        for job_name in [f"tease1_{user_id}", f"tease2_{user_id}", f"tease_vip_{user_id}"]:
            jobs = context.job_queue.get_jobs_by_name(job_name)
            for job in jobs:
                job.schedule_removal()

        await update.message.reply_text(f"❌ Usuario {user_id} sacado de VIP/DEMO")
    except:
        await update.message.reply_text("Uso: /unvip ID_DEL_CLIENTE")

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("vip", activar_vip))
    app.add_handler(CommandHandler("unvip", quitar_vip))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, responder))

    print("✅ Bot iniciado - Modo Chibola Fluida Activado")
    app.run_polling()
