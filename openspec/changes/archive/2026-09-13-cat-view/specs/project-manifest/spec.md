## ADDED Requirements

### Requirement: Configuração de segmentação

O manifesto SHALL aceitar uma configuração opcional de segmentação com listas de
padrões de início e fim de bloco, disponibilizando-a para a visão por segmentos
sem invalidar projetos que não a declarem.

#### Scenario: Configuração presente

- **WHEN** o manifesto declara padrões de início e fim
- **THEN** eles ficam disponíveis para segmentar os textos do projeto

#### Scenario: Configuração ausente

- **WHEN** o manifesto não declara segmentação
- **THEN** o projeto continua válido, apenas sem visão por segmentos

#### Scenario: Configuração inválida

- **WHEN** a segmentação declara listas inválidas
- **THEN** a leitura do manifesto é rejeitada com erro explícito
