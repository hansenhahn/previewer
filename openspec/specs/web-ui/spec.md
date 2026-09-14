# web-ui Specification

## Purpose

Oferecer a interface do produto no navegador: importar e abrir projetos,
navegar pelos textos e editá-los com salvamento.

## Requirements

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

### Requirement: Painéis redimensionáveis

O sistema SHALL permitir redimensionar, arrastando os divisores, o painel de arquivos
e o painel de prévia, exibindo um **puxador** que sinaliza o arrasto e **persistindo**
a largura escolhida.

#### Scenario: Redimensionar a lista de arquivos

- **WHEN** o usuário arrasta o divisor entre a árvore de arquivos e o editor
- **THEN** a largura do painel de arquivos muda, dentro de limites mínimo e máximo

#### Scenario: Redimensionar a prévia

- **WHEN** o usuário arrasta o divisor entre o editor e a prévia
- **THEN** a largura do painel de prévia muda, respeitando um mínimo que não corta a
  imagem

#### Scenario: Persistência

- **WHEN** o usuário redimensiona um painel e recarrega a aplicação
- **THEN** a largura escolhida é restaurada

#### Scenario: Restaurar o padrão

- **WHEN** o usuário dá duplo-clique no divisor
- **THEN** o painel volta à largura padrão

### Requirement: Rolagem no tema

O sistema SHALL apresentar as barras de rolagem estilizadas conforme o tema, de forma
arredondada e discreta, tanto em navegadores WebKit quanto Firefox.

#### Scenario: Barra de rolagem temática

- **WHEN** um painel com conteúdo rolável é exibido
- **THEN** a barra de rolagem usa o estilo do tema (polegar arredondado, trilho
  transparente)
