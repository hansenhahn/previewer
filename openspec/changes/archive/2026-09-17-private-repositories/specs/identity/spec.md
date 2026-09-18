## ADDED Requirements

### Requirement: Login via GitHub

O sistema SHALL iniciar o fluxo OAuth com o GitHub e, no retorno, obter a identidade do
usuário — provedor, identificador estável, login e e-mail — e SHALL solicitar **escopo de
repositório** (`repo`) para permitir listar, importar e contribuir em repositórios **públicos
e privados**.

#### Scenario: Login concluído

- **WHEN** o usuário autoriza o aplicativo no GitHub e retorna ao callback
- **THEN** o sistema estabelece uma sessão autenticada para esse usuário

#### Scenario: Escopos de identidade e repositório

- **WHEN** o fluxo de autorização é iniciado
- **THEN** os escopos solicitados incluem identidade (perfil e e-mail) e acesso a
  repositórios (`repo`), exigindo novo consentimento quando o escopo mudar

## REMOVED Requirements

### Requirement: Login via GitHub (somente identidade)
