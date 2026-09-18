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

### Requirement: Autosave com indicador discreto

O sistema SHALL salvar as edições automaticamente em intervalos (cerca de 1 minuto), exibir
um indicador **discreto** de salvamento (por exemplo: um **tick efêmero** ao salvar e um
**ícone de erro** quando falha) e oferecer um botão **Salvar** para forçar o
salvamento imediato.

#### Scenario: Edição salva sozinha

- **WHEN** o usuário edita um texto e aguarda o intervalo de autosave
- **THEN** a alteração é persistida automaticamente e um **tick efêmero** aparece no indicador

#### Scenario: Salvar

- **WHEN** o usuário aciona "Salvar"
- **THEN** o salvamento é feito imediatamente (sem esperar o intervalo) e o rascunho é
  backupeado no fork

#### Scenario: Salvar em andamento

- **WHEN** o backup/salvamento está em curso
- **THEN** o botão indica progresso e fica indisponível até concluir

#### Scenario: Falha ao salvar

- **WHEN** o salvamento falha (ex.: sem conexão)
- **THEN** o indicador mostra um **ícone de erro** (vermelho) e o salvamento é tentado novamente

### Requirement: Chip de estado com menu contextual

O sistema SHALL representar a alteração por um **chip único** que mostra o estado e, ao ser
acionado, abre um **menu sempre com as mesmas ações** — **Subir rascunho**, **Novo
rascunho**, **Retomar rascunho** e **Descartar rascunho** — habilitando ou desabilitando
cada ação conforme a disponibilidade, sem trocar os itens do menu.

#### Scenario: Chip reflete o estado

- **WHEN** não há alteração ativa
- **THEN** o chip aparece como "sem alteração" (na base)

#### Scenario: Rascunho

- **WHEN** há mudanças não enviadas
- **THEN** o chip indica "rascunho"

#### Scenario: PR aberto

- **WHEN** a alteração tem PR aberto
- **THEN** o chip indica o PR e seu estado (aberto / mudanças solicitadas)

#### Scenario: Menu fixo

- **WHEN** o usuário aciona o chip
- **THEN** o menu mostra Subir / Retomar / Descartar, com as ações indisponíveis desabilitadas

### Requirement: Telas auxiliares da alteração

O sistema SHALL prover as telas auxiliares do fluxo: **nomear** ao subir (título e
descrição do PR; a mensagem de commit é gerada do título), **retomar** (selecionar uma
alteração da lista) e **descartar/abandonar** (com confirmação por serem destrutivas).

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
- **THEN** é pedida confirmação antes de concluir a ação destrutiva

### Requirement: Operação em andamento

O sistema SHALL indicar e **bloquear** a UI durante operações demoradas (abrir projeto ou
arquivo, trocar de alteração, subir, descartar, abandonar), evitando interação duplicada.

#### Scenario: Aguardando o backend

- **WHEN** uma operação demorada está em curso
- **THEN** a UI mostra um indicador de progresso e fica bloqueada até concluir
