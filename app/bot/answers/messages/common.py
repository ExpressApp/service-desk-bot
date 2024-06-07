"""Provide common service bot messages."""

from pybotx import IncomingMessage, OutgoingMessage

from app.bot.answers.bubbles.common import get_default_bubbles


def build_default_message(message: IncomingMessage, body: str) -> OutgoingMessage:
    return OutgoingMessage(
        bot_id=message.bot.id,
        chat_id=message.chat.id,
        body=body,
        bubbles=get_default_bubbles(),
    )
