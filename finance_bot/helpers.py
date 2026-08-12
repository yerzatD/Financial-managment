from telegram import Update
from telegram.ext import ContextTypes

from .api_client import APIClient
from .keyboards import AUTH_MENU


async def get_authed_client(update: Update, context: ContextTypes.DEFAULT_TYPE) -> APIClient | None:
    """Возвращает APIClient с токеном пользователя, либо отправляет просьбу залогиниться и None."""
    storage = context.bot_data["storage"]
    token = storage.get_token(update.effective_user.id)
    if not token:
        await update.effective_message.reply_text(
            "Сначала войдите в аккаунт: нажмите «🔑 Войти» (или «🆕 Регистрация», если у вас нет аккаунта).",
            reply_markup=AUTH_MENU,
        )
        return None
    return APIClient(context.bot_data["api_base_url"], token=token)
