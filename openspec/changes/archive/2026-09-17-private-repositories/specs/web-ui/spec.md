## ADDED Requirements

### Requirement: Indicar repositórios privados na lista de import

O sistema SHALL indicar, na lista de repositórios para import, quais são **privados**, com um
**ícone discreto** (cadeado) ao lado do nome e rótulo acessível, sem alterar as demais
informações (branch, importável).

#### Scenario: Repositório privado indicado

- **WHEN** a lista de import é exibida e um repositório é privado
- **THEN** ele aparece com a marca de privado (cadeado) ao lado do nome

#### Scenario: Repositório público sem marca

- **WHEN** a lista de import é exibida e um repositório é público
- **THEN** ele aparece sem a marca de privado
