from typing import Callable
from uuid import UUID

from pybotx import (
    Bot,
    BotAccount,
    BubbleMarkup,
    Button,
    Chat,
    ChatCreatedEvent,
    ChatCreatedMember,
    ChatTypes,
    IncomingMessage,
    OutgoingMessage,
    UserKinds,
)


async def test__default_message_handler(
    bot: Bot,
    incoming_message_factory: Callable[..., IncomingMessage],
) -> None:
    # - Arrange -
    message = incoming_message_factory()

    # - Act -
    await bot.async_execute_bot_command(message)

    # - Assert -
    bot.send.assert_awaited_once_with(  # type: ignore
        message=OutgoingMessage(
            bot_id=message.bot.id,
            chat_id=message.chat.id,
            body=(
                "Если у Вас возникли сложности в работе приложения eXpress, "
                "с моей помощью Вы сможете быстро отправить обращение "
                "на почту технической поддержки."
            ),
            bubbles=BubbleMarkup(
                [[Button(command="/обращение", label="Оформить новое обращение")]]
            ),
        )
    )


async def test__chat_created_handler(
    bot: Bot,
    bot_id: UUID,
    host: str,
) -> None:
    # - Arrange -
    command = ChatCreatedEvent(
        sync_id=UUID("2c1a31d6-f47f-5f54-aee2-d0c526bb1d54"),
        bot=BotAccount(
            id=bot_id,
            host=host,
        ),
        chat_name="Feature-party",
        chat=Chat(
            id=UUID("dea55ee4-7a9f-5da0-8c73-079f400ee517"),
            type=ChatTypes.GROUP_CHAT,
        ),
        creator_id=UUID("83fbf1c7-f14b-5176-bd32-ca15cf00d4b7"),
        members=[
            ChatCreatedMember(
                is_admin=True,
                huid=bot_id,
                username="Feature bot",
                kind=UserKinds.BOT,
            ),
            ChatCreatedMember(
                is_admin=False,
                huid=UUID("83fbf1c7-f14b-5176-bd32-ca15cf00d4b7"),
                username="Ivanov Ivan Ivanovich",
                kind=UserKinds.CTS_USER,
            ),
        ],
        raw_command=None,
    )

    # - Act -
    await bot.async_execute_bot_command(command)

    # - Assert -
    bot.answer_message.assert_awaited_once_with(  # type: ignore
        (
            "Вас приветствует Помощник технической поддержки приложения eXpress!\n\n"
            "С моей помощью Вы можете отправить обращение "
            "в адрес технической поддержки.\n"
            "Для начала работы нажмите на кнопку ниже."
        ),
        bubbles=BubbleMarkup(
            [[Button(command="/обращение", label="Оформить новое обращение")]]
        ),
    )


async def test__help_handler(
    bot: Bot,
    incoming_message_factory: Callable[..., IncomingMessage],
) -> None:
    # - Arrange -
    message = incoming_message_factory(body="/справка")

    # - Act -
    await bot.async_execute_bot_command(message)

    # - Assert -
    bot.send.assert_awaited_once_with(  # type: ignore
        message=OutgoingMessage(
            bot_id=message.bot.id,
            chat_id=message.chat.id,
            body=(
                "Если у Вас возникли сложности в работе приложения eXpress, "
                "с моей помощью Вы можете быстро отправить обращение на "
                "почту технической поддержки\n\n"
                "**Справка по командам:**\n\n"
                "**/обращение - оформить обращение в поддержку**\n\n"
                "**/справка - справка по командам**"
            ),
            bubbles=BubbleMarkup(
                [[Button(command="/обращение", label="Оформить новое обращение")]]
            ),
        )
    )


async def test__git_commit_sha_handler(
    bot: Bot,
    incoming_message_factory: Callable[..., IncomingMessage],
) -> None:
    # - Arrange -
    message = incoming_message_factory(body="/_debug:git-commit-sha")

    # - Act -
    await bot.async_execute_bot_command(message)

    # - Assert -
    bot.answer_message.assert_awaited_once_with("<undefined>")  # type: ignore
