## ADDED Requirements

### Requirement: Remover projeto pela interface

O sistema SHALL permitir **remover um projeto** pela interface, por meio de uma **ação de
remover em cada projeto** na lista do seletor, com **confirmação** por ser uma ação
destrutiva, e SHALL voltar ao estado "sem projeto" quando o projeto removido estava aberto.

#### Scenario: Remover pela lista de projetos

- **WHEN** o usuário aciona a ação de remover em um projeto do seletor
- **THEN** é pedida confirmação antes de concluir a remoção, e o projeto sai da lista

#### Scenario: Remover com confirmação

- **WHEN** o usuário aciona remover um projeto
- **THEN** é pedida confirmação antes de concluir a remoção

#### Scenario: Confirmação digitada

- **WHEN** o diálogo de remoção é exibido
- **THEN** o botão de remover só fica habilitado depois que o usuário digita **`confirmar`**;
  qualquer outro valor o mantém desabilitado

#### Scenario: Projeto aberto removido

- **WHEN** o usuário remove o projeto que está aberto
- **THEN** a interface volta ao estado "sem projeto" e o projeto sai da lista

## MODIFIED Requirements

### Requirement: Telas auxiliares da alteração

O sistema SHALL prover as telas auxiliares do fluxo: **nomear** ao subir (título e
descrição do PR; a mensagem de commit é gerada do título), **retomar** (selecionar uma
alteração da lista) e **descartar/abandonar** (com **confirmação digitada** por serem
destrutivas).

#### Scenario: Nomear ao subir

- **WHEN** o usuário aciona "Subir rascunho"
- **THEN** é exibida a tela para informar o título e a descrição do PR

#### Scenario: Subir em andamento

- **WHEN** o usuário confirma "Subir"
- **THEN** a ação indica progresso e fica indisponível até concluir

#### Scenario: Selecionar ao retomar

- **WHEN** o usuário aciona "Retomar rascunho"
- **THEN** é exibida a lista de alterações, com status e ação de retomar

#### Scenario: Confirmação ao descartar/abandonar

- **WHEN** o usuário aciona descartar ou abandonar
- **THEN** o botão destrutivo só fica habilitado depois que o usuário digita **`confirmar`**;
  qualquer outro valor o mantém desabilitado
