from fastapi import FastAPI

from app.api.routers import books, loans, users
from app.core.config import settings


app = FastAPI(
    title=settings.app_name,
    version="1.0.0",
    description="REST API for managing library books and loans.",
)

app.include_router(users.router, prefix="/api")
app.include_router(books.router, prefix="/api")
app.include_router(loans.router, prefix="/api")


@app.get("/health", tags=["health"])
def healthcheck() -> dict[str, str]:
    return {"status": "ok"}
