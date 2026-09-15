# project-changes Specification

## Purpose

Transformar edições em contribuições ao projeto original via GitHub, sem expor git ao
usuário: rascunho (= branch efêmera → branch do PR), subir (= PR), retomar, descartar e
abandonar, com a aceitação/merge permanecendo no GitHub.

## Requirements

### Requirement: Rascunho é uma branch efêmera

O sistema SHALL representar cada alteração em andamento como a **branch efêmera**
`previewer/sketch`, criada a partir da **base sincronizada** no **head do usuário** (fork ou
repo próprio), ainda sem pull request até ser submetida. Ao subir, ela SHALL virar a **branch definitiva**
`previewer/<slug-do-título>` (head do PR). A base SHALL permanecer limpa e sincronizada.

#### Scenario: Início automático do rascunho

- **WHEN** o usuário edita um projeto sem alteração ativa
- **THEN** a branch efêmera `previewer/sketch` é criada a partir da base e passa a receber as
  edições

#### Scenario: Base atualizada ao iniciar o rascunho

- **WHEN** um novo rascunho é iniciado
- **THEN** o sistema busca a base no remoto antes de criar a branch, partindo do estado mais
  recente

#### Scenario: Base intocada

- **WHEN** o usuário edita
- **THEN** as mudanças ficam na branch de rascunho, sem alterar a base

#### Scenario: Rascunho sem PR

- **WHEN** um rascunho ainda não foi submetido
- **THEN** ele não tem pull request, mesmo que já tenha backup no fork

#### Scenario: Autosave vira checkpoint

- **WHEN** o autosave persiste uma edição
- **THEN** um commit é adicionado ao rascunho local, formando o histórico da alteração

### Requirement: Backup do rascunho no fork

O sistema SHALL permitir **backupear** o rascunho no head do usuário (fork ou repo próprio),
na **branch separada** `previewer-backup/sketch`, sem criar nem atualizar pull request, de
modo que o trabalho não dependa apenas do storage local. Vale apenas para o rascunho **não
publicado**; a branch de backup SHALL ser removida quando o rascunho virar PR, for descartado
ou abandonado.

#### Scenario: Salvar

- **WHEN** o usuário aciona "Salvar" em um rascunho não publicado
- **THEN** os commits do rascunho são empurrados para a branch de backup no fork

#### Scenario: Sem backup quando já há PR

- **WHEN** a alteração já tem pull request
- **THEN** "Salvar" apenas grava/commita localmente, sem criar branch de backup

#### Scenario: Backup não abre PR

- **WHEN** o backup é feito
- **THEN** nenhum pull request é criado ou atualizado

### Requirement: Novo rascunho a partir da base

O sistema SHALL permitir iniciar um **novo rascunho** voltando à base **sem publicar nem
descartar** a alteração atual, de forma que a próxima edição crie um novo rascunho.

#### Scenario: Novo rascunho

- **WHEN** o usuário inicia um novo rascunho
- **THEN** a base volta a ser a branch ativa e a alteração atual permanece intacta

### Requirement: Subir rascunho abre ou atualiza o PR

O sistema SHALL, ao subir um rascunho, garantir o **fork** do usuário, empurrar a branch
para o fork e **abrir um pull request** (`fork:branch → upstream:base`). Subir novamente a
mesma alteração SHALL **atualizar o mesmo PR** em vez de criar outro.

#### Scenario: Primeira subida

- **WHEN** o usuário sobe um rascunho sem PR
- **THEN** o sistema cria/reusa o fork, renomeia a branch efêmera para
  `previewer/<slug-do-título>`, empurra e abre um PR

#### Scenario: Subidas seguintes

- **WHEN** o usuário sobe novamente a mesma alteração
- **THEN** o sistema faz commit e push no mesmo branch, atualizando o PR existente

#### Scenario: PR enxuto

- **WHEN** o usuário sobe o rascunho
- **THEN** o delta não publicado é reunido em um único commit antes do push

#### Scenario: Sem alterações para subir

- **WHEN** não há mudanças não enviadas
- **THEN** o sistema não abre PR nem faz push (a ação fica indisponível)

### Requirement: Estado do PR visível

O sistema SHALL expor o estado da alteração (rascunho, PR aberto, mudanças solicitadas,
mergeada/fechada) e o vínculo com o PR, atualizado a partir do GitHub.

#### Scenario: Mudanças solicitadas

- **WHEN** o revisor solicita mudanças no PR
- **THEN** a alteração passa a indicar "mudanças solicitadas"

