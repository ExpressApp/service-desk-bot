"""Configuration for bot instance."""

from httpx import AsyncClient, Limits
from pybotx import Bot, CallbackRepoProto
from pybotx_fsm import FSMMiddleware

from app.bot.commands import common
from app.bot.commands.support_request import (
    create as create_support_request,
    update as update_support_request,
)
from app.bot.error_handlers.internal_error import internal_error_handler
from app.bot.middlewares.answer_error import answer_error_middleware
from app.bot.middlewares.smart_logger import smart_logger_middleware
from app.settings import settings

BOTX_CALLBACK_TIMEOUT = 30


def get_bot(callback_repo: CallbackRepoProto, raise_exceptions: bool) -> Bot:
    exception_handlers = {}
    if not raise_exceptions:
        exception_handlers[Exception] = internal_error_handler

    return Bot(
        collectors=[
            common.collector,
            create_support_request.collector,
            update_support_request.collector,
        ],
        bot_accounts=settings.BOT_CREDENTIALS,
        exception_handlers=exception_handlers,  # type: ignore
        default_callback_timeout=BOTX_CALLBACK_TIMEOUT,
        httpx_client=AsyncClient(
            timeout=60,
            limits=Limits(max_keepalive_connections=None, max_connections=None),
        ),
        middlewares=[
            smart_logger_middleware,
            answer_error_middleware,
            FSMMiddleware(
                [
                    create_support_request.fsm,
                    update_support_request.fsm,
                ],
                state_repo_key="redis_repo",
            ),
        ],
        callback_repo=callback_repo,
    )
