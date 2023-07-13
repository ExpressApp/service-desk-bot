from typing import Callable
from unittest.mock import AsyncMock, patch

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
                    [Button(command="/confirm-cancel", label="Да")],
                    [Button(command="/refuse-cancel", label="Нет")],
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
                    [Button(command="/confirm-attachment-addition", label="Да")],
                    [Button(command="/refuse-attachment-addition", label="Нет")],
                ]
            ),
            keyboard=KeyboardMarkup([[Button(command="/cancel", label="ОТМЕНА")]]),
        ),
    )
