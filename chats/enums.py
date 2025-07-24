from enum import IntEnum, StrEnum


class ChatWebSocketCloseCode(IntEnum):
    NOT_A_PARTICIPANT = 4001
    UNAUTHORIZED = 4002


class ChatWebSocketClientEventType(StrEnum):
    """Events sent from client to server"""

    TYPING = "typing"
    STOP_TYPING = "stop_typing"


class ChatWebSocketServerEventType(StrEnum):
    """Events sent from server to client"""

    NEW_MESSAGE = "new_message"
    USER_TYPING = "user_typing"
    USER_STOP_TYPING = "user_stop_typing"
