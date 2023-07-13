"""Keyboards for common handlers."""

from pybotx import KeyboardMarkup

from app.bot.commands.listing import HiddenCommands
from app.resources import strings


def get_cancel_keyboard() -> KeyboardMarkup:
    """Get keyboard to cancel state."""

    keyboard = KeyboardMarkup()
    keyboard.add_button(
        command=HiddenCommands.CANCEL_COMMAND.command,
        label=strings.CANCEL_COMMAND_LABEL,
    )

    return keyboard
