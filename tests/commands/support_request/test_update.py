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

from app.bot.states.support_request import UpdateSupportRequestStates
from app.schemas.support_request import (
    SupportRequestInCreation,
    SupportRequestInUpdating,
)


async def test__update_support_request_handler(
    bot: Bot,
    incoming_message_factory: Callable[..., IncomingMessage],
    fsm_session: FSM,
    default_string: str,
) -> None:
    # - Arrange -
    message = incoming_message_factory(
        body="/update-request",
        data={
            "support_request": {
                "subject": default_string,
                "description": default_string,
                "attachments_names": [],
            }
        },
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
            keyboard=KeyboardMarkup([[Button(command="/cancel", label="ОТМЕНА")]]),
        ),
    )


async def test__select_updating_attribute_handler__empty_message(
    bot: Bot,
    incoming_message_factory: Callable[..., IncomingMessage],
    fsm_session: FSM,
    default_string: str,
) -> None:
    # - Arrange -
    message = incoming_message_factory(body="")
    await fsm_session.change_state(
        state=UpdateSupportRequestStates.SELECT_ATTRIBUTE,
        support_request=SupportRequestInUpdating(
            subject=default_string,
            description=default_string,
        ),
    )
    # - Act -
    await bot.async_execute_bot_command(message)

    # - Assert -
    assert await fsm_session.get_state() == UpdateSupportRequestStates.SELECT_ATTRIBUTE
    assert message.state.fsm_storage.support_request.description == default_string
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
            keyboard=KeyboardMarkup([[Button(command="/cancel", label="ОТМЕНА")]]),
        ),
    )


async def test__select_updating_attribute_handler__update_description_command(
    bot: Bot,
    incoming_message_factory: Callable[..., IncomingMessage],
    fsm_session: FSM,
    default_string: str,
) -> None:
    # - Arrange -
    message = incoming_message_factory(body="/update-description")
    await fsm_session.change_state(
        state=UpdateSupportRequestStates.SELECT_ATTRIBUTE,
        support_request=SupportRequestInUpdating(
            subject=default_string,
            description=default_string,
        ),
    )
    # - Act -
    await bot.async_execute_bot_command(message)

    # - Assert -
    assert (
        await fsm_session.get_state()
        == UpdateSupportRequestStates.ENTER_NEW_DESCRIPTION  # noqa: W503
    )
    assert message.state.fsm_storage.support_request.description == default_string
    bot.send.assert_awaited_once_with(  # type: ignore
        message=OutgoingMessage(
            bot_id=message.bot.id,
            chat_id=message.chat.id,
            body=(
                "❗ Опишите подробно возникшую проблему, укажите какие действия "
                "Вы выполняете и какой результат получаете.\n\n"
                "⚡ От полноты описания будет зависеть скорость "
                "решения Вашего обращения.\n\n📱 Обращение должно быть отправлено "
                "с устройства, где возникла проблема."
            ),
            keyboard=KeyboardMarkup([[Button(command="/cancel", label="ОТМЕНА")]]),
        ),
    )


async def test__select_updating_attribute_handler__update_attachment_command(
    bot: Bot,
    incoming_message_factory: Callable[..., IncomingMessage],
    fsm_session: FSM,
    default_string: str,
) -> None:
    # - Arrange -
    message = incoming_message_factory(body="/update-attachment")
    await fsm_session.change_state(
        state=UpdateSupportRequestStates.SELECT_ATTRIBUTE,
        support_request=SupportRequestInUpdating(
            subject=default_string,
            description=default_string,
        ),
    )
    # - Act -
    await bot.async_execute_bot_command(message)

    # - Assert -
    assert (
        await fsm_session.get_state() == UpdateSupportRequestStates.ADD_NEW_ATTACHMENT
    )
    assert message.state.fsm_storage.support_request.description == default_string
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


async def test__select_updating_attribute_handler__text_instead_command(
    bot: Bot,
    incoming_message_factory: Callable[..., IncomingMessage],
    fsm_session: FSM,
    default_string: str,
) -> None:
    # - Arrange -
    message = incoming_message_factory(body=default_string)
    await fsm_session.change_state(
        state=UpdateSupportRequestStates.SELECT_ATTRIBUTE,
        support_request=SupportRequestInUpdating(
            subject=default_string,
            description=default_string,
        ),
    )
    # - Act -
    await bot.async_execute_bot_command(message)

    # - Assert -
    assert await fsm_session.get_state() == UpdateSupportRequestStates.SELECT_ATTRIBUTE
    assert message.state.fsm_storage.support_request.description == default_string
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
            keyboard=KeyboardMarkup([[Button(command="/cancel", label="ОТМЕНА")]]),
        ),
    )


