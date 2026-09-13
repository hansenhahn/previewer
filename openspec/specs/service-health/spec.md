# service-health Specification

## Purpose

Reportar, por um endpoint de saúde, se o serviço está no ar e se sua dependência
de banco está acessível.

## Requirements

### Requirement: Health check do serviço e do banco

O serviço SHALL expor um endpoint de saúde que verifica a conectividade com o
banco de dados e responde de acordo com o resultado.

#### Scenario: Serviço e banco saudáveis

- **WHEN** o endpoint de saúde é requisitado e o banco responde
- **THEN** o serviço responde com status 200 e um corpo indicando estado saudável

#### Scenario: Banco indisponível

- **WHEN** o endpoint de saúde é requisitado e o banco não responde
- **THEN** o serviço responde com status 503 e um corpo indicando estado degradado

### Requirement: Health check não exige autenticação

O endpoint de saúde SHALL ser acessível sem credenciais.

#### Scenario: Acesso anônimo

- **WHEN** uma requisição anônima chega ao endpoint de saúde
- **THEN** o serviço responde normalmente, sem exigir autenticação
