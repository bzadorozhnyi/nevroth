import uuid

import factory
from django.contrib.auth.hashers import make_password
from factory.django import DjangoModelFactory

from accounts.models import User
from faker import Faker

faker = Faker()


class BaseUserFactory(DjangoModelFactory):
    class Meta:
        model = User

    email = factory.LazyAttribute(
        lambda o: f"{faker.first_name().lower()}.{uuid.uuid4().hex[:4]}@example.com"
    )
    full_name = factory.Faker("name")
    password = factory.PostGenerationMethodCall("set_password", "password")

    is_superuser = False
    is_staff = False

    @factory.post_generation
    def set_password(self, created, extracted, **kwargs):
        if extracted:
            self.password = make_password(extracted)
            if created:
                self.save()


class MemberCreatePayloadFactory(factory.Factory):
    class Meta:
        model = dict

    email = factory.Faker("email")
    full_name = factory.Faker("name")
    password = factory.LazyFunction(lambda: make_password("password"))


class AdminFactory(BaseUserFactory):
    role = User.Role.ADMIN


class MemberFactory(BaseUserFactory):
    role = User.Role.MEMBER
