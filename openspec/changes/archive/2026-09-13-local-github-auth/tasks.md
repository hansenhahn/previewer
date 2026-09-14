## 1. Modelo e migração (identity)

- [x] 1.1 Criar `User` e `UserIdentity` em `backend/infra/models.py` (UUID, `UniqueConstraint(provider, external_id)`); verificar metadata
- [x] 1.2 Criar a migração Alembic `0002` para `users` e `user_identities`; verificar `alembic upgrade head` em banco vazio
- [x] 1.3 Repositório: buscar/criar usuário por identidade (upsert); verificar teste com SQLite in-memory

## 2. IdentityProvider (identity)

- [x] 2.1 Definir `Identity` e o Protocol `IdentityProvider` (login_url/exchange); verificar importação
- [x] 2.2 Implementar `GitHubOAuthProvider` (escopos `read:user user:email`, troca de código, `/user` e `/user/emails`) usando stdlib; verificar com HTTP mockado
- [x] 2.3 Implementar a checagem de allowlist (`GITHUB_ALLOWED_USERS`); verificar permitido e negado

## 3. Rotas e sessão (identity)

- [x] 3.1 Implementar `/auth/login` (gera `state`) e `/auth/callback` (valida `state`, upsert, sessão, redirect), injetando o provider; verificar teste com `FakeProvider`
- [x] 3.2 Implementar `/auth/logout`; verificar que a sessão deixa de valer
- [x] 3.3 Expor o usuário atual (`current_user`) e usá-lo como proprietário; verificar teste
- [x] 3.4 Expor `GET /auth/config` (público: `provider`, `label`, `login_url`) e `GET /auth/me` (público: `authenticated`/`user`); verificar testes

## 4. Controle de acesso (access-control)

- [x] 4.1 Guarda `before_request` no blueprint da API: 401 sem sessão, exceto `/healthz`; verificar teste
- [x] 4.2 Substituir `DEFAULT_OWNER` pelo usuário autenticado; verificar que os recursos ficam escopados ao usuário
- [x] 4.3 Ajustar os testes de API existentes para autenticar (fixture de sessão); verificar suíte

## 5. Configuração, frontend e verificação

- [x] 5.1 Adicionar `github_client_id`, `github_client_secret`, `github_allowed_users` ao `Settings`/`.env.example`; verificar falha explícita quando ausentes
- [x] 5.2 Frontend: view de login **desacoplada** (rótulo/ação vindos de `GET /auth/config`; aponta para `/auth/login`) e um `AuthGate` no bootstrap usando `GET /auth/me`; verificar build
- [x] 5.2.1 Garantir que o frontend não menciona um provedor específico (sem "GitHub" no código); verificar com `grep`
- [x] 5.3 Rodar a suíte Python (de `backend/`) e o `npm test`/`build`; confirmar que passam
- [x] 5.4 Verificar o fluxo no Docker (login/redirect/401) e validar com `openspec validate local-github-auth --strict`

## 6. Perfil e avatar (identity)

- [x] 6.1 Adicionar `avatar_url` a `Identity` e lê-lo de `GET /user` no `GitHubOAuthProvider`, aceitando apenas `https`; verificar com HTTP mockado
- [x] 6.2 Adicionar a coluna `avatar_url` a `user_identities` e a migração Alembic `0003`; verificar `alembic upgrade head`
- [x] 6.3 Persistir/atualizar o avatar no upsert e retornar `login`, `email` e `avatar_url` em `GET /auth/me`; verificar testes

## 7. Conta no cabeçalho (identity / UI)

- [x] 7.1 Adicionar o primitivo `menu` ao `UiKit` (`ui/kit.ts`) e implementá-lo com `wa-dropdown`/`wa-dropdown-item` no adaptador; verificar teste do kit
- [x] 7.2 Criar `shell/account.ts` (gatilho só com o nome; menu com avatar, login, e-mail e ação **Sair** → `/auth/logout`) e o `account-slot` no cabeçalho (`index.html`/`layout.css`) no canto superior direito; verificar build
- [x] 7.3 Obter o rótulo do provedor de `GET /auth/config` e garantir que o frontend não menciona provedor específico; verificar com `grep`
- [x] 7.4 Estender `api.ts`/estado com o perfil e rodar `npm test`/`build` e a suíte Python; confirmar que passam
