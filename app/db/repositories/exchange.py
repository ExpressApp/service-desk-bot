"""Repo for Exchange Web Server."""

import requests.adapters  # noqa:WPS301
from exchangelib import (  # type: ignore
    Account,
    BaseProtocol,
    Configuration,
    Credentials,
    Mailbox,
    Message,
)
from exchangelib.protocol import BaseProtocol  # type: ignore # noqa: F811, WPS440
from pydantic import SecretStr

from app.schemas.support_request import RequestAttachment
from app.services.decorators import async_wrap
from app.settings import settings

if settings.VERIFY_SSL:

    class RootCAAdapter(requests.adapters.HTTPAdapter):
        """Adapter to make exchangelib use custom ca certs."""

        def cert_verify(self, conn, url, verify, cert):  # type: ignore # noqa: D102
            super().cert_verify(
                conn=conn, url=url, verify=settings.CUSTOM_CA_CERT_PATH, cert=cert
            )

    BaseProtocol.HTTP_ADAPTER_CLS = RootCAAdapter


def get_ews_account(
    credential_username: str,
    credential_password: SecretStr,
    sender_email: str,
    server: str,
) -> Account:
    """Return EWS account for connection exchange."""

    credentials = Credentials(
        username=credential_username, password=credential_password.get_secret_value()
    )
    ews_config = Configuration(
        server=server,
        credentials=credentials,
        auth_type=settings.AUTH_METHOD,
    )
    return Account(sender_email, access_type=settings.ACCESS_TYPE, config=ews_config)


class ExchangeRepo:
    def __init__(self, account: Account):
        self.account = account

    @async_wrap
    def send_mail(
        self,
        subject: str,
        body: str,
        user_attachments: list[RequestAttachment],
    ) -> None:
        """Send message with attachments by email."""

        to_recipients = [Mailbox(email_address=settings.RECIPIENT_EMAIL)]

        message = Message(
            account=self.account,
            subject=subject,
            body=body,
            to_recipients=to_recipients,
        )

        for attachment in user_attachments:
            message.attach(attachment.to_ews_type)

        message.send()
