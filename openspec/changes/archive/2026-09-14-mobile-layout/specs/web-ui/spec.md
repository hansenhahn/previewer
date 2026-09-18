## ADDED Requirements

### Requirement: Layout em telas pequenas (mobile)

Em telas pequenas, o sistema SHALL organizar a interface para uso em celular:
um **header único** com um acionador que abre a **gaveta** (projeto + árvore de
arquivos) e o **avatar**; a **prévia fixa no topo**; e a **lista de segmentos**
rolando abaixo. O sistema SHALL ocultar o **editor de texto raw** e os **divisores
arrastáveis** nesse modo.

#### Scenario: Header único

- **WHEN** qualquer tela é exibida no celular
- **THEN** o header mostra o acionador da gaveta à esquerda, a marca e o avatar à
  direita, sem editor de texto raw

#### Scenario: Gaveta de projetos e arquivos

- **WHEN** o usuário aciona o header
- **THEN** uma gaveta é exibida com o seletor de projeto, a árvore de arquivos e a
  ação de importar

### Requirement: Segmentos com prévia fixa

No modo mobile, o sistema SHALL exibir a **prévia fixa no topo** e a **lista de
segmentos** rolando abaixo, com os segmentos de **nome** e de **diálogo**
separados, e SHALL escalar a prévia em **múltiplos inteiros** conforme o espaço.

#### Scenario: Prévia junto dos segmentos

- **WHEN** a lista de segmentos é exibida no celular
- **THEN** a prévia permanece visível no topo enquanto a lista rola

#### Scenario: Seleção atualiza a prévia

- **WHEN** o usuário dá um toque em um segmento
- **THEN** o segmento é selecionado e a prévia passa a refletir esse segmento

#### Scenario: Edição reflete na prévia

- **WHEN** o usuário digita na tradução de um segmento
- **THEN** a prévia é atualizada em tempo real, refletindo a linha do segmento editado

### Requirement: Edição de um segmento em tela dedicada

No modo mobile, um **toque duplo** em um segmento SHALL abrir uma **tela de edição
dedicada** com a prévia e aquele segmento, com navegação para o anterior, o próximo
e para voltar à lista; a navegação SHALL ficar **acima do teclado**.

#### Scenario: Abrir a edição

- **WHEN** o usuário dá um toque duplo em um segmento
- **THEN** a tela de edição daquele segmento é aberta, com a prévia e os campos de
  original/tradução

#### Scenario: Navegar entre segmentos

- **WHEN** o usuário aciona anterior ou próximo
- **THEN** o segmento exibido muda, mantendo a prévia e a tela de edição

#### Scenario: Voltar para a lista

- **WHEN** o usuário aciona a ação de voltar à lista
- **THEN** a lista de segmentos é exibida novamente

#### Scenario: Navegação visível com o teclado

- **WHEN** o teclado virtual está aberto durante a edição
- **THEN** os controles de navegação permanecem visíveis (acima do teclado)
