## Why

O import já traz o projeto do GitHub, mas **não há como contribuir de volta**. Queremos
um fluxo de **Alterações** que esconde o git de colaboradores não técnicos (advogado,
psicólogo, tradutor de fim de semana) e **mantém a aceitação/merge no GitHub** — sem
trazer responsabilidade de mantenedor para o app. Ver
[`docs/ideas/git-collaboration-backend.md`](../../../docs/ideas/git-collaboration-backend.md)
e [`docs/roadmap.md`](../../../docs/roadmap.md) (R1).

## What Changes

- **Alteração = rascunho = branch = PR** (um conceito só, sem expor git).
- **O repo importado é do usuário** (a listagem é do dono): em projetos de terceiros é o
  **fork**; em projeto próprio é o repositório em si. Ele é o `origin` (head) do working
  copy; o **`upstream`** (`owner/repo` + branch base) é detectado pelo `parent` do fork (ou
  é o próprio repo, se não for fork) e **persistido no projeto**.
- **Rascunho = branch efêmera no fork** (`previewer/sketch`), criada **automaticamente no
  1º edit** a partir da **base sincronizada** (o app faz `fetch` da base antes); ainda
  **sem PR**. Cada autosave vira um commit local e o **backup explícito** (Salvar) empurra
  os commits para `previewer-backup/sketch` — durabilidade sem tocar no PR.
- **Novo rascunho**: volta à base para começar outro rascunho sem publicar o atual.
- **Subir rascunho** = **renomear a efêmera para `previewer/<slug-do-título>`** + **squash
  do delta não publicado em 1 commit** + **push no fork** + **abrir PR**
  (`fork:branch → upstream:base`); subir de novo **atualiza o mesmo PR** (acrescenta 1
  commit) e remove a branch de backup.
- **Retomar rascunho** = escolher/continuar uma alteração (checkout; inclui **PRs abertos do
  head**, mesmo criados fora do app). **Descartar** = num rascunho não publicado remove a
  alteração; numa alteração publicada, reseta o trabalho local (PR intacto). **Abandonar** =
  deletar branch/backup e fechar o PR.
- **Autosave** (~1 min) com indicador discreto (**tick efêmero** ao salvar; **ícone de erro**
  ao falhar), mais um botão **Salvar** para forçar o salvamento + backup. Cada autosave vira
  um **commit local** (checkpoint); o delta não publicado é squashado ao Subir.
- **Chip de estado** no header: um controle só; clicar abre o **menu contextual**
  (`fantasma` sem alteração · `tracejado` rascunho · `azul` PR aberto · `âmbar` revisão).
- **Check do upstream antes de publicar** (atualiza o branch / evita PR velho).
- Credencial de escrita via OAuth **`public_repo`** (MVP), encapsulada no seam
  **`ProjectExport`** (GitHub App depois, para privado/enterprise).

## Capabilities

### New Capabilities
- `project-changes`: ciclo de vida da **Alteração** (rascunho/branch efêmera, subir para PR,
  retomar, descartar, abandonar) e a integração GitHub (fork/upstream, branch, PR, status,
  sync) — inclusive repo próprio (sem fork).

### Modified Capabilities
- `web-ui`: **chip de estado + menu contextual**, **autosave** com indicador e as telas
  auxiliares (nomear ao subir, retomar/selecionar, descartar/abandonar).

## Impact

- **Backend:** `backend/infra/` (`ProjectExport`, operações git no working copy, fork/PR
  via API), `backend/web/` (rotas de alterações), modelos/migrações (`changes`,
  `projects.upstream`/`base_branch`), `backend/infra/github.py` (escopo OAuth).
- **Frontend:** `frontend/src/` (chip, menus, sheets/diálogos), `index.html`, `ui/`.
- **Auth:** o login passa a pedir escopo de escrita (`public_repo`); usuários re-consentem.
- **Referência de UI:** mocks em `mock/` — `changes-states-*` (chip + menu) e
  `rascunho-actions-*` (janelas das ações), detalhados no `design.md`.
- **Não alterado:** domínio (fontes/layout/segmentação). O **import** agora também captura
  o `parent` (upstream) e a branch base do repo importado.

## Não-objetivos

- **Conflito por segmento** e merge automático (R2).
- Repos **privados** / GitHub App; escolher **branch base**; export genérico (zip).
- **Aprovação/revisão/merge dentro do app** — isso fica no GitHub.
- **Undo/histórico navegável** por checkpoint (a base fica preservada; a UI vem depois).
- Edição colaborativa em tempo real (CRDT/WebSocket).
