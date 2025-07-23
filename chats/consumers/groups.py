class WebSocketGroup:
    """Utility class for generating consistent WebSocket group names."""

    @classmethod
    def chat(cls, chat_id: int) -> str:
        return f"chat_{chat_id}"

    @classmethod
    def chat_list(cls, user_id: int) -> str:
        return f"user_chat_list_{user_id}"
