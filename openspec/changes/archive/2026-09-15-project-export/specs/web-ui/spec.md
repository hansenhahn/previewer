## ADDED Requirements

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
