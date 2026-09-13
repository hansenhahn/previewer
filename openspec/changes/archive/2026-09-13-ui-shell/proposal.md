## Why

Temos tema, mas a UI/UX continua ruim porque as ações estão **misturadas**: a
toolbar mistura app (tema), projeto (tela) e texto (salvar), e a sidebar mistura
projetos e arquivos. Falta hierarquia e escopo. Vamos adotar um **shell em
camadas**, inspirado no SageMaker Unified Studio, separando claramente as ações
de **aplicação**, **projeto**, **texto** e **previewer**. Refactor de
apresentação/interação, sem mudar contratos (`skip_specs`).

## What Changes

- **Barra superior (Aplicação):** nome do app + tema (claro/escuro/sistema).
- **Rail + painel contextual (Projeto):** navegação entre seções (Projetos,
  Arquivos) e o conteúdo da seção selecionada (lista/importar, árvore de
  arquivos).
- **Workspace** com:
  - **cabeçalho do projeto** (nome, seletor de tela);
  - **barra do texto** (Salvar, alternar Original, indicador de modificado);
  - **abas de arquivos abertos** (selecionar/fechar, marcador de modificado);
  - painéis **Traduzido | Original | Prévia**, com **zoom no cabeçalho da prévia**.
- **Estado de documentos abertos** no frontend (múltiplos arquivos, ativo,
  modificado), preservando edições não salvas ao trocar de aba.
- **Toggle "Original"** que mostra/esconde o painel do original.

## Capabilities

### New Capabilities
- Nenhuma. É refactor de apresentação/interação: `skip_specs: true`
  (abrir/editar/salvar/preview seguem os mesmos comportamentos).

### Modified Capabilities
- Nenhuma.

## Impact

- **Novo:** `frontend/src/shell/` (rail, abas, painéis) e `frontend/src/documents.ts`
  (estado dos arquivos abertos).
- **Alterado:** `frontend/index.html` (regiões do shell), `frontend/src/main.ts`,
  `frontend/src/state.ts`, `frontend/src/lists.ts`, `frontend/src/ui/layout.css`
  e o adaptador (`ui/kit.ts` ganha `icon`).
- **Sem alteração:** backend/API, domínio, preview/canvas e comportamento.

## Não-objetivos

- Mudar backend, API ou specs.
- Busca, diff de linhas, redimensionamento de painéis por arrasto, persistir
  abas entre sessões.
- Reimplementar editor/preview.
