from django.urls import re_path

from chats.consumers.chat_consumers import ChatConsumer, ChatListConsumer

websocket_urlpatterns = [
    re_path(r"ws/chats/(?P<chat_id>\d+)/$", ChatConsumer.as_asgi()),
    re_path(r"ws/chat-list/$", ChatListConsumer.as_asgi()),
]
