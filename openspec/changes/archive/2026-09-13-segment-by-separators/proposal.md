## Why

Alguns projetos (ex.: `playton-3`) têm os textos organizados como uma **sequência de
blocos separados por linhas** (`[..]`, `!***!`), alternando o **nome japonês** e o
**diálogo**. A segmentação por `start`/`end` (pensada para blocos `[header] texto !..!`)
enquadrava o nome em vez do diálogo. Um modo **separador** descreve esse formato
diretamente e cobre outros projetos com a mesma estrutura.

## What Changes

- Novo modo de segmentação por **separadores** (`segments.separators`): as linhas que
  casam são separadores; **cada bloco de linhas consecutivas entre eles é um segmento**.
- O manifesto passa a aceitar `segments.separators` (além de `start`/`end`).
- Domínio (`domain/segmentation.py`) e cliente (`frontend/src/segmentation.ts`) ganham
  `segment_by_separators`/`segmentBySeparators`, mantendo a paridade e a reconstrução fiel.
- A visão por segmentos (`cat-view`) usa o modo separador quando o projeto o declara.

## Capabilities

### New Capabilities
- Nenhuma.

### Modified Capabilities
- `text-segmentation`: adiciona a segmentação por separadores, preservando a reconstrução.
- `project-manifest`: aceita `segments.separators` na configuração de segmentação.

## Impact

- **Backend:** `backend/domain/segmentation.py`, `backend/domain/project.py` (parse/`to_dict`).
- **Frontend:** `frontend/src/segmentation.ts`, `frontend/src/shell/cat.ts`, `frontend/src/api.ts`.
- **Não alterado:** o modo `start`/`end` existente e o comportamento sem segmentação.

## Não-objetivos

- Substituir o modo `start`/`end`.
- Mudanças de UI (tratadas em `resizable-panels`).
