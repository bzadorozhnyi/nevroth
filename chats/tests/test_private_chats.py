import jsonschema

from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from accounts.tests.factories.user import MemberFactory
from chats.models import Chat, ChatMember
from chats.tests.factories.chat import (
    ChatMemberFactory,
    ChatPrivateFactory,
    PrivateChatCreatePayloadFactory,
)

chat_schema = {
    "type": "object",
    "properties": {
        "id": {"type": "integer"},
        "chat_type": {"type": "string", "enum": ["private", "group"]},
    },
    "required": ["id", "chat_type"],
    "additionalProperties": False,
}

chat_list_response_schema = {
    "type": "object",
    "properties": {
        "count": {"type": "integer"},
        "next": {"type": ["string", "null"]},
        "previous": {"type": ["string", "null"]},
        "results": {"type": "array", "items": chat_schema},
    },
    "required": ["count", "next", "previous", "results"],
    "additionalProperties": False,
}


class ChatPrivateTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user1 = MemberFactory()
        cls.user2 = MemberFactory()
        cls.user3 = MemberFactory()

        cls.url = reverse("chat-list-create")

    def test_list_chats_authentication_required(self):
        """Test that authentication is required to list chats"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_chats_success(self):
        """Test that user can list chats"""
        self.client.force_authenticate(user=self.user1)

        # chat between user1 and user2 - we expect as result
        chat1 = ChatPrivateFactory()
        ChatMemberFactory(chat=chat1, user=self.user1)
        ChatMemberFactory(chat=chat1, user=self.user2)

        # chat between user1 and user3 - we expect as result
        chat2 = ChatPrivateFactory()
        ChatMemberFactory(chat=chat2, user=self.user1)
        ChatMemberFactory(chat=chat2, user=self.user3)

        # chat between user2 and user3 - we DO NOT expect as result
        chat3 = ChatPrivateFactory()
        ChatMemberFactory(chat=chat3, user=self.user2)
        ChatMemberFactory(chat=chat3, user=self.user3)

        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        data = response.data
        self.assertEqual(data["count"], 2)
        self.assertIsNone(data["next"])
        self.assertIsNone(data["previous"])

        returned_ids = [chat["id"] for chat in data["results"]]
        expected_ids = [chat1.id, chat2.id]
        self.assertCountEqual(returned_ids, expected_ids)

        for chat in data["results"]:
            self.assertEqual(chat["chat_type"], "private")

        self._assert_list_response_schema(data)

    def test_create_private_chat_authentication_required(self):
        """Test that authentication is required to create chat"""
        payload = PrivateChatCreatePayloadFactory()
        response = self.client.post(self.url, payload)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_private_chat_success(self):
        """Test that user can create private chat"""
        self.client.force_authenticate(user=self.user1)

        payload = PrivateChatCreatePayloadFactory(member=self.user2.id)
        response = self.client.post(self.url, payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        data = response.data
        self.assertEqual(data["chat_type"], Chat.ChatType.PRIVATE)

        # check if both users are members of chat
        self.assertTrue(
            ChatMember.objects.filter(chat=data["id"], user=self.user1).exists()
        )
        self.assertTrue(
            ChatMember.objects.filter(chat=data["id"], user=self.user2).exists()
        )

        # check if no other user in the chat
        self.assertEqual(ChatMember.objects.filter(chat=data["id"]).count(), 2)

        self._assert_chat_response_schema(data)

    def test_cannot_create_private_chat_with_yourself(self):
        """Test that user cannot create private chat with yourself"""
        self.client.force_authenticate(user=self.user1)

        payload = PrivateChatCreatePayloadFactory(member=self.user1.id)
        response = self.client.post(self.url, payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cannot_create_private_chat_without_chat_type(self):
        """Test that user cannot create private chat without chat type"""
        self.client.force_authenticate(user=self.user1)

        payload = PrivateChatCreatePayloadFactory()
        payload.pop("chat_type")

        response = self.client.post(self.url, payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cannot_create_private_chat_without_member(self):
        """Test that user cannot create private chat without member field"""
        self.client.force_authenticate(user=self.user1)

        payload = PrivateChatCreatePayloadFactory()
        payload.pop("member")

        response = self.client.post(self.url, payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def _assert_chat_response_schema(self, data):
        """Validate that the response matches the expected schema."""
        try:
            jsonschema.validate(instance=data, schema=chat_schema)
        except jsonschema.exceptions.ValidationError as e:
            self.fail(f"Response does not match schema: {e}")

    def _assert_list_response_schema(self, data):
        """Validate that the response matches the expected schema."""
        try:
            jsonschema.validate(instance=data, schema=chat_list_response_schema)
        except jsonschema.exceptions.ValidationError as e:
            self.fail(f"Response does not match schema: {e}")
