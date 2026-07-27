"""
Дополнительные команды для бота Эпплджек.
Команды: /advice, /recipe, /farm, /motivate, /truth, /family

Автор: MADAO81
Версия: 1.3 — улучшенный поиск рецептов
"""

import logging
from telegram import Update
from telegram.ext import ContextTypes
from bot.services.ai_service import get_applejack_response
from bot.services.recipe_service import RecipeService
from bot.utils.time_utils import is_working_hours, get_working_status_message

logger = logging.getLogger(__name__)

recipe_service = RecipeService()

async def advice_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_working_hours():
        if update.message.chat.type == "private":
            await update.message.reply_text(get_working_status_message())
        return

    args = context.args
    query = " ".join(args) if args else "жизненную ситуацию"

    status_message = await update.message.reply_text("🤠 Дай-ка подумать...")

    try:
        response = await get_applejack_response(
            user_message=f"Пользователь просит честный и практичный совет: {query}. Говори как Эпплджек.",
            mood_description="happy"
        )

        await status_message.delete()
        if response:
            await update.message.reply_text(f"🤠 *Совет от Эпплджек:*\n\n{response}", parse_mode="Markdown")
        else:
            await update.message.reply_text("🍎 Не смогла придумать совет, ёкарный бабай! Попробуй ещё раз.")
    except Exception as e:
        logger.error(f"❌ Advice error: {e}")
        await status_message.edit_text("😅 Ошибка! Попробуй позже.")

async def recipe_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_working_hours():
        if update.message.chat.type == "private":
            await update.message.reply_text(get_working_status_message())
        return

    args = context.args
    query = " ".join(args).strip() if args else None

    status_message = await update.message.reply_text("🥧 Сейчас поищу рецепт...")

    try:
        if query:
            # Ищем по названию или категории через улучшенный поиск
            recipes = recipe_service.search_recipes(query)
            
            if recipes:
                # Если нашли несколько — показываем первый
                await status_message.delete()
                await update.message.reply_text(
                    f"🍎 Нашла рецепт по запросу '{query}':\n\n"
                    + recipe_service.format_recipe(recipes[0]),
                    parse_mode="Markdown"
                )
                return
            else:
                # Если ничего не найдено
                await status_message.delete()
                await update.message.reply_text(
                    f"😅 Не нашла рецепт по запросу '{query}'. Попробуй другое название или категорию!\n\n"
                    "Доступные категории:\n"
                    f"{', '.join(recipe_service.get_categories())}",
                    parse_mode="Markdown"
                )
                return

        # Если без аргументов — случайный рецепт
        recipe = recipe_service.get_random_recipe()
        if recipe:
            await status_message.delete()
            await update.message.reply_text(
                recipe_service.format_recipe(recipe),
                parse_mode="Markdown"
            )
        else:
            await status_message.edit_text("🍎 Не нашла рецептов в базе! Добавлю скоро.")

    except Exception as e:
        logger.error(f"❌ Recipe error: {e}")
        await status_message.edit_text("😅 Ошибка! Попробуй позже.")

async def farm_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_working_hours():
        if update.message.chat.type == "private":
            await update.message.reply_text(get_working_status_message())
        return

    args = context.args
    query = " ".join(args) if args else "хозяйство"

    status_message = await update.message.reply_text("🌾 Дай-ка подумаю о хозяйстве...")

    try:
        response = await get_applejack_response(
            user_message=f"Пользователь просит совет по хозяйству: {query}. Говори как Эпплджек.",
            mood_description="happy"
        )

        await status_message.delete()
        if response:
            await update.message.reply_text(f"🌾 *Совет по хозяйству от Эпплджек:*\n\n{response}", parse_mode="Markdown")
        else:
            await update.message.reply_text("🍎 Не придумала совет по хозяйству! Попробуй ещё раз.")
    except Exception as e:
        logger.error(f"❌ Farm error: {e}")
        await status_message.edit_text("😅 Ошибка! Попробуй позже.")

async def motivate_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_working_hours():
        if update.message.chat.type == "private":
            await update.message.reply_text(get_working_status_message())
        return

    status_message = await update.message.reply_text("💪 Сейчас я тебя подбодрю...")

    try:
        response = await get_applejack_response(
            user_message="Скажи ободряющую фразу. Говори как Эпплджек.",
            mood_description="happy"
        )

        await status_message.delete()
        if response:
            await update.message.reply_text(f"💪 *Слова от Эпплджек:*\n\n{response}", parse_mode="Markdown")
        else:
            await update.message.reply_text("🍎 Не смогла подбодрить! Попробуй ещё раз.")
    except Exception as e:
        logger.error(f"❌ Motivate error: {e}")
        await status_message.edit_text("😅 Ошибка! Попробуй позже.")

async def truth_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_working_hours():
        if update.message.chat.type == "private":
            await update.message.reply_text(get_working_status_message())
        return

    status_message = await update.message.reply_text("🗣️ Сейчас я скажу правду...")

    try:
        response = await get_applejack_response(
            user_message="Скажи честную, прямую фразу. Говори как Эпплджек.",
            mood_description="happy"
        )

        await status_message.delete()
        if response:
            await update.message.reply_text(f"🗣️ *Правда от Эпплджек:*\n\n{response}", parse_mode="Markdown")
        else:
            await update.message.reply_text("🍎 Не придумала правду! Попробуй ещё раз.")
    except Exception as e:
        logger.error(f"❌ Truth error: {e}")
        await status_message.edit_text("😅 Ошибка! Попробуй позже.")

async def family_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_working_hours():
        if update.message.chat.type == "private":
            await update.message.reply_text(get_working_status_message())
        return

    status_message = await update.message.reply_text("👨‍👩‍👧‍👦 Сейчас я расскажу о своей семье...")

    try:
        response = await get_applejack_response(
            user_message="Расскажи о своей семье и ферме. Говори как Эпплджек.",
            mood_description="happy"
        )

        await status_message.delete()
        if response:
            await update.message.reply_text(f"👨‍👩‍👧‍👦 *Семья Эпплджек:*\n\n{response}", parse_mode="Markdown")
        else:
            await update.message.reply_text("🍎 Не смогла рассказать о семье! Попробуй ещё раз.")
    except Exception as e:
        logger.error(f"❌ Family error: {e}")
        await status_message.edit_text("😅 Ошибка! Попробуй позже.")
