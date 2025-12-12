from django import forms
from .models import OrdemServico
from django.contrib.auth.models import User
from .models import Local
from django.contrib.auth.forms import UserCreationForm

class OrdemServicoForm(forms.ModelForm):
    class Meta:
        model = OrdemServico
        # Agora inclui STATUS e AÇÃO CORRETIVA para permitir a edição completa
        fields = ['titulo', 'descricao', 'local', 'prazo_limite', 'prioridade', 'tecnico_responsavel', 'status', 'acao_corretiva', 'data_execucao', 'hora_inicio', 'hora_fim', 'material_gasto', 'gerou_nova_os', 'ordem_relacionada']
        
        widgets = {
            'titulo': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ex: Conserto do Ar Condicionado'}),
            'descricao': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'local': forms.TextInput(attrs={'class': 'form-control'}),
            'prazo_limite': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'prioridade': forms.Select(attrs={'class': 'form-select'}),
            'tecnico_responsavel': forms.Select(attrs={'class': 'form-select'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
            'acao_corretiva': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Descreva o que foi feito (apenas na baixa)'}),
            'data_execucao': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'hora_inicio': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'hora_fim': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'material_gasto': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'ordem_relacionada': forms.Select(attrs={'class': 'form-select'}),
            'local': forms.Select(attrs={'class': 'form-select'}),
        }


class TecnicoExecutionForm(forms.ModelForm):
    class Meta:
        model = OrdemServico
        fields = ['data_execucao', 'hora_inicio', 'hora_fim', 'material_gasto', 'gerou_nova_os', 'ordem_relacionada']
        widgets = {
            'data_execucao': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'hora_inicio': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'hora_fim': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'material_gasto': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'ordem_relacionada': forms.Select(attrs={'class': 'form-select'}),
        }


class LocalForm(forms.ModelForm):
    class Meta:
        model = Local
        fields = ['nome', 'tecnicos']
        widgets = {
            'nome': forms.TextInput(attrs={'class': 'form-control'}),
            'tecnicos': forms.SelectMultiple(attrs={'class': 'form-select'}),
        }


class NovoUsuarioForm(UserCreationForm):
    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')