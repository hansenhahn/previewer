## Context

Ver `proposal.md` — Why. Hoje `frontend/index.html` tem uma top bar simples, uma
sidebar com duas seções e uma toolbar única misturando escopos; `main.ts` tem um
único documento ativo. Já temos tokens (`ui/tokens.css`), layout (`ui/layout.css`)
e o adaptador `UiKit` (`ui/kit*.ts`). Referência de padrão: SageMaker Unified
Studio (topo global, rail de áreas, painel contextual, workspace com contexto e
abas).

## Goals / Non-Goals

**Goals:**
- Separar ações por escopo (Aplicação, Projeto, Texto, Previewer).
- Rail + painel contextual; workspaces com abas de arquivos.
- Preservar edições ao alternar abas; indicador de modificado.
- Manter tokens, adaptador e isolamento da biblioteca.

**Non-Goals:**
- Backend/API/specs; busca/diff; persistir abas; dividir painéis por arrasto.

## Decisions

### 1. Shell em camadas
```
topo (Aplicação)      → nome + tema
rail + painel         → seções (Projetos, Arquivos)
workspace
  cabeçalho do projeto → nome + seletor de tela
  barra do texto       → Salvar, Original (toggle), ● modificado
  abas                 → arquivos abertos
  painéis              → Traduzido | Original | Prévia (zoom no cabeçalho)
```

### 2. Escopos e ações
| Escopo | Região | Ações |
|---|---|---|
| Aplicação | barra superior | tema (claro/escuro/sistema) |
| Projeto | rail + painel + cabeçalho do projeto | importar, lista/troca de projeto, árvore de arquivos, seletor de tela |
| Texto | barra do texto + abas | salvar, alternar original, modificado, abrir/fechar/ativar aba |
| Previewer | cabeçalho da prévia | zoom |

### 3. Estado de documentos (`frontend/src/documents.ts`)
```ts
interface OpenDocument { path: string; content: string; original: string | null; modified: boolean; }
// estado: documents: OpenDocument[], activePath?: string, showOriginal: boolean
```
- `openDocument(path)`: reusa se já aberto; senão busca traduzido+original e
  adiciona; ativa.
- `activateDocument(path)`: guarda o texto atual do editor no documento ativo e
  carrega o alvo (preserva edições não salvas).
- `closeDocument(path)`: remove e ativa um vizinho.
- `markModified`/`markSaved` para o indicador.
`state` (state.ts) passa a referenciar esses dados.

### 4. Módulos do shell e reuso
- `frontend/src/shell/rail.ts` — rail de seções + painel contextual.
- `frontend/src/shell/tabs.ts` — barra de abas (selecionar/fechar/modificado).
- `frontend/src/lists.ts` — continua com as listas de projetos e arquivos.
- `main.ts` — monta as regiões e liga os eventos; sem lógica de biblioteca.
Ícones do rail vêm do adaptador (`kit.icon`), não de `<wa-*>` direto.

### 5. Adaptador ganha `icon`
`UiKit.icon(name, label?)` cria o ícone (Web Awesome `<wa-icon>`); o rail/abas
usam `kit.icon`. Fallback trocaria isso no mesmo arquivo.

### 6. Original como toggle
O painel do original passa a ser opcional (botão "Original" na barra do texto),
mostrando/escondendo a coluna; o layout se ajusta.

## Risks / Trade-offs

- [Complexidade do estado de abas] → módulo `documents.ts` isolado e testável
  (funções puras de abertura/fechamento/ordenação).
- [Vazamento da lib] → ícones via `kit.icon`; regra de `<wa-*>` só no adaptador.
- [Muitos módulos novos] → cada um pequeno e focado; `main.ts` só orquestra.

## Migration Plan

- Trocar o DOM/estado incrementalmente; comportamento preservado; build/testes a
  cada passo. Rollback: voltar `index.html`/`main.ts`/`state.ts`.

## Open Questions

- Persistir abas e layout entre sessões (localStorage) e dividir painéis por
  arrasto — decidível depois.
