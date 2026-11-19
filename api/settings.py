from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class AgentSettings(BaseSettings):
    """Configuración del agente (OpenAI y GitHub) leída del .env."""

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    openai_api_key: SecretStr
    openai_model: str = "gpt-4.1"
    github_personal_access_token: SecretStr
    github_repo: str = ""  # "owner/repo" donde el agente puede proponer PRs
    github_mcp_url: str = "https://api.githubcopilot.com/mcp/"
