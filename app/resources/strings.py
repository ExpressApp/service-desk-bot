"""Text and templates for messages and api responses."""
from typing import Any, Protocol, cast

from mako.lookup import TemplateLookup

from app.services.service_desk import pretty_file_size
from app.settings import settings


class FormatTemplate(Protocol):
    """
    Protocol for correct templates typing.

    Allow use format() instead of render() method that needed to maintain consistency
    with regular string formatting.
    """

    def format(self, **kwargs: Any) -> str:  # noqa: WPS125 A003
        """Render template."""


class TemplateFormatterLookup(TemplateLookup):
    """Represent a collection of templates from the local filesystem."""

    def get_template(self, uri: str) -> FormatTemplate:
        """Cast default mako template to FormatTemplate."""

        def _format(**kwargs: Any) -> str:  # noqa: WPS430
            return template.render(**kwargs).rstrip()

        template = super().get_template(uri)
        template.format = _format  # noqa: WPS125
        return cast(FormatTemplate, template)


lookup = TemplateFormatterLookup(
    directories=["app/resources/templates"],
    input_encoding="utf-8",
    strict_undefined=True,
)

# bot info:
BOT_PROJECT_NAME = "service-desk-bot"
BOT_DISPLAY_NAME = "Service Desk Bot"

# templates:
DEFAULT_TEMPLATE = lookup.get_template("default.txt.mako")
CHAT_CREATED_TEMPLATE = lookup.get_template("chat_created.txt.mako")
HELP_COMMAND_MESSAGE_TEMPLATE = lookup.get_template("help.txt.mako")
SUBJECT_TEMPLATE = lookup.get_template("subject.txt.mako")
MAX_DESCRIPTION_LENGTH_EXCEEDED_TEMPLATE = lookup.get_template(
    "max_description_length_exceeded.txt.mako"
)
CONFIRM_REQUEST_TEMPLATE = lookup.get_template("confirm_request.txt.mako")
EXISTING_ATTACHMENTS_TEMPLATE = lookup.get_template("existing_attachments.txt.mako")
MAIL_BODY_TEMPLATE = lookup.get_template("mail_body.txt.mako")

# commands:
CREATE_SUPPORT_REQUEST_COMMAND = "/обращение"
HELP_COMMAND = "/справка"
CANCEL_COMMAND = "/cancel"
CONFIRM_CANCEL_COMMAND = "/confirm-cancel"
REFUSE_CANCEL_COMMAND = "/refuse-cancel"
SEND_REQUEST_COMMAND = "/send-request"
SEND_TO_CONFIRM_COMMAND = "/send-to-confirm"
UPDATE_REQUEST_COMMAND = "/update-request"
CONFIRM_ATTACHMENT_ADDITION_COMMAND = "/confirm-attachment-addition"
REFUSE_ATTACHMENT_ADDITION_COMMAND = "/refuse-attachment-addition"
SKIP_COMMAND = "/skip"
UPDATE_DESCRIPTION_COMMAND = "/update-description"
UPDATE_ATTACHMENT_COMMAND = "/update-attachment"
BACK_COMMAND = "/back"

# labels:
CREATE_SUPPORT_REQUEST_COMMAND_LABEL = "Оформить новое обращение"
CANCEL_COMMAND_LABEL = "ОТМЕНА"
YES_LABEL = "Да"
NO_LABEL = "Нет"
SEND_SUPPORT_REQUEST_COMMAND_LABEL = "Отправить обращение"
SKIP_COMMAND_LABEL = "Пропустить"
UPDATE_DESCRIPTION_COMMAND_LABEL = "Описание проблемы"
UPDATE_ATTACHMENT_COMMAND_LABEL = "Файлы"
BACK_COMMAND_LABEL = "Назад"

# descriptions:
CREATE_SUPPORT_REQUEST_COMMAND_DESCRIPTION = "оформить обращение в поддержку"
HELP_COMMAND_DESCRIPTION = "справка по командам"

