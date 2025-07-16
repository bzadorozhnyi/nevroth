import jsonschema

from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from accounts.tests.factories.user import MemberFactory
from chats.tests.factories.chat import ChatMemberFactory, ChatPrivateFactory

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

        cls.list_url = reverse("chat-list")

    def test_list_chats_authentication_required(self):
        """Test that authentication is required to list chats"""
        response = self.client.get(self.list_url)
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

        response = self.client.get(self.list_url)
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

    def _assert_list_response_schema(self, data):
        """Validate that the response matches the expected schema."""
        try:
            jsonschema.validate(instance=data, schema=chat_list_response_schema)
        except jsonschema.exceptions.ValidationError as e:
            self.fail(f"Response does not match schema: {e}")
