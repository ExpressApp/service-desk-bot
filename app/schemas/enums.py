"""Module for enums."""
from enum import Enum


class StrEnum(str, Enum):  # noqa: WPS600
    """Base enum."""


class HealthCheckStatuses(StrEnum):
    OK = "ok"
    ERROR = "error"


class AuthMethods(str, Enum):  # noqa: WPS600
    """Enums authentication methods."""

    NOAUTH = "no authentication"
    NTLM = "NTLM"
    BASIC = "basic"
    DIGEST = "digest"
    GSSAPI = "gssapi"
    SSPI = "sspi"
    OAUTH2 = "OAuth 2.0"
    CBA = "CBA"
