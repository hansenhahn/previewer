# screen-preview Specification

## Purpose

Renderizar no navegador a tela do NDS em 256×192, calculando a disposição dos
glifos no próprio cliente a partir da fonte (atlas) e da configuração da tela,
com zoom e atualização imediata pela edição.

## Requirements

### Requirement: Layout calculado no cliente

O sistema SHALL calcular no navegador a disposição dos glifos a partir do texto,
dos avanços e do leading do atlas e da configuração da tela (posição inicial,
avanço de linha, padrões de `Matches` e `Tags`), sem depender do servidor para
cada edição, sinalizando transbordo horizontal e vertical.

#### Scenario: Disposição calculada localmente

- **WHEN** o texto é exibido na prévia
- **THEN** as posições dos glifos são calculadas no cliente a partir dos avanços
  do atlas e da configuração da tela

#### Scenario: Sem round-trip por edição

- **WHEN** o texto do editor muda
- **THEN** a nova disposição é calculada sem uma nova requisição de layout

#### Scenario: Remoção de tags e linha-pivô

- **WHEN** o texto contém padrões de `Tags` e/ou uma linha correspondente a
  `Matches`
- **THEN** as tags não ocupam espaço e a disposição parte da linha-pivô

#### Scenario: Transbordo sinalizado

- **WHEN** o texto ultrapassa a largura ou a altura da tela
- **THEN** os sinalizadores de transbordo horizontal e/ou vertical são
  observáveis na prévia

### Requirement: Renderização da tela no canvas

O sistema SHALL desenhar a tela em um canvas de 256×192 pixels, compondo o
background e os glifos do atlas nas posições calculadas, com pixels nítidos ao
ampliar.

#### Scenario: Tela renderizada

- **WHEN** um projeto com tela válida é aberto
- **THEN** o canvas exibe o background e os glifos nas posições calculadas

#### Scenario: Zoom sem suavização

- **WHEN** o usuário altera o zoom da prévia
- **THEN** a imagem é ampliada sem interpolação, mantendo os pixels nítidos

### Requirement: Seleção de tela

O sistema SHALL permitir escolher qual tela do projeto a prévia exibe, quando
houver mais de uma.

#### Scenario: Troca de tela

- **WHEN** outra tela do projeto é selecionada
- **THEN** a prévia passa a usar a configuração dessa tela

### Requirement: Equivalência com o layout do domínio

A disposição calculada no cliente SHALL seguir os mesmos casos do layout do
domínio, verificados por uma suíte de conformidade compartilhada.

#### Scenario: Casos de conformidade

- **WHEN** os casos de layout compartilhados são executados no cliente e no
  domínio
- **THEN** ambos produzem as mesmas posições e os mesmos sinalizadores de
  transbordo
