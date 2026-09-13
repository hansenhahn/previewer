# project-catalog Specification

## Purpose

Persistir os metadados dos projetos em Postgres, mantendo a semântica no banco
(e não no layout de pastas) e com o schema evoluindo por migrações.

## Requirements

### Requirement: Persistência de metadados de projeto

O sistema SHALL persistir metadados de projeto — identificador, proprietário,
nome, encoding e marcas de tempo — de forma consultável, mantendo o nome único
por proprietário.

#### Scenario: Criação e leitura de projeto

- **WHEN** um projeto é criado e depois consultado
- **THEN** seus metadados (identificador, proprietário, nome, encoding e marcas
  de tempo) são retornados de forma consistente

#### Scenario: Nome duplicado para o mesmo proprietário

- **WHEN** um projeto é criado com um nome já usado pelo mesmo proprietário
- **THEN** a operação é rejeitada por violar a unicidade

### Requirement: Schema aplicável por migrações

O schema do banco SHALL ser criado e evoluído por migrações versionadas,
aplicáveis a um banco vazio e idempotentes quando reexecutadas.

#### Scenario: Migração em banco vazio

- **WHEN** as migrações são aplicadas a um banco sem schema
- **THEN** as tabelas necessárias passam a existir

#### Scenario: Migrações já aplicadas

- **WHEN** as migrações são reaplicadas a um banco atualizado
- **THEN** nenhuma alteração adicional é feita e a operação conclui sem erro

### Requirement: Proprietário associado desde o início

O sistema SHALL associar cada projeto a um proprietário, mesmo que a
autenticação seja introduzida depois.

#### Scenario: Projeto com proprietário

- **WHEN** um projeto é persistido
- **THEN** ele é associado a um proprietário identificável
