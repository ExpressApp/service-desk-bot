"""Handler for create support request command."""

from pybotx import Bot, HandlerCollector, IncomingMessage
from pybotx_fsm import FSMCollector

from app.bot.answers.messages.support_request import (  # noqa: WPS235
    build_add_attachment_message,
    build_confirm_attachment_addition_message,
    build_confirm_request_message,
    build_description_max_length_exceeded_message,
    build_enter_description_message,
    build_existing_attachments_message,
    build_invalid_attachment_message,
    build_not_confirm_command_message,
    build_select_updating_attribute_message,
    build_text_instead_attachment_message,
)
from app.bot.commands.listing import HiddenCommands, PublicCommands
from app.bot.commands.support_request.send import send_support_request
from app.bot.middlewares.confirm_cancel import confirm_cancel_middleware
from app.bot.states.support_request import (
    CreateSupportRequestStates,
    UpdateSupportRequestStates,
)
from app.db.repositories.service_desk import ServiceDeskRepo
from app.resources import strings
from app.schemas.support_request import (
    SupportRequestInCreation,
    SupportRequestInUpdating,
    SupportRequestToSend,
)
from app.settings import settings

collector = HandlerCollector()
fsm = FSMCollector(CreateSupportRequestStates, middlewares=[confirm_cancel_middleware])


@collector.command(
    PublicCommands.CREATE_SUPPORT_REQUEST_COMMAND.command,
    description=PublicCommands.CREATE_SUPPORT_REQUEST_COMMAND.description,
)
async def create_support_request_handler(message: IncomingMessage, bot: Bot) -> None:
    """Starts support request creation process (FSM)."""  # noqa: D401

    await ServiceDeskRepo(
        sender_huid=message.sender.huid, attachment=message.file  # type: ignore
    ).delete_user_attachments()

    subject = strings.SUBJECT_TEMPLATE.format(
        email_title=settings.EMAIL_TITLE,
        username=message.sender.username,
        show_sender_name_in_email_title=settings.SHOW_SENDER_NAME_IN_EMAIL_TITLE,
    )
    support_request = SupportRequestInCreation(subject=subject)

    await bot.send(message=build_enter_description_message(message))
    await message.state.fsm.change_state(
        state=CreateSupportRequestStates.ENTER_DESCRIPTION,
        support_request=support_request,
    )


@fsm.on(CreateSupportRequestStates.ENTER_DESCRIPTION)
async def enter_support_request_description_handler(
    message: IncomingMessage, bot: Bot
) -> None:
    """Add request description, attachment and switch to next state (FSM)."""

    description = message.body

    if not description:
        await bot.send(message=build_enter_description_message(message))
        return

    if len(description) > settings.MAX_DESCRIPTION_LENGTH:
        await bot.send(message=build_description_max_length_exceeded_message(message))
        return

    service_desk_repo = ServiceDeskRepo(
        sender_huid=message.sender.huid, attachment=message.file  # type: ignore
    )
    support_request: SupportRequestInCreation = (
        message.state.fsm_storage.support_request
    )
    support_request.description = description

    attachment = message.file

    if attachment:
        if not service_desk_repo.is_valid_attachment():
            await bot.send(message=build_invalid_attachment_message(message))
            return

        service_desk_repo.add_user_attachment(
            user_attachment=attachment  # type: ignore
        )
        support_request.attachments_names = (
            service_desk_repo.get_user_attachments_names()
        )
        await bot.send(
            message=build_confirm_request_message(message, request=support_request)
        )
        await message.state.fsm.change_state(
            CreateSupportRequestStates.CONFIRM_REQUEST, support_request=support_request
        )
        return

    await bot.send(message=build_confirm_attachment_addition_message(message))
    await message.state.fsm.change_state(
        CreateSupportRequestStates.WAIT_DECISION_ON_ATTACHMENT,
        support_request=support_request,
    )


@fsm.on(CreateSupportRequestStates.WAIT_DECISION_ON_ATTACHMENT)
async def wait_decision_on_attachment_handler(
    message: IncomingMessage, bot: Bot
) -> None:
    """Wait decision on attachment addition and switch to next state (FSM)."""

    if not message.body:
        await bot.send(message=build_confirm_attachment_addition_message(message))
        return

    support_request: SupportRequestInCreation = (
        message.state.fsm_storage.support_request
    )
    service_desk_repo = ServiceDeskRepo(
        sender_huid=message.sender.huid, attachment=message.file  # type: ignore
    )

    if message.body == HiddenCommands.CONFIRM_ATTACHMENT_ADDITION_COMMAND.command:
        attachments_names = service_desk_repo.get_user_attachments_names()
        support_request.attachments_names = attachments_names

        if attachments_names:
            await bot.send(
                message=build_existing_attachments_message(
                    message, attachments_names=attachments_names
                )
            )
        else:
            await bot.send(message=build_add_attachment_message(message))

        await message.state.fsm.change_state(
            CreateSupportRequestStates.ADD_ATTACHMENT, support_request=support_request
        )

    elif message.body == HiddenCommands.REFUSE_ATTACHMENT_ADDITION_COMMAND.command:
        await service_desk_repo.delete_user_attachments()

        support_request.attachments_names = []
        await bot.send(
            message=build_confirm_request_message(message, request=support_request)
        )
        await message.state.fsm.change_state(
            CreateSupportRequestStates.CONFIRM_REQUEST, support_request=support_request
        )
        return
    else:
        await bot.send(message=build_confirm_attachment_addition_message(message))


@fsm.on(CreateSupportRequestStates.ADD_ATTACHMENT)
async def add_attachment_handler(message: IncomingMessage, bot: Bot) -> None:
    """Add request attachments and switch to next state (FSM)."""

    command = message.body
    attachment = message.file
    service_desk_repo = ServiceDeskRepo(
        sender_huid=message.sender.huid, attachment=message.file  # type: ignore
    )
    support_request: SupportRequestInCreation = (
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
        CreateSupportRequestStates.ADD_ATTACHMENT, support_request=support_request
    )


@fsm.on(CreateSupportRequestStates.CONFIRM_REQUEST)
async def add_confirm_request_handler(message: IncomingMessage, bot: Bot) -> None:
    """Confirm request and drop state (FSM)."""

    command = message.body

    if not command or command not in {  # noqa: WPS337
        HiddenCommands.SEND_REQUEST_COMMAND.command,
        HiddenCommands.UPDATE_SUPPORT_REQUEST_COMMAND.command,
    }:
        await bot.send(message=build_not_confirm_command_message(message))
        return

    support_request: SupportRequestInCreation = (
        message.state.fsm_storage.support_request
    )
    await message.state.fsm.drop_state()

    if command == HiddenCommands.SEND_REQUEST_COMMAND.command:
        support_request_to_send = SupportRequestToSend(**support_request.dict())

        await send_support_request(
            message, bot, support_request=support_request_to_send
        )
    else:
        support_request_in_updating = SupportRequestInUpdating(**support_request.dict())

        await bot.send(message=build_select_updating_attribute_message(message))
        await message.state.fsm.change_state(
            state=UpdateSupportRequestStates.SELECT_ATTRIBUTE,
            support_request=support_request_in_updating,
        )
