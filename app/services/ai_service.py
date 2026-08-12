import requests
from datetime import date, datetime
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status

from ..database import get_db
from ..models.User import User
from ..models.Transaction import Transaction
from ..models.Deposit import Deposit
from ..models.Report import Report
from ..config import settings
from ..schemas.report import ReportRequest, ReportResponse, ReportHistoryResponse
from ..schemas.enum import TypeOfTransaction

GEMINI_MODEL = "gemini-3.5-flash-lite"
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

    def _get_deposits_summary(self, user_id: int) -> list[dict]:
        deposits = self.db.query(Deposit).filter(Deposit.user_id == user_id).all()
        summary = []
        for d in deposits:
            query = self.db.query(Transaction).filter(
                Transaction.user_id == user_id,
                Transaction.type == TypeOfTransaction.EXPENSE,
                Transaction.spent_at >= datetime.combine(d.start_date, datetime.min.time()),
                Transaction.spent_at <= datetime.combine(d.end_date, datetime.max.time()),
            )
            if d.category:
                query = query.filter(Transaction.category == d.category)
            spent = sum(t.amount for t in query.all())
            summary.append({
                "name": d.name,
                "category": d.category or "все категории",
                "limit": d.limit_amount,
                "spent": spent,
                "start_date": d.start_date,
                "end_date": d.end_date,
                "exceeded": spent > d.limit_amount,
            })
        return summary

    def _build_prompt(self, user: User, transactions: list[Transaction], deposits: list[dict]) -> str:
        lines = [
            f"{t.spent_at.date()} | {t.type} | {t.category or '—'} | {t.amount} | {t.description or ''}"
            for t in transactions
        ]
        transactions_block = "\n".join(lines) if lines else "Транзакций за этот период нет."

        if deposits:
            deposit_lines = [
                f"{d['name']} | категория: {d['category']} | лимит: {d['limit']} | "
                f"потрачено: {d['spent']} | период: {d['start_date']} - {d['end_date']} | "
                f"{'ПРЕВЫШЕН' if d['exceeded'] else 'в пределах лимита'}"
                for d in deposits
            ]
            deposits_block = "\n".join(deposit_lines)
        else:
            deposits_block = "Депозитов (бюджетных лимитов) не установлено."

        return (
            "Ты — финансовый ассистент. На основе списка транзакций и бюджетных лимитов "
            "(депозитов) пользователя составь краткий аналитический отчёт на русском языке.\n\n"
            f"Текущий баланс пользователя: {user.balance}\n\n"
            "Список транзакций (дата | тип | категория | сумма | описание):\n"
            f"{transactions_block}\n\n"
            "Бюджетные лимиты пользователя (депозиты):\n"
            f"{deposits_block}\n\n"
            "В отчёте укажи:\n"
            "1. Общий доход и общий расход за период.\n"
            "2. Топ категорий расходов.\n"
            "3. Заметные тенденции или аномалии.\n"
            "4. Явно укажи, какие депозиты превышены и на сколько, если такие есть.\n"
            "5. 2-3 практические рекомендации по управлению бюджетом.\n"
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
        deposits = self._get_deposits_summary(user.id)
        prompt = self._build_prompt(user, transactions, deposits)
        report_text = self._call_gemini(prompt)

        report = Report(
            user_id=user.id,
            report_text=report_text,
            transactions_analyzed=len(transactions),
            period_from=request.date_from,
            period_to=request.date_to,
        )
        self.db.add(report)
        self.db.commit()
        self.db.refresh(report)

        return ReportResponse(
            report=report_text,
            transactions_analyzed=len(transactions),
            period_from=request.date_from,
            period_to=request.date_to,
        )

    def get_report_history(self, user_id: int) -> list[ReportHistoryResponse]:
        reports = (
            self.db.query(Report)
            .filter(Report.user_id == user_id)
            .order_by(Report.created_at.desc())
            .all()
        )
        return [ReportHistoryResponse.model_validate(r) for r in reports]

    def get_report_by_id(self, user_id: int, report_id: int) -> ReportHistoryResponse:
        report = (
            self.db.query(Report)
            .filter(Report.id == report_id, Report.user_id == user_id)
            .first()
        )
        if report is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found")
        return ReportHistoryResponse.model_validate(report)