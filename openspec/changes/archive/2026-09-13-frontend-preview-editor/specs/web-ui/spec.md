## Purpose

Oferecer a interface do produto no navegador: importar e abrir projetos,
navegar pelos textos e editá-los com salvamento.

## ADDED Requirements

### Requirement: Listar e importar projetos

O sistema SHALL listar os projetos disponíveis e permitir importar um projeto a
partir de um arquivo de bundle, exibindo-o na lista e permitindo abri-lo.

#### Scenario: Importação pela interface

- **WHEN** o usuário envia um arquivo de projeto pela interface
- **THEN** o projeto passa a aparecer na lista e pode ser aberto

#### Scenario: Abertura de projeto

- **WHEN** o usuário abre um projeto da lista
- **THEN** a interface exibe os arquivos de texto e a prévia do projeto

### Requirement: Navegar e editar arquivos de texto

O sistema SHALL listar os arquivos de texto do projeto, abrir o conteúdo do
arquivo selecionado no editor e permitir salvá-lo, persistindo a alteração.

#### Scenario: Editar e salvar

- **WHEN** o usuário altera o conteúdo no editor e salva
- **THEN** ao reabrir o arquivo o conteúdo salvo é exibido

#### Scenario: Falha ao carregar projeto

- **WHEN** a importação de um bundle inválido é enviada pela interface
- **THEN** a interface informa o erro sem quebrar
