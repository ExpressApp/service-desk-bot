"""Handler for update support request command."""

from pybotx import Bot, IncomingMessage
from pybotx_fsm import FSMCollector

from app.bot.answers.messages.support_request import (
    build_add_attachment_message,
    build_confirm_request_message,
    build_description_max_length_exceeded_message,
    build_enter_new_description_message,
    build_existing_attachments_message,
    build_invalid_attachment_message,
    build_select_updating_attribute_message,
    build_text_instead_attachment_message,
)
from app.bot.commands.listing import HiddenCommands
from app.bot.middlewares.confirm_cancel import confirm_cancel_middleware
from app.bot.states.support_request import (
    CreateSupportRequestStates,
    UpdateSupportRequestStates,
)
from app.db.repositories.service_desk import ServiceDeskRepo
from app.schemas.support_request import SupportRequestInUpdating
from app.settings import settings

fsm = FSMCollector(UpdateSupportRequestStates, middlewares=[confirm_cancel_middleware])


@fsm.on(UpdateSupportRequestStates.SELECT_ATTRIBUTE)
async def select_updating_attribute_handler(  # noqa: WPS213
    message: IncomingMessage, bot: Bot
) -> None:
    """Select updating attribute and switch to next state (FSM)."""

    command = message.body
    support_request: SupportRequestInUpdating = (
        message.state.fsm_storage.support_request
    )
    service_desk_repo = ServiceDeskRepo(
        sender_huid=message.sender.huid, attachment=message.file  # type: ignore
    )

    if not command or command not in {  # noqa: WPS337
        HiddenCommands.UPDATE_DESCRIPTION_COMMAND.command,
        HiddenCommands.UPDATE_ATTACHMENT_COMMAND.command,
        HiddenCommands.BACK_COMMAND.command,
    }:
        await bot.send(message=build_select_updating_attribute_message(message))
        await message.state.fsm.change_state(
            state=UpdateSupportRequestStates.SELECT_ATTRIBUTE,
            support_request=support_request,
        )
        return

    if command == HiddenCommands.UPDATE_DESCRIPTION_COMMAND.command:
        await bot.send(message=build_enter_new_description_message(message))
        await message.state.fsm.change_state(
            state=UpdateSupportRequestStates.ENTER_DESCRIPTION,
            support_request=support_request,
        )
    elif command == HiddenCommands.UPDATE_ATTACHMENT_COMMAND.command:
        await service_desk_repo.delete_user_attachments()

        await bot.send(message=build_add_attachment_message(message))
        await message.state.fsm.change_state(
            state=UpdateSupportRequestStates.ADD_ATTACHMENT,
            support_request=support_request,
        )
    else:
        await message.state.fsm.drop_state()

        await bot.send(
            message=build_confirm_request_message(message, request=support_request)
        )
        await message.state.fsm.change_state(
            state=CreateSupportRequestStates.CONFIRM_REQUEST,
            support_request=support_request,
        )


@fsm.on(UpdateSupportRequestStates.ENTER_DESCRIPTION)
async def enter_new_description_handler(message: IncomingMessage, bot: Bot) -> None:
    """Add new request description and switch to next state (FSM)."""

    new_description = message.body

    if not new_description:
        await bot.send(message=build_enter_new_description_message(message))
        return

    if len(new_description) > settings.MAX_DESCRIPTION_LENGTH:
        await bot.send(message=build_description_max_length_exceeded_message(message))
        return

    support_request: SupportRequestInUpdating = (
        message.state.fsm_storage.support_request
    )
    support_request.description = new_description
    await message.state.fsm.drop_state()

    await bot.send(
        message=build_confirm_request_message(message, request=support_request)
    )
    await message.state.fsm.change_state(
        CreateSupportRequestStates.CONFIRM_REQUEST, support_request=support_request
    )


@fsm.on(UpdateSupportRequestStates.ADD_ATTACHMENT)
async def add_new_attachment_handler(  # noqa: WPS213
    message: IncomingMessage, bot: Bot
) -> None:
    """Add new request attachments and drop state (FSM)."""

    command = message.body
    attachment = message.file
    service_desk_repo = ServiceDeskRepo(
        sender_huid=message.sender.huid, attachment=message.file  # type: ignore
    )
    support_request: SupportRequestInUpdating = (
        message.state.fsm_storage.support_request
    )

    if command in {  # noqa: WPS337
        HiddenCommands.SKIP_COMMAND.command,
        HiddenCommands.SEND_TO_CONFIRM_COMMAND.command,
    }:
        if command == HiddenCommands.SKIP_COMMAND.command:
            await service_desk_repo.delete_user_attachments()

        support_request.attachments_names = (
            service_desk_repo.get_user_attachments_names()
        )
        await message.state.fsm.drop_state()

        await bot.send(
            message=build_confirm_request_message(message, request=support_request)
        )
        await message.state.fsm.change_state(
            CreateSupportRequestStates.CONFIRM_REQUEST, support_request=support_request
        )
        return

    if not attachment:
        await bot.send(message=build_text_instead_attachment_message(message))
        return

    if not service_desk_repo.is_valid_attachment():
        await bot.send(message=build_invalid_attachment_message(message))
        return

    service_desk_repo.add_user_attachment(user_attachment=attachment)  # type: ignore
    attachments_names = service_desk_repo.get_user_attachments_names()
    support_request.attachments_names = attachments_names
    await bot.send(
        message=build_existing_attachments_message(
            message, attachments_names=attachments_names
        )
    )
    await message.state.fsm.change_state(
        UpdateSupportRequestStates.ADD_ATTACHMENT, support_request=support_request
    )
