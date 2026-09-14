# access-control Specification

## Purpose

Exigir autenticação para as rotas de API, exceto o health, e escopar as operações
ao usuário autenticado.

## Requirements

### Requirement: Rotas de API exigem autenticação

O sistema SHALL responder com erro de não autorizado às requisições às rotas de
API que não estejam autenticadas, exceto o endpoint de saúde, que permanece
isento.

#### Scenario: Requisição sem sessão

- **WHEN** uma requisição sem sessão autenticada chega a uma rota de API
- **THEN** o sistema responde com erro de não autorizado

#### Scenario: Health isento

- **WHEN** uma requisição anônima chega ao endpoint de saúde
- **THEN** o sistema responde normalmente

### Requirement: Isolamento por proprietário

As operações de API SHALL ser escopadas ao usuário autenticado.

#### Scenario: Recursos do próprio usuário

- **WHEN** um usuário autenticado lista ou acessa recursos
- **THEN** apenas os recursos associados a ele são considerados
