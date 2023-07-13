"""Middleware for check cancel request."""

from pybotx import Bot, IncomingMessage, IncomingMessageHandlerFunc

from app.bot.answers.messages.support_request import (
    build_cancel_message,
    build_confirm_cancel_message,
)
from app.bot.commands.listing import HiddenCommands
from app.db.repositories.service_desk import ServiceDeskRepo


async def confirm_cancel_middleware(
    message: IncomingMessage, bot: Bot, call_next: IncomingMessageHandlerFunc
) -> None:
    """Drop state, if cancel command received (with confirmation)."""

    command = message.body

    if command == HiddenCommands.CANCEL_COMMAND.command:
        await bot.send(message=build_confirm_cancel_message(message))
        return
    elif command == HiddenCommands.CONFIRM_CANCEL_COMMAND.command:
        await ServiceDeskRepo(
            sender_huid=message.sender.huid, attachment=message.file  # type: ignore
        ).delete_user_attachments()

        await bot.send(message=build_cancel_message(message))
        await message.state.fsm.drop_state()
        return

    await call_next(message, bot)
