from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import Paginator
from django.contrib.auth.decorators import login_required
from .models import OrdemServico, UserProfile, Local
import json
from django.db.models import Count, Sum
from django.db.models.functions import TruncDate
from django.http import HttpResponse
import csv
from .forms import OrdemServicoForm, TecnicoExecutionForm
from .forms import LocalForm, NovoUsuarioForm
from django.contrib.auth import login
from django.contrib.auth import get_user_model
from django.http import HttpResponseForbidden
from django.conf import settings
from django.contrib.auth import authenticate, login
from django.http import JsonResponse

# 1. Lista todas as ordens (Home)
@login_required
def lista_ordens(request):
    ordens_qs = OrdemServico.objects.all()
    # filtros por query params
    status = request.GET.get('status')
    prioridade = request.GET.get('prioridade')
    local = request.GET.get('local')
    tech = request.GET.get('tech')
    if status:
        ordens_qs = ordens_qs.filter(status=status)
    if prioridade:
        ordens_qs = ordens_qs.filter(prioridade=prioridade)
    if local:
        ordens_qs = ordens_qs.filter(local__id=local)
    if tech:
        ordens_qs = ordens_qs.filter(tecnico_responsavel__id=tech)
    paginator = Paginator(ordens_qs, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    # passar lista de locais para o filtro
    locais = Local.objects.all()
    tecnicos = get_user_model().objects.filter(profile__role=UserProfile.Role.TECNICO)
    return render(request, 'lista_ordens.html', {
        'ordens': page_obj,
        'locals': locais,
        'tecnicos': tecnicos,
        'status_choices': OrdemServico.Status.choices,
        'prioridade_choices': OrdemServico.Prioridade.choices,
    })

# 2. Mostra os detalhes
@login_required
def detalhe_ordem(request, id):
    ordem = get_object_or_404(OrdemServico, id=id)
    historico = ordem.historico.all()
    return render(request, 'detalhe_ordem.html', {'ordem': ordem, 'historico': historico})

# 3. Cria Nova Ordem
@login_required
def nova_ordem(request):
    if request.method == 'POST':
        form = OrdemServicoForm(request.POST)
        if form.is_valid():
            ordem = form.save(commit=False)
            ordem.solicitante = request.user
            ordem.save()
            return redirect('/')
    else:
        form = OrdemServicoForm()
    
    return render(request, 'form_ordem.html', {'form': form, 'titulo': 'Nova O.S.'})

# 4. Edita Ordem Existente
@login_required
def editar_ordem(request, id):
    ordem = get_object_or_404(OrdemServico, id=id)
    user_profile = getattr(request.user, 'profile', None)

    # Premium or manager can edit everything
    can_edit_all = request.user.is_superuser or (user_profile and user_profile.role == UserProfile.Role.PREMIUM)

    if request.method == 'POST':
        if can_edit_all:
            form = OrdemServicoForm(request.POST, instance=ordem)
            if form.is_valid():
                ordem = form.save(commit=False)
                ordem.save(alterado_por=request.user)
                return redirect(f'/ordem/{id}/')
        else:
            # Technician can only update execution fields
            if user_profile and user_profile.role == UserProfile.Role.TECNICO:
                form = TecnicoExecutionForm(request.POST, instance=ordem)
                if form.is_valid():
                    ordem = form.save(commit=False)
                    ordem.save(alterado_por=request.user)
                    return redirect(f'/ordem/{id}/')
            else:
                return redirect('/')
    else:
        if can_edit_all:
            form = OrdemServicoForm(instance=ordem)
        elif user_profile and user_profile.role == UserProfile.Role.TECNICO:
            form = TecnicoExecutionForm(instance=ordem)
        else:
            return redirect('/')

    return render(request, 'form_ordem.html', {'form': form, 'titulo': 'Editar O.S.'})


@login_required
def executar_ordem(request, id):
    ordem = get_object_or_404(OrdemServico, id=id)
    user_profile = getattr(request.user, 'profile', None)
    if not (user_profile and user_profile.role == UserProfile.Role.TECNICO):
        return redirect(f'/ordem/{id}/')

    if request.method == 'POST':
        form = TecnicoExecutionForm(request.POST, instance=ordem)
        if form.is_valid():
            ordem = form.save(commit=False)
            ordem.save(alterado_por=request.user)
            return redirect(f'/ordem/{id}/')
    else:
        form = TecnicoExecutionForm(instance=ordem)

    return render(request, 'form_ordem.html', {'form': form, 'titulo': 'Registrar Execução'})


@login_required
def locais(request):
    user_profile = getattr(request.user, 'profile', None)
    if not (request.user.is_superuser or (user_profile and user_profile.role == UserProfile.Role.PREMIUM)):
        return redirect('/')

    if request.method == 'POST':
        form = LocalForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('/locais/')
    else:
        form = LocalForm()

    locais = Local.objects.all()
    return render(request, 'locais.html', {'locais': locais, 'form': form})


@login_required
def criar_usuario(request):
    user_profile = getattr(request.user, 'profile', None)
    if not (request.user.is_superuser or (user_profile and user_profile.role == UserProfile.Role.PREMIUM)):
        return redirect('/')

    if request.method == 'POST':
        form = NovoUsuarioForm(request.POST)
        role = request.POST.get('role')
        if form.is_valid():
            user = form.save()
            if role:
                profile = user.profile
                profile.role = role
                profile.save()
            return redirect('/locais/')
    else:
        form = NovoUsuarioForm()

    return render(request, 'form_usuario.html', {'form': form})


@login_required
def remover_usuario(request, id):
    user_profile = getattr(request.user, 'profile', None)
    if not (request.user.is_superuser or (user_profile and user_profile.role == UserProfile.Role.PREMIUM)):
        return redirect('/')

    User = get_user_model()
    target = get_object_or_404(User, id=id)
    if request.method == 'POST':
        # Do not allow self-delete by mistake
        if target == request.user:
            return HttpResponseForbidden('Não é permitido excluir a si mesmo.')
        target.delete()
        return redirect('/locais/')

    return render(request, 'confirm_remover_usuario.html', {'target': target})


@login_required
def usuarios(request):
    user_profile = getattr(request.user, 'profile', None)
    if not (request.user.is_superuser or (user_profile and user_profile.role == UserProfile.Role.PREMIUM)):
        return redirect('/')

    User = get_user_model()
    users = User.objects.filter(is_superuser=False).order_by('username')
    # técnicos com contagens/tempo total
    tecnicos_qs = (
        User.objects
        .filter(profile__role=UserProfile.Role.TECNICO)
        .annotate(os_count=Count('os_tecnicas'), total_duration=Sum('os_tecnicas__duracao_exec'))
        .order_by('-os_count')
    )
    tecnicos = []
    for t in tecnicos_qs:
        total_sec = 0
        if t.total_duration:
            total_sec = t.total_duration.total_seconds()
        hours = int(total_sec // 3600)
        minutes = int((total_sec % 3600) // 60)
        hours_str = f"{hours}h {minutes}m"
        tecnicos.append({'user': t, 'os_count': t.os_count, 'hours_str': hours_str})
    return render(request, 'usuarios.html', {'users': users, 'tecnicos': tecnicos})


def demo_login(request):
    # Only available on DEBUG mode
    if not settings.DEBUG:
        return HttpResponseForbidden('Demo login disabled.')

    role = None
    if request.method == 'POST':
        role = request.POST.get('role')
        # map role to user
        role_map = {
            'gerente': ('gerente', True),
            'premium': ('premium', False),
            'solicitante': ('sol1', False),
            'tecnico': ('tech2', False),
        }
        if role not in role_map:
            role = 'gerente'
        username, is_super = role_map[role]
        # create user if not exists
        UserModel = get_user_model()
        user, created = UserModel.objects.get_or_create(username=username, defaults={'email': f'{username}@example.com'})
        if created:
            user.set_password('secret')
            if is_super:
                user.is_staff = True
                user.is_superuser = True
            user.save()
            # ensure role assigned
            profile = getattr(user, 'profile', None)
            if profile:
                if role == 'premium':
                    profile.role = 'PREMIUM'
                elif role == 'solicitante':
                    profile.role = 'SOLICITANTE'
                elif role == 'tecnico':
                    profile.role = 'TECNICO'
                profile.save()
        # authenticate and login
        auth = authenticate(username=username, password='secret')
        if auth:
            login(request, auth)
            return redirect('/dashboard/')

    return render(request, 'demo_login.html')


def health(request):
    # lightweight health check for load balancers
    return JsonResponse({'status': 'ok'})


@login_required
def dashboard(request):
    # resumo por status
    counts = {
        'PENDENTE': OrdemServico.objects.filter(status=OrdemServico.Status.PENDENTE).count(),
        'EM_ANDAMENTO': OrdemServico.objects.filter(status=OrdemServico.Status.EM_ANDAMENTO).count(),
        'ATRASADO': OrdemServico.objects.filter(status=OrdemServico.Status.ATRASADO).count(),
        'CONCLUIDO': OrdemServico.objects.filter(status=OrdemServico.Status.CONCLUIDO).count(),
    }

    # tempo gasto por técnico (soma de duracao_exec)
    time_by_tech = (
        OrdemServico.objects
        .filter(tecnico_responsavel__isnull=False, duracao_exec__isnull=False)
        .values('tecnico_responsavel__id', 'tecnico_responsavel__username')
        .annotate(total_duration=Sum('duracao_exec'))
        .order_by('-total_duration')
    )

    # quantas OS cada técnico fez
    count_by_tech = (
        OrdemServico.objects
        .filter(tecnico_responsavel__isnull=False)
        .values('tecnico_responsavel__id', 'tecnico_responsavel__username')
        .annotate(total_count=Count('id'))
        .order_by('-total_count')
    )
    # período para histórico (7, 30, 90 dias)
    period = int(request.GET.get('period', 30))
    if period not in (7, 30, 90):
        period = 30

    # compute date range
    from datetime import timedelta, date
    today = date.today()
    start_date = today - timedelta(days=period-1)

    # daily aggregates for period
    daily_qs = (
        OrdemServico.objects
        .filter(status=OrdemServico.Status.CONCLUIDO, data_execucao__isnull=False, data_execucao__gte=start_date, data_execucao__lte=today)
        .values('data_execucao')
        .annotate(total_count=Count('id'), total_duration=Sum('duracao_exec'))
        .order_by('data_execucao')
    )

    # build full list of days with defaults
    daily_map = {d['data_execucao']: d for d in daily_qs}
    day_list = [start_date + timedelta(days=i) for i in range(period)]
    daily_labels = [d.strftime('%Y-%m-%d') for d in day_list]
    daily_counts = [daily_map.get(d, {}).get('total_count', 0) for d in day_list]
    daily_time_values = [ (daily_map.get(d, {}).get('total_duration') or 0).total_seconds() / 3600.0 if daily_map.get(d, {}).get('total_duration') else 0 for d in day_list]

    # prepare json data for charts
    # Convert status code keys to readable labels
    status_map = {code: label for code, label in OrdemServico.Status.choices}
    status_labels = [status_map.get(k, k) for k in counts.keys()]
    status_values = list(counts.values())
    time_labels = [t['tecnico_responsavel__username'] for t in time_by_tech]
    # convert total_duration (timedelta) to hours
    # convert timedelta to hours (float) for chart, handle None
    time_values = [ (t['total_duration'].total_seconds() / 3600.0) if t['total_duration'] else 0.0 for t in time_by_tech]
    count_labels = [c['tecnico_responsavel__username'] for c in count_by_tech]
    count_values = [c['total_count'] for c in count_by_tech]

    return render(request, 'dashboard.html', {
        'counts': counts,
        'time_by_tech': time_by_tech,
        'count_by_tech': count_by_tech,
        'status_labels_json': json.dumps(status_labels),
        'status_values_json': json.dumps(status_values),
        'time_labels_json': json.dumps(time_labels),
        'time_values_json': json.dumps(time_values),
        'count_labels_json': json.dumps(count_labels),
        'count_values_json': json.dumps(count_values),
        'period': period,
        'daily_labels_json': json.dumps(daily_labels),
        'daily_counts_json': json.dumps(daily_counts),
        'daily_time_json': json.dumps(daily_time_values),
    })


@login_required
def dashboard_export(request):
    typ = request.GET.get('type', 'counts')
    period = int(request.GET.get('period', 30))
    if period not in (7, 30, 90):
        period = 30
    from datetime import timedelta, date
    today = date.today()
    start_date = today - timedelta(days=period-1)

    qs = (
        OrdemServico.objects
        .filter(status=OrdemServico.Status.CONCLUIDO, data_execucao__isnull=False, data_execucao__gte=start_date, data_execucao__lte=today)
        .values('data_execucao')
        .annotate(total_count=Count('id'), total_duration=Sum('duracao_exec'))
        .order_by('data_execucao')
    )

    # build CSV
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="dashboard_{typ}_{period}d.csv"'
    writer = csv.writer(response)
    if typ == 'counts':
        writer.writerow(['day', 'count'])
        for r in qs:
            writer.writerow([r['data_execucao'].strftime('%Y-%m-%d'), r['total_count']])
    else:
        writer.writerow(['day', 'hours'])
        for r in qs:
            hours = (r['total_duration'].total_seconds() / 3600.0) if r['total_duration'] else 0
            writer.writerow([r['data_execucao'].strftime('%Y-%m-%d'), hours])

    return response