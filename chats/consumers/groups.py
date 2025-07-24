def get_chat_group_name(chat_id: int) -> str:
    return f"chat_{chat_id}"


def get_user_chat_list_group_name(user_id: int) -> str:
    return f"user_chat_list_{user_id}"
