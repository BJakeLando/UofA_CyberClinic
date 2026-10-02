from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    """Scope players to a room.

    Existing players (there should be few or none in production yet) keep
    classroom=NULL and behave as solo players. Nothing is deleted.

    The global unique on Player.handle is replaced by a unique per room,
    which is what lets handles be reused across rooms instead of burning
    a single ~475k namespace nationally.
    """

    dependencies = [
        ('cybergame', '0005_player_completion'),
    ]

    operations = [
        migrations.CreateModel(
            name='Classroom',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=8, unique=True)),
                ('label', models.CharField(blank=True, max_length=60)),
                ('active', models.BooleanField(default=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('last_active', models.DateTimeField(auto_now=True)),
            ],
            options={
                'ordering': ['-last_active'],
            },
        ),
        migrations.AddIndex(
            model_name='classroom',
            index=models.Index(fields=['code'], name='cybergame_c_code_8e21f7_idx'),
        ),
        # drop the old global index before the field changes under it
        migrations.RemoveIndex(
            model_name='player',
            name='cybergame_p_total_p_6f4a1c_idx',
        ),
        migrations.AlterField(
            model_name='player',
            name='handle',
            field=models.CharField(max_length=40),
        ),
        migrations.AddField(
            model_name='player',
            name='classroom',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='players', to='cybergame.classroom'),
        ),
        migrations.AddIndex(
            model_name='player',
            index=models.Index(fields=['classroom', '-total_points', 'created_at'], name='cybergame_p_classro_3b9c4e_idx'),
        ),
        migrations.AlterUniqueTogether(
            name='player',
            unique_together={('classroom', 'handle')},
        ),
    ]
