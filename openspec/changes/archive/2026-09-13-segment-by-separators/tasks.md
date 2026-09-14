## 1. Domínio

- [x] 1.1 Adicionar `separators` a `Segments` e ler/escrever em `parse_manifest`/`to_dict`; verificar `test_manifest.py`
- [x] 1.2 Implementar `segment_by_separators` em `domain/segmentation.py`; verificar `test_segmentation.py`

## 2. Cliente

- [x] 2.1 Adicionar `separators` ao tipo `Manifest.segments` em `api.ts`; verificar build
- [x] 2.2 Implementar `segmentBySeparators` e usar no `cat.ts` quando houver separadores; verificar `segmentation.test.ts`
- [x] 2.3 Passar os separadores em `main.ts` (`loadCat`); verificar `npm test`/`build`

## 3. Projeto playton-3 e verificação

- [x] 3.1 Usar `segments.separators` no `manifest.json` do `playton-3` (local + repo via PR)
- [x] 3.2 Rodar suítes e validar `openspec validate segment-by-separators --strict`
