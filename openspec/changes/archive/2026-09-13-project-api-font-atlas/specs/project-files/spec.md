## Purpose

Permitir navegar e editar os textos de um projeto pela API, respeitando o
encoding declarado no manifesto.

## ADDED Requirements

### Requirement: Listar arquivos de texto do projeto

O sistema SHALL expor a lista dos arquivos de texto do projeto como caminhos
relativos.

#### Scenario: Arquivos disponíveis

- **WHEN** a listagem de arquivos de um projeto é solicitada
- **THEN** os caminhos relativos dos arquivos de texto do projeto são retornados

### Requirement: Ler arquivo de texto do projeto

O sistema SHALL ler o conteúdo de um arquivo de texto do projeto decodificando-o
com o encoding do projeto.

#### Scenario: Leitura com o encoding do projeto

- **WHEN** um arquivo de texto do projeto é lido
- **THEN** o conteúdo é retornado como texto decodificado pelo encoding do
  projeto

#### Scenario: Arquivo inexistente

- **WHEN** um caminho que não existe é lido
- **THEN** o sistema responde com erro de não encontrado

### Requirement: Salvar arquivo de texto do projeto

O sistema SHALL gravar o conteúdo de um arquivo de texto do projeto codificando-o
com o encoding do projeto, preservando o round-trip.

#### Scenario: Salvar e reler

- **WHEN** um texto é salvo em um arquivo do projeto e em seguida lido
- **THEN** o texto retornado é idêntico ao texto salvo
