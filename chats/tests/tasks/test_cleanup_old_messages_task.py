from datetime import timedelta

from django.utils import timezone
from rest_framework.test import APITestCase

from chats.models import ChatMessage
from chats.tasks.cleanup import cleanup_old_messages_task
from chats.tests.factories.chat_message import ChatMessageFactory


class CleanupOldMessagesTaskTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.now = timezone.now()

        cls.old_message = ChatMessageFactory()
        ChatMessage.objects.filter(pk=cls.old_message.pk).update(
            created_at=cls.now - timedelta(days=31)
        )

        cls.new_message = ChatMessageFactory()
        ChatMessage.objects.filter(pk=cls.new_message.pk).update(
            created_at=cls.now - timedelta(days=29)
        )

    def test_cleanup_old_messages_task(self):
        """Test that only old messages are deleted by the cleanup task."""
        cleanup_old_messages_task()

        messages = ChatMessage.objects.all()
        self.assertIn(self.new_message, messages)
        self.assertNotIn(self.old_message, messages)
        self.assertEqual(messages.count(), 1)

    def test_cleanup_old_messages_task_runs_via_celery(self):
        """Ensure that the task runs successfully via Celery's apply() method."""
        result = cleanup_old_messages_task.apply()
        self.assertTrue(result.successful())
