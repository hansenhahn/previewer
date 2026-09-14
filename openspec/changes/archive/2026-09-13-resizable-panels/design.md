## Context

Os painéis eram de largura fixa (`#docs-sidebar: 240px`, prévia dimensionada pela
barra de zoom). Caminhos longos cortavam; o zoom fracionário borrava os pixels.
Ver `proposal.md`.

## Goals / Non-Goals

**Goals:** painéis redimensionáveis com puxador e persistência; prévia ajustada ao
painel em múltiplos inteiros, topo e fundo neutro; rolagem no tema.

**Non-Goals:** mudar layout/renderização ou o manifesto; zoom fracionário.

## Decisions

### 1. Divisores arrastáveis
Divisores (`#sidebar-resizer`, `#preview-resizer`) com `pointer` events +
`setPointerCapture`; a largura é exposta por variáveis CSS
(`--pv-sidebar-width`, `--pv-preview-width`) e **persistida** em `localStorage`.
`dblclick` remove a variável (volta ao padrão).

### 2. Puxador
O divisor mostra um puxador circular via `::after` com o glifo **`⠿`** (grip de
arrastar), `pointer-events: none` para não interferir no arrasto; realce no `hover`.

### 3. Prévia ajustada ao painel (múltiplos inteiros)
`fitPreview()` calcula
`scale = max(1, min(floor(largura/imagem_w), floor(altura/imagem_h)))` a partir das
dimensões do **canvas** (não de constantes) e chama `preview.setZoom(scale)`. Um
`ResizeObserver` no palco da prévia reajusta ao arrastar. A imagem usa
`align-items: flex-start` (topo) e fundo `--pv-color-surface-muted`.

### 4. Mínimo do painel de prévia
`previewMin()` = largura do canvas + padding horizontal do `.preview-body`; o CSS usa
`min-width: calc(var(--pv-preview-image-width, 256px) + 2 * var(--pv-space-m))`.

### 5. Rolagem no tema
Tokens `--pv-color-scroll-thumb`/`-hover` (claro/escuro); `scrollbar-width: thin` +
`::-webkit-scrollbar` com polegar arredondado e trilho transparente.

## Risks / Trade-offs

- [Feedback de tamanho ao ajustar a prévia] → `ResizeObserver` no palco com
  `overflow: hidden`; o tamanho do canvas não altera o palco.
- [`localStorage` indisponível] → larguras ficam em memória; erros silenciados.

## Migration Plan

- Aditivo e sem migração de dados; larguras antigas voltam ao padrão.

## Open Questions

- Nenhuma.
