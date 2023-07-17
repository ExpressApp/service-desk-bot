from typing import Callable
from unittest.mock import AsyncMock, MagicMock, patch

from pybotx import (
    Bot,
    BubbleMarkup,
    Button,
    IncomingMessage,
    KeyboardMarkup,
    OutgoingMessage,
)
from pybotx.models.attachments import AttachmentDocument
from pybotx_fsm import FSM

from app.bot.states.support_request import (
    CreateSupportRequestStates,
    UpdateSupportRequestStates,
)
from app.schemas.support_request import SupportRequestInCreation


@patch(
    "app.bot.commands.support_request.create.ServiceDeskRepo.delete_user_attachments",
    new_callable=AsyncMock,
)
async def test__create_support_request_handler(
    mocked_delete_user_attachments: AsyncMock,
    bot: Bot,
    incoming_message_factory: Callable[..., IncomingMessage],
    fsm_session: FSM,
) -> None:
    # - Arrange -
    message = incoming_message_factory(body="/обращение")

    # - Act -
    await bot.async_execute_bot_command(message)

    # - Assert -
    assert mocked_delete_user_attachments.call_count == 1
    assert await fsm_session.get_state() == CreateSupportRequestStates.ENTER_DESCRIPTION
    bot.send.assert_awaited_once_with(  # type: ignore
        message=OutgoingMessage(
            bot_id=message.bot.id,
            chat_id=message.chat.id,
            body=(
                "❗ Опишите подробно возникшую проблему, укажите какие действия "
                "Вы выполняете и какой результат получаете. Прикрепите фото "
                "или медиафайл.\n\n⚡ От полноты описания будет зависеть "
                "скорость решения Вашего обращения.\n\n📱 Обращение должно "
                "быть отправлено с устройства, где возникла проблема."
            ),
            keyboard=KeyboardMarkup([[Button(command="/cancel", label="ОТМЕНА")]]),
        ),
    )


async def test__enter_support_request_description_handler__empty_message(
    bot: Bot,
    incoming_message_factory: Callable[..., IncomingMessage],
    fsm_session: FSM,
) -> None:
    # - Arrange -
    message = incoming_message_factory(body="")
    await fsm_session.change_state(state=CreateSupportRequestStates.ENTER_DESCRIPTION)

    # - Act -
    await bot.async_execute_bot_command(message)

    # - Assert -
    assert await fsm_session.get_state() == CreateSupportRequestStates.ENTER_DESCRIPTION
    bot.send.assert_awaited_once_with(  # type: ignore
        message=OutgoingMessage(
            bot_id=message.bot.id,
            chat_id=message.chat.id,
            body=(
                "❗ Опишите подробно возникшую проблему, укажите какие действия "
                "Вы выполняете и какой результат получаете. Прикрепите фото "
                "или медиафайл.\n\n⚡ От полноты описания будет зависеть скорость "
                "решения Вашего обращения.\n\n📱 Обращение должно быть отправлено "
                "с устройства, где возникла проблема."
            ),
            keyboard=KeyboardMarkup([[Button(command="/cancel", label="ОТМЕНА")]]),
        ),
    )


@patch("app.bot.commands.support_request.create.settings.MAX_DESCRIPTION_LENGTH", new=5)
async def test__enter_support_request_description_handler__max_description_length_exceeded(  # noqa: E501
    bot: Bot,
    incoming_message_factory: Callable[..., IncomingMessage],
    fsm_session: FSM,
    default_string: str,
) -> None:
    # - Arrange -
    message = incoming_message_factory(body=default_string)
    await fsm_session.change_state(state=CreateSupportRequestStates.ENTER_DESCRIPTION)

    # - Act -
    await bot.async_execute_bot_command(message)

    # - Assert -
    assert await fsm_session.get_state() == CreateSupportRequestStates.ENTER_DESCRIPTION
    bot.send.assert_awaited_once_with(  # type: ignore
        message=OutgoingMessage(
            bot_id=message.bot.id,
            chat_id=message.chat.id,
            body=(
                "Вы ввели недопустимое количество символов. Максимум - 5 символов.\n"
                "**Пожалуйста, сократите текст вашего сообщения и отправьте заново:**"
            ),
            keyboard=KeyboardMarkup([[Button(command="/cancel", label="ОТМЕНА")]]),
        ),
    )


