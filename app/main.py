from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from app.exceptions import SubLedgerError

from app.core.config import settings
from app.api.v1 import auth, plans, customers, subscriptions, invoices, payments

# FastAPI app
app = FastAPI(
    title="SubLedger",
    description="Subscription billing API",
    version="0.1.0",
    debug=settings.DEBUG,
)

@app.exception_handler(SubLedgerError)
async def handle_subledger_error(request: Request, exc: SubLedgerError) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content=exc.to_dict(),
    )

# /health for smoke test
@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}

# /api/v1 prefix ->
# /auth -> ...
app.include_router(
    router=auth.router,
    prefix="/api/v1",
)

# /plans -> ...
app.include_router(
    router=plans.router,
    prefix="/api/v1",
)

# /customers -> ...
app.include_router(
    router=customers.router,
    prefix="/api/v1",
)

# /subscriptions -> ...
app.include_router(
    router=subscriptions.router,
    prefix="/api/v1",
)

# /invoices -> ...
app.include_router(
    router=invoices.router,
    prefix="/api/v1",
)

# /payments -> ...
app.include_router(
    router=payments.router,
    prefix="/api/v1",
)