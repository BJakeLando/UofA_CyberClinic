from django.db import migrations, models


class Migration(migrations.Migration):
    """The pretend tablet: a home screen with apps instead of one pop-up.

    All additive or widening, safe on the live Postgres:

      - Scenario.setup is new, a JSON blob that defaults to {} for every
        existing row. seed_content fills it for tablet scenes.
      - Choice.hotspot grows from 10 to 24 characters so a tablet outcome
        can have a readable key ("call_parent", "report_phish"). Existing
        values all fit. The fixed list of hotspot names goes away because
        tablet scenes each have their own.
      - Scenario.kind gains "tablet". Choices are not enforced in SQL, so
        this only keeps the model and migrations in step.
    """

    dependencies = [
        ('cybergame', '0008_grade_kind'),
    ]

    operations = [
        migrations.AddField(
            model_name='scenario',
            name='setup',
            field=models.JSONField(blank=True, default=dict),
        ),
        migrations.AlterField(
            model_name='choice',
            name='hotspot',
            field=models.CharField(blank=True, max_length=24),
        ),
        migrations.AlterField(
            model_name='scenario',
            name='kind',
            field=models.CharField(choices=[('chat', 'Chat message'), ('popup', 'Pop-up'), ('voice', 'Voice message'), ('ask', 'Plain question'), ('device', 'Tablet screen'), ('text', 'Text message'), ('tablet', 'Whole tablet')], default='ask', max_length=10),
        ),
    ]
