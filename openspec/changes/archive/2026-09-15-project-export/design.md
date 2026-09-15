## Context

O import já cria um **working copy git esparso e persistente** por projeto. Como a
listagem de repos é do dono (`affiliation=owner`), o repo importado é o **fork do usuário**
(para projetos de terceiros); o `origin` do working copy é, portanto, **gravável**, e o
**`upstream`** é o `parent` desse fork. Falta o ciclo de contribuição. Ver `proposal.md` e
`docs/ideas/git-collaboration-backend.md`.

## Goals / Non-Goals

**Goals:** Alteração (= rascunho/branch/PR) com autosave e chip de estado; subir para PR no
fork; retomar/descartar/abandonar; check do upstream antes de publicar; aceitação no GitHub.

**Non-Goals:** conflito por segmento (R2), privados/GitHub App, branch base escolhível,
aprovação/merge dentro do app, tempo real (CRDT).

## Decisões

### 1. Working copy = repo git real; rascunho = branch no fork
O `origin` é o **fork do usuário** (gravável); o `upstream` (`owner/repo`) e a
**branch base** são detectados no import (pelo `parent` do fork) e **persistidos no
projeto** — não são derivados do `origin`. A base é mantida **sincronizada e limpa**. Ao
primeiro edit, o app cria e entra na **branch efêmera** `previewer/sketch` a partir da base;
no **Subir** ela vira a **branch definitiva** `previewer/<slug-do-título>` (head do PR):

```bash
git fetch origin <default>          # base sempre atualizada (pega merges recentes)
git switch -c previewer/sketch origin/<default>
# ... no Subir:
git branch -m previewer/<slug-do-título>
```

Cada autosave adiciona **um commit** ao rascunho local, formando o histórico da alteração
(checkpoints baratos, sobrevivem a crash e servem de base para desfazer). Em **pontos
explícitos** (Salvar), os commits são empurrados para a branch de backup
**`previewer-backup/sketch`** no fork — durabilidade no GitHub sem tocar no PR (branch
separada, existe só enquanto o rascunho é **não publicado**). Depois que vira PR, o backup é
removido e novos "Salvar" só commitam localmente. Para o PR não nascer
poluído, no **Subir** o delta não publicado é **squashado em um único commit**
(`git reset --soft <base|published>` + commit) antes do push: o PR nasce com 1 commit e
cada "Subir" acrescenta 1. O HEAD pré-squash é preservado em
`refs/previewer/scratch/<branch>` (base para undo futuro) e descartado no
Descartar/Abandonar. Expor undo navegável fica fora deste change.

### 2. Subir = push no repo/head + PR
Se o projeto é um **fork**, reusar/validar o fork (já existe desde o import; criar se tiver
sumido). Se é o **repositório próprio** do usuário (não fork), usar o próprio `origin` como
head e abrir o PR de uma branch para a base no mesmo repo. No primeiro "Subir": renomear a
branch efêmera `previewer/sketch` para `previewer/<slug-do-título>`,
sincronizar (`merge-upstream`) e, antes do push, **squashar o delta não publicado
em um único commit** (`git reset --soft <base|published>` + commit):

```bash
git reset --soft origin/<default>        # ou o último published
git commit -m "<título do PR>"
git push fork previewer/<slug>
```

Depois, abrir o PR via API: `fork:<slug> → upstream:<default>`. Subidas seguintes: squash do
delta não publicado em 1 commit + `git push fork` (o PR ganha 1 commit e atualiza) — ou
`PUT /pulls/{n}/update-branch` quando o upstream andou. Ao publicar, remova a branch de
backup (`previewer-backup/sketch`) — a branch definitiva a substitui. Sem mudanças não
enviadas, "Subir" fica **desabilitado** (o GitHub recusa PR sem diff).

### 3. Retomar / Novo rascunho / Descartar / Abandonar
- **Retomar:** a sincronização com o GitHub é **sob demanda** — só ao abrir a tela de
  Retomar (`GET .../changes?sync=1`); o refresh do chip/autosave lê apenas o banco (rápido).
  A lista registra também os **PRs abertos do head do usuário** (via API, `state=open`) —
  mesmo os abertos fora do app. Para cada um, checa se a branch tem
  `manifest.json` (API contents): se não tiver (não é projeto do previewer), a linha aparece
  **não-selecionável** com o motivo. `git switch previewer/<slug>` (só guarda quando há
  **edições não salvas**; commits do rascunho ficam preservados na branch, então trocar é
  seguro). Se a branch local sumiu, faz
  `git fetch origin <branch>`. Como salvaguarda, se após trocar a branch não tiver
  `manifest.json`, volta à base e informa o erro. Depois de trocar de branch (retomar,
  descartar ou abandonar), o app **recarrega o projeto** — o `manifest.json` da branch ativa
  — para não usar segmentação/ativos desatualizados.
