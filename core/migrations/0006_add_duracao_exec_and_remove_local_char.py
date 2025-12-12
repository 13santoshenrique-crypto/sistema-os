from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_populate_local_fk'),
    ]

    operations = [
        migrations.AddField(
            model_name='ordemservico',
            name='duracao_exec',
            field=models.DurationField(blank=True, null=True),
        ),
        migrations.RemoveField(
            model_name='ordemservico',
            name='local',
        ),
        migrations.RenameField(
            model_name='ordemservico',
            old_name='local_fk',
            new_name='local',
        ),
    ]
