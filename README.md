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
