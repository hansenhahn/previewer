## 1. Divisores e puxadores

- [x] 1.1 Adicionar os divisores (`#sidebar-resizer`, `#preview-resizer`) e variáveis de largura no HTML/CSS; verificar build
- [x] 1.2 Implementar arrasto com `pointer` events, limites e persistência em `localStorage` (duplo-clique reseta); verificar no navegador
- [x] 1.3 Puxador circular `⠿` nos dois divisores; verificar render

## 2. Prévia ajustada ao painel

- [x] 2.1 `fitPreview()` com escala em múltiplos inteiros a partir das dimensões do canvas + `ResizeObserver`; verificar
- [x] 2.2 Fundo cinza e alinhamento ao topo; verificar
- [x] 2.3 Mínimo do painel = largura da imagem + padding (JS + CSS); verificar
- [x] 2.4 Remover a barra de zoom; verificar build

## 3. Rolagem e verificação

- [x] 3.1 Tokens de rolagem e estilos WebKit/Firefox; verificar nos dois temas
- [x] 3.2 Rodar `npm test`/`build` e validar `openspec validate resizable-panels --strict`
