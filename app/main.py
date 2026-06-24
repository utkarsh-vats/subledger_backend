from fastapi import FastAPI
from app.core.config import settings

# FastAPI app
app = FastAPI(
    title="SubLedger",
    description="Subscription billing API",
    version="0.1.0",
    debug=settings.DEBUG,
)

# /health for smoke test
@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}