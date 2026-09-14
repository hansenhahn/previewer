## Context

Ver `proposal.md` — Why. Hoje a ingestão é só por zip (`backend/infra/ingestion.py`),
o `StorageBackend` é `FilesystemStorage` (`backend/infra/storage.py`) e a
identidade (change `local-github-auth`, arquivado) já dá sessão, `login` e um
token OAuth **transitório** no `/auth/callback`. O GitHub é o primeiro provedor;
o seam `ProjectSource` (ver `docs/ideas/github-import-export.md`) evita retrabalho
para GitLab etc.

## Goals / Non-Goals

**Goals:**
- Listar os repositórios públicos da conta (cache no login, sem escopo extra).
- Escolher um repo (original ou fork) e validar o `manifest.json` da branch padrão.
- Importar só os arquivos referenciados, via **clone parcial + esparso**.
- Working copy git **persistente** como dados do projeto.
- Endpoints autenticados e UI de import.

**Non-Goals:**
- Repos privados, export/push/PR, escolher branch/tag, GitHub App, LFS/submodules.
- Clonar o repo inteiro.

## Decisions

### 1. Token + listagem no login
- `infra/identity.py`: novo `Authorization(identity, access_token)`; o
  `IdentityProvider.exchange` passa a devolver `Authorization`. O
  `GitHubOAuthProvider` ganha `list_repos(token)` lendo `GET /user/repos`
  (paginado, filtrando `private == false`). Escopos continuam **identity-only**.
- O token é **retido** em `user_identities.access_token` (migração `0005`) para
  permitir **atualizar a lista sob demanda**; nunca é logado nem exposto pela API.
  Um `FakeProvider` nos testes cobre o fluxo.

### 2. Cache de repositórios
- Tabela `user_repositories(id, user_id fk, provider, full_name, default_branch,
  fork, manifest_ok, manifest_error, checked_at, updated_at,
  UniqueConstraint(user_id, provider, full_name))` (migração `0004` + `0005`).
  No login/atualização: upsert dos que vieram e remoção dos que sumiram.
- `GET /api/github/repos` lista o cache do usuário (com o selo de manifest);
  `POST /api/github/repos/refresh` refaz a consulta ao provedor.

### 3. Clone parcial + esparso (manifest primeiro)
- `git clone --filter=blob:none --sparse --depth=1 https://github.com/<full_name> <project_dir>`
- `git -C <dir> show HEAD:manifest.json` (puxa só esse blob) → `parse_manifest`.
- Caminhos: `manifest.json`, `manifest.texts.source` (diretório), `manifest.texts.original`
  (se houver), cada `fonts[].path` e `backgrounds[].path`.
- `git -C <dir> sparse-checkout set --no-cone <paths…>` + `git -C <dir> checkout`.
- Conferir que os arquivos referenciados existem; senão erro + rollback.

### 4. Working copy persistente e storage
- O diretório do projeto (`FilesystemStorage._project_dir`) **é** o clone. Adicionar
  `FilesystemStorage.local_path(owner_id, project_id) -> Path` como seam para o
  import; `FilesystemStorage.list_files` passa a **excluir `.git`**.
- O `GitHubSource` (novo `infra/github_source.py`) recebe o caminho do working copy,
  não depende de git no resto do app. Backends não-filesystem ficam sem o recurso
  (ver Riscos).

### 5. Reuso da ingestão
- Extrair de `import_bundle` a finalização comum (validação anti-traversal de
  caminhos, checagem de assets referenciados, criação do `Project` com
  `ProjectNameConflict` e rollback) para uso do import git. `import_bundle`
  continua funcionando; o `GitHubSource` valida e finaliza pelo mesmo caminho.

### 6. Segurança
- `git` com `GIT_TERMINAL_PROMPT=0`, `GIT_ASKPASS=/bin/true`,
  `-c protocol.file.allow=never`, `--depth=1`, timeout e limite de arquivos/tamanho.
- Só públicos; URL montada de `https://github.com/<full_name>` com validação do
  formato. Caminhos do manifest passam pela validação anti-traversal **antes** do
  sparse-checkout. O token nunca é logado.

### 7. Docker
- Instalar `git` no estágio `runtime` (imagem `python:3.13-slim`); nada de git no build.

### 8. Frontend
- No menu de projeto, item **"Importar do GitHub…"** → modal que carrega
  `GET /api/github/repos`, lista (nome, fork/original, branch) e importa via
  `POST /api/projects/github`; ao concluir, abre o projeto. Estados de
  carregando/erro. É específico do GitHub; o seam provider-agnostic é o
  `ProjectSource` no backend.

### 9. Seam `ProjectSource` / `GitHubSource`
- A rota depende de `GitHubSource` (leitura de arquivos do repo a partir do
  working copy); trocar/adicionar provedor = novo módulo, sem tocar no núcleo
  (OCP), igual a `FontFormat`/`StorageBackend`.

### 10. Validação de manifest (selo verde/cinza)
- Função `check_manifest(full_name, branch, opener=None)` em `infra/github_source.py`
  lê `https://raw.githubusercontent.com/<full_name>/<branch>/manifest.json` e
  chama `parse_manifest`; retorna `(ok, motivo)`. É a mesma validação usada no
  import (que continua relendo o manifest do clone).
- Na atualização (`refresh`), os repos são verificados em paralelo
  (`ThreadPoolExecutor`, poucos workers) e o resultado é gravado em
  `user_repositories.manifest_ok`/`manifest_error`/`checked_at`.
- Import recusa (422) repositório cujo `manifest_ok` não seja verdadeiro.

### 11. Atualização sob demanda e erros visíveis
- `POST /api/github/repos/refresh` usa o token retido para chamar
  `list_repos` e revalidar os manifests; erros do provedor são convertidos em
  resposta JSON (`github_error`) e logados — não são mais engolidos.
- `GET /api/github/repos` devolve o cache; a UI atualiza automaticamente quando
  o cache está vazio.

### 12. UI (verde/cinza)
- `shell/github-import.ts`: cada repo mostra ✅ (importável) ou ⚪ (não
  importável, com `title` do motivo) e um botão **Atualizar**. Itens ⚪ ficam
  desabilitados; ✅ importam ao clicar. Sem repos, dispara um refresh e mostra o
  erro do provedor, se houver.

### 13. Migração `0005`
- `user_identities.access_token` (String(512), nullable) e, em
  `user_repositories`, `manifest_ok` (Boolean, nullable), `manifest_error`
  (String(255), nullable), `checked_at` (DateTime, nullable). Aditiva.

## Risks / Trade-offs

- [Working copy git acopla ao `FilesystemStorage`] → aceito no MVP (storage é
  filesystem); S3 não suporta o recurso; documentado e isolado no seam.
- [`.git` no storage infla disco e pode vazar em listagens] → `list_files` filtra
  `.git`; projeto é escopado ao usuário.
- [Executar git sobre repositório não confiável] → flags restritivas, sem hooks,
  timeout e limites.
- [Rate limit do GitHub na listagem] → cache atualizado no login; o clone usa o
  protocolo git (não a API REST).
- [Repos grandes] → `--depth=1 --filter=blob:none` e sparse-checkout.
- [Manifest referenciando muitos arquivos] → limites e erro claro.

## Migration Plan

- Aditivo: tabela `user_repositories` (`0004`), endpoint e hook pós-login.
  Rollback: remover rotas/tabela; projetos já importados permanecem no storage.

## Open Questions

- Atualizar fork/upstream, escolher ref e export/push/PR → change de export.
- Guardar o token para reusar/refresh fora do login (hoje descartado).
