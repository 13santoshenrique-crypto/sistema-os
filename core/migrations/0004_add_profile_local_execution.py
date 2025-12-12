from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_add_indexes_solicitante_tecnico'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('role', models.CharField(choices=[('PREMIUM', 'Premium'), ('SOLICITANTE', 'Solicitante'), ('TECNICO', 'Técnico')], default='SOLICITANTE', max_length=20)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='profile', to='auth.user')),
            ],
        ),
        migrations.CreateModel(
            name='Local',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nome', models.CharField(max_length=120)),
            ],
        ),
        migrations.AddField(
            model_name='local',
            name='tecnicos',
            field=models.ManyToManyField(blank=True, related_name='locais_tecnicos', to='auth.user'),
        ),
        migrations.AddField(
            model_name='ordemservico',
            name='data_execucao',
            field=models.DateField(blank=True, null=True, verbose_name='Data de Execução'),
        ),
        migrations.AddField(
            model_name='ordemservico',
            name='hora_inicio',
            field=models.TimeField(blank=True, null=True, verbose_name='Hora Início'),
        ),
        migrations.AddField(
            model_name='ordemservico',
            name='hora_fim',
            field=models.TimeField(blank=True, null=True, verbose_name='Hora Fim'),
        ),
        migrations.AddField(
            model_name='ordemservico',
            name='material_gasto',
            field=models.TextField(blank=True, null=True, verbose_name='Material Gasto'),
        ),
        migrations.AddField(
            model_name='ordemservico',
            name='gerou_nova_os',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='ordemservico',
            name='ordem_relacionada',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='ordens_relacionadas', to='core.ordemservico'),
        ),
    ]
