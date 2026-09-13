# Ideia: importar/exportar projeto via GitHub

> Status: **ideia registrada, não agendada**. Não faz parte da Fase 3a
> (`project-api-font-atlas`). Exige autenticação (Fase 4) e um **fork do usuário**.
> Documento para avaliação futura.

## Decisão de direção (2026-09-13)

Direção escolhida: **GitHub-first**. O GitHub será a **fonte da verdade** e
também o **login social**; merge, revisão e aprovação ficam a cargo do GitHub;
por enquanto, **apenas usuários com GitHub** acessam.

Porém, **deferido de propósito**: para validar os fluxos sem adicionar
complexidade agora, a Fase 3a permanece com **ingestão por zip** e identidade
local (stub `owner_id`). A virada GitHub-first entra quando iniciarmos a
**tradução colaborativa**, respeitando os seams (`IdentityProvider`,
`ProjectSource`, `ProjectExport`) para não haver retrabalho.

## Motivação

Hoje a entrada de projeto na Fase 3a é por **upload de um bundle `.zip`**. Para
um produto hospedado com foco em tradução colaborativa, o GitHub é um candidato
natural: versionamento (histórico, diff, rollback), colaboração por
branches/PRs, e a comunidade de tradução já vive em Git.

## Pré-requisito: fork na conta do usuário

O fluxo **não** aceita qualquer repositório público do GitHub. O usuário precisa
**fazer um fork** do projeto original para a própria conta. Nós então:

- autenticamos o usuário (OAuth) e listamos **apenas os repositórios da conta
  dele** (donos ou aos quais ele tem acesso);
- deixamos ele escolher o fork do projeto;
- importamos a partir do fork dele.

Implicações:

- O import via GitHub **exige** conta e autorização do usuário; não existe modo
  anônimo.
- O PR de retorno aponta do **fork do usuário para o repositório upstream**
  (fluxo clássico fork → branch → PR).
- Escopo restrito à conta do usuário: não viramos um "proxy" para clonar
  qualquer repo, o que reduz risco e abuso.
- O `manifest.json` continua obrigatório, e deve existir no fork.

## Modelo proposto: edição local + export sob demanda

- O servidor mantém uma **cópia de trabalho** do projeto no storage (igual ao
  zip). O usuário edita e salva normalmente, sem tocar no Git.
- **Só quando o usuário manda**, o servidor sincroniza: **push direto** (se tiver
  permissão) ou **abertura de PR**.
- Vantagem: separa "editar" de "sincronizar", evita conflito a cada `salvar` e
  mantém a API de arquivos simples.

## O problema: repositório pesado

Não baixar o repositório inteiro. Resolver o "ovo e a galinha" (para saber o que
baixar é preciso ler o manifesto) com esta ordem:

1. Baixar **apenas o `manifest.json`**.
2. O manifesto diz os caminhos de textos, fontes e backgrounds.
3. Baixar **apenas esses caminhos** — idealmente **sob demanda** (buscar o
   arquivo quando o usuário o abre; fonte/background quando o preview precisa).

### Estratégias de download

| Estratégia | Como | Trade-off |
|---|---|---|
| Clone parcial + sparse | `git clone --filter=blob:none --sparse` limitado aos caminhos do manifesto | É repo Git real (commit/push), mas exige `git` e cuidado no commit com sparse |
| Só API do provedor | Lê `manifest.json` + arquivos referenciados pela API; export monta commit/árvore/PR pela API | Não baixa repo, dispensa `git`; acopla ao provedor e consome rate limit |
| Tarball do repo | Baixa o zip do repositório | Simples, mas baixa tudo |

Para o modelo "export sob demanda", a opção **só API** é a mais alinhada: só se
lê alguns arquivos e só se envia de volta o que mudou.

## Fluxo de export (push/PR)

O servidor precisa guardar o **commit base** de cada projeto importado. No
export:

1. Descobrir os arquivos que **mudaram** (diff contra o estado importado).
2. Via API do provedor: criar branch a partir do commit base **no fork do
   usuário**, montar a árvore só com os arquivos alterados, criar o commit e
   abrir o PR do fork para o repositório upstream.
3. Se o upstream mudou no meio-tempo, o merge/PR acusa conflito naturalmente —
   sem reimplementar merge.

## Arquitetura (dois seams, provider-agnostic)

- `ProjectSource` — como o projeto **entra**:
  - `UploadBundleSource` (zip) — primeira implementação, já prevista na 3a.
  - `GitHubSource` (manifest + arquivos via API/clone, a partir dos repositórios
    da conta do usuário autenticado).
- `ProjectExport` — como o projeto **sai**:
  - push direto, abertura de PR, (futuro) exportar zip.

GitHub é a primeira implementação; GitLab, Bitbucket ou servidor Git próprio
caem no mesmo molde. Isso segue o mesmo padrão OCP já usado no domínio
(`FontFormat`, `StorageBackend`).

## Dependências e pré-requisitos

- **Autenticação/OAuth é obrigatória** (Fase 4): precisamos listar os repos da
  conta do usuário e operar em nome dele. Não há leitura anônima no fluxo.
- O usuário precisa ter **forkado** o projeto antes de importar.
- Permissões necessárias: listar repos do usuário e criar branch/commit/PR no
  fork dele.
- `manifest.json` continua sendo o contrato de entrada, dentro do fork.

## Riscos e cuidados

- Rate limit e quotas da API do provedor.
- Acesso restrito aos repos da conta do usuário; ainda assim, dentro do fork o
  repo pode ser grande ou conter LFS, submodules e symlinks — daí o download
  parcial/sob demanda por manifesto.
- Caminhos maliciosos no manifesto → mesma validação anti-zip-slip usada na
  ingestão por zip.
- Acoplamento ao provedor → mitigado pelos seams `ProjectSource`/`ProjectExport`.
- Rastrear o commit base por projeto para o diff/PR fazer sentido.
- Escrita em repo alheio: permissões, autoria do commit, branch/PR e política de
  revisão.

## Questões em aberto

- Editar **direto no repositório** (commit a cada save) ou **cópia com export**
  (recomendado, este documento)?
- Guardar o repo como clone parcial no servidor, ou não persistir repo e usar só
  a API?
- Estratégia de cache/diff dos arquivos editados localmente.
- Qual provedor primeiro e como representar a credencial do usuário.
- Como manter o fork do usuário sincronizado com o upstream (atualizar o fork,
  escolher a branch base e evitar divergência antes de abrir o PR).

## Recomendação

1. Manter a Fase 3a com **zip**, validando o núcleo sem auth.
2. Criar um change separado de **import/export Git** depois da auth (Fase 4),
   começando por leitura via API + export por PR.
3. Quando a 3a for implementada, deixar o **seam** `ProjectSource` no design
   (mesmo que só com o backend zip), para o GitHub não exigir retrabalho.

## Referências

- `MIGRATION.md` — Fase 3, Fase 4 (auth) e §9 (segurança).
- `openspec/changes/project-api-font-atlas/design.md` — design da ingestão por
  zip e do `manifest.json`.