async def test__enter_support_request_description_handler__without_attachment(
    bot: Bot,
    incoming_message_factory: Callable[..., IncomingMessage],
    fsm_session: FSM,
    default_string: str,
) -> None:
    # - Arrange -
    message = incoming_message_factory(body=default_string)
    await fsm_session.change_state(
        state=CreateSupportRequestStates.ENTER_DESCRIPTION,
        support_request=SupportRequestInCreation(),
    )

    # - Act -
    await bot.async_execute_bot_command(message)

    # - Assert -
    assert (
        await fsm_session.get_state()
        == CreateSupportRequestStates.WAIT_DECISION_ON_ATTACHMENT  # noqa: W503
    )
    assert message.state.fsm_storage.support_request.description == default_string
    bot.send.assert_awaited_once_with(  # type: ignore
        message=OutgoingMessage(
            bot_id=message.bot.id,
            chat_id=message.chat.id,
            body=(
                "Хотели бы Вы прикрепить фото или медиафайл? "
                "Скриншот возникшей проблемы поможет ускорить обработку "
                "Вашего обращения."
            ),
            bubbles=BubbleMarkup(
                [
                    [Button(command="/confirm-attachment-addition", label="Да")],
                    [Button(command="/refuse-attachment-addition", label="Нет")],
                ]
            ),
            keyboard=KeyboardMarkup([[Button(command="/cancel", label="ОТМЕНА")]]),
        ),
    )


@patch(
    "app.bot.commands.support_request.create.ServiceDeskRepo.is_valid_attachment",
    return_value=False,
)
async def test__enter_support_request_description_handler__invalid_attachment(
    mocked_is_valid_attachment: MagicMock,
    bot: Bot,
    incoming_message_factory: Callable[..., IncomingMessage],
    incoming_attachment: AttachmentDocument,
    fsm_session: FSM,
    default_string: str,
) -> None:
    # - Arrange -
    message = incoming_message_factory(body=default_string, file=incoming_attachment)
    await fsm_session.change_state(
        state=CreateSupportRequestStates.ENTER_DESCRIPTION,
        support_request=SupportRequestInCreation(),
    )

    # - Act -
    await bot.async_execute_bot_command(message)

    # - Assert -
    assert mocked_is_valid_attachment.call_count == 1
    assert await fsm_session.get_state() == CreateSupportRequestStates.ENTER_DESCRIPTION
    assert message.state.fsm_storage.support_request.description == default_string
    bot.send.assert_awaited_once_with(  # type: ignore
        message=OutgoingMessage(
            bot_id=message.bot.id,
            chat_id=message.chat.id,
            body=(
                "Вы пытаетесь загрузить файл(ы) размер или количество которых "
                "превышает допустимое.\nПожалуйста, уменьшите размер файла(ов) "
                "и загрузите снова.\nТакже Вы можете нажать кнопку **«Отмена»** "
                "для отмены оформления обращения или **«Отправить обращение»** "
                "для регистрации запроса без файлов."
            ),
            keyboard=KeyboardMarkup(
                [
                    [Button(command="/send-to-confirm", label="ОТПРАВИТЬ ОБРАЩЕНИЕ")],
                    [Button(command="/cancel", label="ОТМЕНА")],
                ]
            ),
        ),
    )


