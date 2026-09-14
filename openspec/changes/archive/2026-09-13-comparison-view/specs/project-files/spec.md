## ADDED Requirements

### Requirement: Ler o texto original correspondente

O sistema SHALL permitir ler o texto original correspondente a um arquivo de
texto do projeto, decodificando-o com o encoding do projeto, quando o manifesto
declarar a pasta de originais.

#### Scenario: Original disponível

- **WHEN** o texto original de um arquivo do projeto é solicitado e existe
- **THEN** o conteúdo original é retornado decodificado pelo encoding do projeto

#### Scenario: Original ausente

- **WHEN** o original correspondente não existe ou o projeto não declara pasta
  de originais
- **THEN** o sistema responde com erro de não encontrado
