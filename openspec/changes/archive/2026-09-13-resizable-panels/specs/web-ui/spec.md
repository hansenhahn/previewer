## ADDED Requirements

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
