## 1. Shell e detecção de mobile

- [x] 1.1 Adicionar o breakpoint mobile (media query + `matchMedia`) e desligar divisores/editor raw nesse modo; verificar no navegador
- [x] 1.2 Header único (`☰` + marca + avatar) em todas as telas; verificar

## 2. Gaveta (projeto + árvore)

- [x] 2.1 Implementar a gaveta sobreposta com seletor de projeto, árvore de arquivos e import; fechar ao tocar fora/Esc; verificar
- [x] 2.2 Reaproveitar o componente de árvore atual dentro da gaveta; verificar navegação e arquivo ativo

## 3. Segmentos com prévia fixa

- [x] 3.1 Tela principal mobile: prévia fixa no topo (escala em múltiplos inteiros, reusando `fitPreview`) + lista read-only rolando; verificar
- [x] 3.2 Um toque seleciona o segmento e atualiza a prévia; destacar a seleção; verificar
- [x] 3.3 Nomes e diálogos aparecem como segmentos próprios; verificar com o playton-3

## 4. Edição dedicada

- [x] 4.1 Toque duplo abre a tela de edição do segmento; verificar
- [x] 4.2 Navegação `«` / Lista / `»` abaixo da prévia (sem ser coberta pelo teclado); verificar em dispositivo/emulação
- [x] 4.3 Adaptar a edição para segmento de nome e de diálogo; verificar

## 5. Verificação

- [x] 5.1 Rodar `npm test`/`npm run build` e conferir o layout desktop inalterado
- [x] 5.2 Validar `openspec validate mobile-layout --strict`
