"""States for support request."""

from enum import Enum, auto


class CreateSupportRequestStates(Enum):
    """States to support request creation process."""

    ENTER_DESCRIPTION = auto()
    WAIT_DECISION_ON_ATTACHMENT = auto()
    ADD_ATTACHMENT = auto()
