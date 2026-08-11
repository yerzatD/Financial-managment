import requests
from datetime import date, datetime
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status

from ..database import get_db
from ..models.User import User
from ..models.Transaction import Transaction
from ..config import settings
from ..schemas.report import ReportRequest, ReportResponse

GEMINI_MODEL = "gemini-2.0-flash"
GEMINI_URL = f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODEL}:generateContent"
GEMINI_TIMEOUT_SECONDS = 30


class AIService:
    def __init__(self, db: Session = Depends(get_db)):
        self.db = db

    def _get_transactions(self, user_id: int, date_from: date | None, date_to: date | None) -> list[Transaction]:
        query = self.db.query(Transaction).filter(Transaction.user_id == user_id)
        if date_from:
            query = query.filter(Transaction.spent_at >= datetime.combine(date_from, datetime.min.time()))
        if date_to:
            query = query.filter(Transaction.spent_at <= datetime.combine(date_to, datetime.max.time()))
        return query.order_by(Transaction.spent_at.asc()).all()

    def _build_prompt(self, user: User, transactions: list[Transaction]) -> str:
        lines = [
            f"{t.spent_at.date()} | {t.type} | {t.category or '—'} | {t.amount} | {t.description or ''}"
            for t in transactions
        ]
        transactions_block = "\n".join(lines) if lines else "Транзакций за этот период нет."

        return (
            "Ты — финансовый ассистент. На основе списка транзакций пользователя составь "
            "краткий аналитический отчёт на русском языке.\n\n"
            f"Текущий баланс пользователя: {user.balance}\n\n"
            "Список транзакций (дата | тип | категория | сумма | описание):\n"
            f"{transactions_block}\n\n"
            "В отчёте укажи:\n"
            "1. Общий доход и общий расход за период.\n"
            "2. Топ категорий расходов.\n"
            "3. Заметные тенденции или аномалии.\n"
            "4. 2-3 практические рекомендации по управлению бюджетом.\n"
            "Пиши сжато, структурированно, используй списки где уместно."
        )

    def _call_gemini(self, prompt: str) -> str:
        try:
            response = requests.post(
                GEMINI_URL,
                params={"key": settings.GEMINI_API_KEY},
                json={"contents": [{"parts": [{"text": prompt}]}]},
                timeout=GEMINI_TIMEOUT_SECONDS,
            )
        except requests.RequestException as e:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Failed to reach Gemini API: {e}",
            )

        if response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=f"Gemini API error ({response.status_code}): {response.text}",
            )

        data = response.json()
        try:
            return data["candidates"][0]["content"]["parts"][0]["text"]
        except (KeyError, IndexError):
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="Unexpected response format from Gemini API",
            )

    def generate_report(self, user: User, request: ReportRequest) -> ReportResponse:
        transactions = self._get_transactions(user.id, request.date_from, request.date_to)
        prompt = self._build_prompt(user, transactions)
        report_text = self._call_gemini(prompt)

        return ReportResponse(
            report=report_text,
            transactions_analyzed=len(transactions),
            period_from=request.date_from,
            period_to=request.date_to,
        )