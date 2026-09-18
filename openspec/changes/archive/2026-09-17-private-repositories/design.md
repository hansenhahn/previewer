## Context

Ver `proposal.md` — Why. Estado atual: `SCOPES = "read:user user:email public_repo"`;
`list_repos` descarta `private`; `check_manifest` lê `raw.githubusercontent.com` (público);
`GitHubSource.fetch` clona sem token. O working copy e o fluxo de colaboração já são
agnósticos a public/private.

## Goals / Non-Goals

**Goals:** listar, validar e importar repositórios **privados**; manter o restante do fluxo
(edição e colaboração) funcionando sem contrato novo.

**Non-Goals:** GitHub App / permissões por instalação; cifrar token em repouso; escolher
branch/ref no import.

## Decisions

### 1. Escopo OAuth `repo` (token do usuário), não GitHub App
`repo` cobre privados (e públicos) e já habilita o fluxo de colaboração. Troca simples: só
`SCOPES`, mas exige **re-consentimento** (re-login). GitHub App fica para privado/enterprise
com permissões granulares (fora de escopo), sem trocar a UI.

### 2. Listar sem filtrar privados; marcar public/private
Remover o `if repo.get("private"): continue`. Persistir a marca `private` em
`user_repositories` (nova coluna, migração) e expor na API para a UI rotular. O
`RepositoryRef.private` já existe; falta a coluna e a exposição.

### 2b. Ícone discreto de privado na lista de import
Na lista de import (modal do GitHub), um repositório **privado** ganha um **ícone de cadeado**
ao lado do nome (com `title`/`aria-label` "privado"), discreto e sem deslocar as demais
informações. Reusa o `kit.icon` (ex.: `lock`). O público não recebe marca.

### 3. Manifest via API de contents autenticada
Trocar a leitura por `raw.githubusercontent.com` por `GET /repos/{full_name}/contents/manifest.json?ref={branch}`
com o token, que funciona para público e privado. Erros 404 → "manifest ausente"; outros →
erro reportado. O mesmo endpoint já é usado em `branch_has_manifest` (colaboração); aqui é a
checagem em lote da listagem (paralela, com token).

### 4. Clone autenticado com token sanitizado
`GitHubSource.fetch` passa a receber o token e clonar via URL autenticada
(`https://x-access-token:<token>@github.com/{full_name}.git`), mantendo
`GIT_TERMINAL_PROMPT=0`. Erros são **sanitizados** (remover o token da mensagem), como o
`GitWorkspace` já faz. `import_repository` recebe e repassa o token.

### 5. Reuso do `check_manifest` público como fallback
Sem token (ou em testes), a checagem pode continuar usando a URL raw para públicos; com
token, usa a API. Alternativa considerada: sempre API (exige token); escolhemos híbrido para
não quebrar o caminho sem token e facilitar testes com `opener`.

## Risks / Trade-offs

- **Escopo amplo (`repo`)**: acesso a todos os repositórios privados do usuário; aceitável no
  MVP, mitigado por GitHub App no futuro. Token continua em repouso (endurecimento à parte).
- **Re-consentimento**: usuários precisam re-logar após a mudança de escopo.
- **Clone privado**: mais lento/rede; sem mudança de comportamento para públicos.
