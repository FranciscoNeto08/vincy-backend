from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config.database import Base, engine
from app.config.settings import settings

# Importa todos os models para que Base.metadata os conheça
# antes de criar as tabelas no banco.
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

from app.routes import (
    activities,
    appointments,
    auth,
    campaigns,
    clients,
    comandas,
    dashboard,
    finance,
    services,
    users,
    employees,
)

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    debug=settings.DEBUG,
    description="API para gerenciamento de estabelecimentos.",
)

# Libera o acesso apenas aos domínios autorizados (configurados em ALLOWED_ORIGINS no .env).
# Nunca use "*" em produção — isso permitiria que qualquer site chamasse a API.
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

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
app.include_router(employees.router)


@app.get("/")
def home():
    return {
        "status": "online",
        "mensagem": f"Bem-vindo à {settings.APP_NAME}",
        "versao": settings.APP_VERSION,
    }


@app.get("/health")
def health():
    return {
        "status": "OK",
        "api": settings.APP_NAME,
    }
