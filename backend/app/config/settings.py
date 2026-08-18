from pydantic import field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "Vynce"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    DATABASE_URL: str

    # Segurança JWT. Em produção, use uma chave aleatória de pelo menos 32 caracteres.
    SECRET_KEY: str = ""
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    JWT_ISSUER: str = "vynce-api"
    JWT_AUDIENCE: str = "vynce-web"

    # Chave mestra usada para criptografar credenciais sensíveis salvas no banco.
    # Nunca deve ser commitada no GitHub.
    CREDENTIAL_ENCRYPTION_KEY: str = ""

    # URL pública do frontend.
    FRONTEND_URL: str = ""
    BACKEND_PUBLIC_URL: str = ""

    # CORS / hosts, separados por vírgula.
    ALLOWED_ORIGINS: str = ""
    ALLOWED_HOSTS: str = ""

    # Confirmação de e-mail.
    REQUIRE_EMAIL_VERIFICATION: bool = True

    # Proteção contra força bruta por conta.
    LOGIN_MAX_ATTEMPTS: int = 5
    LOGIN_LOCK_MINUTES: int = 15

    # Limites gerais de abuso/DoS.
    MAX_REQUEST_BODY_BYTES: int = 1_048_576  # 1 MiB
    API_RATE_LIMIT_PER_MINUTE: int = 300
    AUTH_RATE_LIMIT_PER_15_MINUTES: int = 30
    PASSWORD_RECOVERY_LIMIT_PER_15_MINUTES: int = 5
    CAMPAIGN_RATE_LIMIT_PER_MINUTE: int = 10
    MAX_CAMPAIGN_RECIPIENTS: int = 500
    CAMPAIGN_DAILY_RECIPIENT_LIMIT: int = 2000

    # Evolution API / SSRF
    EVOLUTION_ALLOW_PRIVATE_TARGETS: bool = False

    # Resend webhook
    RESEND_WEBHOOK_SECRET: str = ""
    RESEND_WEBHOOK_TOLERANCE_SECONDS: int = 300

    # Banco.
    DB_POOL_SIZE: int = 5
    DB_MAX_OVERFLOW: int = 10
    DB_POOL_RECYCLE_SECONDS: int = 1800

    # RESEND - E-MAIL
    RESEND_API_KEY: str = ""
    RESEND_FROM_EMAIL: str = "onboarding@resend.dev"

    # Comercial / documentos públicos. Não coloque segredos no frontend.
    OWNER_CONTACT: str = "Entre em contato com o responsável pela Vynce"
    LEGAL_TERMS_VERSION: str = "1.0-2026-08-18"
    LEGAL_PRIVACY_VERSION: str = "1.0-2026-08-18"
    # Chave apenas para operação administrativa servidor-a-servidor. Gere valor aleatório longo no Render.
    SUBSCRIPTION_ADMIN_KEY: str = ""

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
        case_sensitive=True,
    )

    @field_validator("ACCESS_TOKEN_EXPIRE_MINUTES")
    @classmethod
    def validate_token_expiration(cls, value: int) -> int:
        if value < 5 or value > 120:
            raise ValueError(
                "ACCESS_TOKEN_EXPIRE_MINUTES deve ficar entre 5 e 120 minutos."
            )
        return value

    @model_validator(mode="after")
    def validate_production_security(self):
        if not self.DEBUG:
            if len(self.SECRET_KEY) < 32:
                raise ValueError(
                    "SECRET_KEY insegura. Em produção configure uma chave aleatória com pelo menos 32 caracteres."
                )

            if not self.CREDENTIAL_ENCRYPTION_KEY:
                raise ValueError(
                    "CREDENTIAL_ENCRYPTION_KEY deve ser configurada em produção."
                )

            if self.FRONTEND_URL and not self.FRONTEND_URL.startswith("https://"):
                raise ValueError(
                    "FRONTEND_URL deve usar HTTPS em produção."
                )

            if not self.ALLOWED_ORIGINS:
                raise ValueError(
                    "ALLOWED_ORIGINS deve ser configurado em produção."
                )

            if not self.BACKEND_PUBLIC_URL.startswith("https://"):
                raise ValueError(
                    "BACKEND_PUBLIC_URL deve usar HTTPS em produção."
                )

            if self.EVOLUTION_ALLOW_PRIVATE_TARGETS:
                raise ValueError(
                    "EVOLUTION_ALLOW_PRIVATE_TARGETS deve permanecer false em produção."
                )

            if len(self.SUBSCRIPTION_ADMIN_KEY) < 32:
                raise ValueError(
                    "SUBSCRIPTION_ADMIN_KEY deve ter pelo menos 32 caracteres em produção."
                )

        return self

    @property
    def allowed_origins_list(self) -> list[str]:
        return [
            origin.strip().rstrip("/")
            for origin in self.ALLOWED_ORIGINS.split(",")
            if origin.strip()
        ]

    @property
    def allowed_hosts_list(self) -> list[str]:
        return [
            host.strip()
            for host in self.ALLOWED_HOSTS.split(",")
            if host.strip()
        ]


settings = Settings()