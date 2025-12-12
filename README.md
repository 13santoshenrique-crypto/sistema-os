# Sistema O.S.

Simple Django app to manage service orders.

## Roles & Permissions

- **Gerente (manager)**: superuser. Pode tudo via admin.
- **Premium**: pode editar 100% de tudo, inclusive criar/editar/remover usuários via interface `Criar Usuário` e `Gerenciar Usuários` (Admin).
- **Solicitante**: somente pode abrir novas O.S. (submit) e visualizar as ordens.
- **Técnico**: pode visualizar O.S. e registrar execução (data de execução, hora início/fim, material gasto, gerar nova OS relacionada).

## Novas features
- `UserProfile` com `role` (PREMIUM/SOLICITANTE/TECNICO).
- `Local` para associar técnicos.
- Campos de execução em `OrdemServico` para técnicos.
- Vistas e formulários restritos por papel.

## Admin
- Gerentes e usuários `premium` podem acessar /admin para gerenciar usuários e outros modelos.

## Deploy
Recomendado: Fly.io + Supabase (Postgres) para persistência grátis no plano inicial.

Local dev:
```bash
docker compose up --build
```

Deploy rápido:
1. Crie o projeto Supabase/Postgres e copie `DATABASE_URL`.
2. Configure `DJANGO_SECRET_KEY` e `DATABASE_URL` como secrets no Fly.
3. Opcional: configurar storage com `AWS_*` (ou S3 compatible) para uploads.
	Storage: If you want persistent media uploads, set the following env vars (supports S3-compatible endpoints like AWS S3, DigitalOcean Spaces or Supabase's S3 gateway when configured):

	```bash
	AWS_ACCESS_KEY_ID=...
	AWS_SECRET_ACCESS_KEY=...
	AWS_STORAGE_BUCKET_NAME=...
	AWS_S3_ENDPOINT_URL=https://your-s3-endpoint.example.com
	```

	If these are present in the environment, `django-storages` will be used as the `DEFAULT_FILE_STORAGE`.
  
You can set repository secrets automatically by running:
```bash
export GITHUB_TOKEN="<token>"  # personal token with repo:write permissions
./scripts/setup-github-secrets.sh --repo owner/repo --env .env
```
This uses the `gh` tool under the hood and requires you to have it authenticated locally.
4. Execute `scripts/fly-setup.sh <app-name>` para criar e deploy.

