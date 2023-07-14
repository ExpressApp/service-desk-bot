"""States for support request."""

from enum import Enum, auto


class CreateSupportRequestStates(Enum):
    """States to support request creation process."""

    ENTER_DESCRIPTION = auto()
    WAIT_DECISION_ON_ATTACHMENT = auto()
    ADD_ATTACHMENT = auto()


class UpdateSupportRequestStates(Enum):
    """States to support request updating process."""

    SELECT_ATTRIBUTE = auto()
    ENTER_NEW_DESCRIPTION = auto()
    ADD_NEW_ATTACHMENT = auto()
