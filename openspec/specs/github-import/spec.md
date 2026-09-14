# github-import Specification

## Purpose

Importar um projeto a partir de um repositório GitHub público: listar os
repositórios da conta, validar o `manifest.json` e baixar apenas os arquivos
referenciados, mantendo um working copy git esparso e persistente.

## Requirements

### Requirement: Listar os repositórios da conta

O sistema SHALL listar os repositórios públicos da conta do usuário usando o
token obtido no login e SHALL permitir atualizar a lista sob demanda, sem
solicitar escopo de repositório adicional e sem descartar erros em silêncio.

#### Scenario: Lista disponível após o login

- **WHEN** o usuário autenticado consulta os repositórios disponíveis para import
- **THEN** o sistema apresenta os repositórios da conta obtidos no login

#### Scenario: Sem escopo de repositório extra

- **WHEN** o login é concluído
- **THEN** a listagem usa o token de identidade, sem exigir escopos de repositório
  adicionais

#### Scenario: Atualização sob demanda

- **WHEN** o usuário solicita atualizar a lista
- **THEN** o sistema consulta novamente o provedor e atualiza os repositórios
  exibidos

#### Scenario: Falha de listagem reportada

- **WHEN** a consulta ao provedor falha
- **THEN** o sistema informa o erro, em vez de exibir uma lista vazia sem
  explicação

### Requirement: Selecionar um repositório

O sistema SHALL permitir escolher um repositório da lista, seja o projeto
original ou um fork do usuário.

#### Scenario: Escolha do repositório

- **WHEN** o usuário seleciona um repositório da lista
- **THEN** o sistema prepara o import a partir desse repositório

### Requirement: Validar o manifest do repositório

O sistema SHALL verificar o `manifest.json` da branch padrão de cada repositório
listado e SHALL indicar quais são importáveis; ao importar, SHALL validá-lo de
novo, recusando o import com erro claro quando o manifest estiver ausente ou
inválido.

#### Scenario: Manifest válido

- **WHEN** o repositório possui um `manifest.json` válido na branch padrão
- **THEN** o sistema prossegue com o import

#### Scenario: Manifest ausente ou inválido

- **WHEN** o repositório não possui `manifest.json` ou ele é inválido
- **THEN** o sistema recusa o import e informa o motivo, sem criar o projeto

#### Scenario: Repositório importável indicado na lista

- **WHEN** a lista de repositórios é exibida
- **THEN** cada repositório com `manifest.json` válido é indicado como importável
  (marca de sucesso)

#### Scenario: Repositório não importável indicado na lista

- **WHEN** um repositório não tem `manifest.json` válido
- **THEN** ele é indicado como não importável (marca neutra), com o motivo, e não
  pode ser importado

### Requirement: Importar apenas os arquivos referenciados

O sistema SHALL criar o projeto baixando o manifest e somente os arquivos por ele
referenciados (textos, fontes e backgrounds), e SHALL NOT baixar o repositório
inteiro.

#### Scenario: Projeto importado e utilizável

- **WHEN** o import de um repositório válido é concluído
- **THEN** o projeto é criado, aparece na lista e pode ser aberto com seus textos
  e prévia

#### Scenario: Arquivos não referenciados

- **WHEN** o repositório contém arquivos que o manifest não referencia
- **THEN** esses arquivos não são baixados para o projeto

### Requirement: Working copy git persistente

O projeto importado SHALL manter um working copy git esparso e persistente como
seus dados, de modo que a leitura e a escrita pela API de arquivos continuem
funcionando e o uso de git (branch/commit depois) seja possível.

#### Scenario: Editar e salvar um arquivo importado

- **WHEN** o usuário edita e salva um arquivo de um projeto importado
- **THEN** a alteração persiste no working copy, preservado entre reinícios

### Requirement: Restrição a repositórios públicos

No MVP, o sistema SHALL importar apenas repositórios públicos e SHALL recusar
repositórios privados.

#### Scenario: Repositório privado

- **WHEN** o repositório escolhido é privado
- **THEN** o sistema recusa o import e informa que apenas repositórios públicos
  são suportados no momento

### Requirement: Import exige sessão

O import SHALL exigir sessão autenticada e o projeto resultante SHALL pertencer ao
usuário autenticado.

#### Scenario: Import sem sessão

- **WHEN** uma requisição de import chega sem sessão autenticada
- **THEN** o sistema responde com erro de não autorizado
