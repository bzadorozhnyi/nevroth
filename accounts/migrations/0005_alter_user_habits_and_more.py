# Generated by Django 5.2.3 on 2025-07-15 14:13

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("accounts", "0004_user_habits_alter_user_role"),
        ("habits", "0005_habitprogress_habits_habi_user_id_a6243a_idx"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="habits",
            field=models.ManyToManyField(
                through="habits.UserHabit", to="habits.habit", verbose_name="habits"
            ),
        ),
        migrations.AddIndex(
            model_name="user",
            index=models.Index(
                fields=["full_name"], name="accounts_us_full_na_88336b_idx"
            ),
        ),
    ]
