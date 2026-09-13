# project-storage Specification

## Purpose

Definir como projetos e seus arquivos são armazenados por trás de um contrato
abstrato, com uma implementação em filesystem isolada sob uma raiz configurável.

## Requirements

### Requirement: Operações de armazenamento de projeto

O sistema SHALL expor operações para criar e listar projetos, listar os arquivos
de um projeto e para ler, escrever e remover arquivos dentro de um projeto,
identificando cada projeto de forma estável.

#### Scenario: Escrita e leitura de arquivo

- **WHEN** um arquivo é escrito em um projeto e em seguida lido
- **THEN** o conteúdo lido é idêntico ao conteúdo escrito

#### Scenario: Listagem de projetos criados

- **WHEN** projetos são criados e a listagem é solicitada
- **THEN** os identificadores dos projetos criados são retornados

#### Scenario: Listagem de arquivos de um projeto

- **WHEN** arquivos são escritos em um projeto e a listagem de arquivos é
  solicitada
- **THEN** os caminhos relativos dos arquivos existentes são retornados

### Requirement: Isolamento sob a raiz de armazenamento

Toda operação SHALL resolver caminhos dentro da raiz de armazenamento
configurada e SHALL rejeitar qualquer caminho que tente escapar dessa raiz.

#### Scenario: Caminho com travessia rejeitado

- **WHEN** uma operação recebe um caminho relativo que resolve para fora da raiz
- **THEN** a operação é rejeitada com erro, sem tocar em arquivos fora da raiz

### Requirement: Backend de armazenamento substituível

O restante do sistema SHALL depender apenas do contrato de armazenamento, de
modo que uma implementação alternativa possa substituir a de filesystem sem
alterar os consumidores.

#### Scenario: Consumidor independente da implementação

- **WHEN** um consumidor usa o contrato de armazenamento com a implementação de
  filesystem
- **THEN** ele opera sem conhecer detalhes de filesystem nem o diretório concreto