@patch(
    "app.bot.commands.support_request.create.ServiceDeskRepo.get_user_attachments_names"
)
@patch("app.bot.commands.support_request.create.ServiceDeskRepo.add_user_attachment")
@patch(
    "app.bot.commands.support_request.create.ServiceDeskRepo.is_valid_attachment",
    return_value=True,
)
async def test__enter_support_request_description_handler__valid_attachment(  # noqa: WPS218, E501
    mocked_is_valid_attachment: MagicMock,
    mocked_add_user_attachment: MagicMock,
    mocked_get_user_attachments_names: MagicMock,
    bot: Bot,
    incoming_message_factory: Callable[..., IncomingMessage],
    incoming_attachment: AttachmentDocument,
    fsm_session: FSM,
    default_string: str,
    default_list: list[str],
) -> None:
    # - Arrange -
    message = incoming_message_factory(body=default_string, file=incoming_attachment)
    await fsm_session.change_state(
        state=CreateSupportRequestStates.ENTER_DESCRIPTION,
        support_request=SupportRequestInCreation(),
    )
    mocked_get_user_attachments_names.return_value = default_list

    # - Act -
    await bot.async_execute_bot_command(message)

    # - Assert -
    assert mocked_is_valid_attachment.call_count == 1
    assert mocked_add_user_attachment.call_count == 1
    assert mocked_get_user_attachments_names.call_count == 1
    assert await fsm_session.get_state() == CreateSupportRequestStates.CONFIRM_REQUEST
    assert message.state.fsm_storage.support_request.description == default_string
    assert message.state.fsm_storage.support_request.attachments_names == default_list
    bot.send.assert_awaited_once_with(  # type: ignore
        message=OutgoingMessage(
            bot_id=message.bot.id,
            chat_id=message.chat.id,
            body=(
                "**Проверьте правильность ввода:**\n"
                "**Описание проблемы:** lorem ipsum\n"
                "**Приложенные файлы:** dolor sit amet, lorem ipsum\n"
                "**Всё верно?**"
            ),
            bubbles=BubbleMarkup(
                [
                    [Button(command="/send-request", label="Да")],
                    [Button(command="/update-request", label="Нет")],
                ]
            ),
            keyboard=KeyboardMarkup([[Button(command="/cancel", label="ОТМЕНА")]]),
        ),
    )


async def test__wait_decision_on_attachment_handler__empty_message(
    bot: Bot,
    incoming_message_factory: Callable[..., IncomingMessage],
    fsm_session: FSM,
    default_string: str,
) -> None:
    # - Arrange -
    message = incoming_message_factory(body="")
    support_request = SupportRequestInCreation(description=default_string)
    await fsm_session.change_state(
        state=CreateSupportRequestStates.WAIT_DECISION_ON_ATTACHMENT,
        support_request=support_request,
    )

    # - Act -
    await bot.async_execute_bot_command(message)

    # - Assert -
    assert (
        await fsm_session.get_state()
        == CreateSupportRequestStates.WAIT_DECISION_ON_ATTACHMENT  # noqa: W503
    )
    assert message.state.fsm_storage.support_request.description == default_string
    assert not message.state.fsm_storage.support_request.attachments_names
    bot.send.assert_awaited_once_with(  # type: ignore
        message=OutgoingMessage(
            bot_id=message.bot.id,
            chat_id=message.chat.id,
            body=(
                "Хотели бы Вы прикрепить фото или медиафайл? "
                "Скриншот возникшей проблемы поможет ускорить обработку"
                " Вашего обращения."
            ),
            bubbles=BubbleMarkup(
                [
                    [Button(command="/confirm-attachment-addition", label="Да")],
                    [Button(command="/refuse-attachment-addition", label="Нет")],
                ]
            ),
            keyboard=KeyboardMarkup([[Button(command="/cancel", label="ОТМЕНА")]]),
        ),
    )


