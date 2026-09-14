## Why

Caminhos longos ficavam **cortados** no painel de arquivos (indentação + largura fixa)
e o painel de prévia era **fixo**, dependendo da barra de zoom para crescer. Além disso,
as barras de rolagem destoavam do tema.

## What Changes

- **Barra lateral redimensionável**: divisor arrastável, largura persistida; um
  **puxador circular** (`⠿`) sinaliza o arrasto; duplo-clique reseta.
- **Painel de prévia redimensionável**: a prévia se **ajusta ao painel em múltiplos
  inteiros** de escala (`floor`, sem 1.1×), alinhada ao **topo**, sobre **fundo cinza**;
  mínimo = largura real da imagem + padding (derivada do canvas).
- **Barras de rolagem no tema**: arredondadas e discretas (WebKit + Firefox).
- **Puxadores circulares** nos dois divisores.

## Capabilities

### New Capabilities
- Nenhuma.

### Modified Capabilities
- `web-ui`: painéis redimensionáveis, puxadores e rolagem no tema.
- `screen-preview`: a prévia preenche o painel em múltiplos inteiros, fundo neutro e
  topo alinhado (substitui o zoom por barra).

## Impact

- **Frontend:** `frontend/index.html`, `frontend/src/main.ts`,
  `frontend/src/ui/layout.css`, `frontend/src/ui/tokens.css`.
- **Não alterado:** cálculo de layout, renderização dos glifos e a API.

## Não-objetivos

- Mudar o cálculo de layout/renderização ou o formato do manifesto.
- Zoom fracionário (foi substituído por múltiplos inteiros).
