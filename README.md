Below is the complete `README.md` file content. Copy it and save as `README.md` in the root of your project.

```markdown
# AI Finance Manager

A personal finance management system with a **FastAPI** backend and a **Telegram bot** interface.  
It allows users to track transactions, set budget limits (deposits), and generate AI‑powered financial reports using Google Gemini.

---

## ✨ Features

- **User Authentication** – registration, login, JWT token management.
- **Transaction Management** – add, edit, delete, list transactions (income/expense) with categories and descriptions.
- **Budget Limits (Deposits)** – create time‑bound spending limits per category; monitor overspending.
- **Financial Summary** – view balance, total income/expense, and breakdown by category.
- **AI Reports** – generate detailed financial reports with trends, category insights, and budget recommendations using Gemini.
- **Telegram Bot** – convenient interface with inline keyboards, conversation handlers, and persistent token storage.
- **RESTful API** – fully documented (Swagger UI at `/docs`).

---

## 🛠️ Tech Stack

### Backend (FastAPI)
- **Python 3.10+**
- **FastAPI** – web framework
- **SQLAlchemy** – ORM
- **SQLite** (default) – can be changed via `database_url`
- **python-jose** – JWT handling
- **pwdlib** – password hashing
- **httpx** – HTTP client for Gemini API
- **Pydantic** – data validation
- **python-dotenv** – environment variables

### Telegram Bot
- **python-telegram-bot** (v21.6)
- **httpx** – API client to communicate with backend
- **JSON** – simple token storage

---

## 📁 Project Structure

```
.
├── bot/                           # Telegram bot source
│   ├── handlers/                  # Conversation and menu handlers
│   │   ├── auth.py
│   │   ├── deposits.py
│   │   ├── reports.py
│   │   └── transactions.py
│   ├── api_client.py              # API client for backend
│   ├── config.py                  # Bot configuration
│   ├── helpers.py                 # Shared utilities
│   ├── keyboards.py               # Inline and reply keyboards
│   ├── main.py                    # Bot entry point
│   ├── states.py                  # Conversation states
│   └── storage.py                 # Token storage (JSON)
│
├── backend/                       # FastAPI backend source
│   ├── routers/                   # API routers
│   │   ├── ai_router.py
│   │   ├── deposit_router.py
│   │   ├── transaction_router.py
│   │   └── user_router.py
│   ├── services/                  # Business logic
│   │   ├── ai_service.py
│   │   ├── deposit_service.py
│   │   ├── transaction_service.py
│   │   └── user_service.py
│   ├── schemas/                   # Pydantic models
│   │   ├── deposit.py
│   │   ├── enum.py
│   │   ├── report.py
│   │   ├── transaction.py
│   │   └── user.py
│   ├── models/                    # SQLAlchemy models
│   │   ├── Deposit.py
│   │   ├── Report.py
│   │   ├── Transaction.py
│   │   └── User.py
│   ├── auth.py                    # JWT auth dependencies
│   ├── config.py                  # Backend settings (Pydantic)
│   ├── database.py                # Database setup
│   └── main.py                    # FastAPI application
│
├── .env.example                   # Example environment variables
├── requirements.txt               # Bot dependencies
└── README.md                      # This file
```

---

## 🔧 Prerequisites

- Python 3.10 or higher
- A Telegram Bot Token (from [@BotFather](https://t.me/botfather))
- Google Gemini API Key (from [Google AI Studio](https://ai.google.dev/))
- (Optional) PostgreSQL or other DB – SQLite is used by default

---

## 📦 Installation

1. **Clone the repository**

   ```bash
   git clone https://github.com/yourusername/ai-finance-manager.git
   cd ai-finance-manager
   ```

2. **Set up a virtual environment (recommended)**

   ```bash
   python -m venv venv
   source venv/bin/activate   # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**

   For the **backend**:

   ```bash
   pip install fastapi uvicorn sqlalchemy python-dotenv pydantic-settings pydantic python-jose[cryptography] pwdlib httpx requests
   ```

   For the **Telegram bot**:

   ```bash
   pip install -r requirements.txt
   ```

   > You can combine both into a single `requirements.txt` if desired.