async def test__wait_decision_on_attachment_handler__text_instead_command(
    bot: Bot,
    incoming_message_factory: Callable[..., IncomingMessage],
    fsm_session: FSM,
    default_string: str,
) -> None:
    # - Arrange -
    message = incoming_message_factory(body=default_string)
    support_request = SupportRequestInCreation(description=default_string)
    await fsm_session.change_state(
        state=CreateSupportRequestStates.WAIT_DECISION_ON_ATTACHMENT,
        support_request=support_request,
    )

    # - Act -
    await bot.async_execute_bot_command(message)

    # - Assert -
    assert (
        await fsm_session.get_state()
        == CreateSupportRequestStates.WAIT_DECISION_ON_ATTACHMENT  # noqa: W503
    )
    assert message.state.fsm_storage.support_request.description == default_string
    assert not message.state.fsm_storage.support_request.attachments_names
    bot.send.assert_awaited_once_with(  # type: ignore
        message=OutgoingMessage(
            bot_id=message.bot.id,
            chat_id=message.chat.id,
            body=(
                "Хотели бы Вы прикрепить фото или медиафайл? "
                "Скриншот возникшей проблемы поможет ускорить обработку "
                "Вашего обращения."
            ),
            bubbles=BubbleMarkup(
                [
                    [Button(command="/confirm-attachment-addition", label="Да")],
                    [Button(command="/refuse-attachment-addition", label="Нет")],
                ]
            ),
            keyboard=KeyboardMarkup([[Button(command="/cancel", label="ОТМЕНА")]]),
        ),
    )


@patch(
    "app.bot.commands.support_request.create.ServiceDeskRepo.delete_user_attachments",
    new_callable=AsyncMock,
)
async def test__wait_decision_on_attachment_handler__refuse_command(
    mocked_delete_user_attachments: AsyncMock,
    bot: Bot,
    incoming_message_factory: Callable[..., IncomingMessage],
    fsm_session: FSM,
    default_string: str,
    default_list: list[str],
) -> None:
    # - Arrange -
    message = incoming_message_factory(body="/refuse-attachment-addition")
    support_request = SupportRequestInCreation(
        description=default_string, attachments_names=default_list
    )
    await fsm_session.change_state(
        state=CreateSupportRequestStates.WAIT_DECISION_ON_ATTACHMENT,
        support_request=support_request,
    )

    # - Act -
    await bot.async_execute_bot_command(message)

    # - Assert -
    assert mocked_delete_user_attachments.call_count == 1
    assert await fsm_session.get_state() == CreateSupportRequestStates.CONFIRM_REQUEST
    assert message.state.fsm_storage.support_request.description == default_string
    assert not message.state.fsm_storage.support_request.attachments_names
    bot.send.assert_awaited_once_with(  # type: ignore
        message=OutgoingMessage(
            bot_id=message.bot.id,
            chat_id=message.chat.id,
            body=(
                "**Проверьте правильность ввода:**\n"
                "**Описание проблемы:** lorem ipsum\n"
                "**Приложенные файлы:** -\n"
                "**Всё верно?**"
            ),
            bubbles=BubbleMarkup(
                [
                    [Button(command="/send-request", label="Да")],
                    [Button(command="/update-request", label="Нет")],
                ]
            ),
            keyboard=KeyboardMarkup([[Button(command="/cancel", label="ОТМЕНА")]]),
        ),
    )


@patch(
    "app.bot.commands.support_request.create.ServiceDeskRepo.get_user_attachments_names"
)
async def test__wait_decision_on_attachment_handler__confirm_command_with_attachments(
    mocked_get_user_attachments_names: MagicMock,
    bot: Bot,
    incoming_message_factory: Callable[..., IncomingMessage],
    fsm_session: FSM,
    default_string: str,
    default_list: list[str],
) -> None:
    # - Arrange -
    message = incoming_message_factory(body="/confirm-attachment-addition")
    support_request = SupportRequestInCreation(description=default_string)
    mocked_get_user_attachments_names.return_value = default_list
    await fsm_session.change_state(
        state=CreateSupportRequestStates.WAIT_DECISION_ON_ATTACHMENT,
        support_request=support_request,
    )

    # - Act -
    await bot.async_execute_bot_command(message)

    # - Assert -
    assert mocked_get_user_attachments_names.call_count == 1
    assert await fsm_session.get_state() == CreateSupportRequestStates.ADD_ATTACHMENT
    assert message.state.fsm_storage.support_request.description == default_string
    assert message.state.fsm_storage.support_request.attachments_names == default_list
    bot.send.assert_awaited_once_with(  # type: ignore
        message=OutgoingMessage(
            bot_id=message.bot.id,
            chat_id=message.chat.id,
            body=(
                "**Прикрепленные файл(ы):**\n"
                "lorem ipsum\n"
                "dolor sit amet\n\n"
                "Отправленные Вами файлы для удобства не отображаются в чате. "
                "Если все необходимые файлы загружены, нажмите кнопку "
                "**Отправить обращение** под полем для ввода сообщений. "
                "Если необходимо добавить вложения — прикрепите их."
            ),
            bubbles=BubbleMarkup(
                [[Button(command="/send-to-confirm", label="Отправить обращение")]]
            ),
            keyboard=KeyboardMarkup([[Button(command="/cancel", label="ОТМЕНА")]]),
        ),
    )


