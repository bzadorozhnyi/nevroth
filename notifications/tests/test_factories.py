from rest_framework.test import APITestCase

from notifications.tests.factories.message import NotificationMessageFactory
from notifications.tests.factories.notification import (
    NotificationFactory,
    NotificationCreateForUserPayloadFactory,
    NotificationCreateByHabitsPayloadFactory,
)


class TestFactories(APITestCase):
    def test_message_factory(self):
        NotificationMessageFactory()

    def test_notification_factory(self):
        NotificationFactory()
        NotificationCreateForUserPayloadFactory()
        NotificationCreateByHabitsPayloadFactory()