# prettify limits:
PRETTY_MAX_ATTACHMENT_SIZE = pretty_file_size(
    settings.MAX_ATTACHMENT_SIZE.human_readable()
)
PRETTY_MAX_ATTACHMENTS_SIZE = pretty_file_size(
    settings.MAX_ATTACHMENTS_SIZE.human_readable()
)

# messages:
ENTER_DESCRIPTION_MESSAGE = "".join(
    "❗ Опишите подробно возникшую проблему, укажите какие действия Вы выполняете "
    "и какой результат получаете. Прикрепите фото или медиафайл.\n\n"
    "⚡ От полноты описания будет зависеть скорость решения Вашего обращения.\n\n"
    "📱 Обращение должно быть отправлено с устройства, где возникла проблема."
)
SOMETHING_GOES_WRONG_MESSAGE = (
    "При обработке сообщения или нажатия на кнопку произошла непредвиденная ошибка. "
    "Пожалуйста, сообщите об этом администратору."
)
CONFIRM_CANCEL_MESSAGE = "".join(
    (
        "**Вы уверены, что хотите отменить оформление обращения?**\n",
        "Введенные данные не будут сохранены.",
    )
)
CANCEL_MESSAGE = "Действие отменено.\nЖелаете отправить новое обращение в адрес технической поддержки?"
INVALID_ATTACHMENT_MESSAGE = (
    "Вы пытаетесь загрузить файл(ы) размер или количество которых превышает допустимое.\n"
    "Пожалуйста, уменьшите размер файла(ов) и загрузите снова.\n"
    "Также Вы можете нажать кнопку **«Отмена»** для отмены оформления обращения "
    "или **«Отправить обращение»** для регистрации запроса без файлов."
)
CONFIRM_ATTACHMENT_ADDITION_MESSAGE = (
    "Хотели бы Вы прикрепить фото или медиафайл? "
    "Скриншот возникшей проблемы поможет ускорить обработку Вашего обращения."
)
ADD_ATTACHMENT_MESSAGE = "".join(
    (
        "**Отправьте фото или медиафайл (опционально).**",
        f"\n\nВы можете загрузить до {settings.MAX_ATTACHMENTS_COUNT} файлов, размером не",
        f" более {PRETTY_MAX_ATTACHMENT_SIZE} каждый и не более {PRETTY_MAX_ATTACHMENTS_SIZE}",
        " суммарно.",
        "\n\nПосле того, как все необходимые файлы будут загружены, нажмите кнопку",
        ' "**Отправить обращение**" под полем для ввода сообщений.',
    )
)
TEXT_INSTEAD_ATTACHMENT_MESSAGE = "".join(
    (
        "На данном этапе вы можете либо добавить файлы, либо пропустить данный шаг.\n",
        "Если вы хотите изменить тему или описание обращения, нажмите кнопку",
        ' "Отмена" и оформите обращение заново.',
    )
)
SELECT_UPDATING_ATTRIBUTE_MESSAGE = "Какое поле в обращении Вы хотите изменить?"
ENTER_NEW_DESCRIPTION_MESSAGE = "".join(
    "❗ Опишите подробно возникшую проблему, укажите какие действия Вы выполняете "
    "и какой результат получаете.\n\n"
    "⚡ От полноты описания будет зависеть скорость решения Вашего обращения.\n\n"
    "📱 Обращение должно быть отправлено с устройства, где возникла проблема."
)

SUCCESS_SEND_MESSAGE = "".join(
    (
        "Ваше обращение отправлено.\n"
        "В случае необходимости получения дополнительной информации, "
        "с Вами свяжется специалист службы технической поддержки.\n"
        "Уведомление о решении обращения будет направлено Вам на электронную почту "
        f"или персональным сообщением в {settings.APP_NAME}."
    )
)
NOT_CONFIRM_COMMAND_MESSAGE = "".join(
    (
        "На данном этапе вам необходидмо подтвердить корректность введенных данных.\n",
        'Если вы хотите оформить новое обращение, нажмите кнопку "Отмена"',
    )
)
