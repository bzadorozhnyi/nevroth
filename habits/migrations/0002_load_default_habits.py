# Generated by Django 5.2.3 on 2025-06-25 10:52

from django.db import migrations


def get_default_habits():
    return [
        {
            "name": "Smoking",
            "description": "The habitual inhalation of tobacco smoke, which can lead to serious health issues including cancer and heart disease.",
        },
        {
            "name": "Excessive screen time",
            "description": "Spending too many hours in front of screens, which can cause eye strain, sleep disruption, and reduced productivity.",
        },
        {
            "name": "Procrastination",
            "description": "The habit of delaying tasks or decisions, often leading to stress and missed deadlines.",
        },
        {
            "name": "Overeating",
            "description": "Consuming more food than the body needs, which can result in weight gain and other health complications.",
        },
        {
            "name": "Late night sleeping",
            "description": "Consistently going to bed very late, which can disrupt circadian rhythms and reduce overall sleep quality.",
        },
        {
            "name": "Nail biting",
            "description": "A nervous habit involving biting one’s nails, often triggered by stress or boredom.",
        },
        {
            "name": "Caffeine addiction",
            "description": "Excessive dependence on caffeinated beverages, which may cause anxiety, insomnia, and restlessness.",
        },
        {
            "name": "Social media addiction",
            "description": "Compulsively checking or scrolling social media, often interfering with real-life interactions and mental focus.",
        },
        {
            "name": "Impulse buying",
            "description": "Making unplanned purchases driven by emotion rather than need, often leading to financial strain.",
        },
        {
            "name": "Skipping meals",
            "description": "Habitually missing meals, which can lead to fatigue, poor concentration, and metabolic issues.",
        },
        {
            "name": "Poor posture",
            "description": "Consistently sitting or standing in unhealthy positions, which can lead to back pain and musculoskeletal problems.",
        },
        {
            "name": "Interrupting others",
            "description": "Regularly cutting people off while they speak, which can harm communication and relationships.",
        },
        {
            "name": "Being chronically late",
            "description": "Frequently failing to arrive on time, which may reflect poor planning and disrespect for others' time.",
        },
        {
            "name": "Excessive gaming",
            "description": "Spending an unhealthy amount of time playing video games, often at the expense of other responsibilities.",
        },
        {
            "name": "Negative self-talk",
            "description": "Engaging in critical or harmful internal dialogue, which can damage self-esteem and mental health.",
        },
        {
            "name": "Not exercising",
            "description": "Neglecting regular physical activity, which is essential for maintaining health and energy.",
        },
        {
            "name": "Gossiping",
            "description": "Spreading or discussing unverified information about others, often leading to misunderstandings and broken trust.",
        },
        {
            "name": "Multitasking",
            "description": "Attempting to do multiple tasks at once, which often reduces efficiency and increases errors.",
        },
        {
            "name": "Staying in comfort zone",
            "description": "Avoiding new challenges or growth opportunities due to fear or complacency.",
        },
        {
            "name": "Poor time management",
            "description": "Failing to plan and prioritize tasks effectively, resulting in stress and missed objectives.",
        },
    ]


def load_default_habits(apps, schema_editor):
    """Load default habits directly into the model"""
    habit_model = apps.get_model("habits", "Habit")
    for habit in get_default_habits():
        habit_model.objects.create(**habit)


def reverse_default_habits(apps, schema_editor):
    """Delete all data from Habits model"""
    habit_model = apps.get_model("habits", "Habit")
    names = [habit["name"] for habit in get_default_habits()]
    habit_model.objects.filter(name__in=names).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("habits", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(load_default_habits, reverse_default_habits),
    ]
