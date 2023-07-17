"""Handler for send support request command."""

from pybotx import Bot, HandlerCollector, IncomingMessage
from pybotx.models.enums import ClientPlatforms
from pybotx_fsm import FSMCollector

from app.bot.answers.messages.support_request import build_success_send_message
from app.bot.commands.listing import HiddenCommands
from app.bot.states.support_request import CreateSupportRequestStates
from app.db.repositories.exchange import ExchangeRepo, get_ews_account
from app.db.repositories.service_desk import ServiceDeskRepo
from app.resources import strings
from app.schemas.support_request import SupportRequestToSend
from app.services.botx_user_search import search_user_on_each_cts
from app.services.exchange import convert_to_ews_html
from app.settings import settings

collector = HandlerCollector()
fsm = FSMCollector(CreateSupportRequestStates)


@collector.command(
    HiddenCommands.SEND_REQUEST_COMMAND.command,
    visible=False,
)
async def send_support_request_handler(  # noqa: WPS210
    message: IncomingMessage, bot: Bot
) -> None:
    """Send support request by email."""

    user, cts = await search_user_on_each_cts(
        bot, huid=message.sender.huid  # type: ignore
    )

    user_platform = (
        str(message.sender.device.platform).split(".")[1]
        if message.sender.device.platform
        else "-"
    )

    incoming_request = message.data.get("support_request", {})
    support_request = SupportRequestToSend(**incoming_request)
    support_request.description = support_request.description.replace("\n", "<br>")

    service_desk_repo = ServiceDeskRepo(
        sender_huid=message.sender.huid, attachment=message.file  # type: ignore
    )

    user_attachments = await service_desk_repo.get_user_attachments()

    body = strings.MAIL_BODY_TEMPLATE.format(
        request=support_request,
        message=message,
        user=user,
        client_platform_enum=ClientPlatforms,
        platform=user_platform,
        app_name=settings.APP_NAME,
        host=cts.host,
    )

    ews_account = get_ews_account(
        credential_username=settings.MAIL_USERNAME,
        credential_password=settings.MAIL_PASSWORD,
        sender_email=settings.SENDER_EMAIL,
        server=settings.MAIL_SERVER,
    )
    exchange_repo = ExchangeRepo(account=ews_account)
    await exchange_repo.send_mail(
        subject=support_request.subject,
        body=convert_to_ews_html(body),
        user_attachments=user_attachments,
    )

    await service_desk_repo.delete_user_attachments()

    await bot.send(message=build_success_send_message(message))
