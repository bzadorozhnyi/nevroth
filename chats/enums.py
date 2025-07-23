from enum import IntEnum, StrEnum


class ChatWebSocketCloseCode(IntEnum):
    NOT_A_PARTICIPANT = 4001


class ChatWebSocketEventType(StrEnum):
    NEW_MESSAGE = "new_message"
    TYPING = "typing"
    STOP_TYPING = "stop_typing"
