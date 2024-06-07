"""For using bot commands as enum."""

from typing import Any, KeysView

from pydantic import BaseModel

from app.resources import strings


class HiddenCommand(BaseModel):
    """For using hidden command as object, not just strings."""

    visible: bool = False
    command: str

    def __getitem__(self, key: str) -> str:
        """Return value of model field."""
        return getattr(self, key)

    def __len__(self) -> int:
        """Return amount of model fields."""
        return len(self.keys())

    def keys(self) -> KeysView[Any]:
        return self.dict().keys()


class Command(HiddenCommand):
    """For using command as object, not just strings."""

    visible: bool = True
    description: str


class PublicCommands:
    CREATE_SUPPORT_REQUEST_COMMAND = Command(
        command=strings.CREATE_SUPPORT_REQUEST_COMMAND,
        description=strings.CREATE_SUPPORT_REQUEST_COMMAND_DESCRIPTION,
    )
    HELP_COMMAND = Command(
        command=strings.HELP_COMMAND,
        description=strings.HELP_COMMAND_DESCRIPTION,
    )


class HiddenCommands:
    CANCEL_COMMAND = HiddenCommand(command=strings.CANCEL_COMMAND)
    CONFIRM_CANCEL_COMMAND = HiddenCommand(command=strings.CONFIRM_CANCEL_COMMAND)
    REFUSE_CANCEL_COMMAND = HiddenCommand(command=strings.REFUSE_CANCEL_COMMAND)
    SEND_TO_CONFIRM_COMMAND = HiddenCommand(command=strings.SEND_TO_CONFIRM_COMMAND)
    UPDATE_SUPPORT_REQUEST_COMMAND = HiddenCommand(
        command=strings.UPDATE_REQUEST_COMMAND
    )
    CONFIRM_ATTACHMENT_ADDITION_COMMAND = HiddenCommand(
        command=strings.CONFIRM_ATTACHMENT_ADDITION_COMMAND
    )
    REFUSE_ATTACHMENT_ADDITION_COMMAND = HiddenCommand(
        command=strings.REFUSE_ATTACHMENT_ADDITION_COMMAND
    )
    SKIP_COMMAND = HiddenCommand(command=strings.SKIP_COMMAND)
    UPDATE_DESCRIPTION_COMMAND = HiddenCommand(
        command=strings.UPDATE_DESCRIPTION_COMMAND
    )
    UPDATE_ATTACHMENT_COMMAND = HiddenCommand(command=strings.UPDATE_ATTACHMENT_COMMAND)
    SEND_REQUEST_COMMAND = HiddenCommand(command=strings.SEND_REQUEST_COMMAND)
    BACK_COMMAND = HiddenCommand(command=strings.BACK_COMMAND)
