from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr


class Settings(BaseSettings):

    bot_token: SecretStr
    admin_id: str
    moder_channel_id: str

    POSTGRES_USER: str
    POSTGRES_PASSWORD: SecretStr
    POSTGRES_PORT: int
    POSTGRES_HOST: str
    POSTGRES_DB: str

    CRYPTO_BOT_TOKEN: str
    YOU_KASSA_TOKEN: str
    # REDIS_HOST: str
    # REDIS_PORT: int

    # PROVIDER_TOKEN: str

    # RULES_URL: str
    # TERMS_URL: str
    # TARIFFS_URL: str

    model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')


config = Settings()