async def test__enter_new_description_handler__empty_message(
    bot: Bot,
    incoming_message_factory: Callable[..., IncomingMessage],
    fsm_session: FSM,
    default_string: str,
) -> None:
    # - Arrange -
    message = incoming_message_factory(body="")
    await fsm_session.change_state(
        state=UpdateSupportRequestStates.ENTER_NEW_DESCRIPTION,
        support_request=SupportRequestInUpdating(
            subject=default_string,
            description=default_string,
        ),
    )
    # - Act -
    await bot.async_execute_bot_command(message)

    # - Assert -
    assert (
        await fsm_session.get_state()
        == UpdateSupportRequestStates.ENTER_NEW_DESCRIPTION  # noqa: W503
    )
    assert message.state.fsm_storage.support_request.description == default_string
    bot.send.assert_awaited_once_with(  # type: ignore
        message=OutgoingMessage(
            bot_id=message.bot.id,
            chat_id=message.chat.id,
            body=(
                "❗ Опишите подробно возникшую проблему, укажите какие действия "
                "Вы выполняете и какой результат получаете.\n\n"
                "⚡ От полноты описания будет зависеть скорость "
                "решения Вашего обращения.\n\n📱 Обращение должно быть отправлено "
                "с устройства, где возникла проблема."
            ),
            keyboard=KeyboardMarkup([[Button(command="/cancel", label="ОТМЕНА")]]),
        ),
    )


@patch("app.bot.commands.support_request.create.settings.MAX_DESCRIPTION_LENGTH", new=5)
async def test__enter_new_description_handler__max_description_length_exceeded(
    bot: Bot,
    incoming_message_factory: Callable[..., IncomingMessage],
    fsm_session: FSM,
    default_string: str,
) -> None:
    # - Arrange -
    message = incoming_message_factory(body=default_string)
    await fsm_session.change_state(
        state=UpdateSupportRequestStates.ENTER_NEW_DESCRIPTION,
        support_request=SupportRequestInUpdating(
            subject=default_string,
            description=default_string,
        ),
    )
    # - Act -
    await bot.async_execute_bot_command(message)

    # - Assert -
    assert (
        await fsm_session.get_state()
        == UpdateSupportRequestStates.ENTER_NEW_DESCRIPTION  # noqa: W503
    )
    assert message.state.fsm_storage.support_request.description == default_string
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


async def test__enter_new_description_handler(
    bot: Bot,
    incoming_message_factory: Callable[..., IncomingMessage],
    fsm_session: FSM,
    default_string: str,
) -> None:
    # - Arrange -
    message = incoming_message_factory(body=default_string)
    await fsm_session.change_state(
        state=UpdateSupportRequestStates.ENTER_NEW_DESCRIPTION,
        support_request=SupportRequestInUpdating(
            subject=default_string,
            description=default_string,
        ),
    )
    # - Act -
    await bot.async_execute_bot_command(message)

    # - Assert -
    assert await fsm_session.get_state() is None
    assert message.state.fsm_storage.support_request.description == default_string
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
                    [Button(command="/confirm-request", label="Да")],
                    [
                        Button(
                            command="/update-request",
                            label="Нет",
                            data={
                                "support_request": SupportRequestInCreation(
                                    subject=default_string,
                                    description=default_string,
                                    attachments_names=[],
                                )
                            },
                        )
                    ],
                ]
            ),
            keyboard=KeyboardMarkup([[Button(command="/cancel", label="ОТМЕНА")]]),
        )
    )


@patch(
    "app.bot.commands.support_request.update.ServiceDeskRepo.delete_user_attachments",
    new_callable=AsyncMock,
)
async def test__add_attachment_handler__text_instead_attachment(
    mocked_delete_user_attachments: AsyncMock,
    bot: Bot,
    incoming_message_factory: Callable[..., IncomingMessage],
    fsm_session: FSM,
    default_string: str,
) -> None:
    # - Arrange -
    message = incoming_message_factory(body="")
    support_request = SupportRequestInCreation(description=default_string)
    await fsm_session.change_state(
        state=UpdateSupportRequestStates.ADD_NEW_ATTACHMENT,
        support_request=support_request,
    )

    # - Act -
    await bot.async_execute_bot_command(message)

    # - Assert -
    assert mocked_delete_user_attachments.call_count == 1
    assert (
        await fsm_session.get_state() == UpdateSupportRequestStates.ADD_NEW_ATTACHMENT
    )
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
    "app.bot.commands.support_request.update.ServiceDeskRepo.delete_user_attachments",
    new_callable=AsyncMock,
)
@patch(
    "app.bot.commands.support_request.update.ServiceDeskRepo.is_valid_attachment",
    return_value=False,
)
async def test__add_attachment_handler__invalid_attachment(
    mocked_is_valid_attachment: MagicMock,
    mocked_delete_user_attachments: AsyncMock,
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
        state=UpdateSupportRequestStates.ADD_NEW_ATTACHMENT,
        support_request=support_request,
    )

    # - Act -
    await bot.async_execute_bot_command(message)

    # - Assert -
    assert mocked_delete_user_attachments.call_count == 1
    assert mocked_is_valid_attachment.call_count == 1
    assert (
        await fsm_session.get_state() == UpdateSupportRequestStates.ADD_NEW_ATTACHMENT
    )
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
                    [Button(command="/confirm-request", label="ОТПРАВИТЬ ОБРАЩЕНИЕ")],
                    [Button(command="/cancel", label="ОТМЕНА")],
                ]
            ),
        ),
    )


