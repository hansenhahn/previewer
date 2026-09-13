## Purpose

Disponibilizar a fonte do projeto como um atlas de glifos em imagem e um
conjunto de métricas, prontos para a renderização da tela no cliente.

## ADDED Requirements

### Requirement: Atlas de glifos como imagem

O sistema SHALL decodificar a fonte referenciada pelo projeto e servir uma
imagem (PNG) contendo os glifos posicionados em um atlas.

#### Scenario: Atlas servido

- **WHEN** o atlas de uma fonte válida do projeto é solicitado
- **THEN** uma imagem PNG com dimensões coerentes com os glifos é retornada

### Requirement: Métricas da fonte

O sistema SHALL expor, para a fonte do projeto, a altura de linha e, para cada
codepoint mapeado, o índice do glifo, sua posição no atlas, largura, altura,
avanço e leading.

#### Scenario: Métricas por codepoint

- **WHEN** as métricas da fonte são solicitadas
- **THEN** o resultado inclui a altura de linha e uma entrada por codepoint
  mapeado com posição no atlas e métricas do glifo

### Requirement: Fonte não suportada

O sistema SHALL responder com erro explícito quando a fonte do projeto não puder
ser decodificada, sem quebrar o serviço.

#### Scenario: Conteúdo de fonte desconhecido

- **WHEN** as métricas são solicitadas para um arquivo de fonte em formato não
  suportado
- **THEN** o sistema responde com erro explícito
