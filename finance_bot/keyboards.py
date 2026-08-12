from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup

MAIN_MENU = ReplyKeyboardMarkup(
    [
        ["💰 Баланс", "📊 Сводка"],
        ["➕ Добавить транзакцию", "📜 История"],
        ["🏦 Депозиты", "➕ Депозит"],
        ["🤖 AI отчёт", "🚪 Выйти"],
    ],
    resize_keyboard=True,
)

AUTH_MENU = ReplyKeyboardMarkup(
    [["🔑 Войти", "🆕 Регистрация"]],
    resize_keyboard=True,
)

CATEGORIES = [
    "food",
    "transport",
    "entertainment",
    "utilities",
    "healthcare",
    "education",
    "shopping",
    "travel",
    "other",
]

CATEGORY_LABELS = {
    "food": "🍔 Еда",
    "transport": "🚗 Транспорт",
    "entertainment": "🎮 Развлечения",
    "utilities": "💡 Коммуналка",
    "healthcare": "🏥 Здоровье",
    "education": "📚 Образование",
    "shopping": "🛍 Покупки",
    "travel": "✈️ Путешествия",
    "other": "🔹 Другое",
    None: "— без категории —",
}


def categories_keyboard(prefix: str) -> InlineKeyboardMarkup:
    buttons = [
        InlineKeyboardButton(CATEGORY_LABELS[c], callback_data=f"{prefix}:{c}")
        for c in CATEGORIES
    ]
    rows = [buttons[i : i + 2] for i in range(0, len(buttons), 2)]
    rows.append([InlineKeyboardButton("Без категории", callback_data=f"{prefix}:none")])
    return InlineKeyboardMarkup(rows)


def transaction_type_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("💵 Доход", callback_data="tx_type:income"),
                InlineKeyboardButton("💸 Расход", callback_data="tx_type:expense"),
            ]
        ]
    )


def deposits_list_keyboard(deposits: list) -> InlineKeyboardMarkup | None:
    rows = [
        [InlineKeyboardButton(f"❌ {d['name']}", callback_data=f"dep_del:{d['id']}")]
        for d in deposits
    ]
    return InlineKeyboardMarkup(rows) if rows else None


def transactions_list_keyboard(transactions: list) -> InlineKeyboardMarkup | None:
    rows = [
        [
            InlineKeyboardButton(
                f"❌ #{t['id']} {t['amount']:.0f} ({t.get('description') or t.get('category') or '—'})",
                callback_data=f"tx_del:{t['id']}",
            )
        ]
        for t in transactions
    ]
    return InlineKeyboardMarkup(rows) if rows else None
