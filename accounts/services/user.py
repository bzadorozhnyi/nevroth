from django.contrib.auth import get_user_model
from django.db.models.aggregates import Count
from django.db.models.query_utils import Q

from habits.models import UserHabit

User = get_user_model()


class UserService:
    @classmethod
    def get_suggested_users(cls, user: User) -> list[User]:
        user_habits = UserHabit.objects.filter(user=user).values("habit_id")

        similar_users = (
            User.objects.filter(userhabit__habit_id__in=user_habits)
            .exclude(id=user.id)
            .exclude(
                Q(sent_friend_requests__to_user=user)
                | Q(received_friend_requests__from_user=user)
            )
            .annotate(
                shared_habits=Count(
                    "userhabit", filter=Q(userhabit__habit_id__in=user_habits)
                )
            )
            .order_by("-shared_habits")
        )

        return similar_users
