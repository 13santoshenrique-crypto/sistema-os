from django.contrib import admin
from django.urls import path
from core.views import lista_ordens, detalhe_ordem, nova_ordem, editar_ordem
from core.views import executar_ordem
from core.views import locais, criar_usuario
from core.views import remover_usuario
from core.views import usuarios, dashboard, dashboard_export, demo_login, health

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', lista_ordens),
    path('ordem/<int:id>/', detalhe_ordem, name='detalhe_ordem'),
    path('nova/', nova_ordem, name='nova_ordem'),
    path('editar/<int:id>/', editar_ordem, name='editar_ordem'),
    path('executar/<int:id>/', executar_ordem, name='executar_ordem'),
    path('locais/', locais, name='locais'),
    path('criar-usuario/', criar_usuario, name='criar_usuario'),
    path('remover-usuario/<int:id>/', remover_usuario, name='remover_usuario'),
    path('usuarios/', usuarios, name='usuarios'),
    path('dashboard/', dashboard, name='dashboard'),
    path('dashboard/export/', dashboard_export, name='dashboard_export'),
    path('demo-login/', demo_login, name='demo_login'),
    path('health/', health, name='health'),
]