"""Support request representation schemas."""

from pydantic import BaseModel


class SupportRequestInCreation(BaseModel):
    """Incoming support request schema."""

    subject: str | None = None
    description: str | None = None
    attachments_names: list[str] = []


class SupportRequestInUpdating(BaseModel):
    """Support request schema to update."""

    subject: str
    description: str
    attachments_names: list[str] = []
