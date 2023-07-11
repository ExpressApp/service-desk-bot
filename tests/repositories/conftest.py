import os
from pathlib import Path
from typing import Callable, Generator

import pytest
from pybotx import IncomingMessage
from pybotx.models.attachments import AttachmentDocument

from app.db.repositories.service_desk import ServiceDeskRepo
from app.settings import settings


@pytest.fixture
def service_desk_repo(
    incoming_message_factory: Callable[..., IncomingMessage],
    incoming_attachment: AttachmentDocument,
    default_string: str,
) -> ServiceDeskRepo:
    message = incoming_message_factory(body=default_string, file=incoming_attachment)
    return ServiceDeskRepo(
        sender_huid=message.sender.huid, attachment=message.file  # type: ignore
    )


@pytest.fixture
def user_attachments_path(tmp_path: Path) -> Generator:
    settings.USERS_ATTACHMENTS_DIR = tmp_path

    user_directory = tmp_path / "cd069aaa-46e6-4223-950b-ccea42b89c06"
    user_directory.mkdir()

    user_attachment = user_directory / "default.txt"
    user_attachment.write_text("some content")

    yield user_directory


@pytest.fixture
def clear_attachments(user_attachments_path: Path) -> None:
    user_attachment_path = user_attachments_path.joinpath("default.txt")
    os.remove(user_attachment_path)
