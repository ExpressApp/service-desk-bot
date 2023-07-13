"""Bubble for support request handlers."""

from pybotx import BubbleMarkup

from app.bot.commands.listing import HiddenCommands
from app.resources import strings


def get_confirm_cancel_bubbles() -> BubbleMarkup:
    """Get confirm cancel bubbles."""

    bubbles = BubbleMarkup()
    bubbles.add_button(
        command=HiddenCommands.CONFIRM_CANCEL_COMMAND.command,
        label=strings.CONFIRM_COMMAND_LABEL,
    )
    bubbles.add_button(
        command=HiddenCommands.REFUSE_CANCEL_COMMAND.command,
        label=strings.REFUSE_COMMAND_LABEL,
    )

    return bubbles


def get_confirm_request_bubbles() -> BubbleMarkup:
    """Get confirm support request bubbles."""

    bubbles = BubbleMarkup()
    bubbles.add_button(
        command=HiddenCommands.SEND_SUPPORT_REQUEST_COMMAND.command,
        label=strings.CONFIRM_COMMAND_LABEL,
    )
    bubbles.add_button(
        command=HiddenCommands.REFUSE_REQUEST_COMMAND.command,
        label=strings.REFUSE_COMMAND_LABEL,
    )

    return bubbles


def get_confirm_attachment_addition_bubbles() -> BubbleMarkup:
    """Get confirm attachment addition bubbles."""

    bubbles = BubbleMarkup()
    bubbles.add_button(
        command=HiddenCommands.CONFIRM_ATTACHMENT_ADDITION_COMMAND.command,
        label=strings.CONFIRM_COMMAND_LABEL,
    )
    bubbles.add_button(
        command=HiddenCommands.REFUSE_ATTACHMENT_ADDITION_COMMAND.command,
        label=strings.REFUSE_COMMAND_LABEL,
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
