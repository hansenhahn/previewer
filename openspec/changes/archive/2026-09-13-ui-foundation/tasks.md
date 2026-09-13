## 1. Tokens e tema

- [x] 1.1 Criar `frontend/src/ui/tokens.css` com `--pv-*` (cores, espaço, raio, tipografia, sombra) para claro/escuro; verificar no navegador
- [x] 1.2 Adicionar `frontend/src/ui/layout.css` (flex/grid, classes `pv-*`) e ligar em `index.html`; verificar build

## 2. Dependência e tema da biblioteca

- [x] 2.1 Adicionar `@awesome.me/webawesome` (versão estável confirmada e fixada) ao `package.json`; verificar `npm install`
- [x] 2.2 Criar `frontend/src/ui/theme-webawesome.css` mapeando tokens da lib para `--pv-*`; verificar o tema aplicado

## 3. Adaptador UiKit

- [x] 3.1 Criar `frontend/src/ui/kit.ts` (tipos/interfaces: `button`, `select`, `toast`, `callout`); verificar `npm run build`
- [x] 3.2 Implementar `frontend/src/ui/kit-webawesome.ts` e `frontend/src/ui/index.ts` (exporta a implementação ativa); verificar `npm run build`
- [x] 3.3 Adicionar teste vitest dos helpers puros do adaptador; verificar `npm test`

## 4. Migrar a UI para tokens + adaptador

- [x] 4.1 Refatorar `index.html` para esqueleto sem classes da lib; verificar build
- [x] 4.2 Migrar `main.ts`/`ui.ts` (botões, select de tela, lista de arquivos, upload, callout de erro, toast de "salvo") para o adaptador; verificar build
- [x] 4.3 Garantir que nenhum `<wa-*>`/classe da lib aparece fora de `frontend/src/ui/kit-*.ts`/`theme-*.css`; verificar com `grep`

## 5. Verificação final

- [x] 5.1 Rodar `npm test` e `npm run build`; verificar que passam
- [x] 5.2 Rodar a suíte Python (de `backend/`) e confirmar que passa
- [x] 5.3 Verificar o Docker end-to-end (build/compose) e o visual/interações principais
- [x] 5.4 Validar a change com `openspec validate ui-foundation --strict`
