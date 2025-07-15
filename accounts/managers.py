from django.contrib.auth.base_user import BaseUserManager
from django.utils.translation import gettext_lazy as _
from django.db import models
from friends.models import FriendsRelation
from django.db.models import Q, Case, When, Value, CharField


class UserQuerySet(models.QuerySet):
    def with_relation_status(self, user):
        return (
            self.exclude(id=user.id)
            .annotate(
                relation_status=Case(
                    # pending incoming
                    When(
                        received_friend_requests__from_user=user,
                        received_friend_requests__status=FriendsRelation.Status.PENDING,
                        then=Value("pending_incoming"),
                    ),
                    # pending outgoing
                    When(
                        sent_friend_requests__to_user=user,
                        sent_friend_requests__status=FriendsRelation.Status.PENDING,
                        then=Value("pending_outgoing"),
                    ),
                    # friends
                    When(
                        Q(
                            received_friend_requests__from_user=user,
                            received_friend_requests__status=FriendsRelation.Status.ACCEPTED,
                        )
                        | Q(
                            sent_friend_requests__to_user=user,
                            sent_friend_requests__status=FriendsRelation.Status.ACCEPTED,
                        ),
                        then=Value("friends"),
                    ),
                    # not friends
                    default=Value("not_friends"),
                    output_field=CharField(),
                )
            )
            .distinct()
            .order_by("full_name")
        )


class UserManager(BaseUserManager):
    use_in_migrations = True

    def get_queryset(self):
        return UserQuerySet(self.model, using=self._db)

    def with_relation_status(self, user):
        return self.get_queryset().with_relation_status(user)

    def _create_user(self, email, password, **extra_fields):
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)

        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError(_("Superuser must have is_staff=True."))

        return self._create_user(email, password, **extra_fields)
