"""Handlers for default bot commands and system events."""

from os import environ

from pybotx import (
    Bot,
    ChatCreatedEvent,
    HandlerCollector,
    IncomingMessage,
    StatusRecipient,
)

from app.bot.answers.bubbles.common import get_default_bubbles
from app.bot.answers.messages.common import build_default_message
from app.bot.commands.listing import PublicCommands
from app.resources import strings
from app.settings import settings

collector = HandlerCollector()


@collector.default_message_handler
async def default_handler(
    message: IncomingMessage,
    bot: Bot,
) -> None:
    """Run if command handler not found."""

    answer_body = strings.DEFAULT_TEMPLATE.format(app_name=settings.APP_NAME)
    await bot.send(message=build_default_message(message, body=answer_body))


@collector.chat_created
async def chat_created_handler(event: ChatCreatedEvent, bot: Bot) -> None:
    """Send a welcome message and the bot functionality in new created chat."""

    answer_body = strings.CHAT_CREATED_TEMPLATE.format(app_name=settings.APP_NAME)

    await bot.answer_message(answer_body, bubbles=get_default_bubbles())


@collector.command(
    PublicCommands.HELP_COMMAND.command,
    description=PublicCommands.HELP_COMMAND.description,
)
async def help_handler(message: IncomingMessage, bot: Bot) -> None:
    """Show commands list."""

    status_recipient = StatusRecipient.from_incoming_message(message)
    status = await bot.get_status(status_recipient)
    command_map = dict(sorted(status.items()))

    answer_body = strings.HELP_COMMAND_MESSAGE_TEMPLATE.format(
        commands=command_map.items(), app_name=settings.APP_NAME
    )

    await bot.send(message=build_default_message(message, body=answer_body))


@collector.command("/_debug:git-commit-sha", visible=False)
async def git_commit_sha(message: IncomingMessage, bot: Bot) -> None:
    """Show git commit SHA."""

    await bot.answer_message(environ.get("GIT_COMMIT_SHA", "<undefined>"))
