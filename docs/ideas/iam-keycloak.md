# Ideia: IAM com Keycloak (identidade) + GitHub (repo)

> Status: **ideia registrada, não agendada**. Base para a **Fase 4** (auth/host) do
> `MIGRATION.md`. Complementa `docs/ideas/github-import-export.md`.

## Objetivo

Adotar uma base de **identidade** e **autorização** com padrões abertos (OIDC),
sem construir auth do zero, e com **acesso limitado** (sem auto-registro) —
adequado para um produto em validação que pode virar genérico/multi-tenant.

- **Identidade:** Keycloak (self-hosted), com **login social via GitHub** como
  Identity Provider.
- **Autorização de repo GitHub:** separada da identidade (GitHub App / token).
- **Onboarding manual:** somente contas pré-existentes no Keycloak entram.

## Princípio central: identidade ≠ autorização de repo

| Necessidade | Quem resolve |
|---|---|
| Quem é o usuário (login) | Keycloak (OIDC; GitHub como IdP) |
| Importar/push em repositório GitHub | Credencial GitHub do usuário (GitHub App / OAuth / PAT) |
| Papéis e permissões no produto | Keycloak (roles globais) + app (`project_members`) |

Estar "logado com GitHub" **não** concede acesso à API de repos. São consentimentos
e escopos diferentes.

## Identidade (Keycloak)

### Contrato OIDC no app
- App = *relying party* (**confidential client**, authorization code flow).
- Valida o token (assinatura/issuer/audience) e lê **roles** de
  `resource_access.<client>.roles`.
- Sessão do app: cookie assinado (`SECRET_KEY`); fora da memória quando
  multiusuário (Redis) no futuro.
- **JIT interno**: no primeiro login bem-sucedido, cria/atualiza `users` a partir
  do `sub`/e-mail (seguro, pois o Keycloak já autorizou a entrada).

### Onboarding manual + linking controlado
- **Sem cadastro**: `Realm → Login → User registration = OFF`.
- **Sem auto-criação no brokering**: no IdP do GitHub, o *first login flow* **não**
  cria usuário e **exige vínculo existente** (`Detect Existing Broker User`); se
  não houver vínculo, **nega o login**.
- Fluxo do admin:
  1. cria o usuário no Keycloak (sem senha, se social-only) ou envia convite;
  2. adiciona o **Federated Identity** do GitHub (link) naquele usuário;
  3. o "Login com GitHub" encontra o vínculo e entra; os demais não entram.
- **Não auto-vincular por e-mail**: o passo *Automatically Set Existing User*
  (match por e-mail/username) é vetor de **account takeover**; como o onboarding é
  manual, pré-vincule e negue o resto.
- **Chave do vínculo**: ID numérico do GitHub (`sub`), estável entre mudanças de
  username.

### RBAC
- **Roles globais** no Keycloak (client do app): `admin`, `reviewer`,
  `translator`.
- **`clientRoles` são por cliente (globais), não por projeto.** A associação por
  projeto fica no app: `project_members(project_id, user_id, role)`.
  - Alternativa (não preferida no MVP): grupos por projeto no Keycloak.
- O app avalia autorização **antes** de tocar projeto/arquivo/storage.

## Autorização de repo GitHub

Ordem de preferência:

1. **GitHub App** (recomendado): permissões granulares + **installation tokens**
   de curta duração + **webhooks** (reconciliação). Usuário faz *installation*, não
   cola token.
2. **OAuth brokerado pelo Keycloak** (*Store tokens*): token vem do login. Recuperar
   o token upstream no RP costuma exigir *token exchange*/leitura — mais atrito.
3. **PAT manual** (fallback): campo opcional no *settings* do previewer, para
   desenvolvimento/self-host sem App/OAuth.

Cuidados: **escopos incrementais** (login leve; pedir repo só ao importar/exportar),
token **cifrado por usuário** (envelope + chave mestra em secret manager), com
expiração/rotação/revogação e **nunca** em log.

## Auditoria

Log **append-only** de eventos sensíveis: provisionamento/vínculo (admin), login,
concessão/revogação de escopo, leitura, save e push/PR.
`audit_log(user, action, resource, timestamp, ip)`.

## Configurações de segurança do Keycloak

- TLS obrigatório; **admin console fechado**; sem admin default.
- Políticas de token curtas; *brute-force protection*; MFA quando fizer sentido.
- **Backup do banco do Keycloak** (é estado crítico).
- Monitorar **CVEs** e versões (imagem Quarkus; há build arm64).

## Deploy (OCI free tier)

- Rodar no **Ampere A1** (4 OCPU / 24 GB) via `docker compose`, junto de app +
  Postgres. Keycloak tem **banco próprio**.
- Mais um serviço **stateful** e **alvo de alto valor** → endurecer e isolar.
- Manter portabilidade (OIDC padrão): o app não depende de OCI nem de serviços
  específicos do Keycloak.

## Fluxos (resumo)

```
Login:      Usuário → Keycloak → (IdP GitHub) → vínculo existente? → app (JIT/roles)
Repo:       Usuário → GitHub App installation → installation token → import/push
Fallback:   Usuário → PAT no settings → import/push
```

## Riscos / cuidados

- Auto-vínculo por e-mail → takeover. Mitigar com pré-vínculo e negação.
- Operar Keycloak é mais superfície (upgrades/CVE/backup). Pesar frente ao MVP.
- Não confundir login com acesso a repo (consentimentos distintos).
- ReDoS nos regex de `tags`/`matches`, limites de upload e rate limiting continuam
  pendentes da Fase 4.

## Recomendação / sequência

1. **Definir o contrato OIDC** no app agora (validar token, ler roles, sessão) —
   permite trocar "GitHub OAuth direto" por "Keycloak" sem mexer no domínio.
2. Modelar `identity`, `authorization`, `audit`, `credentials` como capabilities da
   Fase 4, com `project_members` para authz por projeto.
3. Subir Keycloak no primeiro host **ou** começar com login simples e migrar
   (decisão de ops, não de arquitetura).

## Questões em aberto

- Convite por e-mail vs criação manual no admin (onboarding em escala pequena).
- MFA obrigatório desde o início? MFA é por conta (Keycloak), não por IdP social.
- Modelar revisão (reviewer) por projeto como papel em `project_members` ou grupo
  no Keycloak.
- Estratégia de migração caso um usuário tenha sido vinculado por e-mail antes.
