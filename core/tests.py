from django.test import TestCase
from django.contrib.auth.models import User
from django.urls import reverse
from .models import OrdemServico, HistoricoStatus, Local
from django.utils import timezone
from django.test import override_settings

# Create your tests here.
class OrdemServicoModelTests(TestCase):
	def setUp(self):
		self.user = User.objects.create_user(username='user1', password='pass')
		self.tech = User.objects.create_user(username='tech', password='pass')
		self.local_obj = Local.objects.create(nome='Setor Teste')

	def test_create_and_history_on_status_change(self):
		ordem = OrdemServico.objects.create(
			titulo='Teste', descricao='Desc', local=self.local_obj, solicitante=self.user
		)

		self.assertEqual(ordem.status, OrdemServico.Status.PENDENTE)

		# Change status and tecnico and save
		ordem.status = OrdemServico.Status.CONCLUIDO
		ordem.tecnico_responsavel = self.tech
		ordem.save()

		historicos = HistoricoStatus.objects.filter(ordem=ordem)
		self.assertTrue(historicos.exists())
		hist = historicos.first()
		self.assertEqual(hist.status_antigo, OrdemServico.Status.PENDENTE)
		self.assertEqual(hist.status_novo, OrdemServico.Status.CONCLUIDO)

	def test_ordering_and_pagination(self):
		# Create 12 ordens
		for i in range(12):
			OrdemServico.objects.create(
				titulo=f'Teste {i}', descricao='Desc', local=self.local_obj, solicitante=self.user
			)

		# need to login because we wrapped view with login_required
		self.client.login(username='user1', password='pass')
		response = self.client.get('/')
		self.assertEqual(response.status_code, 200)
		# Page object should be in context
		self.assertIn('ordens', response.context)
		page_obj = response.context['ordens']
		self.assertEqual(page_obj.paginator.count, 12)
		self.assertEqual(len(page_obj.object_list), 10)

	def test_prazo_limite_nao_pode_ser_anterior(self):
		ordem = OrdemServico(
			titulo='Teste Datas', descricao='Desc', local=self.local_obj, solicitante=self.user
		)
		import datetime
		ordem.data_criacao = timezone.make_aware(datetime.datetime(2020, 1, 10))
		ordem.prazo_limite = datetime.date(2020, 1, 1)
		from django.core.exceptions import ValidationError
		with self.assertRaises(ValidationError):
			ordem.full_clean()

	def test_editar_ordem_registra_alterado_por(self):
		editor = User.objects.create_user(username='editor', password='pass')
		editor.profile.role = 'PREMIUM'
		editor.profile.save()
		ordem = OrdemServico.objects.create(
			titulo='Para editar', descricao='Desc', local=self.local_obj, solicitante=self.user
		)

		self.client.login(username='editor', password='pass')
		data = {
			'titulo': ordem.titulo,
			'descricao': ordem.descricao,
			'local': ordem.local.id,
			'prazo_limite': '',
			'prioridade': OrdemServico.Prioridade.MEDIA,
			'tecnico_responsavel': self.tech.id,
			'status': OrdemServico.Status.EM_ANDAMENTO,
			'acao_corretiva': ''
		}
		resp = self.client.post(f'/editar/{ordem.id}/', data)
		self.assertEqual(resp.status_code, 302)

		hist = HistoricoStatus.objects.filter(ordem=ordem).first()
		self.assertIsNotNone(hist)
		self.assertEqual(hist.alterado_por, editor)

	def test_roles_permissions(self):
		# Create users with roles
		premium = User.objects.create_user(username='prem', password='pass')
		premium.profile.role = 'PREMIUM'
		premium.profile.save()

		solicitante = User.objects.create_user(username='req', password='pass')
		solicitante.profile.role = 'SOLICITANTE'
		solicitante.profile.save()

		tecnico = User.objects.create_user(username='t', password='pass')
		tecnico.profile.role = 'TECNICO'
		tecnico.profile.save()

		ordem = OrdemServico.objects.create(titulo='Role test', descricao='X', local=self.local_obj, solicitante=solicitante)

		# Premium can edit all via form
		self.client.login(username='prem', password='pass')
		data = {
			'titulo': 'Role test edited', 'descricao': ordem.descricao,
			'local': ordem.local.id,
			'prazo_limite': '', 'prioridade': OrdemServico.Prioridade.MEDIA, 'tecnico_responsavel': '',
			'status': OrdemServico.Status.EM_ANDAMENTO, 'acao_corretiva': ''
		}
		resp = self.client.post(f'/editar/{ordem.id}/', data)
		self.assertEqual(resp.status_code, 302)
		ordem.refresh_from_db()
		self.assertEqual(ordem.titulo, 'Role test edited')

		# Solicitante cannot edit via editar view (should redirect home)
		self.client.login(username='req', password='pass')
		resp = self.client.get(f'/editar/{ordem.id}/')
		self.assertEqual(resp.status_code, 302)

		# Técnico can only edit execution fields
		self.client.login(username='t', password='pass')
		data_exec = {'data_execucao': '2025-12-01', 'hora_inicio': '08:00', 'hora_fim': '09:00', 'material_gasto': 'Parafusos', 'gerou_nova_os': False}
		resp = self.client.post(f'/editar/{ordem.id}/', data_exec)
		self.assertEqual(resp.status_code, 302)
		ordem.refresh_from_db()
		self.assertEqual(str(ordem.data_execucao), '2025-12-01')

	def test_premium_can_create_user(self):
		premium = User.objects.create_user(username='prem2', password='pass')
		premium.profile.role = 'PREMIUM'
		premium.profile.save()
		self.client.login(username='prem2', password='pass')
		data = {'username': 'novo', 'email': 'novo@example.com', 'password1': 'strong-pass-1', 'password2': 'strong-pass-1', 'role': 'SOLICITANTE'}
		resp = self.client.post('/criar-usuario/', data)
		self.assertEqual(resp.status_code, 302)
		novo = User.objects.filter(username='novo').first()
		self.assertIsNotNone(novo)
		self.assertEqual(novo.profile.role, 'SOLICITANTE')

	def test_premium_can_create_local_and_assign_tecnico(self):
		premium = User.objects.create_user(username='prem3', password='pass')
		premium.profile.role = 'PREMIUM'
		premium.profile.save()
		tecnico = User.objects.create_user(username='tech3', password='pass')
		tecnico.profile.role = 'TECNICO'
		tecnico.profile.save()
		self.client.login(username='prem3', password='pass')
		data = {'nome': 'Oficina Secundária', 'tecnicos': [tecnico.id]}
		resp = self.client.post('/locais/', data)
		self.assertEqual(resp.status_code, 302)
		local = Local.objects.filter(nome='Oficina Secundária').first()
		self.assertIsNotNone(local)
		self.assertTrue(local.tecnicos.filter(username='tech3').exists())

	def test_premium_can_remove_user(self):
		premium = User.objects.create_user(username='prem_remove', password='pass')
		premium.profile.role = 'PREMIUM'
		premium.profile.save()
		target = User.objects.create_user(username='alvo', password='pass')
		self.client.login(username='prem_remove', password='pass')
		resp_get = self.client.get(f'/remover-usuario/{target.id}/')
		self.assertEqual(resp_get.status_code, 200)
		resp_post = self.client.post(f'/remover-usuario/{target.id}/')
		self.assertEqual(resp_post.status_code, 302)
		self.assertFalse(User.objects.filter(username='alvo').exists())

	def test_premium_cannot_remove_self(self):
		premium = User.objects.create_user(username='prem_self', password='pass')
		premium.profile.role = 'PREMIUM'
		premium.profile.save()
		self.client.login(username='prem_self', password='pass')
		resp_post = self.client.post(f'/remover-usuario/{premium.id}/')
		self.assertEqual(resp_post.status_code, 403)

	def test_non_premium_cannot_remove_user(self):
		regular = User.objects.create_user(username='regular', password='pass')
		target = User.objects.create_user(username='alvo2', password='pass')
		self.client.login(username='regular', password='pass')
		resp = self.client.post(f'/remover-usuario/{target.id}/')
		# redirected to home since not allowed
		self.assertEqual(resp.status_code, 302)

	def test_dashboard_charts_data(self):
		# Create premium and technicians
		premium = User.objects.create_user(username='prem_dash', password='pass')
		premium.profile.role = 'PREMIUM'
		premium.profile.save()
		tecs = []
		for i in range(3):
			u = User.objects.create_user(username=f'tech_dash_{i}', password='pass')
			u.profile.role = 'TECNICO'
			u.profile.save()
			tecs.append(u)

		local = Local.objects.create(nome='Oficina Dashboard')
		# Distribution: 34, 33, 33
		dist = [34, 33, 33]
		from datetime import timedelta
		for idx, count in enumerate(dist):
			for j in range(count):
				OrdemServico.objects.create(
					titulo=f'Dash OS {idx}-{j}',
					descricao='Teste Dashboard',
					local=local,
					solicitante=premium,
					tecnico_responsavel=tecs[idx],
					status=OrdemServico.Status.CONCLUIDO,
					duracao_exec=timedelta(hours=4)
				)

		# Now fetch the dashboard
		self.client.login(username='prem_dash', password='pass')
		resp = self.client.get('/dashboard/')
		self.assertEqual(resp.status_code, 200)
		# Check counts: all 100 concluded
		self.assertEqual(resp.context['counts']['CONCLUIDO'], 100)

		# Check time_by_tech totals
		from datetime import timedelta
		expected = { t.username: timedelta(hours=4 * c) for t, c in zip(tecs, dist) }
		# Map out actual totals
		actual = {item['tecnico_responsavel__username']: item['total_duration'] for item in resp.context['time_by_tech']}
		for uname, td in expected.items():
			self.assertEqual(actual.get(uname), td)

		# Count_by_tech
		actual_counts = {item['tecnico_responsavel__username']: item['total_count'] for item in resp.context['count_by_tech']}
		for t, c in zip(tecs, dist):
			self.assertEqual(actual_counts.get(t.username), c)

		# Check that template includes charts and Chart.js CDN/script tag
		self.assertContains(resp, 'cdn.jsdelivr.net/npm/chart.js')
		self.assertContains(resp, 'id="statusChart"')
		self.assertContains(resp, 'id="timeChart"')
		self.assertContains(resp, 'id="countChart"')
		self.assertContains(resp, 'id="download-time"')
		self.assertContains(resp, 'id="download-count"')
		self.assertContains(resp, 'id="download-status"')

	def test_dashboard_daily_and_export(self):
		premium = User.objects.create_user(username='prem_hist', password='pass')
		premium.profile.role = 'PREMIUM'
		premium.profile.save()
		tech = User.objects.create_user(username='tech_hist', password='pass')
		tech.profile.role = 'TECNICO'
		tech.profile.save()
		local = Local.objects.create(nome='Local Hist')
		from datetime import date, timedelta
		today = date.today()
		# create 3 days of entries
		from datetime import datetime
		for i in range(3):
			d = today - timedelta(days=i)
			OrdemServico.objects.create(
				titulo=f'Hist {i}', descricao='Hist', local=local, solicitante=premium, tecnico_responsavel=tech,
				status=OrdemServico.Status.CONCLUIDO, data_execucao=d, duracao_exec=(timedelta(hours=2))
			)

		self.client.login(username='prem_hist', password='pass')
		resp = self.client.get('/dashboard/?period=7')
		self.assertEqual(resp.status_code, 200)
		self.assertEqual(resp.context['period'], 7)
		# JSON strings should be present
		self.assertIn('daily_labels_json', resp.context)
		self.assertIn('daily_counts_json', resp.context)

		# Now test CSV export
		csv_resp = self.client.get('/dashboard/export/?type=counts&period=7')
		self.assertEqual(csv_resp.status_code, 200)
		self.assertTrue(csv_resp.has_header('Content-Disposition'))
		self.assertTrue(csv_resp.getvalue().decode().startswith('day,count'))

	@override_settings(DEBUG=True)
	def test_demo_login_page_AND_post(self):
		# ensure demo page loads
		resp = self.client.get('/demo-login/')
		self.assertEqual(resp.status_code, 200)
		self.assertContains(resp, 'Login Demo')

		# post to login as gerente
		resp2 = self.client.post('/demo-login/', {'role': 'gerente'})
		# should redirect to dashboard
		self.assertEqual(resp2.status_code, 302)
		# client should be logged in
		follow = self.client.get('/')
		self.assertTrue(follow.context['user'].is_authenticated)
		self.assertEqual(follow.context['user'].username, 'gerente')
