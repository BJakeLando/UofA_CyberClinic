from django.db import migrations, models


class Migration(migrations.Migration):
    """Let a Grade row stand for a group (Girl Scouts) as well as a grade.

    One additive column. Every existing row defaults to "grade", so grades
    3-6 and everything hanging off them (tracks, scenarios, players'
    completions) are untouched. The Girl Scouts row itself is created by
    seed_content, which runs right after migrate on every deploy.
    """

    dependencies = [
        ('cybergame', '0007_text_scene'),
    ]

    operations = [
        migrations.AddField(
            model_name='grade',
            name='kind',
            field=models.CharField(
                choices=[('grade', 'School grade'), ('group', 'Group')],
                default='grade',
                max_length=8,
            ),
        ),
    ]
