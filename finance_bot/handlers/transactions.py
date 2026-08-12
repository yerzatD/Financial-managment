from datetime import datetime

from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler

from ..api_client import APIError
from ..helpers import get_authed_client
from ..keyboards import (
    CATEGORY_LABELS,
    MAIN_MENU,
    categories_keyboard,
    transaction_type_keyboard,
    transactions_list_keyboard,
)
from ..states import States


async def show_balance(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    client = await get_authed_client(update, context)
    if client is None:
        return
    try:
        me = await client.get_me()
    except APIError as e:
        await update.message.reply_text(f"⚠️ Ошибка: {e.detail}")
        return
    await update.message.reply_text(f"💰 Текущий баланс: {me['balance']:.2f}")


async def show_summary(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    client = await get_authed_client(update, context)
    if client is None:
        return
    try:
        summary = await client.transaction_summary()
    except APIError as e:
        await update.message.reply_text(f"⚠️ Ошибка: {e.detail}")
        return

    lines = [
        f"📊 Доходы: {summary['total_income']:.2f}",
        f"📊 Расходы: {summary['total_expense']:.2f}",
        f"📊 Баланс: {summary['balance']:.2f}",
        f"📊 Транзакций всего: {summary['transaction_count']}",
        "",
        "По категориям:",
    ]
    for cat, val in summary["categories_summary"].items():
        label = CATEGORY_LABELS.get(cat, cat)
        lines.append(f"  {label}: {val:.2f}")
    await update.message.reply_text("\n".join(lines))


async def show_history(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    client = await get_authed_client(update, context)
    if client is None:
        return
    try:
        txs = await client.list_transactions()
    except APIError as e:
        await update.message.reply_text(f"⚠️ Ошибка: {e.detail}")
        return

    if not txs:
        await update.message.reply_text("Транзакций пока нет.")
        return

    txs = sorted(txs, key=lambda t: t["spent_at"], reverse=True)
    lines = []
    for t in txs[:20]:
        sign = "+" if t["type"] == "income" else "-"
        cat = CATEGORY_LABELS.get(t.get("category"), t.get("category"))
        date_str = t["spent_at"][:10]
        lines.append(f"{date_str} | {sign}{t['amount']:.2f} | {cat} | {t.get('description') or ''}")
    await update.message.reply_text("\n".join(lines))

    keyboard = transactions_list_keyboard(txs[:10])
    if keyboard:
        await update.message.reply_text("Нажмите, чтобы удалить транзакцию:", reply_markup=keyboard)


# ---------------- Add transaction conversation ----------------


async def add_tx_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    client = await get_authed_client(update, context)
    if client is None:
        return ConversationHandler.END
    await update.message.reply_text("Выберите тип транзакции:", reply_markup=transaction_type_keyboard())
    return States.TX_TYPE


async def tx_type_chosen(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    tx_type = query.data.split(":", 1)[1]
    context.user_data["tx_type"] = tx_type
    await query.edit_message_text("Введите сумму (число):")
    return States.TX_AMOUNT


async def tx_amount_entered(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = update.message.text.strip().replace(",", ".")
    try:
        amount = float(text)
        if amount <= 0:
            raise ValueError
    except ValueError:
        await update.message.reply_text("Введите положительное число, например 1500.50")
        return States.TX_AMOUNT

    context.user_data["tx_amount"] = amount
    await update.message.reply_text("Выберите категорию:", reply_markup=categories_keyboard("tx_cat"))
    return States.TX_CATEGORY


async def tx_category_chosen(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    query = update.callback_query
    await query.answer()
    category = query.data.split(":", 1)[1]
    context.user_data["tx_category"] = None if category == "none" else category
    await query.edit_message_text("Добавьте описание (или отправьте «-», чтобы пропустить):")
    return States.TX_DESCRIPTION


async def tx_description_entered(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    text = update.message.text.strip()
    description = None if text == "-" else text

    client = await get_authed_client(update, context)
    if client is None:
        return ConversationHandler.END

    tx_type = context.user_data.pop("tx_type")
    amount = context.user_data.pop("tx_amount")
    category = context.user_data.pop("tx_category")
    spent_at = datetime.now().isoformat()

    try:
        await client.create_transaction(amount, tx_type, category, description, spent_at)
    except APIError as e:
        await update.message.reply_text(f"⚠️ Ошибка: {e.detail}", reply_markup=MAIN_MENU)
        return ConversationHandler.END

    label = "доход" if tx_type == "income" else "расход"
    await update.message.reply_text(f"✅ Добавлен {label}: {amount:.2f}", reply_markup=MAIN_MENU)
    return ConversationHandler.END


async def tx_cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text("Отменено.", reply_markup=MAIN_MENU)
    return ConversationHandler.END


async def delete_transaction_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    await query.answer()
    tx_id = int(query.data.split(":", 1)[1])

    client = await get_authed_client(update, context)
    if client is None:
        return
    try:
        await client.delete_transaction(tx_id)
    except APIError as e:
        await query.edit_message_text(f"⚠️ Ошибка удаления: {e.detail}")
        return
    await query.edit_message_text("🗑 Транзакция удалена.")
