## 1. API: texto original (project-files)

- [x] 1.1 Implementar `GET /api/projects/<id>/files/<path>?variant=original` mapeando o caminho via `manifest.texts` e decodificando com o encoding do projeto; verificar teste do original retornado
- [x] 1.2 Tratar ausência do original (pasta não declarada ou arquivo inexistente) com 404; verificar teste
- [x] 1.3 Garantir que `variant=source` (e o padrão) não mudam; verificar teste existente do traduzido

## 2. Editor somente-leitura

- [x] 2.1 Adicionar `createReadOnlyEditor` em `frontend/src/editor.ts`; verificar `npm run build`

## 3. Painel do original (comparison-view)

- [x] 3.1 Adicionar o painel do original em `frontend/index.html` e o layout de três colunas em `style.css`; verificar `npm run build`
- [x] 3.2 Estender `frontend/src/api.ts` (`readFile` com variante); verificar teste de URL/parametro no vitest
- [x] 3.3 Em `frontend/src/main.ts`, buscar e exibir o original ao abrir o arquivo, com placeholder quando ausente; verificar build e smoke real
- [x] 3.4 Atualizar os dois painéis na troca de arquivo; verificar smoke real

## 4. Verificação final

- [x] 4.1 Rodar a suíte Python (de `backend/`) e confirmar que passa
- [x] 4.2 Rodar `npm test` e `npm run build` no frontend e confirmar que passam
- [x] 4.3 Verificar o Docker end-to-end (build/compose) e o fluxo original × traduzido
- [x] 4.4 Validar a change com `openspec validate comparison-view --strict`
