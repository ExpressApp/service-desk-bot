"""Service Desk repo."""

import itertools
from contextlib import suppress
from pathlib import Path
from uuid import UUID

import aiofiles
from aiofiles import os as aioos
from pybotx import AttachmentDocument

from app.schemas.support_request import RequestAttachment
from app.settings import settings


class ServiceDeskRepo:  # noqa: WPS338
    def __init__(self, sender_huid: UUID, attachment: AttachmentDocument | None):
        self._sender_huid = str(sender_huid)
        self._attachment = attachment

    async def delete_user_attachments(self) -> None:
        """Delete all user attachments by user_huid from local storage."""

        user_dir = settings.USERS_ATTACHMENTS_DIR.joinpath(self._sender_huid)

        with suppress(FileNotFoundError):
            for user_path_file in user_dir.iterdir():
                await aioos.remove(user_path_file)

            await aioos.rmdir(user_dir)

    def add_user_attachment(
        self, user_attachment: AttachmentDocument  # type: ignore
    ) -> None:
        """Add user attachment by user_huid to local storage."""

        user_dir = settings.USERS_ATTACHMENTS_DIR.joinpath(self._sender_huid)
        user_path_attachment = user_dir.joinpath(user_attachment.filename)

        user_dir.mkdir(exist_ok=True)

        if user_path_attachment.exists():
            user_path_attachment = self._get_new_attachment_name(user_path_attachment)

        with user_path_attachment.open("wb") as file_w:
            file_w.write(user_attachment.content)

    async def get_user_attachments(self) -> list[RequestAttachment]:
        """Return all user attachments by user_huid from local storage."""
        user_dir = settings.USERS_ATTACHMENTS_DIR.joinpath(self._sender_huid)
        user_attachments = []

        with suppress(FileNotFoundError):
            for path_to_attachment in user_dir.iterdir():
                async with aiofiles.open(path_to_attachment, "rb") as file_object:
                    user_attachment = await RequestAttachment.from_aiofile(
                        aiofile=file_object, attachment_name=path_to_attachment.name
                    )

                user_attachments.append(user_attachment)

        return user_attachments

    def get_user_attachments_names(self) -> list[str]:
        """Return user attachments names."""

        user_dir = settings.USERS_ATTACHMENTS_DIR.joinpath(self._sender_huid)

        try:
            return sorted(user_file.name for user_file in user_dir.iterdir())
        except FileNotFoundError:
            return []

    def _get_new_attachment_name(  # type: ignore
        self, user_path_attachment: Path
    ) -> Path:
        """Return new attachment name."""
        for index in itertools.count(1):
            new_attachment_name = (
                f"{user_path_attachment.stem} ({index}){user_path_attachment.suffix}"
            )
            user_path_attachment = user_path_attachment.parent.joinpath(
                new_attachment_name
            )

            if not user_path_attachment.exists():
                return user_path_attachment

    def _get_user_attachments_count(self) -> int:
        """Return user attachments count."""

        user_dir = settings.USERS_ATTACHMENTS_DIR.joinpath(self._sender_huid)

        try:
            return len(list(user_dir.iterdir()))
        except FileNotFoundError:
            return 0

    def _get_user_attachments_size(self) -> int:
        """Return user attachments total size."""

        user_dir = settings.USERS_ATTACHMENTS_DIR.joinpath(self._sender_huid)

        try:
            return sum(user_file.stat().st_size for user_file in user_dir.iterdir())
        except FileNotFoundError:
            return 0

    def is_valid_attachment(self) -> bool:
        """Check attachment."""

        file_size = self._attachment.size  # type: ignore
        total_count = self._get_user_attachments_count() + 1
        total_size = self._get_user_attachments_size() + file_size

        is_valid_total_count = total_count <= settings.MAX_ATTACHMENTS_COUNT
        is_valid_total_size = total_size <= settings.MAX_ATTACHMENTS_SIZE
        is_valid_file_size = file_size <= settings.MAX_ATTACHMENT_SIZE

        return all((is_valid_total_count, is_valid_total_size, is_valid_file_size))
