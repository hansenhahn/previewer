## 1. Estado de documentos

- [x] 1.1 Criar `frontend/src/documents.ts` com as operações puras (abrir/ativar/fechar/marcar modificado) e testes vitest
- [x] 1.2 Estender `frontend/src/state.ts` com `documents`, `activePath` e `showOriginal`; verificar build

## 2. Adaptador: ícone

- [x] 2.1 Adicionar `kit.icon(name, label?)` em `ui/kit.ts`/`kit-webawesome.ts`; verificar build e isolamento (nenhum `<wa-*>` fora do adaptador)

## 3. Shell (DOM + CSS)

- [x] 3.1 Reestruturar `frontend/index.html` em topo (Aplicação), rail + painel, workspace (cabeçalho do projeto, barra do texto, abas, painéis); verificar build
- [x] 3.2 Atualizar `frontend/src/ui/layout.css` com as regiões e a hierarquia visual; verificar build

## 4. Rail + painel contextual (Projeto)

- [x] 4.1 Implementar `frontend/src/shell/rail.ts` (seções Projetos/Arquivos + painel contextual); verificar build e smoke
- [x] 4.2 Ligar as listas (`lists.ts`) dentro do painel; verificar abertura/troca de projeto

## 5. Cabeçalho do projeto e barra do texto

- [x] 5.1 Cabeçalho do projeto com nome + seletor de tela; verificar troca de tela refletindo na prévia
- [x] 5.2 Barra do texto com Salvar, toggle "Original" e indicador de modificado; verificar salvar e toggle

## 6. Abas de arquivos

- [x] 6.1 Implementar `frontend/src/shell/tabs.ts` (ativar/fechar/modificado); verificar build
- [x] 6.2 Ligar as abas ao estado de documentos, preservando edições não salvas ao trocar; verificar smoke

## 7. Verificação final

- [x] 7.1 Rodar `npm test` e `npm run build`; verificar que passam
- [x] 7.2 Rodar a suíte Python (de `backend/`) e confirmar que passa
- [x] 7.3 Verificar o Docker end-to-end (build/compose) e o fluxo com abas/toggle
- [x] 7.4 Confirmar isolamento da biblioteca (`grep`) e validar com `openspec validate ui-shell --strict`
