import os
from pathlib import Path

from pybotx.models.attachments import AttachmentDocument

from app.db.repositories.service_desk import ServiceDeskRepo


async def test__delete_user_attachments(
    service_desk_repo: ServiceDeskRepo,
    user_attachments_path: Path,
) -> None:
    # - Act -
    await service_desk_repo.delete_user_attachments()

    # - Assert -
    assert not service_desk_repo.get_user_attachments_names()
    assert not os.path.exists(user_attachments_path)


async def test__delete_user_attachments__empty_directory(
    service_desk_repo: ServiceDeskRepo,
    user_attachments_path: Path,
    clear_attachments: None,
) -> None:
    # - Act -
    await service_desk_repo.delete_user_attachments()

    # - Assert -
    assert not service_desk_repo.get_user_attachments_names()
    assert not os.path.exists(user_attachments_path)


async def test__add_user_attachments(
    service_desk_repo: ServiceDeskRepo,
    user_attachments_path: Path,
    incoming_attachment: AttachmentDocument,
) -> None:
    # - Act -
    service_desk_repo.add_user_attachment(user_attachment=incoming_attachment)

    # - Assert -
    assert service_desk_repo.get_user_attachments_names() == [
        "attachment.txt",
        "default.txt",
    ]


async def test__add_user_attachments__same_names(
    service_desk_repo: ServiceDeskRepo,
    user_attachments_path: Path,
    incoming_attachment: AttachmentDocument,
) -> None:
    # - Arrange -
    service_desk_repo.add_user_attachment(user_attachment=incoming_attachment)

    # - Act -
    service_desk_repo.add_user_attachment(user_attachment=incoming_attachment)

    # - Assert -
    assert service_desk_repo.get_user_attachments_names() == [
        "attachment (1).txt",
        "attachment.txt",
        "default.txt",
    ]


async def test__get_user_attachments_names(
    service_desk_repo: ServiceDeskRepo,
    user_attachments_path: Path,
    incoming_attachment: AttachmentDocument,
) -> None:
    # - Arrange -
    service_desk_repo.add_user_attachment(user_attachment=incoming_attachment)

    # - Act -
    received_names = service_desk_repo.get_user_attachments_names()

    # - Assert -
    assert received_names == ["attachment.txt", "default.txt"]


async def test__get_user_attachments_names__empty_directory(
    service_desk_repo: ServiceDeskRepo,
    user_attachments_path: Path,
    clear_attachments: None,
) -> None:
    # - Act -
    received_names = service_desk_repo.get_user_attachments_names()

    # - Assert -
    assert not received_names


async def test__get_user_attachments_count(
    service_desk_repo: ServiceDeskRepo,
    user_attachments_path: Path,
) -> None:
    # - Act -
    received_attachments_count = (
        service_desk_repo._get_user_attachments_count()  # noqa: WPS437
    )

    # - Assert -
    assert received_attachments_count == 1


async def test__get_user_attachments_count__empty_directory(
    service_desk_repo: ServiceDeskRepo,
    user_attachments_path: Path,
    clear_attachments: None,
) -> None:
    # - Act -
    received_attachments_count = (
        service_desk_repo._get_user_attachments_count()  # noqa: WPS437
    )

    # - Assert -
    assert received_attachments_count == 0


async def test__get_user_attachments_size(
    service_desk_repo: ServiceDeskRepo,
    user_attachments_path: Path,
) -> None:
    # - Act -
    received_attachments_size = (
        service_desk_repo._get_user_attachments_size()  # noqa: WPS437
    )

    # - Assert -
    assert received_attachments_size == 12


async def test__get_user_attachments_size__empty_directory(
    service_desk_repo: ServiceDeskRepo,
    user_attachments_path: Path,
    clear_attachments: None,
) -> None:
    # - Act -
    received_attachments_size = (
        service_desk_repo._get_user_attachments_size()  # noqa: WPS437
    )

    # - Assert -
    assert received_attachments_size == 0


async def test__is_valid_attachment(
    service_desk_repo: ServiceDeskRepo,
    user_attachments_path: Path,
) -> None:
    # - Act -
    is_valid = service_desk_repo.is_valid_attachment()

    # - Assert -
    assert is_valid


async def test__is_valid_attachment__invalid_attachment_size(
    service_desk_repo: ServiceDeskRepo,
    user_attachments_path: Path,
) -> None:
    # - Arrange -
    service_desk_repo._attachment.size = 99999999  # type: ignore # noqa: WPS437

    # - Act -
    is_valid = service_desk_repo.is_valid_attachment()

    # - Assert -
    assert not is_valid
