from django.db import migrations, models
from django.conf import settings


def populate_local_fk(apps, schema_editor):
    Local = apps.get_model('core', 'Local')
    OrdemServico = apps.get_model('core', 'OrdemServico')
    for ordem in OrdemServico.objects.all():
        if ordem.local:
            local_obj, created = Local.objects.get_or_create(nome=ordem.local)
            ordem.local_fk = local_obj
            ordem.save()


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_add_profile_local_execution'),
    ]

    operations = [
        migrations.AddField(
            model_name='ordemservico',
            name='local_fk',
            field=models.ForeignKey(blank=True, null=True, on_delete=models.SET_NULL, related_name='ordens', to='core.local'),
        ),
        migrations.RunPython(populate_local_fk, reverse_code=migrations.RunPython.noop),
    ]
