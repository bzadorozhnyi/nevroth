import jsonschema

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from chats.models import Chat
from accounts.tests.factories.user import MemberFactory
from chats.tests.factories.chat import ChatPrivateFactory, ChatMemberFactory
from chats.tests.factories.chat_message import ChatMessageFactory

sender_schema = {
    "type": "object",
    "properties": {
        "id": {"type": "integer"},
        "full_name": {"type": "string"},
    },
    "required": ["id", "full_name"],
    "additionalProperties": False,
}

chat_message_schema = {
    "type": "object",
    "properties": {
        "id": {"type": "integer"},
        "content": {"type": "string"},
        "sender": sender_schema,
    },
    "required": ["id", "content", "sender"],
    "additionalProperties": False,
}

chat_message_list_response_schema = {
    "type": "object",
    "properties": {
        "count": {"type": "integer"},
        "next": {"type": ["string", "null"]},
        "previous": {"type": ["string", "null"]},
        "results": {
            "type": "array",
            "items": chat_message_schema,
        },
    },
    "required": ["count", "next", "previous", "results"],
    "additionalProperties": False,
}


class ChatMessageListViewTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user1 = MemberFactory(full_name="Alice Example")
        cls.user2 = MemberFactory(full_name="Bob Bubble")
        cls.user3 = MemberFactory(full_name="Carol Example")

        cls.chat = ChatPrivateFactory(chat_type=Chat.ChatType.PRIVATE)
        # user1 and user2 are members
        ChatMemberFactory(chat=cls.chat, user=cls.user1)
        ChatMemberFactory(chat=cls.chat, user=cls.user2)

        # messages in chat
        cls.message1 = ChatMessageFactory(
            chat=cls.chat, sender=cls.user1, content="Hello from user1"
        )
        cls.message2 = ChatMessageFactory(
            chat=cls.chat, sender=cls.user2, content="Reply from user2"
        )

        cls.url = reverse("chat-messages-list", kwargs={"id": cls.chat.id})

    def test_list_chat_messages_authentication_required(self):
        """Test that authentication is required to list chat messages."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_cannot_list_messages_if_not_chat_member(self):
        """Test that non-member cannot list chat messages."""
        self.client.force_authenticate(user=self.user3)  # user3 is not a chat member
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_list_chat_messages_success(self):
        """Test that user can list chat messages."""
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.data

        message_ids = {m["id"] for m in data["results"]}
        expected_ids = {self.message1.id, self.message2.id}
        self.assertEqual(data["count"], len(expected_ids))
        self.assertSetEqual(message_ids, expected_ids)

        self._assert_list_response_schema(data)

    def test_paginated_list_chat_messages_multiple_pages(self):
        """Test that chat messages are listed with correct pagination over multiple pages."""
        self.client.force_authenticate(user=self.user1)
        for i in range(15):
            ChatMessageFactory(chat=self.chat, sender=self.user1)

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.data
        self.assertEqual(data["count"], 17)  # 2 old + 15 new

        self.assertEqual(len(data["results"]), 10)
        self.assertIsNotNone(data["next"])
        self.assertIsNone(data["previous"])
        self._assert_list_response_schema(data)

        next_url = data["next"]
        response2 = self.client.get(next_url)
        self.assertEqual(response2.status_code, status.HTTP_200_OK)

        data2 = response2.data
        self.assertEqual(len(data2["results"]), 7)
        self.assertIsNone(data2["next"])
        self.assertIsNotNone(data2["previous"])
        self._assert_list_response_schema(data2)

    def _assert_list_response_schema(self, data):
        """Validate that the response matches the expected schema."""
        try:
            jsonschema.validate(instance=data, schema=chat_message_list_response_schema)
        except jsonschema.exceptions.ValidationError as e:
            self.fail(f"Response does not match schema: {e}")
