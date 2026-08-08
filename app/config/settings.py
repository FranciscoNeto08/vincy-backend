from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    APP_NAME: str
    APP_VERSION: str
    DEBUG: bool

    DATABASE_URL: str

    SECRET_KEY: str = "change-this-secret-key-in-production-please"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # URL pública do frontend (usada nos links de confirmação de e-mail e redefinição de senha).
    FRONTEND_URL: str = ""

    # Domínios autorizados a chamar a API (CORS), separados por vírgula no .env.
    ALLOWED_ORIGINS: str = ""

    # Exige confirmação de e-mail para poder fazer login.
    REQUIRE_EMAIL_VERIFICATION: bool = True

    # Proteção contra força bruta no login.
    LOGIN_MAX_ATTEMPTS: int = 5
    LOGIN_LOCK_MINUTES: int = 15

    # =====================================================
    # RESEND - E-MAIL MARKETING
    # =====================================================

    RESEND_API_KEY: str = ""
    RESEND_FROM_EMAIL: str = "onboarding@resend.dev"

    # =====================================================
    # CONFIGURAÇÃO DO .ENV
    # =====================================================

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore"
    )

    @property
    def allowed_origins_list(self) -> list[str]:
        """Converte ALLOWED_ORIGINS (string separada por vírgula) em lista, para uso no CORSMiddleware."""
        return [origin.strip() for origin in self.ALLOWED_ORIGINS.split(",") if origin.strip()]


settings = Settings()