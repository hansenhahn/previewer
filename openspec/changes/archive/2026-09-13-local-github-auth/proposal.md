## Why

O app não tem autenticação — todas as rotas `/api` são abertas e o proprietário é
o stub `local`. Para validar o fluxo hospedado (Fase 4) **sem** a complexidade
operacional do Keycloak, vamos integrar **login via GitHub (somente identidade)**,
com **sessão** e **onboarding manual** (allowlist). Isso exercita o fluxo de
identidade e o seam que depois acomodará o Keycloak sem retrabalho.

## What Changes

- Introduzir o contrato **`IdentityProvider`** (`login_url`, `exchange`) com uma
  implementação **GitHub OAuth** (identity-only, escopos `read:user user:email`).
- Rotas `/auth/login`, `/auth/callback` e `/auth/logout` com **sessão** em cookie
  assinado (Flask).
- **Onboarding manual** via allowlist em variável de ambiente
  (`GITHUB_ALLOWED_USERS`): só identidades permitidas criam/associam usuário.
- Persistir **`users`** e **`user_identities`** (migração Alembic), mapeando
  `provider` + `external_id` estável.
- **Proteger as rotas `/api`**: requisições sem sessão recebem **401**; `/healthz`
  fica isento.
- Usar o **usuário autenticado como proprietário** das operações (substitui o stub
  `local`).
- Expor o **perfil** do usuário atual (login, e-mail e avatar) e **persistir o
  avatar** obtido do provedor (migração adicional).
- **Conta no cabeçalho**: nome/avatar no canto superior direito e um **menu de
  conta** (dropdown) com login, e-mail, provedor e **Sair**. O rótulo do provedor
  vem da configuração de entrada, mantendo o frontend desacoplado.
- Adicionar o primitivo **menu/dropdown** ao adaptador `UiKit` (Web Awesome atrás
  do adaptador; nenhuma tag `wa-*` fora de `ui/kit-*.ts`).
- Novas variáveis de ambiente: `GITHUB_CLIENT_ID`, `GITHUB_CLIENT_SECRET`,
  `GITHUB_ALLOWED_USERS`.

## Capabilities

### New Capabilities
- `identity`: autenticar via GitHub (somente identidade), manter sessão, encerrar
  sessão, expor o perfil (login, e-mail, avatar) do usuário atual, aplicar
  onboarding manual por allowlist, oferecer a tela de login e o menu de conta —
  ambos desacoplados do provedor.
- `access-control`: exigir autenticação para as rotas de API (exceto o health) e
  escopar as operações ao usuário autenticado.

### Modified Capabilities
- Nenhuma. As specs de projeto já falam em "proprietário"; apenas deixamos de usar
  o stub.

## Impact

- **Backend:** `backend/web/` (rotas de auth, guarda, perfil em `/auth/me`),
  `backend/infra/` (`IdentityProvider` com avatar, modelos/`users`/`user_identities`,
  migração do avatar), `backend/web/config.py` (env), `backend/tests/`.
- **Frontend:** `frontend/src/shell/` (conta no cabeçalho + menu), `frontend/src/ui/`
  (primitivo de menu no `UiKit` e no adaptador), `frontend/src/api.ts` (perfil) e
  estilos do cabeçalho/menu.
- **Não alterado:** domínio, storage, segmentação, preview.
- Referência: `docs/ideas/iam-keycloak.md` (identidade ≠ autorização de repo; seam
  para trocar por Keycloak).

## Não-objetivos

- Keycloak/OIDC, login social múltiplo.
- Acesso a repositório GitHub (GitHub App/token) e import/export Git.
- RBAC por projeto (`project_members`), MFA.
- Edição de perfil, upload/troca de avatar ou troca de e-mail (o avatar é somente
  o do provedor).
- ReDoS nas `tags`/`matches`, limites de upload e rate limiting (endurecimento da
  Fase 4, em change próprio).
