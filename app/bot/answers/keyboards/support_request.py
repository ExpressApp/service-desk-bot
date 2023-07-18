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


def get_back_to_confirm_keyboard() -> KeyboardMarkup:
    """Get keyboard for back to confirm state."""

    keyboard = KeyboardMarkup()
    keyboard.add_button(
        command=HiddenCommands.BACK_COMMAND.command,
        label=strings.BACK_COMMAND_LABEL,
    )
    keyboard.add_button(
        command=HiddenCommands.CANCEL_COMMAND.command,
        label=strings.CANCEL_COMMAND_LABEL,
    )

    return keyboard
