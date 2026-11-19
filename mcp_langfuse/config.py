from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuración leída de variables de entorno LANGFUSE_*."""

    model_config = SettingsConfigDict(env_prefix="LANGFUSE_", env_file=".env", extra="ignore")

    host: str = "http://localhost:3000"
    public_key: str
    secret_key: SecretStr
    timeout_s: float = 15.0
