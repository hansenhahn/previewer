## ADDED Requirements

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