@patch(
    "app.bot.commands.support_request.update.ServiceDeskRepo.delete_user_attachments",
    new_callable=AsyncMock,
)
@patch(
    "app.bot.commands.support_request.update.ServiceDeskRepo.get_user_attachments_names"
)
@patch("app.bot.commands.support_request.update.ServiceDeskRepo.add_user_attachment")
@patch(
    "app.bot.commands.support_request.update.ServiceDeskRepo.is_valid_attachment",
    return_value=True,
)
async def test__add_attachment_handler__valid_attachment(  # noqa: WPS218
    mocked_is_valid_attachment: MagicMock,
    mocked_add_user_attachment: MagicMock,
    mocked_get_user_attachments_names: MagicMock,
    mocked_delete_user_attachments: AsyncMock,
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
        state=UpdateSupportRequestStates.ADD_NEW_ATTACHMENT,
        support_request=support_request,
    )

    # - Act -
    await bot.async_execute_bot_command(message)

    # - Assert -
    assert mocked_delete_user_attachments.call_count == 1
    assert mocked_is_valid_attachment.call_count == 1
    assert mocked_add_user_attachment.call_count == 1
    assert mocked_get_user_attachments_names.call_count == 1
    assert (
        await fsm_session.get_state() == UpdateSupportRequestStates.ADD_NEW_ATTACHMENT
    )
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
                [[Button(command="/confirm-request", label="Отправить обращение")]]
            ),
            keyboard=KeyboardMarkup([[Button(command="/cancel", label="ОТМЕНА")]]),
        ),
    )


@patch(
    "app.bot.commands.support_request.update.ServiceDeskRepo.delete_user_attachments",
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
        state=UpdateSupportRequestStates.ADD_NEW_ATTACHMENT,
        support_request=support_request,
    )

    # - Act -
    await bot.async_execute_bot_command(message)

    # - Assert -
    assert mocked_delete_user_attachments.call_count == 2
    assert await fsm_session.get_state() is None
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
                    [Button(command="/confirm-request", label="Да")],
                    [
                        Button(
                            command="/update-request",
                            label="Нет",
                            data={
                                "support_request": SupportRequestInCreation(
                                    subject=None,
                                    description=default_string,
                                    attachments_names=[],
                                )
                            },
                        )
                    ],
                ]
            ),
            keyboard=KeyboardMarkup([[Button(command="/cancel", label="ОТМЕНА")]]),
        ),
    )


@patch(
    "app.bot.commands.support_request.update.ServiceDeskRepo.delete_user_attachments",
    new_callable=AsyncMock,
)
@patch(
    "app.bot.commands.support_request.update.ServiceDeskRepo.get_user_attachments_names"
)
async def test__add_attachment_handler__confirm_request_command(
    mocked_get_user_attachments_names: MagicMock,
    mocked_delete_user_attachments: AsyncMock,
    bot: Bot,
    incoming_message_factory: Callable[..., IncomingMessage],
    fsm_session: FSM,
    default_string: str,
    default_list: list[str],
) -> None:
    # - Arrange -
    message = incoming_message_factory(body="/confirm-request")
    support_request = SupportRequestInCreation(
        description=default_string, attachments_names=default_list
    )
    mocked_get_user_attachments_names.return_value = default_list
    await fsm_session.change_state(
        state=UpdateSupportRequestStates.ADD_NEW_ATTACHMENT,
        support_request=support_request,
    )

    # - Act -
    await bot.async_execute_bot_command(message)

    # - Assert -
    assert mocked_get_user_attachments_names.call_count == 1
    assert mocked_delete_user_attachments.call_count == 1
    assert await fsm_session.get_state() is None
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
                    [Button(command="/confirm-request", label="Да")],
                    [
                        Button(
                            command="/update-request",
                            label="Нет",
                            data={
                                "support_request": SupportRequestInCreation(
                                    subject=None,
                                    description=default_string,
                                    attachments_names=default_list,
                                )
                            },
                        )
                    ],
                ]
            ),
            keyboard=KeyboardMarkup([[Button(command="/cancel", label="ОТМЕНА")]]),
        ),
    )
