## Why

O app foi desenhado para **desktop** (editor + original + prévia lado a lado, com
divisores arrastáveis). No **celular** esses painéis não cabem e o editor de texto
raw é desconfortável. Queremos um modo mobile focado em **revisão e edição
segmento a segmento**, com a **prévia sempre visível** — referência nos mocks
`mock/mobile-list-preview-edit.html` e `mock/mobile-b-preview-pinned.html`.

## What Changes

- **Header único** em todas as telas: `☰` (abre a gaveta) + marca + avatar. Sem
  editor raw no mobile.
- **Gaveta** (`☰`): seletor de **projeto** + **árvore de diretórios** + import.
- **Tela principal (Segmentos)**: **prévia fixa no topo** (escala em **múltiplos
  inteiros**; 1× no celular, com margens) e **lista read-only** rolando abaixo. Os
  **nomes** e os **diálogos** são **segmentos próprios** (parser por separadores).
- **Interação**: **um toque** seleciona o segmento (atualiza a prévia); **toque
  duplo** abre a **edição**.
- **Tela de edição (foco)**: prévia + o segmento; navegação `«` / `Lista` / `»`
  **abaixo da prévia** (para o teclado não cobrir) e os campos de original/tradução.
- Breakpoint de mobile que desliga os **divisores arrastáveis** e o layout de painéis.

## Capabilities

### New Capabilities
- Nenhuma.

### Modified Capabilities
- `web-ui`: adiciona o **layout em telas pequenas (mobile)** — navegação por gaveta,
  segmentos com prévia fixa, toque simples/duplo e tela de edição dedicada.

## Impact

- **Frontend:** `frontend/index.html`, `frontend/src/main.ts`,
  `frontend/src/ui/layout.css`, `frontend/src/shell/` (gaveta/nav).
- **Reuso:** a prévia em múltiplos inteiros e o mínimo do painel já existem
  (`fitPreview`, `previewMin`) e são reaproveitados.
- **Não alterado:** backend, API, manifesto, segmentação e o layout desktop.

## Não-objetivos

- Gestos avançados (swipe entre arquivos), PWA/offline ou app nativo.
- Edição de texto longa no celular (o editor raw fica no desktop).
- Mudança no formato do manifesto, na segmentação ou no backend.
- Reescrever o layout desktop.