#### Scenario: Mergeada

- **WHEN** o PR é mergeado no GitHub
- **THEN** a alteração passa a indicar mergeada

### Requirement: Retomar uma alteração

O sistema SHALL permitir **retomar** uma alteração existente (rascunho ou branch de PR),
tornando-a a branch ativa para edição.

#### Scenario: Retomar rascunho

- **WHEN** o usuário retoma uma alteração existente
- **THEN** a branch dessa alteração passa a ser a ativa e o usuário continua de onde parou

#### Scenario: Retomar PR aberto fora do app

- **WHEN** o usuário lista as alterações e há PRs abertos do seu head que o app não criou
- **THEN** o sistema os registra e, ao retomar, carrega a branch do remoto e a torna ativa

#### Scenario: PR aberto que não é projeto do previewer

- **WHEN** um PR aberto do head tem branch sem `manifest.json`
- **THEN** ele aparece na lista como **não-selecionável**, com o motivo informado, e não pode
  ser retomado

#### Scenario: Edições não salvas ao trocar

- **WHEN** o usuário tenta retomar outra alteração com edições não salvas
- **THEN** o sistema pede para salvar ou descartar antes de trocar

#### Scenario: Trocar com rascunho salvo

- **WHEN** o usuário troca para outra alteração com um rascunho já salvo (commitado), mesmo
  sem publicar
- **THEN** a troca é permitida e, ao voltar, o rascunho continua preservado na sua branch

### Requirement: Descartar uma alteração

O sistema SHALL permitir **descartar** uma alteração. Um **rascunho não publicado** SHALL ser
removido por inteiro (branch efêmera, backup remoto e a alteração), voltando à base. Uma
**alteração publicada** SHALL ter apenas o trabalho não publicado descartado, restaurando a
branch ao último commit publicado, sem afetar o PR.

#### Scenario: Descartar rascunho não publicado

- **WHEN** o usuário descarta um rascunho sem PR
- **THEN** a branch efêmera, o backup remoto e a alteração são removidos e a base volta a
  ser a branch ativa

#### Scenario: Descartar trabalho de alteração publicada

- **WHEN** o usuário descarta uma alteração já publicada
- **THEN** a branch volta ao último commit publicado e o PR não é afetado

### Requirement: Abandonar uma alteração

O sistema SHALL permitir **abandonar** uma alteração, voltando à base, removendo a branch
local e a de **backup** no fork e, se houver PR, fechando-o.

#### Scenario: Abandonar

- **WHEN** o usuário abandona uma alteração
- **THEN** a base volta a ser a branch ativa, as branches local e de backup são removidas e
  um PR aberto é fechado

### Requirement: Fork e upstream gerenciados

O sistema SHALL reusar/criar e sincronizar o fork do usuário (o `origin` do working copy) de
forma automática, sem expor o conceito ao usuário, e SHALL registrar o **upstream**
(`owner/repo` + branch base) do projeto a partir do `parent` do fork.

#### Scenario: Upstream registrado no import

- **WHEN** o usuário importa um repositório que é um fork
- **THEN** o sistema registra o `parent` como upstream e a branch base do projeto

#### Scenario: Fork reusado antes do push

- **WHEN** o usuário sobe a primeira alteração de um projeto
- **THEN** o fork é reusado/validado e sincronizado antes do push

#### Scenario: Repositório próprio (sem fork)

- **WHEN** o projeto não é um fork (o usuário é dono do repositório)
- **THEN** o sistema usa o próprio repositório como head e abre o PR de uma branch para a
  base no mesmo repositório, sem criar fork

### Requirement: Check do upstream antes de publicar

O sistema SHALL, antes de publicar, verificar se o upstream avançou e, se necessário,
atualizar o branch da alteração para evitar PR desatualizado.

#### Scenario: Upstream avançou

- **WHEN** o upstream está à frente da base da alteração no momento de subir
- **THEN** o sistema atualiza o branch com as mudanças do upstream antes do push

### Requirement: Credencial de escrita

O sistema SHALL realizar as operações de escrita no GitHub com uma credencial do usuário
(escopo de escrita em repositório público no MVP), isolada atrás do contrato
`ProjectExport`, sem expor token na API.

#### Scenario: Escopo de escrita

- **WHEN** o usuário autoriza o fluxo de contribuição
- **THEN** o sistema usa uma credencial com permissão de escrita apenas no necessário
  para push no fork e abertura de PR
