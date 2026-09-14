## MODIFIED Requirements

### Requirement: Renderização da tela no canvas

O sistema SHALL desenhar a tela em um canvas de 256×192 pixels, compondo o
background e os glifos do atlas nas posições calculadas, com pixels nítidos ao
ampliar. A prévia SHALL **preencher o painel disponível**, ajustando a escala em
**múltiplos inteiros** (sem frações), alinhada ao **topo** e sobre **fundo neutro**.

#### Scenario: Tela renderizada

- **WHEN** um projeto com tela válida é aberto
- **THEN** o canvas exibe o background e os glifos nas posições calculadas

#### Scenario: Zoom sem suavização

- **WHEN** o usuário altera o zoom da prévia
- **THEN** a imagem é ampliada sem interpolação, mantendo os pixels nítidos

#### Scenario: Escala em múltiplos inteiros

- **WHEN** o painel de prévia é redimensionado
- **THEN** a prévia ajusta a escala para o maior múltiplo inteiro que cabe no painel,
  sem interpolação e sem tamanhos fracionários

#### Scenario: Fundo e alinhamento

- **WHEN** a prévia é exibida
- **THEN** a imagem fica alinhada ao topo, centralizada na horizontal, sobre um fundo
  neutro (cinza do tema)

#### Scenario: Tamanho mínimo do painel

- **WHEN** o usuário encolhe o painel de prévia
- **THEN** ele não fica menor que a largura da imagem em escala 1× mais o padding
