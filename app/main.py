from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .database import engine, Base
from .routers import (
    user_router,
    account_router,
    transfer_router,
    deposit_router,
    product_router,
    order_router,
    ai_router,
)

app = FastAPI(title=settings.app_name, debug=settings.debug)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user_router)
app.include_router(account_router)
app.include_router(transfer_router)
app.include_router(deposit_router)
app.include_router(product_router)
app.include_router(order_router)
app.include_router(ai_router)


@app.on_event("startup")
async def on_startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)