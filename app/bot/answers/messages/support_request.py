"""Provide service bot messages for support request."""

from pybotx import IncomingMessage, OutgoingMessage

from app.bot.answers.bubbles.common import get_default_bubbles
from app.bot.answers.bubbles.support_request import (
    get_confirm_attachment_addition_bubbles,
    get_confirm_cancel_bubbles,
    get_confirm_request_bubbles,
    get_select_attribute_bubbles,
    get_send_request_bubbles,
    get_skip_bubbles,
)
from app.bot.answers.keyboards.common import get_cancel_keyboard
from app.bot.answers.keyboards.support_request import (
    get_back_to_confirm_keyboard,
    get_invalid_attachment_keyboard,
)
from app.resources import strings
from app.schemas.support_request import (
    SupportRequestInCreation,
    SupportRequestInUpdating,
)
from app.settings import settings


def build_enter_description_message(message: IncomingMessage) -> OutgoingMessage:
    return OutgoingMessage(
        bot_id=message.bot.id,
        chat_id=message.chat.id,
        body=strings.ENTER_DESCRIPTION_MESSAGE,
        keyboard=get_cancel_keyboard(),
    )


def build_description_max_length_exceeded_message(
    message: IncomingMessage,
) -> OutgoingMessage:
    answer_body = strings.MAX_DESCRIPTION_LENGTH_EXCEEDED_TEMPLATE.format(
        max_description_length=settings.MAX_DESCRIPTION_LENGTH
    )

    return OutgoingMessage(
        bot_id=message.bot.id,
        chat_id=message.chat.id,
        body=answer_body,
        keyboard=get_cancel_keyboard(),
    )


def build_invalid_attachment_message(message: IncomingMessage) -> OutgoingMessage:
    return OutgoingMessage(
        bot_id=message.bot.id,
        chat_id=message.chat.id,
        body=strings.INVALID_ATTACHMENT_MESSAGE,
        keyboard=get_invalid_attachment_keyboard(),
    )


def build_confirm_request_message(
    message: IncomingMessage,
    request: SupportRequestInCreation | SupportRequestInUpdating,
) -> OutgoingMessage:
    return OutgoingMessage(
        bot_id=message.bot.id,
        chat_id=message.chat.id,
        body=strings.CONFIRM_REQUEST_TEMPLATE.format(request=request),
        bubbles=get_confirm_request_bubbles(),
        keyboard=get_cancel_keyboard(),
    )


def build_confirm_attachment_addition_message(
    message: IncomingMessage,
) -> OutgoingMessage:
    return OutgoingMessage(
        bot_id=message.bot.id,
        chat_id=message.chat.id,
        body=strings.CONFIRM_ATTACHMENT_ADDITION_MESSAGE,
        bubbles=get_confirm_attachment_addition_bubbles(),
        keyboard=get_cancel_keyboard(),
    )


def build_confirm_cancel_message(message: IncomingMessage) -> OutgoingMessage:
    return OutgoingMessage(
        bot_id=message.bot.id,
        chat_id=message.chat.id,
        body=strings.CONFIRM_CANCEL_MESSAGE,
        bubbles=get_confirm_cancel_bubbles(),
    )


def build_cancel_message(message: IncomingMessage) -> OutgoingMessage:
    return OutgoingMessage(
        bot_id=message.bot.id,
        chat_id=message.chat.id,
        body=strings.CANCEL_MESSAGE,
        bubbles=get_default_bubbles(),
    )


def build_add_attachment_message(message: IncomingMessage) -> OutgoingMessage:
    return OutgoingMessage(
        bot_id=message.bot.id,
        chat_id=message.chat.id,
        body=strings.ADD_ATTACHMENT_MESSAGE,
        bubbles=get_skip_bubbles(),
        keyboard=get_cancel_keyboard(),
    )


def build_existing_attachments_message(
    message: IncomingMessage, attachments_names: list[str]
) -> OutgoingMessage:
    answer_body = strings.EXISTING_ATTACHMENTS_TEMPLATE.format(
        attachments_names=attachments_names
    )

    return OutgoingMessage(
        bot_id=message.bot.id,
        chat_id=message.chat.id,
        body=answer_body,
        bubbles=get_send_request_bubbles(),
        keyboard=get_cancel_keyboard(),
    )


def build_text_instead_attachment_message(message: IncomingMessage) -> OutgoingMessage:
    return OutgoingMessage(
        bot_id=message.bot.id,
        chat_id=message.chat.id,
        body=strings.TEXT_INSTEAD_ATTACHMENT_MESSAGE,
        bubbles=get_skip_bubbles(),
        keyboard=get_cancel_keyboard(),
    )


def build_select_updating_attribute_message(
    message: IncomingMessage,
) -> OutgoingMessage:
    return OutgoingMessage(
        bot_id=message.bot.id,
        chat_id=message.chat.id,
        body=strings.SELECT_UPDATING_ATTRIBUTE_MESSAGE,
        bubbles=get_select_attribute_bubbles(),
        keyboard=get_back_to_confirm_keyboard(),
    )


def build_enter_new_description_message(message: IncomingMessage) -> OutgoingMessage:
    return OutgoingMessage(
        bot_id=message.bot.id,
        chat_id=message.chat.id,
        body=strings.ENTER_NEW_DESCRIPTION_MESSAGE,
        keyboard=get_cancel_keyboard(),
    )


def build_success_send_message(message: IncomingMessage) -> OutgoingMessage:
    return OutgoingMessage(
        bot_id=message.bot.id,
        chat_id=message.chat.id,
        body=strings.SUCCESS_SEND_MESSAGE,
        bubbles=get_default_bubbles(),
    )


def build_not_confirm_command_message(message: IncomingMessage) -> OutgoingMessage:
    return OutgoingMessage(
        bot_id=message.bot.id,
        chat_id=message.chat.id,
        body=strings.NOT_CONFIRM_COMMAND_MESSAGE,
        keyboard=get_cancel_keyboard(),
    )
