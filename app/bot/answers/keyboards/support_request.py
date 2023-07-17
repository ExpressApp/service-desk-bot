"""Keyboards for support request handlers."""

from pybotx import KeyboardMarkup

from app.bot.commands.listing import HiddenCommands
from app.resources import strings


def get_invalid_attachment_keyboard() -> KeyboardMarkup:
    """Get keyboard to cancel state."""

    keyboard = KeyboardMarkup()
    keyboard.add_button(
        command=HiddenCommands.SEND_TO_CONFIRM_COMMAND.command,
        label=strings.SEND_SUPPORT_REQUEST_COMMAND_LABEL.upper(),
    )
    keyboard.add_button(
        command=HiddenCommands.CANCEL_COMMAND.command,
        label=strings.CANCEL_COMMAND_LABEL,
    )

    return keyboard
