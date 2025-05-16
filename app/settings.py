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

    # certificates:
    CUSTOM_CA_CERT_PATH: str = ""
    CLIENT_CERT_PATH: str = ""
    CLIENT_CERT_KEY_PATH: str = ""

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

    # templates:
    SHOW_SENDER_NAME_IN_EMAIL_TITLE: bool | None = True
    EMAIL_TITLE: str = "Обращение по eXpress"
    SHOW_SENDER_PHONE_IN_EMAIL_BODY: bool | None = True

    # exchange:
    MAIL_SERVER: str
    MAIL_USERNAME: str
    MAIL_PASSWORD: SecretStr
    SENDER_EMAIL: EmailStr
    RECIPIENT_EMAIL: EmailStr
    AUTH_METHOD: AuthMethods = AuthMethods.BASIC
    VERIFY_SSL: bool = False
    ACCESS_TYPE: Literal["delegate", "impersonation"] = "delegate"
    EXCHANGE_CUSTOM_CA_PATH: str = ""

    @validator("APP_NAME", pre=True)
    @classmethod
    def check_app_name(cls, app_name: str) -> str:
        """Return default value if APP_NAME is empty string."""

        return app_name or "eXpress"

    @validator("SHOW_SENDER_NAME_IN_EMAIL_TITLE", pre=True)
    @classmethod
    def check_show_sender_name_in_email_title(
        cls, show_sender_name_in_email_title: bool | None
    ) -> bool:
        """Return default value if SHOW_SENDER_NAME_IN_EMAIL_TITLE is None."""

        return show_sender_name_in_email_title or True

    @validator("SHOW_SENDER_PHONE_IN_EMAIL_BODY", pre=True)
    @classmethod
    def check_show_sender_phone_in_email_body(
        cls, show_sender_phone_in_email_body: bool | None
    ) -> bool:
        """Return default value if SHOW_SENDER_PHONE_IN_EMAIL_BODY is None."""

        return show_sender_phone_in_email_body or True

    @validator("EMAIL_TITLE", pre=True)
    @classmethod
    def check_email_title(cls, email_title: str | None) -> str:
        """Return default value if EMAIL_TITLE is empty string or None."""

        return email_title or "Обращение по eXpress"

    @classmethod
    def _build_credentials_from_string(
        cls, credentials_str: str
    ) -> BotAccountWithSecret:
        credentials_str = credentials_str.replace("|", "@")
        assert credentials_str.count("@") == 2, "Have you forgot to add `bot_id`?"

        cts_url, secret_key, bot_id = [
            str_value.strip() for str_value in credentials_str.split("@")
        ]

        if "://" not in cts_url:
            cts_url = f"https://{cts_url}"

        return BotAccountWithSecret(
            id=UUID(bot_id),
            cts_url=cts_url,  # type: ignore[arg-type]
            secret_key=secret_key,
        )

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


settings = AppSettings()  # type: ignore[call-arg]
