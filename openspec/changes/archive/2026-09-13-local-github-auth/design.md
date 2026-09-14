## Context

Ver `proposal.md` — Why. Hoje `backend/web/api.py` usa `DEFAULT_OWNER = "local"`
e não há autenticação. Já temos Flask, SQLAlchemy/Alembic, `StorageBackend` e o
`Settings` por env. A visão de longo prazo (`docs/ideas/iam-keycloak.md`) prevê
Keycloak para identidade; aqui antecipamos só a **identidade via GitHub** para
validar o fluxo localmente, mantendo o **seam** para o Keycloak.

## Goals / Non-Goals

**Goals:**
- Login GitHub identity-only + sessão + logout.
- Onboarding manual (allowlist por env).
- `/api` protegido (401 sem sessão); `/healthz` isento.
- Usuário autenticado como proprietário.
- Seam `IdentityProvider` para trocar por Keycloak sem mexer no domínio.

**Non-Goals:**
- RBAC por projeto, acesso a repositório, import/export Git, MFA.
- Endurecimento (ReDoS, limites de upload, rate limiting) — change próprio.

## Decisions

### 1. Contrato `IdentityProvider` (seam)
```python
@dataclass(frozen=True)
class Identity:
    provider: str        # "github"
    external_id: str     # id numérico do GitHub (estável)
    login: str
    email: str | None

class IdentityProvider(Protocol):
    name: str
    label: str            # rótulo exibido (ex.: "GitHub"); com Keycloak, "SSO"
    def login_url(self, state: str, redirect_uri: str) -> str: ...
    def exchange(self, code: str, redirect_uri: str) -> Identity: ...
```

O `redirect_uri` é calculado pelo blueprint (`url_for("auth.callback", _external=True)`)
e passado ao provider; assim o adapter não precisa de contexto Flask nem de uma
variável de base URL (por enquanto).
A implementação `GitHubOAuthProvider` usa `urllib.request` (stdlib) para trocar o
código e ler `GET /user` e `/user/emails` (escopos `read:user user:email`). Nada
de `repo`. O provider é **injetado** em `create_app` para testes (`FakeProvider`).

### 2. Sessão
Sessão em **cookie assinado** do Flask (`SECRET_KEY`). Guardamos apenas o
`user_id` interno. `state` do OAuth é gerado por requisição e conferido no
callback (anti-CSRF). Em localhost o cookie não é `Secure`.

### 3. Onboarding manual (allowlist)
`GITHUB_ALLOWED_USERS` (lista separada por vírgula de logins). No callback, se o
login não estiver na lista → acesso negado, sem criar usuário. Quem está na lista:
JIT de `users` (primeiro login) + linha em `user_identities`.

### 4. Modelo de dados (migração `0002`)
- `users(id UUID pk, created_at)`.
- `user_identities(id, user_id fk, provider, external_id, login, email,
  created_at)`, com `UniqueConstraint(provider, external_id)`.
Persistimos só identidade; nenhum token do GitHub é armazenado (não precisamos,
é identity-only).

### 5. Proprietário = usuário autenticado
Substitui o stub `local`: as operações usam o `user_id` do usuário autenticado
como `owner_id`. Storage continua recebendo uma string (UUID).

### 6. Controle de acesso
Um `before_request` no blueprint da API: sem sessão válida → **401 JSON**; exceto
`/healthz`. `/auth/*` é público. O 401 deve ser reconhecido pelo frontend para
mostrar o login.

### 7. Configuração e injeção
`Settings` ganha `github_client_id`, `github_client_secret`,
`github_allowed_users`. `create_app(settings, database, storage, identity_provider)`
injeta o provider (default: `GitHubOAuthProvider(settings)`).

### 8. Rotas
`GET /auth/login` → gera `state`, redireciona ao GitHub. `GET /auth/callback` →
valida `state`, troca o código, checa allowlist, faz upsert, grava sessão,
redireciona para `/`. `GET|POST /auth/logout` → limpa a sessão.

Públicas (sem sessão):
- `GET /auth/config` → `{provider, label, login_url: "/auth/login"}` (o frontend só
  sabe que existe "uma ação de entrada", não que é GitHub).
- `GET /auth/me` → `{authenticated: bool, user?}` (evita 401 ruidoso no bootstrap).

### 9. Tela de login desacoplada do provedor
O frontend tem uma **view de login** genérica que, no bootstrap, chama
`GET /auth/me`: se não autenticado, exibe a tela com o **rótulo** e a **ação** de
entrada vindos de `GET /auth/config` e aponta para `/auth/login`; se autenticado,
monta o workspace. **Nada de "GitHub" no frontend.** Com Keycloak, `label`/
`login_url` passam a apontar para o Keycloak, que apresenta a própria tela (com o
botão do GitHub) — sem tocar no frontend.

### 10. Perfil e avatar
`Identity` ganha `avatar_url`. O `GitHubOAuthProvider` lê `avatar_url` de
`GET /user` (informação pública de perfil, coberta por `read:user`) e o persiste
em `user_identities.avatar_url` (migração `0003`, aditiva). `GET /auth/me` passa a
retornar `user = {id, login, email, avatar_url}`. O frontend só consome esse
payload; o avatar é **do provedor**, sem upload. Segurança: a URL é validada
(esquema `https:`) e usada apenas como atributo `src` de `<img>` — nunca
`innerHTML`.

### 11. Conta no cabeçalho (UiKit `menu`)
Adiciona-se o primitivo `menu` ao `UiKit`:
```ts
export interface MenuItem { label: string; onSelect: () => void; icon?: string; danger?: boolean }
export interface MenuHandle { element: HTMLElement; open(): void; close(): void }
export function menu(options: { trigger: HTMLElement; header?: HTMLElement; items: MenuItem[] }): MenuHandle
```
No adaptador Web Awesome, `menu` usa `wa-dropdown` + `wa-dropdown-item` (trigger no
`slot="trigger"`); nenhuma tag `wa-*` escapa de `ui/kit-*.ts`. Em `shell/account.ts`
monta-se o gatilho (avatar + login) no `account-slot` do cabeçalho e o menu com o
cabeçalho (avatar, login, e-mail) e o item **Sair** → `location.assign("/auth/logout")`.
O nome do provedor no menu vem de `GET /auth/config` (`label`), mantendo o
desacoplamento. O `account-slot` é posicionado no canto superior direito, após o
tema.

## Risks / Trade-offs

- [Validar OAuth sem rede nos testes] → provider injetável; `FakeProvider` cobre o
  fluxo e o allowlist.
- [Segurança do fluxo] → exigir `state`, redirect URI fixo, não logar código/token,
  escopo mínimo; cookie `Secure` fora de localhost.
- [Migrar para Keycloak depois] → `current_user` é estável; troca-se o provider e a
  origem das roles.
- [Owner muda de "local" para usuário] → dados de teste existentes ficam órfãos;
  recriar no volume é aceitável em dev.

## Migration Plan

- Aditivo: novas tabelas/migrações (`0002` users/user_identities; `0003` coluna
  `avatar_url`), rotas e guarda. Projetos antigos (owner `local`) não aparecem para
  usuários autenticados — dev pode limpar o volume.
- Rollback: remover rotas/provider/menu e voltar o `DEFAULT_OWNER`; a coluna
  `avatar_url` pode ficar (nula).

## Open Questions

- Convite/e-mails de onboarding, MFA e RBAC por projeto — decidíveis na Fase 4 com
  o Keycloak.
