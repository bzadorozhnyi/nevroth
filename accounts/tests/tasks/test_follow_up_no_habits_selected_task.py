from django.core import mail

from rest_framework.test import APITestCase

from accounts.tasks.followup import follow_up_no_habits_selected_task
from accounts.tests.factories.user import MemberFactory
from habits.tests.factories.habit import UserHabitFactory


class FollowUpNoHabitsSelectedTaskTests(APITestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = MemberFactory()

    def test_send_reminder_no_selected_habits(self):
        """Test that a reminder email is sent if the user has not selected any habits."""
        follow_up_no_habits_selected_task(self.user.id)

        self.assertGreater(len(mail.outbox), 0)
        sent_email = mail.outbox[-1]
        self.assertIn(self.user.email, sent_email.to)
        self.assertEqual(sent_email.subject, "Nevroth Select Habits Reminder")

    def test_no_reminder_send_if_habits_selected(self):
        """Test that no reminder email is sent if the user has already selected habits."""
        # selecting habits for user
        UserHabitFactory.create_batch(3, user=self.user)

        follow_up_no_habits_selected_task(self.user.id)

        self.assertEqual(len(mail.outbox), 0)
