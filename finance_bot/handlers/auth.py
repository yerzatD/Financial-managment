from telegram import ReplyKeyboardRemove, Update
from telegram.ext import ContextTypes, ConversationHandler

from ..api_client import APIClient, APIError
from ..keyboards import AUTH_MENU, MAIN_MENU
from ..states import States


def _client(context: ContextTypes.DEFAULT_TYPE) -> APIClient:
    return APIClient(context.bot_data["api_base_url"])


# ---------------- Registration ----------------


async def register_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        "Придумайте логин (username):", reply_markup=ReplyKeyboardRemove()
    )
    return States.REG_USERNAME


async def register_username(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["reg_username"] = update.message.text.strip()
    await update.message.reply_text("Введите email:")
    return States.REG_EMAIL


async def register_email(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["reg_email"] = update.message.text.strip()
    await update.message.reply_text("Придумайте пароль:")
    return States.REG_PASSWORD


async def register_password(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    password = update.message.text.strip()
    username = context.user_data.pop("reg_username")
    email = context.user_data.pop("reg_email")

    client = _client(context)
    try:
        await client.register(username, email, password)
    except APIError as e:
        await update.message.reply_text(f"⚠️ Ошибка регистрации: {e.detail}", reply_markup=AUTH_MENU)
        return ConversationHandler.END

    try:
        token_data = await client.login(username, password)
    except APIError as e:
        await update.message.reply_text(
            f"Регистрация прошла успешно, но авто-вход не удался: {e.detail}\nПопробуйте войти вручную.",
            reply_markup=AUTH_MENU,
        )
        return ConversationHandler.END

    context.bot_data["storage"].set_token(update.effective_user.id, token_data["access_token"])
    await update.message.reply_text("✅ Регистрация и вход выполнены!", reply_markup=MAIN_MENU)
    return ConversationHandler.END


# ---------------- Login ----------------


async def login_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Введите логин:", reply_markup=ReplyKeyboardRemove())
    return States.LOGIN_USERNAME


async def login_username(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["login_username"] = update.message.text.strip()
    await update.message.reply_text("Введите пароль:")
    return States.LOGIN_PASSWORD


async def login_password(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    username = context.user_data.pop("login_username")
    password = update.message.text.strip()

    client = _client(context)
    try:
        token_data = await client.login(username, password)
    except APIError as e:
        await update.message.reply_text(f"⚠️ Не удалось войти: {e.detail}", reply_markup=AUTH_MENU)
        return ConversationHandler.END

    context.bot_data["storage"].set_token(update.effective_user.id, token_data["access_token"])
    await update.message.reply_text("✅ Вход выполнен!", reply_markup=MAIN_MENU)
    return ConversationHandler.END


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Отменено.", reply_markup=AUTH_MENU)
    return ConversationHandler.END


async def logout(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    context.bot_data["storage"].clear_token(update.effective_user.id)
    await update.message.reply_text("Вы вышли из аккаунта.", reply_markup=AUTH_MENU)
