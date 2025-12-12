from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin
from .models import OrdemServico, HistoricoStatus, UserProfile, Local

class HistoricoInline(admin.TabularInline):
    model = HistoricoStatus
    readonly_fields = ('status_antigo', 'status_novo', 'alterado_por', 'data_alteracao')
    extra = 0


@admin.register(OrdemServico)
class OrdemServicoAdmin(admin.ModelAdmin):
    def _local_display(self, obj):
        return obj.local.nome if obj.local else ''

    _local_display.short_description = 'Local'

    list_display = ('id', 'titulo', '_local_display', 'status', 'prioridade', 'prazo_limite', 'data_criacao', 'updated_at')
    list_filter = ('status', 'prioridade', 'local')
    inlines = [HistoricoInline]
    search_fields = ('titulo', 'descricao', 'local')


@admin.register(HistoricoStatus)
class HistoricoStatusAdmin(admin.ModelAdmin):
    list_display = ('ordem', 'status_antigo', 'status_novo', 'alterado_por', 'data_alteracao')
    list_filter = ('status_antigo', 'status_novo')
    search_fields = ('ordem__titulo',)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role')
    list_filter = ('role',)
    search_fields = ('user__username', 'user__email')


@admin.register(Local)
class LocalAdmin(admin.ModelAdmin):
    list_display = ('nome',)
    filter_horizontal = ('tecnicos',)


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Perfil'


class UserAdmin(DefaultUserAdmin):
    inlines = (UserProfileInline,)

# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)