# comparison-view Specification

## Purpose

Exibir o texto traduzido e o texto original lado a lado, permitindo comparar a
tradução com a fonte enquanto se edita.

## Requirements

### Requirement: Original ao lado do traduzido

O sistema SHALL exibir, para o arquivo selecionado, um painel somente-leitura
com o texto original ao lado do editor do texto traduzido.

#### Scenario: Original exibido

- **WHEN** um arquivo com original correspondente é aberto
- **THEN** o painel do original mostra o texto original e o editor mostra o
  traduzido

#### Scenario: Original ausente

- **WHEN** o arquivo selecionado não tem original correspondente
- **THEN** o painel do original indica a ausência sem quebrar a interface

### Requirement: Sincronização com o arquivo selecionado

O sistema SHALL atualizar os dois painéis ao trocar o arquivo selecionado.

#### Scenario: Troca de arquivo

- **WHEN** outro arquivo é selecionado
- **THEN** o painel do original e o editor passam a mostrar o novo arquivo

### Requirement: Original somente-leitura

O painel do original SHALL ser somente-leitura, enquanto o painel do traduzido
permanece editável e salvável.

#### Scenario: Original não editável

- **WHEN** o usuário tenta editar o painel do original
- **THEN** o conteúdo não é alterado

#### Scenario: Traduzido continua editável

- **WHEN** o usuário edita o painel do traduzido e salva
- **THEN** a alteração é persistida normalmente
