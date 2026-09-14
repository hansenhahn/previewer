# identity Specification

## Purpose

Autenticar o usuário via GitHub (somente identidade), manter sessão, permitir
encerrá-la e aplicar onboarding manual, sem conceder acesso a repositórios.

## Requirements

### Requirement: Login via GitHub (somente identidade)

O sistema SHALL iniciar o fluxo OAuth com o GitHub e, no retorno, obter a
identidade do usuário — provedor, identificador estável, login e e-mail —
**sem** solicitar acesso a repositórios.

#### Scenario: Login concluído

- **WHEN** o usuário autoriza o aplicativo no GitHub e retorna ao callback
- **THEN** o sistema estabelece uma sessão autenticada para esse usuário

#### Scenario: Escopos apenas de identidade

- **WHEN** o fluxo de autorização é iniciado
- **THEN** os escopos solicitados se limitam à identidade do usuário (perfil e
  e-mail), sem escopos de repositório

### Requirement: Onboarding manual por allowlist

O sistema SHALL permitir o login apenas para identidades presentes na lista
configurada pelo operador e SHALL NOT criar conta para identidades ausentes dessa
lista.

#### Scenario: Identidade permitida

- **WHEN** um usuário cuja identidade está na lista autoriza o aplicativo
- **THEN** o usuário é associado e a sessão é estabelecida

#### Scenario: Identidade não permitida

- **WHEN** um usuário cuja identidade não está na lista autoriza o aplicativo
- **THEN** o acesso é negado e nenhuma conta é criada

### Requirement: Sessão e encerramento

O sistema SHALL manter a sessão autenticada entre requisições e SHALL permitir que
o usuário encerre a sessão.

#### Scenario: Sessão persistida

- **WHEN** o usuário autenticado faz uma nova requisição
- **THEN** o sistema o reconhece como autenticado

#### Scenario: Encerrar sessão

- **WHEN** o usuário solicita logout
- **THEN** a sessão deixa de ser válida

### Requirement: Usuário atual

O sistema SHALL expor o usuário autenticado, identificado de forma estável pelo
provedor, com o **perfil** (login, e-mail e avatar), e SHALL usá-lo como
proprietário das operações.

#### Scenario: Operações com o proprietário autenticado

- **WHEN** um usuário autenticado cria ou acessa recursos
- **THEN** os recursos são associados a esse usuário

#### Scenario: Perfil exposto

- **WHEN** o usuário autenticado consulta o estado de autenticação
- **THEN** o sistema retorna o login, o e-mail e o avatar do usuário

#### Scenario: Avatar vindo do provedor

- **WHEN** o login é concluído
- **THEN** o avatar é obtido do provedor de identidade, sem upload pelo usuário

### Requirement: Estado de autenticação consultável

O sistema SHALL expor, sem exigir sessão, a configuração de entrada (rótulo do
provedor e ação de login) e o estado do usuário atual, de modo que o frontend não
codifique um provedor específico.

#### Scenario: Usuário não autenticado

- **WHEN** o estado de autenticação é consultado sem sessão válida
- **THEN** o sistema informa que não há usuário autenticado e fornece o rótulo/ação
  de entrada do provedor configurado

#### Scenario: Usuário autenticado

- **WHEN** o estado de autenticação é consultado com sessão válida
- **THEN** o sistema retorna o usuário atual

### Requirement: Tela de login desacoplada do provedor

O sistema SHALL apresentar uma tela de login quando não houver usuário
autenticado, obtendo do backend o rótulo do provedor e a ação de entrada, sem
codificar um provedor específico no frontend.

#### Scenario: Login exibido

- **WHEN** o app carrega e não há usuário autenticado
- **THEN** a tela de login é exibida com a ação de entrada do provedor configurado

#### Scenario: Workspace após login

- **WHEN** o usuário está autenticado
- **THEN** o workspace é exibido, sem a tela de login

#### Scenario: Troca de provedor sem alterar o frontend

- **WHEN** o provedor de identidade é trocado (por exemplo, para Keycloak)
- **THEN** a tela de login continua funcionando, exibindo o rótulo e a ação do
  novo provedor sem alteração no frontend

### Requirement: Conta no cabeçalho

O sistema SHALL exibir, no canto superior direito, o nome (login) do usuário
autenticado e SHALL abrir um menu de conta a partir desse elemento; o menu mostra
o avatar, o login, o e-mail e o provedor, com uma ação de sair.

#### Scenario: Identificação do usuário logado

- **WHEN** o usuário está autenticado
- **THEN** o cabeçalho mostra apenas o nome da conta, sem avatar

#### Scenario: Menu de conta aberto

- **WHEN** o usuário aciona o nome da conta
- **THEN** um menu ancorado no canto superior direito é exibido com o avatar, o
  login, o e-mail, o provedor e a ação de sair

#### Scenario: Sair pelo menu

- **WHEN** o usuário aciona "sair" no menu de conta
- **THEN** a sessão é encerrada e a tela de login é exibida

#### Scenario: Provedor desacoplado no menu

- **WHEN** o provedor de identidade é trocado
- **THEN** o nome do provedor exibido no menu vem da configuração de entrada, sem
  alteração no frontend
