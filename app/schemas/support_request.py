"""Support request representation schemas."""
from typing import Any

from exchangelib import FileAttachment  # type: ignore
from pydantic import BaseModel


class RequestAttachment(BaseModel):
    """Schema for support request attachment."""

    name: str
    data: bytes  # noqa: WPS110

    @classmethod
    async def from_aiofile(
        cls, aiofile: Any, attachment_name: str
    ) -> "RequestAttachment":
        """Convert aiofile object."""

        attachment_data = await aiofile.read()
        return cls(name=attachment_name, data=attachment_data)

    @property
    def to_ews_type(self) -> FileAttachment:
        """Convert to FileAttachment object."""

        return FileAttachment(name=self.name, content=self.data)


class SupportRequestInCreation(BaseModel):
    """Incoming support request schema."""

    subject: str | None = None
    description: str | None = None
    attachments_names: list[str] = []


class SupportRequestBase(BaseModel):
    """Support request base schema."""

    subject: str
    description: str
    attachments_names: list[str] = []


class SupportRequestInUpdating(SupportRequestBase):
    """Support request schema to update."""


class SupportRequestToSend(SupportRequestBase):
    """Support request schema to send."""