@patch(
    "app.bot.commands.support_request.create.ServiceDeskRepo.get_user_attachments_names"
)
async def test__wait_decision_on_attachment_handler__confirm_command_without_attachments(  # noqa: E501
    mocked_get_user_attachments_names: MagicMock,
    bot: Bot,
    incoming_message_factory: Callable[..., IncomingMessage],
    fsm_session: FSM,
    default_string: str,
    default_list: list[str],
) -> None:
    # - Arrange -
    message = incoming_message_factory(body="/confirm-attachment-addition")
    support_request = SupportRequestInCreation(description=default_string)
    mocked_get_user_attachments_names.return_value = []
    await fsm_session.change_state(
        state=CreateSupportRequestStates.WAIT_DECISION_ON_ATTACHMENT,
        support_request=support_request,
    )

    # - Act -
    await bot.async_execute_bot_command(message)

    # - Assert -
    assert mocked_get_user_attachments_names.call_count == 1
    assert await fsm_session.get_state() == CreateSupportRequestStates.ADD_ATTACHMENT
    assert message.state.fsm_storage.support_request.description == default_string
    assert not message.state.fsm_storage.support_request.attachments_names
    bot.send.assert_awaited_once_with(  # type: ignore
        message=OutgoingMessage(
            bot_id=message.bot.id,
            chat_id=message.chat.id,
            body=(
                "**Отправьте фото или медиафайл (опционально).**"
                "\n\nВы можете загрузить до 20 файлов, размером не "
                "более 9.9 МБ каждый и не более 20.0 МБ "
                "суммарно.\n\nПосле того, как все необходимые файлы будут "
                'загружены, нажмите кнопку "**Отправить обращение**" '
                "под полем для ввода сообщений."
            ),
            bubbles=BubbleMarkup([[Button(command="/skip", label="Пропустить")]]),
            keyboard=KeyboardMarkup([[Button(command="/cancel", label="ОТМЕНА")]]),
        ),
    )


async def test__add_attachment_handler__text_instead_attachment(
    bot: Bot,
    incoming_message_factory: Callable[..., IncomingMessage],
    fsm_session: FSM,
    default_string: str,
) -> None:
    # - Arrange -
    message = incoming_message_factory(body="")
    support_request = SupportRequestInCreation(description=default_string)
    await fsm_session.change_state(
        state=CreateSupportRequestStates.ADD_ATTACHMENT, support_request=support_request
    )

    # - Act -
    await bot.async_execute_bot_command(message)

    # - Assert -
    assert await fsm_session.get_state() == CreateSupportRequestStates.ADD_ATTACHMENT
    assert message.state.fsm_storage.support_request.description == default_string
    assert not message.state.fsm_storage.support_request.attachments_names
    bot.send.assert_awaited_once_with(  # type: ignore
        message=OutgoingMessage(
            bot_id=message.bot.id,
            chat_id=message.chat.id,
            body=(
                "На данном этапе вы можете либо добавить файлы, либо пропустить "
                "данный шаг.\nЕсли вы хотите изменить тему или описание обращения, "
                'нажмите кнопку "Отмена" и оформите обращение заново.'
            ),
            bubbles=BubbleMarkup([[Button(command="/skip", label="Пропустить")]]),
            keyboard=KeyboardMarkup([[Button(command="/cancel", label="ОТМЕНА")]]),
        ),
    )


