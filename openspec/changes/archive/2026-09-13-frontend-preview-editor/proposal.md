## Why

A Fase 3a entregou a API (projetos, arquivos, atlas), mas nada disso é visível:
o serviço só tem uma página de placeholder. Esta é a **Fase 3b do MIGRATION.md**
(metade frontend da Fase 3): dar ao usuário uma interface para importar/abrir um
projeto, editar os textos e ver o preview da tela do NDS. Sem ela, o núcleo
funcional existe mas não é utilizável.

## What Changes

- Criar o frontend com **Vite + TypeScript + CodeMirror 6** (sem framework de
  UI), consumindo a API `/api` da 3a.
- **Fluxo completo mínimo** na UI: importar projeto (upload `.zip`), listar,
  abrir, navegar pelos arquivos de texto e editar/salvar no CodeMirror.
- **Preview da tela 256×192** em `<canvas>`, com fundo + glifos, zoom com
  `image-rendering: pixelated` e atualização conforme a edição.
- **Layout no cliente**: a disposição da tela (avanço, quebra, pivô por
  `Matches`, remoção de `Tags`, limites 256×192) é calculada no navegador a
  partir do atlas e da configuração da tela, espelhando `domain.layout` e
  verificada por uma suíte de conformidade compartilhada. O preview é efêmero:
  nada de round-trip por edição.
- **Servir ativos binários do projeto** (backgrounds) por um endpoint dedicado,
  necessário para o canvas (a 3a só expôs o atlas da fonte).
- **Build do frontend no container**: estágio Node no `Dockerfile` gerando os
  estáticos servidos pelo Flask na mesma origem.

## Capabilities

### New Capabilities
- `project-assets`: servir os ativos binários do projeto (backgrounds) por nome.
- `screen-preview`: cálculo do layout no cliente e renderização da tela 256×192
  no canvas, com zoom, atualização pela edição e equivalência com `domain.layout`.
- `web-ui`: aplicação de página única com importação/listagem de projetos,
  navegação de arquivos e editor com salvamento.

### Modified Capabilities
- Nenhuma. `web-shell` continua satisfeita (a raiz segue respondendo HTML e
  ativos pela mesma origem); o roteamento da SPA é por hash, sem exigir fallback
  no servidor.

## Impact

- **Novo:** `frontend/` (Vite/TS, `package.json`, `tsconfig`, `vite.config`,
  `src/`), assets construídos servidos pelo Flask, testes de frontend.
- **Alterado:** `app/api.py` (endpoint de ativos), `app/__init__.py` (servir o
  build), `infra/atlas.py` (expor `default_advance` nas métricas), `Dockerfile`
  (estágio Node), `.gitignore` (`node_modules/`, `frontend/dist/`).
- **Não alterado:** `domain/` (apenas consumido via endpoint), o app legado e as
  rotas existentes.
- **Dependências novas:** toolchain Node (Vite, TypeScript, CodeMirror 6), apenas
  em build; nenhuma dependência Python nova.
- **Não-objetivos:** ver seção própria.
- Referência: `MIGRATION.md` §7 (Fase 3) e §8 (build do front em stage Node).

## Não-objetivos

- Autenticação, GitHub, multiusuário — Fase 4 e a ideia registrada em
  `docs/ideas/github-import-export.md`.
- Renderização de imagem no servidor (o canvas é no cliente).
- Múltiplas telas por projeto na UI (usa a tela selecionada do manifesto, com
  opção básica de troca), i18n, temas, mobile, acessibilidade avançada.
- Edição do manifesto, diff/undo global, tempo real/colaboração.
