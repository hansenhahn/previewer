# project-text Specification

## Purpose

Ler e escrever o texto de um projeto respeitando o encoding declarado, de forma
que o texto permaneça íntegro em um ciclo de leitura e escrita.

## Requirements

### Requirement: Decodificação com o encoding do projeto

O sistema SHALL decodificar os bytes de um arquivo de texto do projeto usando o
encoding declarado na configuração do projeto, expondo o conteúdo como texto
Unicode.

#### Scenario: Bytes decodificados pelo encoding do projeto

- **WHEN** um arquivo de texto é lido com o encoding do projeto
- **THEN** o conteúdo é exposto como texto Unicode sem erro de decodificação

#### Scenario: Bytes inválidos para o encoding

- **WHEN** o conteúdo contém bytes inválidos para o encoding declarado
- **THEN** um erro de decodificação explícito é retornado

### Requirement: Escrita com round-trip preservado

O sistema SHALL codificar o texto de volta para bytes usando o mesmo encoding do
projeto, de modo que decodificar o resultado reproduza exatamente o texto de
entrada.

#### Scenario: Round-trip de leitura e escrita

- **WHEN** um texto é escrito e em seguida lido com o mesmo encoding
- **THEN** o texto resultante é idêntico ao texto original

### Requirement: Normalização de fim de linha

O sistema SHALL normalizar as quebras de linha do texto lido para `\n`,
tratando `\r\n` e `\r` como uma única quebra.

#### Scenario: Arquivo com CRLF

- **WHEN** um arquivo usa `\r\n` como quebra de linha
- **THEN** o texto exposto contém apenas `\n` como quebra de linha
