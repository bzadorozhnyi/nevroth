class WebSocketGroup:
    @classmethod
    def chat(cls, chat_id: int) -> str:
        return f"chat_{chat_id}"

    @classmethod
    def chat_list(cls, user_id: int) -> str:
        return f"chat_{user_id}"