@patch(
    "app.bot.commands.support_request.create.ServiceDeskRepo.is_valid_attachment",
    return_value=False,
)
async def test__add_attachment_handler__invalid_attachment(
    mocked_is_valid_attachment: MagicMock,
    bot: Bot,
    incoming_message_factory: Callable[..., IncomingMessage],
    incoming_attachment: AttachmentDocument,
    fsm_session: FSM,
    default_string: str,
) -> None:
    # - Arrange -
    message = incoming_message_factory(body="", file=incoming_attachment)
    support_request = SupportRequestInCreation(description=default_string)
    await fsm_session.change_state(
        state=CreateSupportRequestStates.ADD_ATTACHMENT, support_request=support_request
    )

    # - Act -
    await bot.async_execute_bot_command(message)

    # - Assert -
    assert mocked_is_valid_attachment.call_count == 1
    assert await fsm_session.get_state() == CreateSupportRequestStates.ADD_ATTACHMENT
    assert message.state.fsm_storage.support_request.description == default_string
    assert not message.state.fsm_storage.support_request.attachments_names
    bot.send.assert_awaited_once_with(  # type: ignore
        message=OutgoingMessage(
            bot_id=message.bot.id,
            chat_id=message.chat.id,
            body=(
                "Вы пытаетесь загрузить файл(ы) размер или количество которых "
                "превышает допустимое.\nПожалуйста, уменьшите размер файла(ов) "
                "и загрузите снова.\nТакже Вы можете нажать кнопку **«Отмена»** "
                "для отмены оформления обращения или **«Отправить обращение»** "
                "для регистрации запроса без файлов."
            ),
            keyboard=KeyboardMarkup(
                [
                    [Button(command="/send-to-confirm", label="ОТПРАВИТЬ ОБРАЩЕНИЕ")],
                    [Button(command="/cancel", label="ОТМЕНА")],
                ]
            ),
        ),
    )


@patch(
    "app.bot.commands.support_request.create.ServiceDeskRepo.get_user_attachments_names"
)
@patch("app.bot.commands.support_request.create.ServiceDeskRepo.add_user_attachment")
@patch(
    "app.bot.commands.support_request.create.ServiceDeskRepo.is_valid_attachment",
    return_value=True,
)
async def test__add_attachment_handler__valid_attachment(  # noqa: WPS218
    mocked_is_valid_attachment: MagicMock,
    mocked_add_user_attachment: MagicMock,
    mocked_get_user_attachments_names: MagicMock,
    bot: Bot,
    incoming_message_factory: Callable[..., IncomingMessage],
    incoming_attachment: AttachmentDocument,
    fsm_session: FSM,
    default_string: str,
    default_list: list[str],
) -> None:
    # - Arrange -
    message = incoming_message_factory(body="", file=incoming_attachment)
    support_request = SupportRequestInCreation(description=default_string)
    mocked_get_user_attachments_names.return_value = default_list
    await fsm_session.change_state(
        state=CreateSupportRequestStates.ADD_ATTACHMENT, support_request=support_request
    )

    # - Act -
    await bot.async_execute_bot_command(message)

    # - Assert -
    assert mocked_is_valid_attachment.call_count == 1
    assert mocked_add_user_attachment.call_count == 1
    assert mocked_get_user_attachments_names.call_count == 1
    assert await fsm_session.get_state() == CreateSupportRequestStates.ADD_ATTACHMENT
    assert message.state.fsm_storage.support_request.description == default_string
    assert message.state.fsm_storage.support_request.attachments_names == default_list
    bot.send.assert_awaited_once_with(  # type: ignore
        message=OutgoingMessage(
            bot_id=message.bot.id,
            chat_id=message.chat.id,
            body=(
                "**Прикрепленные файл(ы):**\n"
                "lorem ipsum\n"
                "dolor sit amet\n\n"
                "Отправленные Вами файлы для удобства не отображаются в чате. "
                "Если все необходимые файлы загружены, нажмите кнопку "
                "**Отправить обращение** под полем для ввода сообщений. "
                "Если необходимо добавить вложения — прикрепите их."
            ),
            bubbles=BubbleMarkup(
                [[Button(command="/send-to-confirm", label="Отправить обращение")]]
            ),
            keyboard=KeyboardMarkup([[Button(command="/cancel", label="ОТМЕНА")]]),
        ),
    )


