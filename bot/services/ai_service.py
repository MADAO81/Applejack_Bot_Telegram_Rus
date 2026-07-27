"""
AI сервис для бота Эпплджек (DeepSeek V4).

Автор: MADAO81
Версия: 1.0
"""

import logging
from typing import Optional, List
from openai import OpenAI
from bot.config import Config
from bot.core.constants import SYSTEM_PROMPT

logger = logging.getLogger(__name__)

# Инициализация клиента DeepSeek
client = OpenAI(
    api_key=Config.DEEPSEEK_API_KEY,
    base_url="https://api.deepseek.com/v1"
)

async def get_applejack_response(
    user_message: str,
    mood_description: str = "happy",
    context_history: Optional[List[dict]] = None
) -> Optional[str]:
    try:
        system_prompt = SYSTEM_PROMPT

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "system", "content": f"Your current mood is: {mood_description}"}
        ]

        if context_history:
            messages.extend(context_history[-10:])

        messages.append({"role": "user", "content": user_message})

        response = client.chat.completions.create(
            model=Config.DEEPSEEK_MODEL,
            messages=messages,
            max_tokens=Config.DEEPSEEK_MAX_TOKENS,
            temperature=Config.DEEPSEEK_TEMPERATURE
        )

        if response.choices and len(response.choices) > 0:
            return response.choices[0].message.content.strip()
        return None

    except Exception as e:
        logger.error(f"❌ DeepSeek error: {e}")
        return None
