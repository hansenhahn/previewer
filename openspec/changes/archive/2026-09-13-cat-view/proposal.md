## Why

O previewer já mostra o original ao lado do traduzido, mas em texto corrido. A
ideia é evoluí-lo para um **CAT simplificado**: quebrar os textos em **blocos**
(falas/caixas de diálogo) por expressões regulares de início e fim — como o
previewer legado detectava —, **alinhar** original e traduzido por bloco e exibir
cada par numa **caixa editável** (estilo memoQ). Isso dá contexto real de
tradução: você vê a fala original e a tradução juntas, com status e navegação.

## What Changes

- **Manifesto**: nova seção opcional `segments: { "start": [...], "end": [...] }`
  com os padrões de início e fim de bloco (os `matches`/`tags` seguem para a
  prévia).
- **Segmentação e reconstrução** (domínio puro em Python + espelho no cliente,
  com suíte de conformidade compartilhada): dividir o texto em **segmentos** e
  **separadores**, de forma que reconstruir o texto não editado reproduza o
  original exatamente.
- **Alinhamento por ordem**: casar os segmentos do original com os do traduzido;
  quando a contagem divergir, sinalizar os blocos não pareados.
- **Visão "Segmentos" (CAT)**: caixas alinhadas com original (somente-leitura) e
  traduzido (editável), status (vazio/preenchido) e navegação próximo/anterior.
- **Abstração das tags de separação**: cada caixa mostra/edita apenas o **corpo**
  do bloco (o diálogo); as linhas delimitadoras (início/fim) ficam preservadas
  para a reconstrução fiel.
- **Visão inicial**: abre na visão por segmentos quando o projeto declara
  `segments`.
- **Salvar por reconstrução**: ao salvar, o arquivo traduzido é remontado a
  partir dos segmentos editados + separadores e persistido pelo endpoint atual.
- **Prévia ao vivo**: a prévia passa a usar o texto **reconstruído** (incluindo
  edições não salvas), mantendo o que já existe.

## Capabilities

### New Capabilities
- `text-segmentation`: segmentar o texto por padrões de início/fim, preservar os
  separadores para reconstrução e alinhar os pares por ordem.
- `cat-view`: exibir/editar os segmentos alinhados em caixas, com status,
  navegação, salvamento por reconstrução e prévia refletindo as edições.

### Modified Capabilities
- `project-manifest`: adiciona a configuração de segmentação (requisito novo; os
  existentes não mudam).

## Impact

- **Backend:** `backend/domain/project.py` (campo `segments`),
  `backend/domain/segmentation.py` (novo), testes e fixture de conformidade.
- **Frontend:** `frontend/src/segmentation.ts` (espelho) + `segmentation_cases.json`,
  `frontend/src/shell/cat.ts` (caixas), ajustes em `main.ts`, `state.ts` e CSS.
- **Sem alteração:** API (salvar/ler texto seguem iguais), preview/canvas, layout
  e demais fluxos.
- Referência: comportamento de detecção de bloco do legado (`legacy/editor.py`).

## Não-objetivos

- Memória de tradução, glossário, QA automático, propagação de tradução.
- Exigir marcadores/IDs dentro dos textos (alinhamento por ordem por enquanto).
- Múltiplos arquivos por visão de segmentos, diff linha a linha.
- Alterar o formato de empacotamento (o `segments` é aditivo no manifesto).
