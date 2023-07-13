"""Bubble for support request handlers."""

from pybotx import BubbleMarkup

from app.bot.commands.listing import HiddenCommands
from app.resources import strings
from app.schemas.support_request import (
    SupportRequestInCreation,
    SupportRequestInUpdating,
)


def get_confirm_cancel_bubbles() -> BubbleMarkup:
    """Get confirm cancel bubbles."""

    bubbles = BubbleMarkup()
    bubbles.add_button(
        command=HiddenCommands.CONFIRM_CANCEL_COMMAND.command,
        label=strings.YES_LABEL,
    )
    bubbles.add_button(
        command=HiddenCommands.REFUSE_CANCEL_COMMAND.command,
        label=strings.NO_LABEL,
    )

    return bubbles


def get_confirm_request_bubbles(
    request: SupportRequestInCreation | SupportRequestInUpdating,
) -> BubbleMarkup:
    """Get confirm support request bubbles."""

    bubbles = BubbleMarkup()
    bubbles.add_button(
        command=HiddenCommands.SEND_SUPPORT_REQUEST_COMMAND.command,
        label=strings.YES_LABEL,
    )
    bubbles.add_button(
        command=HiddenCommands.UPDATE_SUPPORT_REQUEST_COMMAND.command,
        label=strings.NO_LABEL,
        data={
            "support_request": {
                "subject": request.subject,
                "description": request.description,
                "attachments_names": request.attachments_names,
            }
        },
    )

    return bubbles


def get_confirm_attachment_addition_bubbles() -> BubbleMarkup:
    """Get confirm attachment addition bubbles."""

    bubbles = BubbleMarkup()
    bubbles.add_button(
        command=HiddenCommands.CONFIRM_ATTACHMENT_ADDITION_COMMAND.command,
        label=strings.YES_LABEL,
    )
    bubbles.add_button(
        command=HiddenCommands.REFUSE_ATTACHMENT_ADDITION_COMMAND.command,
        label=strings.NO_LABEL,
    )

    return bubbles


def get_send_request_bubbles() -> BubbleMarkup:
    """Get send support request bubbles."""

    bubbles = BubbleMarkup()
    bubbles.add_button(
        command=HiddenCommands.SEND_SUPPORT_REQUEST_COMMAND.command,
        label=strings.SEND_SUPPORT_REQUEST_COMMAND_LABEL,
    )

    return bubbles


def get_skip_bubbles() -> BubbleMarkup:
    """Get skip state bubbles."""

    bubbles = BubbleMarkup()
    bubbles.add_button(
        command=HiddenCommands.SKIP_COMMAND.command,
        label=strings.SKIP_COMMAND_LABEL,
    )

    return bubbles


def get_select_attribute_bubbles() -> BubbleMarkup:
    """Get bubbles for select updating attribute."""

    bubbles = BubbleMarkup()
    bubbles.add_button(
        command=HiddenCommands.UPDATE_DESCRIPTION_COMMAND.command,
        label=strings.UPDATE_DESCRIPTION_COMMAND_LABEL,
    )
    bubbles.add_button(
        command=HiddenCommands.UPDATE_ATTACHMENT_COMMAND.command,
        label=strings.UPDATE_ATTACHMENT_COMMAND_LABEL,
    )

    return bubbles
