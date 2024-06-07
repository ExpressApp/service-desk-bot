"""Bubble for common handlers."""

from pybotx import BubbleMarkup

from app.bot.commands.listing import PublicCommands
from app.resources import strings


def get_default_bubbles() -> BubbleMarkup:
    """Get default bubbles with base commands."""

    bubbles = BubbleMarkup()
    bubbles.add_button(
        command=PublicCommands.CREATE_SUPPORT_REQUEST_COMMAND.command,
        label=strings.CREATE_SUPPORT_REQUEST_COMMAND_LABEL,
    )

    return bubbles
