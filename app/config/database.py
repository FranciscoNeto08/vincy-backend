from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

from app.config.settings import settings

# URL de conexão com o banco
DATABASE_URL = settings.DATABASE_URL

# Cria a conexão com o banco
engine = create_engine(
    DATABASE_URL,
    echo=settings.DEBUG
)


SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base para todos os Models
Base = declarative_base()


def get_db():
    """
    Cria uma sessão com o banco de dados.
    """
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()