from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('cybergame', '0004_backfill_beginner_tracks'),
    ]

    operations = [
        migrations.CreateModel(
            name='Player',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('handle', models.CharField(max_length=40, unique=True)),
                ('avatar', models.CharField(max_length=8)),
                ('total_points', models.PositiveIntegerField(db_index=True, default=0)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('last_seen', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ['-total_points', 'created_at'],
            },
        ),
        migrations.CreateModel(
            name='Completion',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('points', models.PositiveSmallIntegerField(default=0)),
                ('best_possible', models.PositiveSmallIntegerField(default=0)),
                ('attempts', models.PositiveSmallIntegerField(default=1)),
                ('first_try_best', models.BooleanField(default=False)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('player', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='completions', to='cybergame.player')),
                ('scenario', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='completions', to='cybergame.scenario')),
            ],
        ),
        migrations.AddIndex(
            model_name='player',
            index=models.Index(fields=['-total_points', 'created_at'], name='cybergame_p_total_p_6f4a1c_idx'),
        ),
        migrations.AddIndex(
            model_name='completion',
            index=models.Index(fields=['player', 'scenario'], name='cybergame_c_player__0a7b2d_idx'),
        ),
        migrations.AlterUniqueTogether(
            name='completion',
            unique_together={('player', 'scenario')},
        ),
    ]
