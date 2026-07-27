"""
Планировщик для бота Эпплджек.
Отправка слова дня в 9:15 и рецепта дня в 18:15.

Автор: MADAO81
Версия: 1.0
"""

import logging
import sqlite3
from telegram import Update
from telegram.ext import ContextTypes
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from bot.config import Config
from bot.services.ai_service import get_applejack_response

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()
DB_PATH = Config.DATA_DIR / "subscriptions.db"


def _get_connection():
    return sqlite3.connect(DB_PATH)


def _init_db():
    conn = _get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS subscriptions (
            chat_id INTEGER PRIMARY KEY,
            subscribed_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()


def add_chat(chat_id: int):
    _init_db()
    conn = _get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO subscriptions (chat_id) VALUES (?)", (chat_id,))
    conn.commit()
    conn.close()
    logger.info(f"📋 Чат {chat_id} добавлен для рассылки")


def remove_chat(chat_id: int):
    _init_db()
    conn = _get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM subscriptions WHERE chat_id = ?", (chat_id,))
    conn.commit()
    conn.close()
    logger.info(f"📋 Чат {chat_id} удалён из рассылки")


def get_active_chats():
    _init_db()
    conn = _get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT chat_id FROM subscriptions")
    rows = cursor.fetchall()
    conn.close()
    return [row[0] for row in rows]


async def subscribe_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    add_chat(chat_id)
    await update.message.reply_text(
        "🍎 *Ты подписался на ежедневные рассылки Эпплджек!*\n\n"
        "🤠 Каждый день в 9:15 я буду присылать тебе мудрость о трудолюбии,\n"
        "а в 18:15 — рецепт деревенской кухни!\n\n"
        "Чтобы отписаться, напиши /unsubscribe 🍎",
        parse_mode="Markdown"
    )


async def unsubscribe_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    remove_chat(chat_id)
    await update.message.reply_text(
        "😢 *Ты отписался от рассылок!*\n\n"
        "Если захочешь вернуться — напиши /subscribe 🍎",
        parse_mode="Markdown"
    )


async def send_word(app):
    active_chats = get_active_chats()
    if not active_chats:
        return
    logger.info(f"🍎 Отправка слова дня в {len(active_chats)} чатов...")
    response = await get_applejack_response(
        user_message="Дай короткую, мудрую фразу о трудолюбии, честности или помощи ближнему. Говори как Эпплджек.",
        mood_description="happy"
    )
    if not response:
        response = "🍎 *Слово от Эпплджек:* Труд кормит, а лень портит. Помни это, ёкарный бабай! 🤠"
    for chat_id in active_chats:
        try:
            await app.bot.send_message(chat_id=chat_id, text=response, parse_mode="Markdown")
            logger.info(f"✅ Слово дня отправлено в чат {chat_id}")
        except Exception as e:
            logger.error(f"❌ Ошибка отправки в чат {chat_id}: {e}")
            if "bot was blocked" in str(e) or "chat not found" in str(e):
                remove_chat(chat_id)


async def send_recipe(app):
    active_chats = get_active_chats()
    if not active_chats:
        return
    logger.info(f"🥧 Отправка рецепта дня в {len(active_chats)} чатов...")
    response = await get_applejack_response(
        user_message="Дай простой и вкусный деревенский рецепт с яблоками. Говори как Эпплджек.",
        mood_description="happy"
    )
    if not response:
        response = "🥧 *Рецепт от Эпплджек:* Яблочный пирог — простое и вкусное блюдо! Главное — хорошие яблоки и немного терпения. 🍎"
    for chat_id in active_chats:
        try:
            await app.bot.send_message(chat_id=chat_id, text=response, parse_mode="Markdown")
            logger.info(f"✅ Рецепт дня отправлен в чат {chat_id}")
        except Exception as e:
            logger.error(f"❌ Ошибка отправки в чат {chat_id}: {e}")
            if "bot was blocked" in str(e) or "chat not found" in str(e):
                remove_chat(chat_id)


def start_scheduler(app):
    try:
        _init_db()

        default_chats = getattr(Config, 'DEFAULT_CHATS', "")
        if default_chats:
            for chat_id in default_chats.split(","):
                try:
                    chat_id = int(chat_id.strip())
                    add_chat(chat_id)
                    logger.info(f"✅ Автоматически добавлен чат: {chat_id}")
                except Exception as e:
                    logger.error(f"❌ Ошибка добавления чата {chat_id}: {e}")

        scheduler.add_job(
            send_word,
            CronTrigger(hour=9, minute=15),
            args=[app],
            id='applejack_word',
            replace_existing=True
        )

        scheduler.add_job(
            send_recipe,
            CronTrigger(hour=18, minute=15),
            args=[app],
            id='applejack_recipe',
            replace_existing=True
        )

        scheduler.start()
        logger.info("✅ Планировщик Эпплджек запущен: слово дня в 9:15, рецепт дня в 18:15")

    except Exception as e:
        logger.error(f"❌ Ошибка при запуске планировщика: {e}")