@patch(
    "app.bot.commands.support_request.create.ServiceDeskRepo.delete_user_attachments",
    new_callable=AsyncMock,
)
async def test__add_attachment_handler__skip_command(
    mocked_delete_user_attachments: AsyncMock,
    bot: Bot,
    incoming_message_factory: Callable[..., IncomingMessage],
    fsm_session: FSM,
    default_string: str,
) -> None:
    # - Arrange -
    message = incoming_message_factory(body="/skip")
    support_request = SupportRequestInCreation(description=default_string)
    await fsm_session.change_state(
        state=CreateSupportRequestStates.ADD_ATTACHMENT, support_request=support_request
    )

    # - Act -
    await bot.async_execute_bot_command(message)

    # - Assert -
    assert mocked_delete_user_attachments.call_count == 1
    assert await fsm_session.get_state() == CreateSupportRequestStates.CONFIRM_REQUEST
    assert message.state.fsm_storage.support_request.description == default_string
    assert not message.state.fsm_storage.support_request.attachments_names
    bot.send.assert_awaited_once_with(  # type: ignore
        message=OutgoingMessage(
            bot_id=message.bot.id,
            chat_id=message.chat.id,
            body=(
                "**Проверьте правильность ввода:**\n"
                "**Описание проблемы:** lorem ipsum\n"
                "**Приложенные файлы:** -\n"
                "**Всё верно?**"
            ),
            bubbles=BubbleMarkup(
                [
                    [Button(command="/send-request", label="Да")],
                    [Button(command="/update-request", label="Нет")],
                ]
            ),
            keyboard=KeyboardMarkup([[Button(command="/cancel", label="ОТМЕНА")]]),
        ),
    )


@patch(
    "app.bot.commands.support_request.create.ServiceDeskRepo.get_user_attachments_names"
)
async def test__add_attachment_handler__confirm_request_command(
    mocked_get_user_attachments_names: MagicMock,
    bot: Bot,
    incoming_message_factory: Callable[..., IncomingMessage],
    fsm_session: FSM,
    default_string: str,
    default_list: list[str],
) -> None:
    # - Arrange -
    message = incoming_message_factory(body="/send-to-confirm")
    support_request = SupportRequestInCreation(
        description=default_string, attachments_names=default_list
    )
    mocked_get_user_attachments_names.return_value = default_list
    await fsm_session.change_state(
        state=CreateSupportRequestStates.ADD_ATTACHMENT, support_request=support_request
    )

    # - Act -
    await bot.async_execute_bot_command(message)

    # - Assert -
    assert await fsm_session.get_state() == CreateSupportRequestStates.CONFIRM_REQUEST
    assert message.state.fsm_storage.support_request.description == default_string
    assert message.state.fsm_storage.support_request.attachments_names == default_list
    bot.send.assert_awaited_once_with(  # type: ignore
        message=OutgoingMessage(
            bot_id=message.bot.id,
            chat_id=message.chat.id,
            body=(
                "**Проверьте правильность ввода:**\n"
                "**Описание проблемы:** lorem ipsum\n"
                "**Приложенные файлы:** dolor sit amet, lorem ipsum\n"
                "**Всё верно?**"
            ),
            bubbles=BubbleMarkup(
                [
                    [Button(command="/send-request", label="Да")],
                    [Button(command="/update-request", label="Нет")],
                ]
            ),
            keyboard=KeyboardMarkup([[Button(command="/cancel", label="ОТМЕНА")]]),
        ),
    )


