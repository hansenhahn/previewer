# web-shell Specification

## Purpose

Servir a tela inicial e os arquivos estáticos do serviço web, funcionando como
ponto de entrada único do app no navegador.

## Requirements

### Requirement: Tela inicial servida

O serviço SHALL responder na raiz com uma página HTML que carrega os ativos
estáticos da aplicação, servindo-os pela mesma origem do serviço.

#### Scenario: Requisição à raiz

- **WHEN** o navegador requisita a raiz do serviço
- **THEN** o serviço responde com status 200 e conteúdo HTML

#### Scenario: Ativo estático servido pela mesma origem

- **WHEN** a página inicial referencia um ativo estático do caminho do serviço
- **THEN** o ativo é servido com status 200 e o tipo de conteúdo correspondente
