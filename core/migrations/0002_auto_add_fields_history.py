from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='HistoricoStatus',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status_antigo', models.CharField(choices=[('PENDENTE', 'Pendente'), ('EM_ANDAMENTO', 'Em Andamento'), ('ATRASADO', 'Atrasado'), ('CONCLUIDO', 'Concluído')], max_length=20)),
                ('status_novo', models.CharField(choices=[('PENDENTE', 'Pendente'), ('EM_ANDAMENTO', 'Em Andamento'), ('ATRASADO', 'Atrasado'), ('CONCLUIDO', 'Concluído')], max_length=20)),
                ('data_alteracao', models.DateTimeField(auto_now_add=True)),
                ('alterado_por', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='auth.user')),
                ('ordem', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='historico', to='core.ordemservico')),
            ],
            options={'ordering': ['-data_alteracao']},
        ),
        migrations.AddField(
            model_name='ordemservico',
            name='updated_at',
            field=models.DateTimeField(auto_now=True, null=True),
        ),
        migrations.AlterField(
            model_name='ordemservico',
            name='solicitante',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='os_abertas', to='auth.user'),
        ),
        migrations.AlterField(
            model_name='ordemservico',
            name='status',
            field=models.CharField(db_index=True, choices=[('PENDENTE', 'Pendente'), ('EM_ANDAMENTO', 'Em Andamento'), ('ATRASADO', 'Atrasado'), ('CONCLUIDO', 'Concluído')], default='PENDENTE', max_length=20),
        ),
        migrations.AlterField(
            model_name='ordemservico',
            name='prioridade',
            field=models.CharField(db_index=True, choices=[('BAIXA', 'Baixa'), ('MEDIA', 'Média'), ('ALTA', 'Alta'), ('CRITICA', 'Crítica')], default='MEDIA', max_length=10),
        ),
        migrations.AlterField(
            model_name='ordemservico',
            name='prazo_limite',
            field=models.DateField(blank=True, null=True, verbose_name='Prazo Limite', db_index=True),
        ),
    ]
