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
from pybotx_fsm import FSM

from app.bot.states.support_request import CreateSupportRequestStates
from app.schemas.support_request import SupportRequestInCreation


async def test__confirm_cancel_middleware__cancel_command(
    bot: Bot,
    incoming_message_factory: Callable[..., IncomingMessage],
    fsm_session: FSM,
) -> None:
    # - Arrange -
    message = incoming_message_factory(body="/cancel")
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
                "**Вы уверены, что хотите отменить оформление обращения?**\n"
                "Введенные данные не будут сохранены."
            ),
            bubbles=BubbleMarkup(
                [
                    [
                        Button(command="/confirm-cancel", label="Да"),
                        Button(command="/refuse-cancel", label="Нет"),
                    ],
                ]
            ),
        ),
    )


@patch(
    "app.bot.middlewares.confirm_cancel.ServiceDeskRepo.delete_user_attachments",
    new_callable=AsyncMock,
)
async def test__confirm_cancel_middleware__confirm_cancel_command(
    mocked_delete_user_attachments: AsyncMock,
    bot: Bot,
    incoming_message_factory: Callable[..., IncomingMessage],
    fsm_session: FSM,
) -> None:
    # - Arrange -
    message = incoming_message_factory(body="/confirm-cancel")
    await fsm_session.change_state(state=CreateSupportRequestStates.ENTER_DESCRIPTION)

    # - Act -
    await bot.async_execute_bot_command(message)

    # - Assert -
    assert mocked_delete_user_attachments.call_count == 1
    assert await fsm_session.get_state() is None
    bot.send.assert_awaited_once_with(  # type: ignore
        message=OutgoingMessage(
            bot_id=message.bot.id,
            chat_id=message.chat.id,
            body=(
                "Действие отменено.\n"
                "Желаете отправить новое обращение в адрес технической поддержки?"
            ),
            bubbles=BubbleMarkup(
                [[Button(command="/обращение", label="Оформить новое обращение")]]
            ),
        ),
    )


async def test__confirm_cancel_middleware__other_command(
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
    bot.send.assert_awaited_once_with(  # type: ignore
        message=OutgoingMessage(
            bot_id=message.bot.id,
            chat_id=message.chat.id,
            body=(
                "Хотели бы Вы прикрепить фото или медиафайл? "
                "Скриншот возникшей проблемы поможет ускорить "
                "обработку Вашего обращения."
            ),
            bubbles=BubbleMarkup(
                [
                    [
                        Button(command="/confirm-attachment-addition", label="Да"),
                        Button(command="/refuse-attachment-addition", label="Нет"),
                    ],
                ]
            ),
            keyboard=KeyboardMarkup([[Button(command="/cancel", label="ОТМЕНА")]]),
        ),
    )


async def test__confirm_cancel_middleware__refuse_cancel_command__confirm_request_state(
    bot: Bot,
    incoming_message_factory: Callable[..., IncomingMessage],
    fsm_session: FSM,
    default_string: str,
) -> None:
    # - Arrange -
    message = incoming_message_factory(body="/refuse-cancel")
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
                "**Проверьте правильность ввода:**\n"
                "**Описание проблемы:** lorem ipsum\n"
                "**Приложенные файлы:** -\n"
                "**Всё верно?**"
            ),
            bubbles=BubbleMarkup(
                [
                    [
                        Button(command="/send-request", label="Да"),
                        Button(command="/update-request", label="Нет"),
                    ],
                ]
            ),
            keyboard=KeyboardMarkup([[Button(command="/cancel", label="ОТМЕНА")]]),
            silent_response=True,
        ),
    )


@patch("app.bot.middlewares.confirm_cancel.ServiceDeskRepo.get_user_attachments_names")
async def test__confirm_cancel_middleware__refuse_command__add_first_attachment_state(
    mocked_get_user_attachments_names: MagicMock,
    bot: Bot,
    incoming_message_factory: Callable[..., IncomingMessage],
    fsm_session: FSM,
    default_string: str,
    default_list: list[str],
) -> None:
    # - Arrange -
    message = incoming_message_factory(body="/refuse-cancel")
    await fsm_session.change_state(
        state=CreateSupportRequestStates.ADD_ATTACHMENT,
        support_request=SupportRequestInCreation(
            description=default_string,
            attachments_names=default_list,
        ),
    )
    mocked_get_user_attachments_names.return_value = []

    # - Act -
    await bot.async_execute_bot_command(message)

    # - Assert -
    assert mocked_get_user_attachments_names.call_count == 1
    assert await fsm_session.get_state() == CreateSupportRequestStates.ADD_ATTACHMENT
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
                'загружены, нажмите кнопку "**Отправить обращение**".'
            ),
            bubbles=BubbleMarkup([[Button(command="/skip", label="Пропустить")]]),
            keyboard=KeyboardMarkup([[Button(command="/cancel", label="ОТМЕНА")]]),
            silent_response=True,
        ),
    )


@patch("app.bot.middlewares.confirm_cancel.ServiceDeskRepo.get_user_attachments_names")
async def test__confirm_cancel_middleware__refuse_command__add_attachment_state(
    mocked_get_user_attachments_names: MagicMock,
    bot: Bot,
    incoming_message_factory: Callable[..., IncomingMessage],
    fsm_session: FSM,
    default_string: str,
    default_list: list[str],
) -> None:
    # - Arrange -
    message = incoming_message_factory(body="/refuse-cancel")
    await fsm_session.change_state(
        state=CreateSupportRequestStates.ADD_ATTACHMENT,
        support_request=SupportRequestInCreation(
            description=default_string,
            attachments_names=default_list,
        ),
    )
    mocked_get_user_attachments_names.return_value = default_list

    # - Act -
    await bot.async_execute_bot_command(message)

    # - Assert -
    assert mocked_get_user_attachments_names.call_count == 1
    assert await fsm_session.get_state() == CreateSupportRequestStates.ADD_ATTACHMENT
    assert message.state.fsm_storage.support_request.description == default_string
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
                "**Отправить обращение**. "
                "Если необходимо добавить вложения — прикрепите их."
            ),
            bubbles=BubbleMarkup(
                [[Button(command="/send-to-confirm", label="Отправить обращение")]]
            ),
            keyboard=KeyboardMarkup([[Button(command="/cancel", label="ОТМЕНА")]]),
            silent_response=True,
        ),
    )


async def test__confirm_cancel_middleware__refuse_command__other_state(
    bot: Bot,
    incoming_message_factory: Callable[..., IncomingMessage],
    fsm_session: FSM,
    default_string: str,
) -> None:
    # - Arrange -
    message = incoming_message_factory(body="/refuse-cancel")
    await fsm_session.change_state(
        state=CreateSupportRequestStates.WAIT_DECISION_ON_ATTACHMENT,
        support_request=SupportRequestInCreation(
            description=default_string,
        ),
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
                "Скриншот возникшей проблемы поможет ускорить "
                "обработку Вашего обращения."
            ),
            bubbles=BubbleMarkup(
                [
                    [
                        Button(command="/confirm-attachment-addition", label="Да"),
                        Button(command="/refuse-attachment-addition", label="Нет"),
                    ]
                ]
            ),
            keyboard=KeyboardMarkup([[Button(command="/cancel", label="ОТМЕНА")]]),
        ),
    )
