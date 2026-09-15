## Context

Hoje o layout é de desktop: `.docs-body` com a árvore fixa + `.panes` (editor,
original, prévia) e **divisores arrastáveis** (`#sidebar-resizer`,
`#preview-resizer`), com prévia em **múltiplos inteiros** (`fitPreview`,
`previewMin`) e lista de segmentos (`cat-view`). Referência de desenho:
`mock/mobile-list-preview-edit.html` e `mock/mobile-b-preview-pinned.html`.

## Goals / Non-Goals

**Goals:** experiência mobile de revisão/edição por segmento; prévia sempre
visível; gaveta com projeto + árvore; sem editor raw nem divisores no celular.

**Non-Goals:** mexer no backend/API/manifesto/segmentação; reescrever o desktop;
gestos avançados ou PWA.

## Decisions

### 1. Detecção de "mobile" por breakpoint
Usar **CSS media query** (ex.: `max-width: 640px`) e, quando precisar de lógica, um
`matchMedia` — **sem** sniffing de user-agent. O layout desktop permanece intacto
acima do breakpoint.

### 2. Gaveta (drawer)
O `☰` abre uma **gaveta** sobreposta com: seletor de **projeto**, **árvore de
arquivos** (componente existente) e a ação **Importar do GitHub**. Fecha ao tocar
fora/Esc. Reaproveita o `tree`/menus atuais; só muda o contêiner.

### 3. Tela principal: prévia fixa + lista
A prévia fica **presa no topo** (reusa `fitPreview`/`previewMin` com escala em
múltiplos inteiros — 1× no celular) e a **lista de segmentos** rola abaixo. A lista
é **read-only**; nomes e diálogos já são segmentos próprios (parser por separadores).
Um toque **seleciona** (e atualiza a prévia); a seleção é destacada.

### 4. Toque simples vs. toque duplo
`click` → seleciona; `dblclick` (ou dois toques dentro de ~300 ms) → abre a edição.
Mostrar a dica "1 toque seleciona · 2 toques para editar". Evitar conflito com o
scroll (não usar `touchstart` que impeça o scroll).

### 5. Tela de edição dedicada
Componente focado com a **prévia** e **apenas o segmento** (original + tradução;
para segmento de nome, só o texto). Navegação `«` / **Lista** / `»` numa faixa
**abaixo da prévia**, garantindo visibilidade com o teclado aberto.

### 6. Ocultar editor raw e divisores
No breakpoint mobile: esconder o painel do editor raw (CodeMirror) e desligar os
divisores arrastáveis; a navegação passa a ser a gaveta + a lista de segmentos.

### 7. Reuso
Prévia, árvore, modal de import e tokens do tema são reaproveitados; o trabalho é
principalmente de **layout/shell** no frontend.

## Risks / Trade-offs

- [Toque duplo x zoom/scroll do sistema] → usar `click`/`dblclick` (não
  `preventDefault` no toque), com dica visível.
- [Teclado cobrindo ações] → navegação acima da prévia; campo de texto no fim.
- [Divergência desktop x mobile] → mudanças isoladas por media query; desktop
  permanece o mesmo.

## Migration Plan

- Sem migração de dados. Desktop inalterado; mobile ativado por breakpoint.
- Rollback: remover as regras de media query e o shell mobile.

## Open Questions

- Breakpoint exato (640px?) e o que fazer em **tablet** (layout desktop em telas
  médias?).
- Toque duplo nativo (`dblclick`) vs. detecção manual de dois toques.
- Persistir a preferência desktop/mobile ou seguir só o tamanho da tela.
