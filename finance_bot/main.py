import logging

from telegram import Update
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

from .config import load_config
from .handlers import auth, deposits, reports, transactions
from .keyboards import AUTH_MENU, MAIN_MENU
from .states import States
from .storage import TokenStorage

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    storage: TokenStorage = context.bot_data["storage"]
    token = storage.get_token(update.effective_user.id)
    if token:
        await update.message.reply_text("С возвращением! Выберите действие:", reply_markup=MAIN_MENU)
    else:
        await update.message.reply_text(
            "👋 Привет! Я бот для управления личными финансами (AI Finance Manager).\n\n"
            "Войдите или зарегистрируйтесь, чтобы начать.",
            reply_markup=AUTH_MENU,
        )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Используйте кнопки меню внизу экрана.\n\n"
        "Команды:\n"
        "/start — начать / открыть меню\n"
        "/reports — история AI-отчётов\n"
        "/report_view <id> — посмотреть отчёт целиком\n"
        "/cancel — отменить текущее действие"
    )


async def unknown_text(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Не понимаю 🤔 Используйте меню ниже.")


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.error("Unhandled exception while processing update %s", update, exc_info=context.error)


def build_application() -> Application:
    config = load_config()
    if not config.bot_token:
        raise RuntimeError(
            "BOT_TOKEN не задан. Укажите его в .env (см. .env.example) или переменной окружения."
        )

    application = Application.builder().token(config.bot_token).build()
    application.bot_data["storage"] = TokenStorage(config.tokens_file)
    application.bot_data["api_base_url"] = config.api_base_url

    # --- basic commands ---
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("reports", reports.list_report_history))
    application.add_handler(CommandHandler("report_view", reports.view_report))
    application.add_handler(MessageHandler(filters.Regex("^🚪 Выйти$"), auth.logout))

    # --- registration ---
    register_conv = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^🆕 Регистрация$"), auth.register_start)],
        states={
            States.REG_USERNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, auth.register_username)],
            States.REG_EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, auth.register_email)],
            States.REG_PASSWORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, auth.register_password)],
        },
        fallbacks=[CommandHandler("cancel", auth.cancel)],
    )

    # --- login ---
    login_conv = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^🔑 Войти$"), auth.login_start)],
        states={
            States.LOGIN_USERNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, auth.login_username)],
            States.LOGIN_PASSWORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, auth.login_password)],
        },
        fallbacks=[CommandHandler("cancel", auth.cancel)],
    )

    # --- add transaction ---
    add_tx_conv = ConversationHandler(
        entry_points=[
            MessageHandler(filters.Regex("^➕ Добавить транзакцию$"), transactions.add_tx_start)
        ],
        states={
            States.TX_TYPE: [CallbackQueryHandler(transactions.tx_type_chosen, pattern="^tx_type:")],
            States.TX_AMOUNT: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, transactions.tx_amount_entered)
            ],
            States.TX_CATEGORY: [CallbackQueryHandler(transactions.tx_category_chosen, pattern="^tx_cat:")],
            States.TX_DESCRIPTION: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, transactions.tx_description_entered)
            ],
        },
        fallbacks=[CommandHandler("cancel", transactions.tx_cancel)],
        per_message=False,
    )

    # --- add deposit ---
    add_dep_conv = ConversationHandler(
        entry_points=[
            MessageHandler(filters.Regex("^➕ Депозит$"), deposits.add_deposit_start),
            CommandHandler("add_deposit", deposits.add_deposit_start),
        ],
        states={
            States.DEP_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, deposits.dep_name_entered)],
            States.DEP_CATEGORY: [CallbackQueryHandler(deposits.dep_category_chosen, pattern="^dep_cat:")],
            States.DEP_LIMIT: [MessageHandler(filters.TEXT & ~filters.COMMAND, deposits.dep_limit_entered)],
            States.DEP_START: [MessageHandler(filters.TEXT & ~filters.COMMAND, deposits.dep_start_entered)],
            States.DEP_END: [MessageHandler(filters.TEXT & ~filters.COMMAND, deposits.dep_end_entered)],
        },
        fallbacks=[CommandHandler("cancel", deposits.dep_cancel)],
        per_message=False,
    )

    # --- AI report ---
    report_conv = ConversationHandler(
        entry_points=[MessageHandler(filters.Regex("^🤖 AI отчёт$"), reports.report_menu)],
        states={
            States.REPORT_MENU: [CallbackQueryHandler(reports.report_period_chosen, pattern="^report:")],
            States.REPORT_FROM: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, reports.report_from_entered)
            ],
            States.REPORT_TO: [MessageHandler(filters.TEXT & ~filters.COMMAND, reports.report_to_entered)],
        },
        fallbacks=[CommandHandler("cancel", reports.report_cancel)],
        per_message=False,
    )

    application.add_handler(register_conv)
    application.add_handler(login_conv)
    application.add_handler(add_tx_conv)
    application.add_handler(add_dep_conv)
    application.add_handler(report_conv)

    # --- plain menu buttons ---
    application.add_handler(MessageHandler(filters.Regex("^💰 Баланс$"), transactions.show_balance))
    application.add_handler(MessageHandler(filters.Regex("^📊 Сводка$"), transactions.show_summary))
    application.add_handler(MessageHandler(filters.Regex("^📜 История$"), transactions.show_history))
    application.add_handler(MessageHandler(filters.Regex("^🏦 Депозиты$"), deposits.show_deposits))

    # --- delete buttons ---
    application.add_handler(
        CallbackQueryHandler(transactions.delete_transaction_callback, pattern="^tx_del:")
    )
    application.add_handler(CallbackQueryHandler(deposits.delete_deposit_callback, pattern="^dep_del:"))

    # --- fallback ---
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, unknown_text))

    application.add_error_handler(error_handler)

    return application


def main() -> None:
    application = build_application()
    logger.info("Bot started, polling for updates...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
