from __future__ import annotations

import httpx


class APIError(Exception):
    def __init__(self, status_code: int, detail: str):
        self.status_code = status_code
        self.detail = detail
        super().__init__(f"{status_code}: {detail}")


class APIClient:
    """Тонкая обёртка над FastAPI-эндпоинтами AI Finance Manager."""

    def __init__(self, base_url: str, token: str | None = None):
        self.base_url = base_url.rstrip("/")
        self.token = token

    def _headers(self) -> dict:
        headers = {}
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    async def _request(self, method: str, path: str, **kwargs) -> httpx.Response:
        url = f"{self.base_url}{path}"
        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.request(method, url, headers=self._headers(), **kwargs)
        if resp.status_code >= 400:
            try:
                body = resp.json()
                detail = body.get("detail", resp.text)
            except ValueError:
                detail = resp.text
            raise APIError(resp.status_code, str(detail))
        return resp

    # ---------------- users ----------------

    async def register(self, username: str, email: str, password: str) -> dict:
        resp = await self._request(
            "POST",
            "/api/users/register",
            json={"username": username, "email": email, "password": password},
        )
        return resp.json()

    async def login(self, username: str, password: str) -> dict:
        resp = await self._request(
            "POST",
            "/api/users/token",
            data={"username": username, "password": password},
        )
        return resp.json()

    async def get_me(self) -> dict:
        resp = await self._request("GET", "/api/users/me")
        return resp.json()

    # ---------------- transactions ----------------

    async def create_transaction(
        self, amount: float, type_: str, category: str | None, description: str | None, spent_at: str
    ) -> dict:
        payload = {
            "amount": amount,
            "type": type_,
            "category": category,
            "description": description,
            "spent_at": spent_at,
        }
        resp = await self._request("POST", "/transactions/", json=payload)
        return resp.json()

    async def list_transactions(self) -> list:
        resp = await self._request("GET", "/transactions/")
        return resp.json()

    async def delete_transaction(self, transaction_id: int) -> None:
        await self._request("DELETE", f"/transactions/{transaction_id}")

    async def transaction_summary(self) -> dict:
        resp = await self._request("GET", "/transactions/summary/")
        return resp.json()

    # ---------------- deposits ----------------

    async def create_deposit(
        self, name: str, category: str | None, limit_amount: float, start_date: str, end_date: str
    ) -> dict:
        payload = {
            "name": name,
            "category": category,
            "limit_amount": limit_amount,
            "start_date": start_date,
            "end_date": end_date,
        }
        resp = await self._request("POST", "/deposits/", json=payload)
        return resp.json()

    async def list_deposits(self) -> list:
        resp = await self._request("GET", "/deposits/")
        return resp.json()

    async def delete_deposit(self, deposit_id: int) -> None:
        await self._request("DELETE", f"/deposits/{deposit_id}")

    # ---------------- AI reports ----------------

    async def generate_report(self, date_from: str | None, date_to: str | None) -> dict:
        resp = await self._request(
            "POST", "/api/reports/", json={"date_from": date_from, "date_to": date_to}
        )
        return resp.json()

    async def list_reports(self) -> list:
        resp = await self._request("GET", "/api/reports/")
        return resp.json()

    async def get_report_by_id(self, report_id: int) -> dict:
        resp = await self._request("GET", f"/api/reports/{report_id}")
        return resp.json()
