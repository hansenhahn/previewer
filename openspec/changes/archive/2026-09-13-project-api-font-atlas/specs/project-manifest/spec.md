## Purpose

Definir e validar o manifesto que descreve um projeto da plataforma, servindo de
contrato de entrada para importação e de fonte de configuração do preview.

## ADDED Requirements

### Requirement: Manifesto de projeto

O sistema SHALL ler um manifesto que descreve o projeto, incluindo o formato e a
versão, o nome, o encoding dos textos, as pastas de texto e de original, as
fontes, os backgrounds, as telas e os padrões de tags e matches.

#### Scenario: Manifesto válido

- **WHEN** um manifesto com formato e versão reconhecidos e campos obrigatórios
  preenchidos é lido
- **THEN** o manifesto é aceito e seus valores ficam disponíveis para a
  importação

### Requirement: Rejeição de manifesto inválido

O sistema SHALL rejeitar com erro explícito um manifesto ausente, com versão não
suportada, ou com campos obrigatórios faltando ou inválidos, sem prosseguir com
a importação.

#### Scenario: Manifesto ausente

- **WHEN** um bundle não contém o manifesto
- **THEN** a leitura é rejeitada com erro explícito

#### Scenario: Versão não suportada

- **WHEN** o manifesto declara uma versão de formato não suportada
- **THEN** a leitura é rejeitada com erro explícito

#### Scenario: Campo obrigatório inválido

- **WHEN** o manifesto omite ou traz um valor inválido para um campo obrigatório
- **THEN** a leitura é rejeitada com erro explícito indicando o campo
