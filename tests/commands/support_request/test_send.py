from typing import Callable
from unittest.mock import AsyncMock, Mock, patch

from pybotx import Bot, BubbleMarkup, Button, IncomingMessage, OutgoingMessage
from pybotx_fsm import FSM

from app.bot.states.support_request import CreateSupportRequestStates
from app.schemas.support_request import SupportRequestToSend


@patch(
    "app.bot.commands.support_request.send.ServiceDeskRepo.delete_user_attachments",
    new_callable=AsyncMock,
)
@patch(
    "app.bot.commands.support_request.send.get_ews_account",
    new_callable=AsyncMock,
)
@patch(
    "app.bot.commands.support_request.send.ExchangeRepo.send_mail",
    new_callable=AsyncMock,
)
@patch(
    "app.bot.commands.support_request.send.ServiceDeskRepo.get_user_attachments",
    new_callable=AsyncMock,
)
@patch(
    "app.bot.commands.support_request.send.search_user_on_each_cts",
    new_callable=AsyncMock,
)
async def test__send_support_request(
    mocked_search_user_on_each_cts: AsyncMock,
    mocked_get_user_attachments: AsyncMock,
    mocked_send_mail: AsyncMock,
    mocked_get_ews_account: AsyncMock,
    mocked_delete_user_attachments: AsyncMock,
    bot: Bot,
    fsm_session: FSM,
    incoming_message_factory: Callable[..., IncomingMessage],
    default_string: str,
) -> None:
    # - Arrange -
    await fsm_session.change_state(
        state=CreateSupportRequestStates.CONFIRM_REQUEST,
        support_request=SupportRequestToSend(
            subject=default_string,
            description=default_string,
        ),
    )
    message = incoming_message_factory(body="/send-request")

    mocked_user = Mock()
    mocked_user.emails = []
    mocked_cts = Mock()
    mocked_search_user_on_each_cts.return_value = (mocked_user, mocked_cts)

    # - Act -
    await bot.async_execute_bot_command(message)

    # - Assert -
    assert mocked_search_user_on_each_cts.call_count == 1
    assert mocked_get_user_attachments.call_count == 1
    assert mocked_send_mail.call_count == 1
    assert mocked_get_ews_account.call_count == 1
    assert mocked_delete_user_attachments.call_count == 1
    bot.send.assert_awaited_once_with(  # type: ignore
        message=OutgoingMessage(
            bot_id=message.bot.id,
            chat_id=message.chat.id,
            body=(
                "Ваше обращение отправлено.\n"
                "В случае необходимости получения дополнительной информации, "
                "с Вами свяжется специалист службы технической поддержки.\n"
                "Уведомление о решении обращения будет направлено "
                "Вам на электронную почту или персональным сообщением в eXpress."
            ),
            bubbles=BubbleMarkup(
                [[Button(command="/обращение", label="Оформить новое обращение")]]
            ),
        ),
    )
