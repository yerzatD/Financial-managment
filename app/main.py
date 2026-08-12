from fastapi import FastAPI
from .routers import transaction_router,user_router,ai_router,deposit_router
from .database import Base
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .database import engine, Base

app = FastAPI(title="AI FINANCE MANAGER")
app.include_router(transaction_router)
app.include_router(user_router)
app.include_router(ai_router)
app.include_router(deposit_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


Base.metadata.create_all(engine)