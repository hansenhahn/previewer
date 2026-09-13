# service-config Specification

## Purpose

Carregar a configuração do serviço a partir do ambiente e validá-la antes de
levantar a aplicação, evitando comportamento com valores implícitos ou
inseguros.

## Requirements

### Requirement: Configuração por variáveis de ambiente

O serviço SHALL ler sua configuração de variáveis de ambiente, incluindo a raiz
de armazenamento, a conexão com o banco, a chave secreta e o modo de execução,
sem depender de caminhos fixos no código.

#### Scenario: Configuração completa

- **WHEN** todas as variáveis obrigatórias estão definidas com valores válidos
- **THEN** o serviço inicia normalmente

#### Scenario: Variável obrigatória ausente

- **WHEN** uma variável obrigatória não está definida
- **THEN** o serviço falha ao iniciar com uma mensagem explícita indicando a
  variável faltante, sem iniciar parcialmente

### Requirement: Sem segredo padrão inseguro

O serviço SHALL exigir uma chave secreta fornecida pelo ambiente e SHALL NOT
assumir um valor padrão inseguro quando ela não for informada.

#### Scenario: Chave secreta ausente

- **WHEN** a chave secreta não é fornecida
- **THEN** o serviço falha ao iniciar, em vez de usar um valor padrão
