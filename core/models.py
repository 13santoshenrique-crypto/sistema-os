from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.db.models.signals import post_save
from django.dispatch import receiver

class OrdemServico(models.Model):
    class Status(models.TextChoices):
        PENDENTE = 'PENDENTE', 'Pendente'
        EM_ANDAMENTO = 'EM_ANDAMENTO', 'Em Andamento'
        ATRASADO = 'ATRASADO', 'Atrasado'
        CONCLUIDO = 'CONCLUIDO', 'Concluído'

    class Prioridade(models.TextChoices):
        BAIXA = 'BAIXA', 'Baixa'
        MEDIA = 'MEDIA', 'Média'
        ALTA = 'ALTA', 'Alta'
        CRITICA = 'CRITICA', 'Crítica'

    titulo = models.CharField("Item / Título", max_length=200)
    descricao = models.TextField("Descrição do Problema")
    # Agora `local` é uma FK para Local (migração removeu o charfield)
    local = models.ForeignKey('Local', null=True, blank=True, on_delete=models.SET_NULL, related_name='ordens')
    
    data_criacao = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    data_conclusao = models.DateTimeField("Data da Realização", null=True, blank=True)
    # campos de execução que somente técnicos podem preencher
    data_execucao = models.DateField("Data de Execução", null=True, blank=True)
    hora_inicio = models.TimeField("Hora Início", null=True, blank=True)
    hora_fim = models.TimeField("Hora Fim", null=True, blank=True)
    material_gasto = models.TextField("Material Gasto", null=True, blank=True)
    gerou_nova_os = models.BooleanField(default=False)
    ordem_relacionada = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='ordens_relacionadas')
    duracao_exec = models.DurationField(null=True, blank=True)

    solicitante = models.ForeignKey(User, on_delete=models.PROTECT, related_name='os_abertas', db_index=True)
    tecnico_responsavel = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='os_tecnicas', db_index=True)
    
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDENTE, db_index=True)
    prioridade = models.CharField(max_length=10, choices=Prioridade.choices, default=Prioridade.MEDIA, db_index=True)
    prazo_limite = models.DateField("Prazo Limite", null=True, blank=True, db_index=True)
    acao_corretiva = models.TextField("Ação Corretiva", blank=True, null=True)

    def __str__(self):
        return f"OS #{self.id} - {self.titulo}"

    class Meta:
        ordering = ['-data_criacao']

    def clean(self):
        # Validações simples de datas
        if self.prazo_limite and self.prazo_limite < (self.data_criacao.date() if self.data_criacao else timezone.now().date()):
            raise ValidationError({'prazo_limite': 'Prazo não pode ser anterior à data de criação.'})
        if self.data_conclusao and self.data_conclusao < self.data_criacao:
            raise ValidationError({'data_conclusao': 'Data de conclusão não pode ser anterior à data de criação.'})

    def save(self, *args, **kwargs):
        # Mantemos um registro de alterações de status/tecnico
        try:
            orig = OrdemServico.objects.get(pk=self.pk)
        except OrdemServico.DoesNotExist:
            orig = None
        # optional kwarg to capture the user performing this save
        altered_by = kwargs.pop('alterado_por', None)

        super().save(*args, **kwargs)

        if orig:
            if orig.status != self.status or orig.tecnico_responsavel_id != self.tecnico_responsavel_id:
                HistoricoStatus.objects.create(
                    ordem=self,
                    status_antigo=orig.status,
                    status_novo=self.status,
                    alterado_por=altered_by,
                )

        # calcula `duracao_exec` quando ambos hora_inicio e hora_fim definidos
        if self.hora_inicio and self.hora_fim:
            # hora_fim e hora_inicio são objetos time; precisamos convertê-los para datetime
            from datetime import datetime
            from django.utils import timezone as djtz
            today = djtz.now().date()
            dt_start = datetime.combine(today, self.hora_inicio)
            dt_end = datetime.combine(today, self.hora_fim)
            if dt_end < dt_start:
                # assume crossing midnight -> soma um dia
                from datetime import timedelta
                dt_end = dt_end + timedelta(days=1)
            self.duracao_exec = dt_end - dt_start
            super(OrdemServico, self).save(update_fields=['duracao_exec'])


class HistoricoStatus(models.Model):
    ordem = models.ForeignKey(OrdemServico, on_delete=models.CASCADE, related_name='historico')
    status_antigo = models.CharField(max_length=20, choices=OrdemServico.Status.choices)
    status_novo = models.CharField(max_length=20, choices=OrdemServico.Status.choices)
    alterado_por = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    data_alteracao = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-data_alteracao']

    def __str__(self):
        return f"OS #{self.ordem.id} {self.get_status_antigo_display()} → {self.get_status_novo_display()}"  


class UserProfile(models.Model):
    class Role(models.TextChoices):
        PREMIUM = 'PREMIUM', 'Premium'
        SOLICITANTE = 'SOLICITANTE', 'Solicitante'
        TECNICO = 'TECNICO', 'Técnico'

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.SOLICITANTE)

    def __str__(self):
        return f"{self.user.username} ({self.get_role_display()})"


class Local(models.Model):
    nome = models.CharField(max_length=120)
    tecnicos = models.ManyToManyField(User, blank=True, related_name='locais_tecnicos')

    def __str__(self):
        return self.nome


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)