async def test__add_confirm_request_handler__empty_message(
    bot: Bot,
    incoming_message_factory: Callable[..., IncomingMessage],
    fsm_session: FSM,
    default_string: str,
) -> None:
    # - Arrange -
    message = incoming_message_factory(body="")
    await fsm_session.change_state(
        state=CreateSupportRequestStates.CONFIRM_REQUEST,
        support_request=SupportRequestInCreation(
            description=default_string,
        ),
    )

    # - Act -
    await bot.async_execute_bot_command(message)

    # - Assert -
    assert await fsm_session.get_state() == CreateSupportRequestStates.CONFIRM_REQUEST
    assert message.state.fsm_storage.support_request.description == default_string
    bot.send.assert_awaited_once_with(  # type: ignore
        message=OutgoingMessage(
            bot_id=message.bot.id,
            chat_id=message.chat.id,
            body=(
                "На данном этапе вам необходидмо подтвердить корректность "
                "введенных данных.\nЕсли вы хотите оформить новое обращение, "
                'нажмите кнопку "Отмена"'
            ),
            keyboard=KeyboardMarkup([[Button(command="/cancel", label="ОТМЕНА")]]),
        ),
    )


async def test__add_confirm_request_handler__undefined_command(
    bot: Bot,
    incoming_message_factory: Callable[..., IncomingMessage],
    fsm_session: FSM,
    default_string: str,
) -> None:
    # - Arrange -
    message = incoming_message_factory(body=default_string)
    await fsm_session.change_state(
        state=CreateSupportRequestStates.CONFIRM_REQUEST,
        support_request=SupportRequestInCreation(
            description=default_string,
        ),
    )

    # - Act -
    await bot.async_execute_bot_command(message)

    # - Assert -
    assert await fsm_session.get_state() == CreateSupportRequestStates.CONFIRM_REQUEST
    assert message.state.fsm_storage.support_request.description == default_string
    bot.send.assert_awaited_once_with(  # type: ignore
        message=OutgoingMessage(
            bot_id=message.bot.id,
            chat_id=message.chat.id,
            body=(
                "На данном этапе вам необходидмо подтвердить корректность "
                "введенных данных.\nЕсли вы хотите оформить новое обращение, "
                'нажмите кнопку "Отмена"'
            ),
            keyboard=KeyboardMarkup([[Button(command="/cancel", label="ОТМЕНА")]]),
        ),
    )


@patch(
    "app.bot.commands.support_request.create.send_support_request",
    new_callable=AsyncMock,
)
async def test__add_confirm_request_handler__send_request_command(
    mocked_send_support_request: AsyncMock,
    bot: Bot,
    incoming_message_factory: Callable[..., IncomingMessage],
    fsm_session: FSM,
    default_string: str,
) -> None:
    # - Arrange -
    message = incoming_message_factory(body="/send-request")
    await fsm_session.change_state(
        state=CreateSupportRequestStates.CONFIRM_REQUEST,
        support_request=SupportRequestInCreation(
            subject=default_string,
            description=default_string,
        ),
    )

    # - Act -
    await bot.async_execute_bot_command(message)

    # - Assert -
    assert not await fsm_session.get_state()
    assert mocked_send_support_request.call_count == 1


async def test__add_confirm_request_handler__update_request_command(
    bot: Bot,
    incoming_message_factory: Callable[..., IncomingMessage],
    fsm_session: FSM,
    default_string: str,
) -> None:
    # - Arrange -
    message = incoming_message_factory(body="/update-request")
    await fsm_session.change_state(
        state=CreateSupportRequestStates.CONFIRM_REQUEST,
        support_request=SupportRequestInCreation(
            subject=default_string,
            description=default_string,
        ),
    )

    # - Act -
    await bot.async_execute_bot_command(message)

    # - Assert -
    assert await fsm_session.get_state() == UpdateSupportRequestStates.SELECT_ATTRIBUTE
    bot.send.assert_awaited_once_with(  # type: ignore
        message=OutgoingMessage(
            bot_id=message.bot.id,
            chat_id=message.chat.id,
            body="Какое поле в обращении Вы хотите изменить?",
            bubbles=BubbleMarkup(
                [
                    [Button(command="/update-description", label="Описание проблемы")],
                    [Button(command="/update-attachment", label="Файлы")],
                ]
            ),
            keyboard=KeyboardMarkup(
                [
                    [Button(command="/back", label="Назад")],
                    [Button(command="/cancel", label="ОТМЕНА")],
                ]
            ),
        ),
    )
