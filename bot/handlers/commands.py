import logging
from telegram import Update
from telegram.ext import ContextTypes
from bot.services.weather_service import WeatherService
from bot.utils.time_utils import is_working_hours, get_working_status_message
from bot.core.constants import VERSION

logger = logging.getLogger(__name__)
weather_service = WeatherService()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_working_hours():
        if update.message.chat.type == "private":
            await update.message.reply_text(get_working_status_message())
        return

    text = (
        "🍎 *Привет! Я Эпплджек!*\n\n"
        "🤠 Я — честная, трудолюбивая пони с фермы «Сладкое Яблоко». Я всегда говорю правду, даже если она горькая.\n\n"
        "📋 *Вот что я умею:*\n"
        "/help — список всех команд 📖\n"
        "/weather — погода 🌤️\n"
        "/advice — честный и практичный совет 🤠\n"
        "/recipe — деревенский рецепт 🥧\n"
        "/farm — совет по хозяйству 🌾\n"
        "/motivate — подбодрить 💪\n"
        "/truth — сказать правду в глаза 🗣️\n"
        "/family — о семье и традициях 👨‍👩‍👧‍👦\n"
        "/subscribe — подписаться на рассылки 📬\n"
        "/unsubscribe — отписаться\n"
        "/cleardata — очистить историю 🗑️\n\n"
        f"🤖 *Версия:* {VERSION}"
    )
    await update.message.reply_text(text, parse_mode="Markdown")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_working_hours():
        if update.message.chat.type == "private":
            await update.message.reply_text(get_working_status_message())
        return

    text = (
        "📖 *Команды Эпплджек:*\n\n"
        "/start — начать общение 🍎\n"
        "/help — эта справка 📖\n"
        "/weather — погода 🌤️\n"
        "/advice — честный совет 🤠\n"
        "/recipe — деревенский рецепт 🥧\n"
        "/farm — совет по хозяйству 🌾\n"
        "/motivate — подбодрить 💪\n"
        "/truth — правда в глаза 🗣️\n"
        "/family — о семье и традициях 👨‍👩‍👧‍👦\n"
        "/subscribe — подписаться на рассылки 📬\n"
        "/unsubscribe — отписаться\n"
        "/cleardata — очистить историю 🗑️\n\n"
        "✨ Я работаю с 9:00 до 22:00 ежедневно 🍎"
    )
    await update.message.reply_text(text, parse_mode="Markdown")

async def weather_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_working_hours():
        if update.message.chat.type == "private":
            await update.message.reply_text(get_working_status_message())
        return

    args = context.args
    city = " ".join(args) if args else None
    status_message = await update.message.reply_text("🌤️ Смотрю в окно...")

    try:
        if city:
            weather = await weather_service.get_weather_by_city(city)
            if not weather:
                await status_message.edit_text(f"😅 Не могу найти город '{city}'!")
                return
        else:
            weather = await weather_service.get_weather()

        if weather:
            weather_text = weather_service.get_weather_text(weather)
            await status_message.delete()
            await update.message.reply_text(f"🌤️ *Погода*\n\n{weather_text}", parse_mode="Markdown")
        else:
            await status_message.edit_text("😅 Не могу узнать погоду!")
    except Exception as e:
        logger.error(f"❌ Weather error: {e}")
        await status_message.edit_text("😅 Ошибка! Попробуй позже.")
