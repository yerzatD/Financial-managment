from datetime import date, datetime

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes, ConversationHandler

from ..api_client import APIError
from ..helpers import get_authed_client
from ..keyboards import MAIN_MENU
from ..states import States


def _report_period_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [InlineKeyboardButton("За всё время", callback_data="report:all")],
            [InlineKeyboardButton("Этот месяц", callback_data="report:month")],
            [InlineKeyboardButton("Свой период", callback_data="report:custom")],
        ]
    )


async def report_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    client = await get_authed_client(update, context)
    if client is None:
        return ConversationHandler.END
    await update.message.reply_text(
        "Выберите период для AI-отчёта:", reply_markup=_report_period_keyboard()
    )
    return States.REPORT_MENU


async def _generate_and_send(
    update: Update, context: ContextTypes.DEFAULT_TYPE, date_from: str | None, date_to: str | None
) -> None:
    chat_id = update.effective_chat.id
    client = await get_authed_client(update, context)
    if client is None:
        return
    await context.bot.send_message(chat_id, "⏳ Генерирую отчёт, это может занять до минуты...")
    try:
        report = await client.generate_report(date_from, date_to)
    except APIError as e:
        await context.bot.send_message(chat_id, f"⚠️ Ошибка: {e.detail}")
        return
    await context.bot.send_message(chat_id, report["report"])


async def report_period_chosen(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    choice = query.data.split(":", 1)[1]

    if choice == "all":
        await query.edit_message_text("Готовлю отчёт за всё время...")
        await _generate_and_send(update, context, None, None)
        return ConversationHandler.END

    if choice == "month":
        today = date.today()
        date_from = today.replace(day=1).isoformat()
        await query.edit_message_text("Готовлю отчёт за этот месяц...")
        await _generate_and_send(update, context, date_from, today.isoformat())
        return ConversationHandler.END

    await query.edit_message_text("Введите дату начала периода (YYYY-MM-DD):")
    return States.REPORT_FROM


async def report_from_entered(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        d = datetime.strptime(update.message.text.strip(), "%Y-%m-%d").date()
    except ValueError:
        await update.message.reply_text("Неверный формат. Введите дату как 2026-01-01.")
        return States.REPORT_FROM
    context.user_data["report_from"] = d.isoformat()
    await update.message.reply_text("Введите дату окончания периода (YYYY-MM-DD):")
    return States.REPORT_TO


async def report_to_entered(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    try:
        d = datetime.strptime(update.message.text.strip(), "%Y-%m-%d").date()
    except ValueError:
        await update.message.reply_text("Неверный формат. Введите дату как 2026-01-31.")
        return States.REPORT_TO
    date_from = context.user_data.pop("report_from")
    await update.message.reply_text("⏳ Генерирую отчёт...")
    await _generate_and_send(update, context, date_from, d.isoformat())
    return ConversationHandler.END


async def report_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Отменено.", reply_markup=MAIN_MENU)
    return ConversationHandler.END


# ---------------- Report history ----------------


async def list_report_history(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    client = await get_authed_client(update, context)
    if client is None:
        return
    try:
        history = await client.list_reports()
    except APIError as e:
        await update.message.reply_text(f"⚠️ Ошибка: {e.detail}")
        return

    if not history:
        await update.message.reply_text("Отчётов пока нет.")
        return

    lines = []
    for r in history[:10]:
        created = r["created_at"][:10]
        period = f"{r.get('period_from') or '—'} — {r.get('period_to') or '—'}"
        lines.append(f"#{r['id']} | {created} | период: {period} | транзакций: {r['transactions_analyzed']}")
    lines.append("\nЧтобы посмотреть отчёт целиком: /report_view <id>")
    await update.message.reply_text("\n".join(lines))


async def view_report(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.args:
        await update.message.reply_text("Использование: /report_view <id>")
        return
    try:
        report_id = int(context.args[0])
    except ValueError:
        await update.message.reply_text("ID должен быть числом.")
        return

    client = await get_authed_client(update, context)
    if client is None:
        return
    try:
        report = await client.get_report_by_id(report_id)
    except APIError as e:
        await update.message.reply_text(f"⚠️ Ошибка: {e.detail}")
        return
    await update.message.reply_text(report["report"])
