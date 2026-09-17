## ADDED Requirements

### Requirement: Remover um projeto

O sistema SHALL permitir **remover** um projeto do usuário, apagando o registro, as
alterações associadas e o working copy, **sem afetar o repositório remoto**.

#### Scenario: Remover projeto

- **WHEN** o usuário remove um projeto
- **THEN** o projeto deixa de aparecer na lista, suas alterações são apagadas e o working
  copy é removido

#### Scenario: Remoção isolada por dono

- **WHEN** um usuário tenta remover um projeto que não lhe pertence
- **THEN** o sistema não remove nada e responde como não encontrado

#### Scenario: Projeto inexistente

- **WHEN** o usuário remove um projeto que não existe
- **THEN** o sistema responde como não encontrado
