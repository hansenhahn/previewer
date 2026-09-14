# text-segmentation Specification

## Purpose

Dividir um texto em segmentos (blocos) por padrões de início e fim e alinhá-los
entre original e traduzido, preservando o texto de forma que ele possa ser
reconstruído.

## Requirements

### Requirement: Segmentação por padrões de início e fim

O sistema SHALL dividir o texto em segmentos usando padrões de início e fim de
bloco, mantendo como separadores as partes que ficam fora dos blocos. Sem padrões
configurados, o texto SHALL ser tratado como um único separador, sem segmentos.

#### Scenario: Blocos identificados

- **WHEN** o texto contém trechos delimitados por linhas que casam com os padrões
  de início e fim
- **THEN** cada trecho delimitado é retornado como um segmento, na ordem em que
  aparece

#### Scenario: Sem configuração

- **WHEN** não há padrões de início/fim
- **THEN** nenhum segmento é produzido

### Requirement: Reconstrução fiel

O sistema SHALL preservar os separadores entre os segmentos, de modo que
reconstruir o texto a partir dos segmentos e separadores reproduza exatamente o
texto original quando nada foi editado.

#### Scenario: Reconstruir sem edição

- **WHEN** os segmentos e separadores extraídos são remontados sem edições
- **THEN** o texto resultante é idêntico ao original

### Requirement: Alinhamento por ordem

O sistema SHALL alinhar os segmentos do original com os do traduzido por ordem de
aparição e SHALL sinalizar os segmentos que ficarem sem par quando as quantidades
divergirem.

#### Scenario: Quantidades iguais

- **WHEN** original e traduzido têm a mesma quantidade de segmentos
- **THEN** todos os segmentos são pareados na ordem

#### Scenario: Quantidades diferentes

- **WHEN** original e traduzido têm quantidades diferentes de segmentos
- **THEN** os segmentos excedentes são sinalizados como não pareados

### Requirement: Abstração dos delimitadores

O sistema SHALL separar, em cada segmento, as linhas delimitadoras (início/fim)
do **corpo**, expondo o corpo para exibição/edição e preservando os delimitadores
para a reconstrução.

#### Scenario: Corpo sem delimitadores

- **WHEN** um segmento delimitado por linha de início e de fim é produzido
- **THEN** o corpo exposto não contém as linhas delimitadoras

#### Scenario: Reconstrução reinclui os delimitadores

- **WHEN** o corpo é reconstruído junto do segmento
- **THEN** as linhas delimitadoras são reincluídas exatamente como no original

### Requirement: Segmentação por separadores

O sistema SHALL permitir segmentar o texto por **linhas separadoras**: cada bloco
de linhas consecutivas que não casam com os padrões de separador SHALL ser retornado
como um segmento, e as linhas que casam SHALL ser preservadas como separadores.

#### Scenario: Blocos entre separadores

- **WHEN** o texto é uma sequência de blocos separados por linhas que casam com os
  padrões de separador
- **THEN** cada bloco é retornado como um segmento, na ordem em que aparece

#### Scenario: Sem padrões de separador

- **WHEN** não há padrões de separador configurados
- **THEN** nenhum segmento é produzido por esse modo

#### Scenario: Reconstrução fiel com separadores

- **WHEN** os segmentos e separadores extraídos pelo modo separador são remontados
  sem edições
- **THEN** o texto resultante é idêntico ao original
