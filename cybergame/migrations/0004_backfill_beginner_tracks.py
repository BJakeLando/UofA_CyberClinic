"""Give every existing scenario a home.

Before this migration, a Scenario belonged only to a Grade. Difficulty
lanes now live on Track, so each grade gets a Beginner track and all of
its current scenarios move into it. Nothing is deleted and nothing is
orphaned; re-running seed_content afterwards is still safe.
"""

from django.db import migrations

BLURB = "Words and pictures, with hints"


def forwards(apps, schema_editor):
    Grade = apps.get_model("cybergame", "Grade")
    Track = apps.get_model("cybergame", "Track")

    for grade in Grade.objects.all():
        track, _ = Track.objects.get_or_create(
            grade=grade,
            difficulty="beginner",
            defaults={"blurb": BLURB, "emoji": "🌱", "order": 0, "show_hints": True},
        )
        grade.scenarios.filter(track__isnull=True).update(track=track)


def backwards(apps, schema_editor):
    Scenario = apps.get_model("cybergame", "Scenario")
    Track = apps.get_model("cybergame", "Track")
    Scenario.objects.update(track=None)
    Track.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('cybergame', '0003_track_scenario_track_choice_hotspot_and_more'),
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
    ]
