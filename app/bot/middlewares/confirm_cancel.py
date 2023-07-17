"""Middleware for check cancel request."""

from pybotx import Bot, IncomingMessage, IncomingMessageHandlerFunc

from app.bot.answers.messages.support_request import (  # noqa: WPS235
    build_add_attachment_message,
    build_cancel_message,
    build_confirm_attachment_addition_message,
    build_confirm_cancel_message,
    build_confirm_request_message,
    build_enter_description_message,
    build_enter_new_description_message,
    build_existing_attachments_message,
    build_select_updating_attribute_message,
)
from app.bot.commands.listing import HiddenCommands
from app.bot.states.support_request import (
    CreateSupportRequestStates,
    UpdateSupportRequestStates,
)
from app.db.repositories.service_desk import ServiceDeskRepo
from app.schemas.support_request import SupportRequestInCreation

STATE_MESSAGES = {  # noqa: WPS407
    CreateSupportRequestStates.ENTER_DESCRIPTION: build_enter_description_message,
    UpdateSupportRequestStates.ENTER_DESCRIPTION: build_enter_new_description_message,
    CreateSupportRequestStates.WAIT_DECISION_ON_ATTACHMENT: build_confirm_attachment_addition_message,  # noqa: E501
    CreateSupportRequestStates.ADD_ATTACHMENT: build_add_attachment_message,
    UpdateSupportRequestStates.ADD_ATTACHMENT: build_add_attachment_message,
    UpdateSupportRequestStates.SELECT_ATTRIBUTE: build_select_updating_attribute_message,  # noqa: E501
}


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
    elif command == HiddenCommands.REFUSE_CANCEL_COMMAND.command:
        await _send_current_state_message(message, bot)
        return

    await call_next(message, bot)


async def _send_current_state_message(message: IncomingMessage, bot: Bot) -> None:
    """Send state message if received /refuse-cancel command."""

    current_state = await message.state.fsm.get_state()

    if current_state == CreateSupportRequestStates.CONFIRM_REQUEST:
        support_request: SupportRequestInCreation = (
            message.state.fsm_storage.support_request
        )
        await bot.send(
            message=build_confirm_request_message(message, request=support_request)
        )
    elif current_state in {  # noqa: WPS337
        CreateSupportRequestStates.ADD_ATTACHMENT,
        UpdateSupportRequestStates.ADD_ATTACHMENT,
    }:
        attachments_names = ServiceDeskRepo(
            sender_huid=message.sender.huid, attachment=message.file  # type: ignore
        ).get_user_attachments_names()

        if attachments_names:
            await bot.send(
                message=build_existing_attachments_message(
                    message, attachments_names=attachments_names
                )
            )
        else:
            await bot.send(message=build_add_attachment_message(message))
    else:
        await bot.send(message=STATE_MESSAGES[current_state](message))
