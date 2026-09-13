## Purpose

Disponibilizar os ativos binários referenciados pelo projeto (como backgrounds)
para que o cliente possa montar o preview.

## ADDED Requirements

### Requirement: Ativo binário do projeto servido

O sistema SHALL servir os bytes de um ativo binário referenciado pelo manifesto
do projeto, identificado pelo seu nome, com o tipo de conteúdo correspondente.

#### Scenario: Background servido

- **WHEN** um background referenciado pelo manifesto é solicitado pelo nome
- **THEN** seus bytes são retornados com o tipo de conteúdo de imagem

#### Scenario: Ativo inexistente

- **WHEN** um ativo não referenciado pelo manifesto é solicitado
- **THEN** o sistema responde com erro de não encontrado

#### Scenario: Caminho fora do projeto

- **WHEN** a solicitação tenta um caminho que escapa do diretório do projeto
- **THEN** a operação é rejeitada com erro, sem tocar em arquivos fora do projeto
