from enum import Enum, auto

class TicketStates(Enum):
    TITLE = auto()
    CONTENT = auto()
    CONFIRM = auto()
    EDIT_TITLE = auto()
    EDIT_MSG_1 = auto()
    EDIT_MSG_2 = auto()
    EDIT_MSG_3 = auto()

class AdminStates(Enum):
    REPLYING = auto()
    BROADCAST = auto()
