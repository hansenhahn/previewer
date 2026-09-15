# Git/GitHub como backend de colaboração

> Status: **ideia/plano registrado**. Complementa `github-import-export.md`
> (import/export) e `security-hardening.md`. Não implementado.

## Decisão

Usar o **Git/GitHub como backend de colaboração** do previewer. O produto não é
"usar git" — é **esconder o git** para quem não é técnico. A **aceitação**
(PR, review, aprovação, merge, proteção de branch, threads) permanece **no
GitHub**; o previewer é um **cliente que gera PRs limpos** e mostra o estado
deles. Não trazemos a responsabilidade de mantenedor para o projeto.

## Propósito

Grupos de tradução trabalham no mesmo projeto, mas os colaboradores têm níveis
técnicos variados — de dev experiente a advogado/psicólogo que traduz no tempo
livre. Git é difícil até para dev; a **camada de colaboração** é o que permite
que essas pessoas contribuam sem saber o que é fork/branch/commit/PR, e facilita
a vida do mantenedor.

## Precedentes (UI sobre git)

- **Tradução:** **Weblate** (clone + push/**PR via API**), **Pontoon** (Mozilla),
  e SaaS (Crowdin/Transifex/Lokalise) com sync via git.
- **CMS git-based:** **Decap/Sveltia/Tina** — editor é só UI; conteúdo no repo
  (histórico, rollback, branch e PR "de graça").
- **Wikis:** Gollum, Wiki.js.

Conclusão: delegar versionamento/colaboração é **redução de escopo**;
reimplementar diff/merge/PR é que seria overengineering.

## Escopo

**Dentro (previewer):**
- Editar/revisar com a UX boa (segmentos, prévia fiel), inclusive revisão
  linguística.
- **Publicar** = criar/atualizar um **PR no GitHub** automaticamente (branch +
  commit + PR), sem o usuário ver git.
- **Sincronizar** com o upstream de forma simples.
- Mostrar **status/links** dos PRs e de mudanças pendentes.

**Fora (GitHub):** aprovar, mergear, resolver conflito "de verdade", threads de
review e regras de proteção.

## Credenciais

- **MVP:** token OAuth do colaborador com escopo **`public_repo`** (mais estreito
  que `repo`) — cobre o caso comum (projetos públicos de tradução): criar fork,
  empurrar branch e abrir PR em nome do usuário.
- **Evolução:** **GitHub App** instalado no upstream para repos privados/enterprise
  e permissões granulares. O seam **`ProjectExport`** acomoda a troca sem
  retrabalho.
- **Atribuição:** commits com `Co-authored-by`/autoria do colaborador, para o
  crédito aparecer no histórico.

## Publicação (fork → branch → commit → PR)

O `ProjectExport` orquestra via API: **fork → branch (`previewer/<projeto>`) →
commit → PR**. O mantenedor vê um **PR normal** e mergeia como sempre.

- **Conflito:** se o GitHub marcar o PR como conflitante, o app tenta
  update/rebase automático; se não der, avisa o colaborador e (opcional) comenta
  no PR para o mantenedor — sem tentar resolver merge dentro do app.

## Sync dos forks com o upstream

Como mantemos um **clone completo** no servidor, fazemos git de verdade e só
orquestramos. Guardamos por projeto o **commit base** (SHA importado) e o
`upstream` (`owner/repo` + branch).

- **Sincronizar fork:** `POST /repos/{fork}/merge-upstream {branch}`.
- **Branch de contribuição:** `git fetch upstream && git merge upstream/master`
  (ou rebase) e `push --force-with-lease`; ou `PUT /pulls/{n}/update-branch`.
- **Automático quando limpo:** ao abrir/publicar, se o merge é limpo, atualiza
  sozinho e o PR se atualiza.

## Detecção de mudanças — polling em camadas

Como não queremos exigir do mantenedor configurar **webhook** no repo, a detecção é
por **polling**, em camadas:

1. **Ao abrir o projeto (lazy):** 1 request; mostra o banner "N commits novos". É o
   suficiente para o MVP.
2. **Antes de publicar (obrigatório):** checa upstream e, se estiver atrás,
   sincroniza/atualiza o branch **antes** de criar o PR — evita PR velho/conflitante.
3. **Periódico em background (opcional, depois):** avisa "mudou" com o projeto aberto.

**Como baratear:**
- `GET /repos/{up}/commits/{branch}?per_page=1` (ou `/git/ref/heads/{branch}`) e
  compara só o **SHA** com o `base_commit` guardado — 1 request, não um `compare`.
- Manda **`If-None-Match: <etag>`**: se nada mudou, vem **304**, que **não conta no
  rate limit** do GitHub. O polling periódico fica praticamente **de graça**.
- Só quando o SHA muda vale chamar `compare/{base}...{branch}` (ahead_by + arquivos).

**Onde roda:** no **backend**, deduplicado por upstream (`owner/repo@branch`) — um
poll para N usuários. O navegador nunca fala com o GitHub.

**E webhook?** Dá tempo real, mas exige configurar no repo (responsabilidade do
mantenedor). A única forma sem trabalho por-repo é um **GitHub App** (webhook por
instalação) — que já está no radar para privado/enterprise. Até lá: **sem webhook**.


## Conflitos — merge por segmento (diferencial)

Em vez de conflito cru de linhas, usamos a **segmentação**:

1. Tentamos o merge no clone; base/mine/theirs saem do merge-base do git.
2. **Merge a três vias por segmento:**
   - só o upstream mudou → pega o deles;
   - só a tradução mudou → mantém a sua;
   - **os dois mudaram** → caixa "O original mudou; use a nova / mantenha a minha /
     mesclar", com a **prévia fiel** para decidir.
3. **Assets binários** (fontes/fundos): "theirs wins" ou aviso.
4. **Último recurso:** se ainda conflitar, sinaliza o projeto e (opcional) comenta
   no PR para o mantenedor decidir — a aceitação continua no GitHub.

O conflito é resolvido **no nível de tradução**, não de git.

## Detalhes que evitam dor

- **Merge em vez de rebase** em branch já publicado (rebase reescreve histórico e
  bagunça review); rebase só antes do primeiro push, se quisermos linearidade.
- **Sincronizar sempre no open** → drift pequeno → maioria dos casos é auto-merge.
- **Lock/claims** (opcional, futuro): "fulano está editando este arquivo" para
  reduzir conflito na origem — sem mover a aprovação para cá.
- **Rate limit:** `compare` é barato; `merge-upstream`/push são raros.

## Push ao cliente — SSE vs WebSocket

Se quisermos **empurrar** o aviso para a tela:

- **SSE** (Server-Sent Events) resolve o caso **one-way** (servidor → cliente) e é
  bem mais simples que WebSocket; WS só se precisássemos de bidirecional.
- **Restrição atual:** o gunicorn roda com worker **`sync`** (`wsgi:app`); SSE/WS
  seguram **um worker por conexão** — poucas abas já esgotam. Push de verdade
  exigiria **gevent/eventlet** (ou um serviço assíncrono separado).
- **Sem push (recomendado no MVP):** o cliente faz um **poll leve no nosso** endpoint
  `/api/.../upstream` (que responde do cache; o poll no GitHub é server-side). Zero
  infra nova.
- Mudanças de tradução são **esporádicas** (minutos/horas); "tempo real" agrega pouco.
- **Edição colaborativa ao vivo** (cursores) é outro patamar: **CRDT/OT** (Yjs/
  Automerge) + camada realtime dedicada — **fora de escopo**; não combina com o
  modelo de contribuir via PR/revisão.

**Recomendação:** lazy (open) + check antes de publicar + poll leve no backend;
**SSE** opcional depois (trocando o worker do gunicorn para gevent); **WS/CRDT** só
se um dia houver edição simultânea em tempo real.

## Encaixe no código (seams)

- **`ProjectExport`** (push/commit/PR/merge-upstream/compare) e complemento no
  **`ProjectSource`** (`ahead_of_upstream`, `sync_upstream`, `conflicts`).
- Provider-agnóstico: GitHub primeiro; GitLab/Gitea depois, mesmo molde.
- Guardar `source_ref`/`base_commit` por projeto (e, quando preciso, o snapshot
  base para o merge a três vias — o git já fornece via `git show <base>:path`).

## Questões em aberto

- Merge vs rebase como padrão do branch de contribuição.
- Notificações (banner no open vs. e-mail/periodicidade).
- Lock/claims por arquivo/segmento (quando entrar).
- Fluxo para repos **privados** (GitHub App) e organizações.
- Como tratar reestruturação grande do arquivo (perda de alinhamento de segmentos).
