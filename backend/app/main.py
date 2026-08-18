from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.trustedhost import TrustedHostMiddleware

from app.config.database import Base, engine
from app.config.settings import settings
from app.middleware.security import (
    InMemoryRateLimitMiddleware,
    RequestBodyLimitMiddleware,
    SecurityHeadersMiddleware,
)

# Importa todos os models antes do create_all.
import app.models.user  # noqa: F401
import app.models.client  # noqa: F401
import app.models.service  # noqa: F401
import app.models.comanda  # noqa: F401
import app.models.history  # noqa: F401
import app.models.activity  # noqa: F401
import app.models.finance  # noqa: F401
import app.models.appointment  # noqa: F401
import app.models.campaign  # noqa: F401
import app.models.employee  # noqa: F401
import app.models.email_token  # noqa: F401
import app.models.audit_log  # noqa: F401
import app.models.evolution  # noqa: F401
import app.models.legal_acceptance  # noqa: F401
import app.models.product  # noqa: F401

from app.routes import (
    activities, appointments, auth, campaigns, clients, comandas,
    dashboard, finance, services, users, employees, evolution, webhooks, subscriptions, feedback, inventory,
)

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
    description="API para gerenciamento de estabelecimentos.",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    openapi_url="/openapi.json" if settings.DEBUG else None,
)

# Ordem: último middleware adicionado é o primeiro a receber a requisição.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Accept", "X-Request-ID"],
    expose_headers=["X-Request-ID", "Retry-After"],
    max_age=600,
)

if settings.allowed_hosts_list:
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=settings.allowed_hosts_list)

app.add_middleware(RequestBodyLimitMiddleware, max_bytes=settings.MAX_REQUEST_BODY_BYTES)
app.add_middleware(InMemoryRateLimitMiddleware)
app.add_middleware(SecurityHeadersMiddleware)

# Mantido por compatibilidade com o fluxo atual; Alembic continua sendo a fonte
# de verdade para alterações de schema em produção.
Base.metadata.create_all(bind=engine)

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(clients.router)
app.include_router(services.router)
app.include_router(comandas.router)
app.include_router(dashboard.router)
app.include_router(finance.router)
app.include_router(activities.router)
app.include_router(appointments.router)
app.include_router(campaigns.router)
app.include_router(evolution.router)
app.include_router(employees.router)
app.include_router(webhooks.router)
app.include_router(subscriptions.router)
app.include_router(feedback.router)
app.include_router(inventory.router)


@app.get("/")
def home():
    return {"status": "online", "versao": settings.APP_VERSION}


@app.get("/health")
def health():
    return {"status": "OK"}