---

## ⚙️ Configuration

Create a `.env` file in the **root directory** (or adjust paths) with the following variables:

```env
# Backend
SECRET_KEY=your-secret-key-here
GEMINI_API_KEY=your-gemini-api-key
BOT_TOKEN=your-telegram-bot-token
DATABASE_URL=sqlite:///./finance.db          # or postgresql://user:pass@localhost/db

# Optional: override default FastAPI settings
APP_NAME=AI Finance Manager
DEBUG=True
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Bot
API_BASE_URL=http://127.0.0.1:8000          # URL where backend is served
TOKENS_FILE=tokens.json                      # file to store user tokens
```

> ⚠️ **Important**: The backend and bot each use their own `config.py`.  
> The backend expects `SECRET_KEY` and `GEMINI_API_KEY`; the bot expects `BOT_TOKEN` and `API_BASE_URL`.  
> You may place all variables in one `.env` file or create separate files.

---

## 🚀 Running the Application

### 1. Start the FastAPI backend

```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://127.0.0.1:8000`.  
Swagger documentation: `http://127.0.0.1:8000/docs`

### 2. Start the Telegram bot

```bash
cd bot
python main.py
```

The bot will start polling and respond to commands.

---

## 🤖 Telegram Bot Usage

After starting the bot, you can interact with it using the buttons in the menu:

- **🔑 Войти** – login with existing credentials
- **🆕 Регистрация** – create a new account
- **💰 Баланс** – view current balance
- **📊 Сводка** – see summary (income/expense, category breakdown)
- **➕ Добавить транзакцию** – add a new transaction (income/expense) with category and description
- **📜 История** – list recent transactions; delete them if needed
- **🏦 Депозиты** – view existing budget limits
- **➕ Депозит** – create a new budget limit (name, category, amount, period)
- **🤖 AI отчёт** – generate an AI report for a selected period
- **🚪 Выйти** – log out

All data is stored in the backend database and synced with the bot.

---

## 📚 API Endpoints (Backend)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST   | `/api/users/register` | Register a new user |
| POST   | `/api/users/token` | Login and obtain access token |
| GET    | `/api/users/me` | Get current user info |
| PATCH  | `/api/users/me` | Update user profile |
| POST   | `/transactions/` | Create a transaction |
| GET    | `/transactions/` | List all transactions |
| GET    | `/transactions/summary/` | Get summary (income/expense/categories) |
| PUT    | `/transactions/{id}` | Update a transaction |
| DELETE | `/transactions/{id}` | Delete a transaction |
| POST   | `/deposits/` | Create a deposit (budget limit) |
| GET    | `/deposits/` | List all deposits |
| DELETE | `/deposits/{id}` | Delete a deposit |
| POST   | `/api/reports/` | Generate AI report |
| GET    | `/api/reports/` | List report history |
| GET    | `/api/reports/{id}` | Get a specific report |

Full API documentation is available at `/docs` when the backend is running.

---

## 🧪 Development Notes

- **Database**: SQLite is used by default. To use PostgreSQL, change `DATABASE_URL` accordingly.
- **Token Storage**: The bot stores access tokens in a local JSON file (`tokens.json`). For production, consider a more secure store (e.g., Redis).
- **AI Service**: The Gemini API key must have access to the `gemini-3.5-flash-lite` model (adjust in `ai_service.py` if needed).
- **CORS**: The backend allows origins configured in `settings.cors_origins` – update if you use a different frontend.

---

## 🤝 Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

---

## 📄 License

[MIT](LICENSE)

---

## 📬 Contact

For questions or suggestions, feel free to open an issue or contact the maintainer.

---

**Happy budgeting!** 💰📊