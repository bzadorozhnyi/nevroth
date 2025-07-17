import jsonschema

from django.urls import reverse

from rest_framework import status
from rest_framework.test import APITestCase

from accounts.tests.factories.user import MemberFactory
from chats.models import ChatMessage
from chats.tests.factories.chat import ChatFactory, ChatMemberFactory
from chats.tests.factories.chat_message import (
    ChatMessageCreatePayloadFactory,
    ChatMessageFactory,
    ChatMessageUpdatePayloadFactory,
)

chat_message_schema = {
    "type": "object",
    "properties": {
        "id": {"type": "integer", "minimum": 1},
        "content": {"type": "string", "minLength": 1, "maxLength": 256},
        "chat": {"type": "integer", "minimum": 1},
    },
    "required": ["id", "content", "chat"],
    "additionalProperties": False,
}


class ChatMessagesTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = MemberFactory()
        cls.chat = ChatFactory()

        cls.list_url = reverse("chat-message-list")
        cls.detail_url = "chat-message-detail"

    def test_create_chat_message_authentication_required(self):
        """Test that authentication is required to create chat message."""
        payload = ChatMessageCreatePayloadFactory(chat=self.chat.id)
        response = self.client.post(self.list_url, payload)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_create_chat_message_success(self):
        """Test that user can create chat message."""
        self.client.force_authenticate(user=self.user)

        # add user to chat
        ChatMemberFactory(chat=self.chat, user=self.user)

        payload = ChatMessageCreatePayloadFactory(chat=self.chat.id)
        response = self.client.post(self.list_url, payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertTrue(
            ChatMessage.objects.filter(sender=self.user, chat=self.chat).exists()
        )

        chat_message = ChatMessage.objects.get(sender=self.user, chat=self.chat)

        data = response.data
        self.assertEqual(chat_message.sender, self.user)
        self.assertEqual(chat_message.chat, self.chat)
        self.assertEqual(chat_message.content, payload["content"])

        self._assert_chat_message_response_schema(data)

    def test_non_member_cannot_create_chat_message(self):
        """Test that non-member of chat cannot create chat message."""
        self.client.force_authenticate(user=self.user)

        payload = ChatMessageCreatePayloadFactory(chat=self.chat.id)
        response = self.client.post(self.list_url, payload)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_cannot_create_chat_message_with_empty_content(self):
        """Test that user cannot create chat message with empty content."""
        self.client.force_authenticate(user=self.user)

        # add user to chat
        ChatMemberFactory(chat=self.chat, user=self.user)

        payload = ChatMessageCreatePayloadFactory(chat=self.chat.id)
        payload["content"] = ""

        response = self.client.post(self.list_url, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cannot_create_chat_message_without_content_field(self):
        """Test that user cannot create chat message without content field."""
        self.client.force_authenticate(user=self.user)

        # add user to chat
        ChatMemberFactory(chat=self.chat, user=self.user)

        payload = ChatMessageCreatePayloadFactory(chat=self.chat.id)
        payload.pop("content")

        response = self.client.post(self.list_url, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cannot_create_chat_message_without_chat_field(self):
        """Test that user cannot create chat message without chat field."""
        self.client.force_authenticate(user=self.user)

        # add user to chat
        ChatMemberFactory(chat=self.chat, user=self.user)

        payload = ChatMessageCreatePayloadFactory(chat=self.chat.id)
        payload.pop("chat")

        response = self.client.post(self.list_url, payload)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_update_chat_message_authentication_required(self):
        """Test that authentication is required to update chat message."""
        # add user to chat
        ChatMemberFactory(chat=self.chat, user=self.user)

        message = ChatMessageFactory(sender=self.user, chat=self.chat, content="test")

        update_payload = ChatMessageUpdatePayloadFactory()
        url = reverse(self.detail_url, kwargs={"pk": message.id})
        response = self.client.put(url, update_payload)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_update_chat_message_success(self):
        """Test that user can update chat message."""
        self.client.force_authenticate(user=self.user)

        # add user to chat
        ChatMemberFactory(chat=self.chat, user=self.user)

        message = ChatMessageFactory(
            sender=self.user, chat=self.chat, content="before update"
        )

        update_payload = ChatMessageUpdatePayloadFactory()
        url = reverse(self.detail_url, kwargs={"pk": message.id})
        response = self.client.put(url, update_payload)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.assertTrue(ChatMessage.objects.filter(id=message.id).exists())

        chat_message = ChatMessage.objects.get(id=message.id)

        data = response.data
        self.assertEqual(chat_message.sender, self.user)
        self.assertEqual(chat_message.chat, self.chat)
        self.assertEqual(chat_message.content, update_payload["content"])

        self._assert_chat_message_response_schema(data)

    def test_cannot_update_chat_message_without_content(self):
        """Test that user cannot update chat message without content."""
        self.client.force_authenticate(user=self.user)

        # add user to chat
        ChatMemberFactory(chat=self.chat, user=self.user)

        message = ChatMessageFactory(
            sender=self.user, chat=self.chat, content="before update"
        )

        update_payload = ChatMessageUpdatePayloadFactory()
        update_payload.pop("content")

        url = reverse(self.detail_url, kwargs={"pk": message.id})
        response = self.client.put(url, update_payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_cannot_update_chat_message_with_empty_content(self):
        """Test that user cannot update chat message with empty content."""
        self.client.force_authenticate(user=self.user)

        # add user to chat
        ChatMemberFactory(chat=self.chat, user=self.user)

        message = ChatMessageFactory(
            sender=self.user, chat=self.chat, content="before update"
        )

        update_payload = ChatMessageUpdatePayloadFactory()
        update_payload["content"] = ""

        url = reverse(self.detail_url, kwargs={"pk": message.id})
        response = self.client.put(url, update_payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_delete_chat_message_authentication_required(self):
        """Test that authentication is required to delete chat message."""
        # add user to chat
        ChatMemberFactory(chat=self.chat, user=self.user)

        message = ChatMessageFactory(sender=self.user, chat=self.chat, content="test")

        url = reverse(self.detail_url, kwargs={"pk": message.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_delete_chat_message_success(self):
        """Test that user can delete chat message."""
        self.client.force_authenticate(user=self.user)

        # add user to chat
        ChatMemberFactory(chat=self.chat, user=self.user)
        message = ChatMessageFactory(
            sender=self.user, chat=self.chat, content="before update"
        )

        url = reverse(self.detail_url, kwargs={"pk": message.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        self.assertFalse(ChatMessage.objects.filter(id=message.id).exists())

    def test_cannot_delete_other_user_chat_message(self):
        """Test that user can delete chat message."""
        self.client.force_authenticate(user=self.user)

        other_user = MemberFactory()

        # add user to chat
        ChatMemberFactory(chat=self.chat, user=other_user)
        message = ChatMessageFactory(
            sender=other_user, chat=self.chat, content="before update"
        )

        url = reverse(self.detail_url, kwargs={"pk": message.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def _assert_chat_message_response_schema(self, data):
        """Validate that the response matches the expected schema."""
        try:
            jsonschema.validate(instance=data, schema=chat_message_schema)
        except jsonschema.exceptions.ValidationError as e:
            self.fail(f"Response does not match schema: {e}")
