## Why

Hoje o app é **public-only**: a listagem descarta repositórios privados, o escopo OAuth é
`public_repo`, e o clone e a verificação de `manifest.json` usam URLs públicas (sem token).
Precisamos **listar e usar repositórios privados** (ex.: tornar um projeto privado e continuar
editando/contribuindo). É o item de **repos privados** do roadmap
([`docs/roadmap.md`](../../../docs/roadmap.md), R5), hoje sob o escopo do GitHub App.

## What Changes

- **Escopo OAuth** passa a incluir acesso a repositórios privados (`repo`), exigindo
  **re-consentimento** (re-login). (Antes: `read:user user:email public_repo`.)
- **Listar** os repositórios **públicos e privados** da conta (remover o filtro de privados).
- **Indicar repositórios privados** na lista de import com um **ícone discreto** (cadeado) ao
  lado do nome, para diferenciar dos públicos.
- **Verificar o `manifest.json` de forma autenticada** (API de contents com o token), o que
  passa a funcionar também para repositórios privados.
- **Clonar/baixar o repositório autenticado** (token na operação git, com sanitização nos
  erros) para importar projetos privados.
- As demais operações (working copy, edição, e o fluxo de colaboração de `project-changes`)
  passam a funcionar com privados sem mudança de contrato.

## Capabilities

### New Capabilities
(nenhuma)

### Modified Capabilities
- `github-import`: listar repositórios **públicos e privados**, validar o manifest de forma
  **autenticada** e **remover a restrição a repositórios públicos**.
- `identity`: o login passa a solicitar **escopo de repositório** (`repo`) para acessar
  privados (além dos escopos de identidade), o que implica novo consentimento.

## Impact

- **Backend:** `backend/infra/github.py` (escopo + listagem, sem filtro de privados),
  `backend/infra/github_source.py` (`check_manifest` autenticado; `fetch`/`import_repository`
  com token), `backend/web/api.py` (passar o token ao verificar e importar),
  `UserRepository`/store (guardar a marca de privado, opcional).
- **Auth:** novo escopo no login → usuários **re-consentem**.
- **Testes:** listagem com privados; manifest autenticado (privado); import autenticado.
- **Não alterado:** domínio, layout e a mecânica de colaboração (fork/PR), que já é
  agnóstica a public/private.

## Não-objetivos

- **GitHub App** / permissões granulares por instalação (privado/enterprise) — fica para
  depois; aqui usamos o token do usuário com escopo `repo`.
- **Organizações** além do que o token do usuário já acessa.
- Escolher branch/ref no import (continua a branch padrão).
- Cifrar o token em repouso (endurecimento à parte).
