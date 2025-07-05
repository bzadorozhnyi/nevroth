from rest_framework.test import APITestCase

from accounts.tests.factories.user import (
    AdminFactory,
    MemberFactory,
    MemberCreatePayloadFactory,
)
from accounts.tests.factories.verify_token import VerifyTokenFactory


class TestFactories(APITestCase):
    def test_user_factories(self):
        AdminFactory()
        MemberFactory()

    def test_verify_token_factory(self):
        VerifyTokenFactory()

    def test_member_create_payload_factory(self):
        MemberCreatePayloadFactory()
