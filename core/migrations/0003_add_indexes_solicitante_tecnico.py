from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_auto_add_fields_history'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ordemservico',
            name='solicitante',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='os_abertas', to='auth.user', db_index=True),
        ),
        migrations.AlterField(
            model_name='ordemservico',
            name='tecnico_responsavel',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='os_tecnicas', to='auth.user', db_index=True),
        ),
    ]
