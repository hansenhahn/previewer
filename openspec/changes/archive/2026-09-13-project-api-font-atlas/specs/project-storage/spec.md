## MODIFIED Requirements

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
