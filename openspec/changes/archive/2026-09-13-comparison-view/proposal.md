## Why

O previewer original exibia o **texto traduzido e o original lado a lado** para
comparação (no legado, `textview1` traduzido e `textview2` original em um
`GtkHPaned`). O web app atual só mostra o traduzido. O dado já existe
(`manifest.texts.source` e `manifest.texts.original`), mas não é exposto nem
exibido — sem isso, traduzir perde a referência visual do texto de origem.

## What Changes

- **API**: permitir ler o **texto original** correspondente a um arquivo de
  texto do projeto (além do traduzido), decodificado com o encoding do projeto.
- **Frontend**: adicionar um **painel somente-leitura com o original** ao lado do
  editor do traduzido, sincronizado com o arquivo selecionado.
- O painel do traduzido continua editável e salvável; o original é apenas
  leitura.

## Capabilities

### New Capabilities
- `comparison-view`: exibição lado a lado do original (somente-leitura) e do
  traduzido (editável), sincronizada com o arquivo selecionado.

### Modified Capabilities
- `project-files`: adiciona a leitura do **texto original** correspondente
  (requisito novo; os existentes não mudam).

## Impact

- **Backend:** `backend/web/api.py` (variante do arquivo de leitura),
  `backend/infra/storage.py` (já cobre leitura; sem mudança) e testes.
- **Frontend:** `frontend/src/main.ts`, `frontend/src/ui.ts`, novo painel
  original (reusa CodeMirror em modo somente-leitura) e `style.css`.
- **Sem alteração:** modelo de dados, `manifest.json`, escrita/salvamento e o
  preview.
- Referência: comportamento do legado (`legacy/editor.ui`, `legacy/editor.py`).

## Não-objetivos

- Diff linha a linha, destaque de diferenças ou sincronização de rolagem.
- Editar o texto original.
- Outras melhorias de UX (busca/pulo de linha, indicadores de transbordo,
  redimensionamento por arrasto) — ficam para changes seguintes.
