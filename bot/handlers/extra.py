"""
Дополнительные команды для бота Эпплджек.
Команды: /advice, /recipe, /farm, /motivate, /truth, /family

Автор: MADAO81
Версия: 1.4 — усиленные fallback-ответы
"""

import logging
import random
from telegram import Update
from telegram.ext import ContextTypes
from bot.services.ai_service import get_applejack_response
from bot.services.recipe_service import RecipeService
from bot.utils.time_utils import is_working_hours, get_working_status_message

logger = logging.getLogger(__name__)

recipe_service = RecipeService()

# === ЛОКАЛЬНЫЕ FALLBACK-ОТВЕТЫ ===
FALLBACK_ADVICE = [
    "🍎 *Совет от Эпплджек:*\n\nЁкарный бабай, если взялся за дело — делай его до конца, не бросай на полпути. Честность — она дороже золота, я ж!",
    "🍎 *Совет от Эпплджек:*\n\nТруд кормит, а лень портит. Помни это, кум! Если не знаешь, с чего начать — начни с малого.",
    "🍎 *Совет от Эпплджек:*\n\nДержи слово, что дал — и люди к тебе потянутся. А если обещал — сделай, даже если трудно.",
]

FALLBACK_FARM = [
    "🌾 *Совет по хозяйству:*\n\nЗемлю любить надо, я ж! Без любви и ухода — ничего не вырастет. Поливай вовремя, рыхли, и урожай будет годный!",
    "🌾 *Совет по хозяйству:*\n\nСамое главное — не лениться! Каждый день по чуть-чуть, и огород будет радовать. Удобряй, поливай, и всё получится!",
]

FALLBACK_MOTIVATE = [
    "💪 *Слова от Эпплджек:*\n\nТю! Не вешай нос, ёкарный бабай! Ты сильнее, чем думаешь. Вставай, отряхнись и иди вперёд — у тебя всё получится!",
    "💪 *Слова от Эпплджек:*\n\nТрудности — они как сорняки: если не выдернуть вовремя, задушат урожай. Борись, и победа будет за тобой!",
]

FALLBACK_TRUTH = [
    "🗣️ *Правда от Эпплджек:*\n\nПравду говорю: честность — она как яблоко. Если одно гнилое — портит весь урожай. Будь честен с собой и с другими.",
    "🗣️ *Правда от Эпплджек:*\n\nПрямо скажу: врать — себе дороже. Всегда лучше сказать правду, даже если она горькая. Зато совесть чиста!",
]

FALLBACK_FAMILY = [
    "👨‍👩‍👧‍👦 *Семья Эпплджек:*\n\nМоя семья — это ферма «Сладкое Яблоко». Там живут моя бабушка Гренни, брат Биг Макинтош и сестрёнка Эппл Блум. Мы всегда вместе, всегда помогаем друг другу. Семья — это главное, ёкарный бабай! 🍎",
    "👨‍👩‍👧‍👦 *Семья Эпплджек:*\n\nНаша ферма — это труд, любовь и традиции. Гренни учила меня всему, что знает. Мы вместе собираем урожай, печём пироги и держимся друг за друга. Я горжусь своей семьёй!",
]


async def _get_fallback_response(command_type: str) -> str:
    """Возвращает случайный fallback-ответ для команды."""
    fallbacks = {
        'advice': FALLBACK_ADVICE,
        'farm': FALLBACK_FARM,
        'motivate': FALLBACK_MOTIVATE,
        'truth': FALLBACK_TRUTH,
        'family': FALLBACK_FAMILY,
    }
    return random.choice(fallbacks.get(command_type, FALLBACK_ADVICE))


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
            await update.message.reply_text(await _get_fallback_response('advice'), parse_mode="Markdown")
    except Exception as e:
        logger.error(f"❌ Advice error: {e}")
        await status_message.edit_text(await _get_fallback_response('advice'), parse_mode="Markdown")


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
            recipes = recipe_service.search_recipes(query)
            if recipes:
                await status_message.delete()
                await update.message.reply_text(
                    f"🍎 Нашла рецепт по запросу '{query}':\n\n"
                    + recipe_service.format_recipe(recipes[0]),
                    parse_mode="Markdown"
                )
                return
            else:
                await status_message.delete()
                await update.message.reply_text(
                    f"😅 Не нашла рецепт по запросу '{query}'. Попробуй другое название или категорию!\n\n"
                    "Доступные категории:\n"
                    f"{', '.join(recipe_service.get_categories())}",
                    parse_mode="Markdown"
                )
                return

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
        await status_message.edit_text("🍎 Ошибка! Попробуй позже.")


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
            await update.message.reply_text(await _get_fallback_response('farm'), parse_mode="Markdown")
    except Exception as e:
        logger.error(f"❌ Farm error: {e}")
        await status_message.edit_text(await _get_fallback_response('farm'), parse_mode="Markdown")


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
            await update.message.reply_text(await _get_fallback_response('motivate'), parse_mode="Markdown")
    except Exception as e:
        logger.error(f"❌ Motivate error: {e}")
        await status_message.edit_text(await _get_fallback_response('motivate'), parse_mode="Markdown")


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
            await update.message.reply_text(await _get_fallback_response('truth'), parse_mode="Markdown")
    except Exception as e:
        logger.error(f"❌ Truth error: {e}")
        await status_message.edit_text(await _get_fallback_response('truth'), parse_mode="Markdown")


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
            await update.message.reply_text(await _get_fallback_response('family'), parse_mode="Markdown")
    except Exception as e:
        logger.error(f"❌ Family error: {e}")
        await status_message.edit_text(await _get_fallback_response('family'), parse_mode="Markdown")
