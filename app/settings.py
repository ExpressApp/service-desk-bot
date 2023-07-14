"""Application settings."""

from pathlib import Path
from typing import Any, Literal
from uuid import UUID

from pybotx import BotAccountWithSecret
from pydantic import BaseSettings, ByteSize, EmailStr, SecretStr, validator

from app.schemas.enums import AuthMethods


class AppSettings(BaseSettings):  # noqa: WPS338
    class Config:  # noqa: WPS431
        env_file = ".env"

    # TODO: Change type to `list[BotAccountWithSecret]` after closing:
    # https://github.com/samuelcolvin/pydantic/issues/1458
    BOT_CREDENTIALS: Any

    # base kwargs:
    DEBUG: bool = False

    # TODO: Change type to `list[UUID]` after closing:
    # https://github.com/samuelcolvin/pydantic/issues/1458
    # User huids for debug
    SMARTLOG_DEBUG_HUIDS: Any

    # app info:
    APP_NAME: str = "eXpress"

    # database:
    POSTGRES_DSN: str
    SQL_DEBUG: bool = False

    # redis:
    REDIS_DSN: str

    # healthcheck:
    WORKER_TIMEOUT_SEC: float = 4

    # limits:
    MAX_ATTACHMENTS_COUNT: int = 20
    MAX_ATTACHMENT_SIZE: ByteSize = "9.9MiB"  # type: ignore
    MAX_ATTACHMENTS_SIZE: ByteSize = "20MiB"  # type: ignore
    MAX_DESCRIPTION_LENGTH: int = 3500

    # storage:
    USERS_ATTACHMENTS_DIR = Path("./attachments")

    # exchange:
    MAIL_SERVER: str
    MAIL_USERNAME: str
    MAIL_PASSWORD: SecretStr
    SENDER_EMAIL: EmailStr
    RECIPIENT_EMAIL: EmailStr
    AUTH_METHOD: AuthMethods = AuthMethods.BASIC
    VERIFY_SSL: bool = False
    ACCESS_TYPE: Literal["delegate", "impersonation"] = "delegate"

    @classmethod
    def _build_credentials_from_string(
        cls, credentials_str: str
    ) -> BotAccountWithSecret:
        credentials_str = credentials_str.replace("|", "@")
        assert credentials_str.count("@") == 2, "Have you forgot to add `bot_id`?"

        host, secret_key, bot_id = [
            str_value.strip() for str_value in credentials_str.split("@")
        ]
        return BotAccountWithSecret(id=UUID(bot_id), host=host, secret_key=secret_key)

    @validator("BOT_CREDENTIALS", pre=True)
    @classmethod
    def parse_bot_credentials(cls, raw_credentials: Any) -> list[BotAccountWithSecret]:
        """Parse bot credentials separated by comma.

        Each entry must be separated by "@" or "|".
        """
        if not raw_credentials:
            return []

        return [
            cls._build_credentials_from_string(credentials_str)
            for credentials_str in raw_credentials.replace(",", " ").split()
        ]

    @validator("SMARTLOG_DEBUG_HUIDS", pre=True)
    @classmethod
    def parse_smartlog_debug_huids(cls, raw_huids: Any) -> list[UUID]:
        """Parse debug huids separated by comma."""
        if not raw_huids:
            return []

        return [UUID(huid) for huid in raw_huids.split(",")]


settings = AppSettings()
