# project-ingestion Specification

## Purpose

Importar um projeto a partir de um bundle enviado, guardá-lo com segurança e
mantê-lo disponível para uso.

## Requirements

### Requirement: Importação de projeto por bundle

O sistema SHALL aceitar um bundle compactado contendo o manifesto e os arquivos
por ele referenciados, validar o manifesto, armazenar os arquivos do projeto e
registrar seus metadados no catálogo.

#### Scenario: Importação bem-sucedida

- **WHEN** um bundle válido é enviado
- **THEN** o projeto é registrado e passa a aparecer na listagem de projetos

#### Scenario: Bundle sem manifesto

- **WHEN** um bundle sem manifesto válido é enviado
- **THEN** a importação é rejeitada com erro e nenhum projeto é criado

#### Scenario: Nome de projeto já existente

- **WHEN** um projeto é importado com um nome já usado pelo mesmo proprietário
- **THEN** a importação é rejeitada por conflito de nome

### Requirement: Extração segura do bundle

O sistema SHALL rejeitar membros do bundle cujo caminho resolva para fora do
diretório do projeto e SHALL NOT escrever qualquer arquivo fora dele.

#### Scenario: Membro com travessia de caminho

- **WHEN** o bundle contém um membro cujo caminho tenta escapar do diretório do
  projeto
- **THEN** a importação é rejeitada e nenhum arquivo é escrito fora do diretório
  do projeto

### Requirement: Listagem de projetos

O sistema SHALL expor a lista dos projetos disponíveis para o proprietário
atual, com seus metadados básicos.

#### Scenario: Projetos disponíveis

- **WHEN** a listagem de projetos é solicitada
- **THEN** os projetos previamente importados são retornados
