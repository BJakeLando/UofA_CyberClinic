from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('cybergame', '0002_choice_emoji_scenario_art_scenario_kind_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Track',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('difficulty', models.CharField(choices=[('beginner', 'Beginner'), ('intermediate', 'Intermediate'), ('advanced', 'Advanced')], max_length=14)),
                ('blurb', models.CharField(blank=True, max_length=60)),
                ('emoji', models.CharField(blank=True, max_length=8)),
                ('order', models.PositiveSmallIntegerField(default=0)),
                ('show_hints', models.BooleanField(default=True)),
                ('grade', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tracks', to='cybergame.grade')),
            ],
            options={
                'ordering': ['grade__number', 'order'],
                'unique_together': {('grade', 'difficulty')},
            },
        ),
        migrations.AddField(
            model_name='choice',
            name='hotspot',
            field=models.CharField(blank=True, choices=[('bait', 'The tempting button'), ('close', 'The little X'), ('report', 'The report flag')], max_length=10),
        ),
        migrations.AlterField(
            model_name='scenario',
            name='kind',
            field=models.CharField(choices=[('chat', 'Chat message'), ('popup', 'Pop-up'), ('voice', 'Voice message'), ('ask', 'Plain question'), ('device', 'Tablet screen')], default='ask', max_length=10),
        ),
        migrations.AddField(
            model_name='scenario',
            name='track',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='scenarios', to='cybergame.track'),
        ),
    ]
