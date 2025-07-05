import uuid
from datetime import datetime, timedelta
import random

import factory
from django.utils.timezone import make_aware
from factory.django import DjangoModelFactory

from accounts.models import VerifyToken
from accounts.tests.factories.user import BaseUserFactory


class VerifyTokenFactory(DjangoModelFactory):
    class Meta:
        model = VerifyToken

    user = factory.SubFactory(BaseUserFactory)
    email = factory.LazyAttribute(lambda obj: obj.user.email)
    token = factory.LazyAttribute(lambda o: uuid.uuid4())
    created_at = factory.LazyFunction(
        lambda: make_aware(datetime.now() - timedelta(days=random.randint(1, 30)))
    )
