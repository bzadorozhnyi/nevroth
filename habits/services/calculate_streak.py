from datetime import timedelta

from django.db import connection
from django.utils import timezone

from habits.models import HabitProgress


class CalculateStreakService:
    """Service to calculate current and max streaks of habit progress"""

    @classmethod
    def calculate_streaks(cls, user_id: int, habit_id: int):
        """Calculate current and max streaks of habit progress"""

        return {
            "current": CalculateStreakService.calculate_current_streak(
                user_id, habit_id
            ),
            "max": CalculateStreakService.calculate_max_streak(user_id, habit_id),
        }

    @classmethod
    def calculate_current_streak(cls, user_id: int, habit_id: int):
        """Calculate current streak of habit progress"""
        today = timezone.now().date()
        streak = 0
        day = today

        while True:
            if HabitProgress.objects.filter(
                user__id=user_id, habit__id=habit_id, date=day, status="success"
            ).exists():
                streak += 1
                day -= timedelta(days=1)
            else:
                break

        return streak

    @classmethod
    def calculate_max_streak(cls, user_id: int, habit_id: int):
        """Calculate max streak of habit progress"""

        with connection.cursor() as cursor:
            cursor.execute(
                """
                           WITH ordered AS (SELECT
                               date
                              , status
                              , date - INTERVAL '1 day' * ROW_NUMBER() OVER (ORDER BY date) AS grp
                           FROM habits_habitprogress
                           WHERE status = 'success'
                             AND user_id = %s
                             AND habit_id = %s
                               )
                               , grouped AS (
                           SELECT COUNT (*) AS streak
                           FROM ordered
                           GROUP BY grp
                               )
                           SELECT COALESCE(MAX(streak), 0)
                           FROM grouped;
                           """,
                [user_id, habit_id],
            )

            return cursor.fetchone()[0]
