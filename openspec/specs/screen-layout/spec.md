# screen-layout Specification

## Purpose

Calcular o posicionamento dos glifos do texto na tela 256×192 do NDS a partir de
um texto, uma fonte e uma configuração de tela, cobrindo avanço, quebra, linha
de referência e limites da tela.

## Requirements

### Requirement: Posicionamento e avanço dos glifos

O layout SHALL iniciar cada linha na posição horizontal `ScreenXPos` e desenhar
os glifos em sequência, avançando a posição horizontal pelo avanço do glifo mais
um pixel. Ao concluir a linha, o layout SHALL reposicionar a horizontal em
`ScreenXPos` e avançar a vertical em `ScreenNewLine`.

#### Scenario: Linha de texto posicionada

- **WHEN** uma linha é disposta com a configuração de tela ativa
- **THEN** as posições horizontais seguem a soma dos avanços dos glifos a partir
  de `ScreenXPos`, e a linha seguinte começa em `ScreenYPos + ScreenNewLine`

### Requirement: Limite horizontal da tela

O layout SHALL sinalizar transbordo horizontal quando a posição horizontal
ultrapassar a largura da tela (256 pixels), interrompendo o desenho do restante
da linha.

#### Scenario: Linha longa demais

- **WHEN** a soma dos avanços ultrapassa a largura da tela
- **THEN** o layout sinaliza transbordo horizontal e não posiciona glifos além do
  limite

### Requirement: Limite vertical da tela

O layout SHALL sinalizar transbordo vertical quando a posição vertical
ultrapassar a altura da tela (192 pixels), interrompendo o desenho de novas
linhas.

#### Scenario: Muitas linhas

- **WHEN** o número de linhas excede a altura disponível da tela
- **THEN** o layout sinaliza transbordo vertical e não posiciona novas linhas

### Requirement: Linha de referência (pivô)

O layout SHALL iniciar a disposição a partir da primeira linha, acima ou na
posição atual, que corresponda a um dos padrões de `Matches`. Se nenhuma linha
corresponder, o layout SHALL iniciar do começo do texto.

#### Scenario: Pivô encontrado

- **WHEN** existe uma linha que corresponde a um padrão de `Matches`
- **THEN** a disposição começa na linha imediatamente após o pivô

#### Scenario: Sem pivô

- **WHEN** nenhuma linha corresponde aos padrões de `Matches`
- **THEN** a disposição começa na primeira linha do texto

### Requirement: Remoção de tags antes da medição

O layout SHALL remover todas as ocorrências dos padrões de `Tags` de cada linha
antes de calcular posições, de modo que as tags não ocupem espaço na tela.

#### Scenario: Linha com tag

- **WHEN** uma linha contém uma tag definida em `Tags`
- **THEN** a tag não contribui para o avanço nem aparece na disposição
