## Context

Ver `proposal.md` — Why. O legado (`legacy/editor.ui`) mostrava original e
traduzido num `GtkHPaned`; hoje o web app tem um único editor (traduzido) e o
preview. O `manifest.json` já carrega `texts.source` e `texts.original`
(`domain/project.py`). A leitura de arquivos mora em `web/api.py` + `domain/text.py`
+ `infra/storage.py`.

## Goals / Non-Goals

**Goals:**
- Ler o texto original correspondente pela API.
- Painel somente-leitura do original ao lado do editor, sincronizado com a
  seleção de arquivo.
- Manter o traduzido editável/salvável e o preview funcionando.

**Non-Goals:**
- Diff/destaque, sincronização de rolagem, editar o original.
- Redimensionamento por arrasto, responsividade mobile, outras melhorias de UX.
- Mudar `manifest.json` ou o modelo de dados.

## Decisions

### 1. API: variante do arquivo de texto
`GET /api/projects/<id>/files/<path>?variant=source|original` (padrão `source`).
Para `variant=original`:
- exige `manifest.texts.original`; senão `404`;
- monta o caminho trocando o prefixo `texts.source` por `texts.original`,
  mantendo o restante relativo do arquivo;
- lê via `StorageBackend.read_file` (isolamento já garantido) e decodifica com
  `decode_text` usando o encoding do projeto;
- arquivo ausente → `404`.

Alternativa: endpoint dedicado `/original/<path>` — rejeitada por duplicar a
rota; o parâmetro deixa explícito que é o mesmo arquivo em outra variante.
O `GET /files` (listagem) continua listando apenas os traduzidos.

### 2. Editor somente-leitura para o original
`frontend/src/editor.ts` ganha `createReadOnlyEditor(parent)` (mesmo CodeMirror,
com `EditorState.readOnly` e `EditorView.editable.of(false)`), evitando um
componente de texto paralelo e mantendo a mesma aparência.

### 3. Layout em três painéis
`.panes` passa a ter: **traduzido** (editável), **original** (somente-leitura) e
**prévia** (canvas). Flexbox em linha; a prévia mantém largura fixa. Sem
divisórias arrastáveis nesta entrega.

### 4. Sincronização na abertura de arquivo
`openFile(path)` busca o traduzido (`variant=source`) e, em paralelo, o original
(`variant=original`); se o original responder `404`, o painel mostra um
placeholder ("sem original") em vez de erro. A troca de arquivo atualiza ambos os
painéis e o preview.

## Risks / Trade-offs

- [Três painéis apertados em telas pequenas] → larguras flexíveis e a prévia com
  largura fixa; redimensionamento fica para depois.
- [Mapeamento do caminho do original] → assume-se espelho de nomes (como no
  legado); ausência vira placeholder/404, sem quebrar.
- [Regressão na leitura do traduzido] → teste garantindo que `variant=source`
  (e o padrão sem parâmetro) continuam iguais.

## Migration Plan

- Aditivo: parâmetro opcional na leitura e um painel novo; nada muda para quem
  não usa o original.
- Rollback: remover o parâmetro e o painel do original.

## Open Questions

- Sincronizar a rolagem dos dois painéis e/ou realçar diferenças — avaliar depois,
  sem afetar specs ou abordagem.
