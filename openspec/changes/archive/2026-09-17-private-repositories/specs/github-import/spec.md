## ADDED Requirements

### Requirement: Listar os repositórios da conta (públicos e privados)

O sistema SHALL listar os repositórios **públicos e privados** da conta do usuário usando o
token obtido no login e SHALL permitir atualizar a lista sob demanda, sem descartar erros em
silêncio.

#### Scenario: Lista disponível após o login

- **WHEN** o usuário autenticado consulta os repositórios disponíveis para import
- **THEN** o sistema apresenta os repositórios da conta obtidos no login

#### Scenario: Repositórios privados listados

- **WHEN** a conta do usuário tem repositórios privados
- **THEN** eles também aparecem na lista, identificados como privados

#### Scenario: Atualização sob demanda

- **WHEN** o usuário solicita atualizar a lista
- **THEN** o sistema consulta novamente o provedor e atualiza os repositórios
  exibidos

#### Scenario: Falha de listagem reportada

- **WHEN** a consulta ao provedor falha
- **THEN** o sistema informa o erro, em vez de exibir uma lista vazia sem
  explicação

## MODIFIED Requirements

### Requirement: Validar o manifest do repositório

O sistema SHALL verificar o `manifest.json` da branch padrão de cada repositório listado de
forma **autenticada** (o que inclui repositórios privados) e SHALL indicar quais são
importáveis; ao importar, SHALL validá-lo de novo, recusando o import com erro claro quando o
manifest estiver ausente ou inválido.

#### Scenario: Manifest válido

- **WHEN** o repositório possui um `manifest.json` válido na branch padrão
- **THEN** o sistema prossegue com o import

#### Scenario: Manifest de repositório privado

- **WHEN** o repositório é privado e possui um `manifest.json` válido na branch padrão
- **THEN** o sistema prossegue com o import, usando o token do usuário

#### Scenario: Manifest ausente ou inválido

- **WHEN** o repositório não possui `manifest.json` ou ele é inválido
- **THEN** o sistema recusa o import e informa o motivo, sem criar o projeto

#### Scenario: Repositório importável indicado na lista

- **WHEN** a lista de repositórios é exibida
- **THEN** cada repositório com `manifest.json` válido é indicado como importável
  (marca de sucesso)

#### Scenario: Repositório não importável indicado na lista

- **WHEN** um repositório não tem `manifest.json` válido
- **THEN** ele é indicado como não importável (marca neutra), com o motivo, e não
  pode ser importado

## REMOVED Requirements

### Requirement: Listar os repositórios da conta

### Requirement: Restrição a repositórios públicos
