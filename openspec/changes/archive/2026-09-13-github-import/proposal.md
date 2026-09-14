## Why

Hoje a entrada de projeto é só por **upload de zip**. Depois de resolvida a
identidade (change `local-github-auth`, arquivado), o próximo passo é o
**import a partir do GitHub**: localizar um repositório (o original de um projeto
ou o **fork** do usuário), validar o `manifest.json` e baixar **apenas** os
arquivos referenciados. É o primeiro tijolo do fluxo GitHub-first registrado em
`docs/ideas/github-import-export.md`.

## What Changes

- **Listar os repositórios da conta** no login, com o token de identidade
  (opção "buscar e cachear"), **sem** solicitar escopo de repositório adicional.
- **Selecionar** um repositório da lista (pode ser o original ou um fork).
- **Validar o `manifest.json`** da branch padrão, reutilizando o parser do
  domínio (`domain.project.parse_manifest`), e **indicar na lista** quais
  repositórios são importáveis (✅) e quais não são (⚪, com o motivo).
- **Atualizar a lista sob demanda** (o token do login é retido para isso), sem
  engolir erros de listagem em silêncio.
- **Importar via clone parcial + esparso** (`git clone --filter=blob:none
  --sparse` limitado aos caminhos do manifest) — sem baixar o repositório inteiro.
- O **working copy git persiste** como os dados do projeto no storage; leitura e
  edição continuam pela API de arquivos existente.
- Endpoints `GET /api/github/repos` e `POST /api/projects/github`; UI de escolha
  do repositório no menu de projeto.
- Adicionar **`git`** à imagem de runtime.

## Capabilities

### New Capabilities
- `github-import`: listar os repositórios públicos da conta, escolher um, validar
  o manifest e importar o projeto baixando só os arquivos referenciados, mantendo
  um working copy git esparso e persistente.

### Modified Capabilities
- Nenhuma. A lista de repositórios é um comportamento do import; a autenticação
  (`identity`) e o controle de acesso (`access-control`) permanecem como estão —
  o import apenas usa a sessão e o token já existentes.

## Impact

- **Backend:** `backend/infra/` (novo `github_source` com clone esparso e cache de
  repositórios; refatorar a ingestão para reaproveitar a validação), `backend/web/`
  (rotas de repos/import e hook pós-login), `backend/domain/` (reuso de
  `parse_manifest`), migração para a tabela de repositórios, `backend/tests/`.
- **Frontend:** UI de import (escolher repo → importar) e tratamento de erro.
- **Docker:** `git` na imagem de runtime.
- **Storage:** o diretório do projeto importado é um **working copy git esparso**
  (acopla o import ao `FilesystemStorage`; ver Riscos).
- **Não alterado:** segmentação, layout, preview, atlas.
- **Depende de:** `local-github-auth` (já arquivado).

## Não-objetivos

- Repositórios **privados** (só públicos no MVP).
- **Export/push/PR**, commit e sincronização com o GitHub (change futuro).
- Escolher branch/tag/commit (MVP usa a **branch padrão**).
- GitHub App / instalação; submodules, LFS, repositórios grandes.
- Baixar o repositório inteiro (tarball) ou clonar fora do storage de projeto.
- Editar o manifest pela UI ou importar projetos sem `manifest.json`.
- Criptografia em repouso do token retido (MVP guarda o token da sessão do
  provedor; endurecer depois).
