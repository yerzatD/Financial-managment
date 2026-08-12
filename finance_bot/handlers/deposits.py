from datetime import datetime

from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

from ..api_client import APIError
from ..helpers import get_authed_client
from ..keyboards import CATEGORY_LABELS, MAIN_MENU, categories_keyboard, deposits_list_keyboard
from ..states import States


def _parse_date(text: str) -> str | None:
    try:
        return datetime.strptime(text.strip(), "%Y-%m-%d").date().isoformat()
    except ValueError:
        return None


async def show_deposits(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    client = await get_authed_client(update, context)
    if client is None:
        return
    try:
        deposits = await client.list_deposits()
    except APIError as e:
        await update.message.reply_text(f"⚠️ Ошибка: {e.detail}")
        return

    if not deposits:
        await update.message.reply_text(
            "У вас пока нет депозитов (бюджетных лимитов).\nНажмите «➕ Депозит», чтобы создать."
        )
        return

    lines = []
    for d in deposits:
        cat = CATEGORY_LABELS.get(d.get("category"), d.get("category"))
        status = "🔴 превышен" if d["is_exceeded"] else "🟢 в норме"
        lines.append(
            f"«{d['name']}» ({cat})\n"
            f"  Лимит: {d['limit_amount']:.2f} | Потрачено: {d['spent_amount']:.2f} | "
            f"Остаток: {d['remaining_amount']:.2f} | {status}\n"
            f"  Период: {d['start_date']} — {d['end_date']}"
        )
    await update.message.reply_text("\n\n".join(lines))

    keyboard = deposits_list_keyboard(deposits)
    if keyboard:
        await update.message.reply_text("Нажмите, чтобы удалить депозит:", reply_markup=keyboard)


# ---------------- Add deposit conversation ----------------


async def add_deposit_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    client = await get_authed_client(update, context)
    if client is None:
        return ConversationHandler.END
    await update.message.reply_text("Введите название депозита (лимита), например «Еда на месяц»:")
    return States.DEP_NAME


async def dep_name_entered(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data["dep_name"] = update.message.text.strip()
    await update.message.reply_text(
        "Выберите категорию (или «Без категории» для общего лимита):",
        reply_markup=categories_keyboard("dep_cat"),
    )
    return States.DEP_CATEGORY


async def dep_category_chosen(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    category = query.data.split(":", 1)[1]
    context.user_data["dep_category"] = None if category == "none" else category
    await query.edit_message_text("Введите лимит суммы (число):")
    return States.DEP_LIMIT


async def dep_limit_entered(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = update.message.text.strip().replace(",", ".")
    try:
        limit_amount = float(text)
        if limit_amount <= 0:
            raise ValueError
    except ValueError:
        await update.message.reply_text("Введите положительное число.")
        return States.DEP_LIMIT
    context.user_data["dep_limit"] = limit_amount
    await update.message.reply_text("Введите дату начала периода (в формате YYYY-MM-DD):")
    return States.DEP_START


async def dep_start_entered(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    start_date = _parse_date(update.message.text)
    if start_date is None:
        await update.message.reply_text("Неверный формат. Введите дату как 2026-08-01.")
        return States.DEP_START
    context.user_data["dep_start"] = start_date
    await update.message.reply_text("Введите дату окончания периода (YYYY-MM-DD):")
    return States.DEP_END


async def dep_end_entered(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    end_date = _parse_date(update.message.text)
    if end_date is None:
        await update.message.reply_text("Неверный формат. Введите дату как 2026-08-31.")
        return States.DEP_END

    client = await get_authed_client(update, context)
    if client is None:
        return ConversationHandler.END

    name = context.user_data.pop("dep_name")
    category = context.user_data.pop("dep_category")
    limit_amount = context.user_data.pop("dep_limit")
    start_date = context.user_data.pop("dep_start")

    try:
        await client.create_deposit(name, category, limit_amount, start_date, end_date)
    except APIError as e:
        await update.message.reply_text(f"⚠️ Ошибка: {e.detail}", reply_markup=MAIN_MENU)
        return ConversationHandler.END

    await update.message.reply_text(f"✅ Депозит «{name}» создан.", reply_markup=MAIN_MENU)
    return ConversationHandler.END


async def dep_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Отменено.", reply_markup=MAIN_MENU)
    return ConversationHandler.END


async def delete_deposit_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    dep_id = int(query.data.split(":", 1)[1])

    client = await get_authed_client(update, context)
    if client is None:
        return
    try:
        await client.delete_deposit(dep_id)
    except APIError as e:
        await query.edit_message_text(f"⚠️ Ошибка удаления: {e.detail}")
        return
    await query.edit_message_text("🗑 Депозит удалён.")
