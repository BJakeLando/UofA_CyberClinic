from django.db import migrations, models


class Migration(migrations.Migration):
    """Add the impersonation text-message scene type.

    All three operations are additive and safe to replay:

      - Scenario.kind gains a "text" choice. Choices are not enforced by
        the database, so this is a no-op at the SQL level, but keeping the
        field definition honest stops `makemigrations` generating a stray
        migration on someone's laptop later.
      - Choice.hotspot gains a "verify" choice, same reasoning. "verify" is
        6 characters, so the existing max_length=10 still holds.
      - Scenario.hint is new. It defaults to blank, so every existing row
        gets an empty string and keeps the old generic hint line.

    No scenario, choice, player or completion row is touched.
    """

    dependencies = [
        ('cybergame', '0006_classroom'),
    ]

    operations = [
        migrations.AddField(
            model_name='scenario',
            name='hint',
            field=models.CharField(blank=True, max_length=160),
        ),
        migrations.AlterField(
            model_name='scenario',
            name='kind',
            field=models.CharField(
                choices=[
                    ('chat', 'Chat message'),
                    ('popup', 'Pop-up'),
                    ('voice', 'Voice message'),
                    ('ask', 'Plain question'),
                    ('device', 'Tablet screen'),
                    ('text', 'Text message'),
                ],
                default='ask',
                max_length=10,
            ),
        ),
        migrations.AlterField(
            model_name='choice',
            name='hotspot',
            field=models.CharField(
                blank=True,
                choices=[
                    ('bait', 'The tempting button'),
                    ('close', 'The little X'),
                    ('report', 'The report flag'),
                    ('verify', 'The saved contact'),
                ],
                max_length=10,
            ),
        ),
    ]
