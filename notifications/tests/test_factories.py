from rest_framework.test import APITestCase

from notifications.tests.factories.message import MessageFactory
from notifications.tests.factories.notification import (
    NotificationFactory,
    NotificationCreateForUserPayloadFactory,
    NotificationCreateByHabitsPayloadFactory,
)


class TestFactories(APITestCase):
    def test_message_factory(self):
        MessageFactory()

    def test_notification_factory(self):
        NotificationFactory()
        NotificationCreateForUserPayloadFactory()
        NotificationCreateByHabitsPayloadFactory()
