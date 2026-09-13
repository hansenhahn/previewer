## 1. Setup do frontend

- [x] 1.1 Criar `frontend/package.json` com Vite, TypeScript, CodeMirror 6 e vitest; verificar `npm install` concluindo
- [x] 1.2 Criar `tsconfig.json`, `vite.config.ts` (base `/static/dist/`, outDir `../app/static/dist`, proxy `/api`) e `index.html`; verificar `npm run build` gerando `app/static/dist`
- [x] 1.3 Atualizar `.gitignore` e `.dockerignore` com `node_modules/` e `frontend/dist/`; verificar que não aparecem no `git status`

## 2. Endpoint de ativos (project-assets)

- [x] 2.1 Implementar `GET /api/projects/<id>/backgrounds/<name>` servindo os bytes com `Content-Type` de imagem; verificar teste 200 e `image/png`
- [x] 2.2 Tratar ativo inexistente; verificar teste 404
- [x] 2.3 Rejeitar nome com travessia de caminho; verificar teste que não toca fora do projeto
- [x] 2.4 Expor `default_advance` nas métricas do atlas; verificar teste do atlas com o valor

## 3. Layout no cliente (screen-preview)

- [x] 3.1 Criar `frontend/src/layout.ts` espelhando `domain/layout.py` (avanço, quebra, pivô, tags, transbordo, `default_advance`); verificar `npm run build`
- [x] 3.2 Criar `frontend/src/layout_cases.json` com os casos compartilhados (básico, tags, pivô, não mapeado, transbordo H/V)
- [x] 3.3 Teste de conformidade no pytest rodando `domain.layout` sobre os casos; verificar `.venv/bin/python -m pytest -k conformidade`
- [x] 3.4 Teste de conformidade no vitest rodando `layout.ts` sobre os mesmos casos; verificar `npm test`
- [x] 3.5 Remover o endpoint de layout do servidor e seus testes; verificar que `POST /screens/<name>/layout` responde 404 e a suíte passa

## 4. Interface (web-ui)

- [x] 4.1 Implementar listagem e importação de projetos (upload `.zip`); verificado por build + upload real
- [x] 4.2 Implementar editor CodeMirror 6 e salvamento (`PUT`); verificado por build + persistência real
- [x] 4.3 Exibir erros da API na interface; verificado com bundle inválido

## 5. Prévia no canvas (screen-preview)

- [x] 5.1 Criar `frontend/src/render.ts` (placements + atlas → comandos de desenho); verificar teste vitest
- [x] 5.2 `preview.ts` calcula o layout localmente e desenha background + glifos; verificar `npm run build` e smoke real
- [x] 5.3 Zoom com `image-rendering: pixelated` e atualização imediata (redesenho no próximo frame, sem debounce); verificar smoke real
- [x] 5.4 Seleção de tela da prévia; verificar smoke real de troca de tela

## 6. Integração e Docker

- [x] 6.1 Servir `app/static/dist` no Flask e devolver o `index.html` na rota `/`; verificado com `GET /`
- [x] 6.2 Adicionar estágio Node no `Dockerfile`; verificado com `docker build`
- [x] 6.3 Compose de ponta a ponta; verificado `/` (SPA), `/healthz` e upload reais

## 7. Verificação final

- [x] 7.1 Rodar a suíte Python (`.venv/bin/python -m pytest`) e confirmar que passa
- [x] 7.2 Rodar os testes do frontend (`npm test`) e o build (`npm run build`); confirmar que passam
- [x] 7.3 Confirmar que o novo código não importa GTK/cairo; verificar com `git grep -n "gtk\|cairo" -- app/ infra/ domain/ frontend/`
- [x] 7.4 Validar a change com `openspec validate frontend-preview-editor --strict`