- **Novo rascunho:** volta à base (`git switch <base>`) sem remover a alteração atual; o
  próximo edit cria um novo rascunho.
- **Descartar:** para um **rascunho não publicado**, remove a alteração por inteiro (branch
  `previewer/sketch`, backup `previewer-backup/sketch`, `refs/previewer/scratch`) e volta à
  base. Para uma **alteração publicada**, `git reset --hard <published>` descarta só o
  trabalho não publicado (o PR não é afetado). Desfazer um checkpoint específico (undo) fica
  fora deste change.
- **Abandonar:** `git switch <base> && git branch -D previewer/<slug>` (+ fechar o PR e
  apagar a branch remota de backup, se houver).

### 4. Credencial e seam
Operações de escrita atrás do contrato **`ProjectExport`**: `ensure_fork`, `ensure_branch`,
`commit`, `backup`, `publish` (squash+push+PR), `sync` (compare/update-branch),
`pr_status`, `checkout_base`. No MVP, token OAuth do usuário com **`public_repo`**; GitHub App
depois (privado/enterprise) sem trocar a UI. Atribuição via `Co-authored-by`/autoria do
usuário.

### 5. Modelo de dados
O **`projects`** ganha `upstream` (`owner/repo`) e `base_branch`, capturados no import pelo
`parent` do fork (o `origin` é o fork). O `upstream` é o alvo do PR; a `base_branch` define
o ponto de partida do rascunho e o destino do merge. Tabela **`changes`**: `id, project_id,
user_id, branch, title, base_commit, pr_number,
status (draft|open|changes_requested|merged|closed), created_at, updated_at`. Uma alteração
por `(project, user, branch)`. O working copy é um só por projeto; a "alteração ativa" define
a branch em checkout.

### 6. UI: autosave + chip + menu fixo
- **Autosave** a cada ~1 minuto persiste o arquivo no working copy (commit do rascunho) e
  acende um indicador discreto no header (**tick efêmero** ao salvar; **ícone de erro** se
  falhar); um botão **Salvar** força o salvamento imediato (flush) e o **backup** para
  `previewer-backup/<slug>` no fork — backup **apenas** enquanto o rascunho não foi publicado.
- **Chip de estado**: `fantasma` (base, sem alteração) · `tracejado` (rascunho, sem PR;
  pode já ter backup no fork) · `azul` (PR aberto) · `âmbar` (mudanças solicitadas).
- **Menu sempre igual** (não muda de itens): **Subir rascunho**, **Novo rascunho**,
  **Retomar rascunho**, **Descartar rascunho**; habilita/desabilita por disponibilidade.
- **Telas auxiliares**: nomear ao subir (título + descrição do PR; a mensagem de commit é
  gerada do título), retomar (lista) e confirmação de descartar/abandonar.

### 7. Sync do upstream (mínimo)
O `origin` é o fork; o `upstream` persistido é adicionado como remote (`git remote add
upstream <url>`) quando preciso. Antes de publicar, `fetch upstream` + merge se o upstream
avançou (`merge-upstream`/`git merge` + `update-branch`). O polling em camadas (ETag/304) e
o conflito por segmento ficam para depois (R2).

Referência de UI (mocks em `mock/`):
- **chip de estado + menu fixo**: [changes-states-desktop](../../../mock/changes-states-desktop.html) · [changes-states-mobile](../../../mock/changes-states-mobile.html)
- **janelas das ações** (Subir / Alterar / Descartar + resultado): [rascunho-actions-desktop](../../../mock/rascunho-actions-desktop.html) · [rascunho-actions-mobile](../../../mock/rascunho-actions-mobile.html)

## Riscos / Trade-offs

- [Escopo de escrita amplia a permissão OAuth] → `public_repo` no MVP; GitHub App depois.
- [Base suja / switch com trabalho pendente] → guardas e auto-commit antes de trocar.
- [PR sem diff] → "Subir" fica desabilitado quando não há mudanças não enviadas.
- [Repo grande / rate limit] → operações de git são locais; API só para fork/PR/status/compare.
- [Não empurrar o upstream diretamente] → PR sempre; merge no GitHub.

## Migration Plan

- Aditivo: colunas `upstream`/`base_branch` em `projects` e tabela `changes` (migrações),
  rotas e UI. O escopo OAuth exige **re-login** dos usuários (re-consentimento). Projetos já
  importados continuam válidos; sem `upstream` persistido, o app cai no `origin` como
  fallback até reimportar.

## Open Questions

- Rebase vs merge ao sincronizar o branch antes do primeiro push.
- Conflito por segmento (R2) e notificações de "mudanças solicitadas".
- GitHub App (privado/enterprise) e organizações.
