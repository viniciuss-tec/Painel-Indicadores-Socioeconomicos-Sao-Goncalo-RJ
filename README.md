# Projeto de Índices Socioeconômicos de São Gonçalo - RJ

> Um projeto para reunir, organizar e apresentar indicadores socioeconômicos de São Gonçalo - RJ em um único lugar.

[![Status](https://img.shields.io/badge/status-em%20desenvolvimento-blue)](https://github.com/viniciuss-tec/Painel-Indicadores-Socioeconomicos-Sao-Goncalo-RJ)
[![Frontend](https://img.shields.io/badge/frontend-HTML%20%2B%20CSS%20%2B%20JavaScript-orange)](https://github.com/viniciuss-tec/Painel-Indicadores-Socioeconomicos-Sao-Goncalo-RJ/tree/main/front)
[![Dados](https://img.shields.io/badge/dados-CSV%20%2B%20pandas-green)](https://github.com/viniciuss-tec/Painel-Indicadores-Socioeconomicos-Sao-Goncalo-RJ/tree/main/data)

## Sobre o projeto

O **Projeto de Índices Socioeconômicos de São Gonçalo - RJ** tem como objetivo reunir indicadores relevantes do município em uma aplicação simples de consultar e manter.

A proposta surgiu da dispersão dos dados entre diferentes fontes, formatos e períodos. O projeto organiza essas informações por temas e apresenta seus valores históricos junto de informações sobre definição, uso e fonte.


> **Importante:** os indicadores devem ser interpretados de acordo com a metodologia e a fonte de origem. A aplicação não substitui as publicações oficiais das instituições responsáveis pelos dados.


O site atual é publicado pelo **GitHub Pages** e utiliza a pasta `front/` como conteúdo estático.

## Temas

Os indicadores são organizados inicialmente nos seguintes temas:

| Tema | Exemplos de indicadores |
|---|---|
| **Saúde** | Mortalidade infantil, expectativa de vida, atenção primária, cobertura vacinal |
| **Educação** | Matrículas, analfabetismo, abandono escolar |
| **Segurança Pública** | Homicídios, ameaças, estelionato, desaparecimentos, latrocínio |
| **Assistência Social** | Pobreza, Cadastro Único, Bolsa Família, CRAS, CREAS, Centro POP |
| **Saneamento básico** | Atendimento de água, atendimento de esgoto, tratamento de esgoto, coleta seletiva |
| **Desenvolvimento econômico** | Emprego formal e emprego por setor |
| **Mobilidade urbana** | Frota de ônibus, micro-ônibus, motocicletas e automóveis |
| **Meio ambiente** | Emissões líquidas de gases de efeito estufa |

A composição dos indicadores pode mudar conforme novas fontes são analisadas e os dados são revisados.

## Como os dados são organizados

O projeto separa o **catálogo dos indicadores** dos **dados históricos**.

### Catálogo de indicadores

Arquivo:

```text
data/indicadores.csv
```

O catálogo concentra os metadados dos indicadores, como:

```text
CODIGO
TEMA
INDICADOR
UNIDADE
DEFINICAO
USO
METODOLOGIA
PERIODICIDADE
FONTE
```

### Dados históricos

Arquivo:

```text
data/dados_em_csv/dados_socioeconomicos.csv
```

Os valores são mantidos em formato de planilha para facilitar a coleta e a manutenção:

```text
CODIGO | 2000 | 2006 | 2007 | ... | 2025
```

### Dados normalizados

Durante o processamento, o histórico é transformado para o formato:

```text
CODIGO | ANO | VALOR
```

Resultado:

```text
data/dados_processados/observacoes_normalizadas.csv
```

Esse formato foi escolhido pensando na futura utilização com banco de dados.

## Pipeline de dados

```text
                         DADOS
                           |
              +------------+------------+
              |                         |
              v                         v
       indicadores.csv       dados_socioeconomicos.csv
              |                         |
              +------------+------------+
                           |
                           v
                  validar_dados.py
                           |
                           v
                 padronizar_dados.py
                           |
                           v
              observacoes_normalizadas.csv
                           |
                           v
                    gerar_json.py
                           |
                           v
                  indicadores.json
                           |
                           v
                    HTML + CSS + JS
```

Os scripts de preparação são executados quando os dados precisam ser atualizados. O site não executa pandas a cada acesso.

## Validação dos dados

O projeto possui uma etapa de validação antes da publicação ou futura importação em banco de dados.

Execute:

```bash
python scripts/validar_dados.py
```

Para uma validação mais rígida:

```bash
python scripts/validar_dados.py --strict
```

O validador verifica, entre outros pontos:

- códigos duplicados;
- códigos ausentes;
- estrutura dos arquivos;
- correspondência entre catálogo e histórico;
- valores que não podem ser interpretados como números;
- anos inválidos;
- campos importantes de metadados;
- linhas históricas sem código.

### Regra para ausência de dados

Campo histórico vazio significa **ausência de dado**.

Não é convertido para zero.

No tratamento do sistema, esse caso poderá ser exibido como:

> **Sem dados correspondentes para o período.**

## Scripts

### `validar_dados.py`

Valida os arquivos de entrada e separa problemas em **erros** e **avisos**.

### `padronizar_dados.py`

Transforma os dados históricos do formato de coleta para o formato normalizado `CODIGO | ANO | VALOR`.

### `gerar_json.py`

Gera o arquivo JSON utilizado pelo frontend:

```text
front/data/indicadores.json
```

### `exibir_front.py`

Inicia um servidor HTTP local para visualizar o site.

### `orquest_init_projeto.py`

É o ponto de entrada recomendado para iniciar o projeto localmente. Ele reúne as etapas necessárias e abre o navegador automaticamente.

```bash
python scripts/orquest_init_projeto.py
```

O fluxo é:

```text
verificação/preparação do ambiente
          |
          v
validação dos dados
          |
          v
normalização
          |
          v
geração do JSON
          |
          v
servidor local
          |
          v
navegador
```

### `importar_banco_dados.py`

Atualmente funciona como ponto de integração planejado para a futura camada PostgreSQL, que na versao 1 ainda nao foi implementada.

## Frontend

O frontend foi construído sem framework JavaScript, priorizando uma base simples de manter e fácil de evoluir.

### Tecnologias atuais

- HTML5
- CSS3
- JavaScript
- SVG para o gráfico histórico

### Funcionalidades atuais

- navegação por temas em abas;
- busca por palavra-chave;
- listagem de indicadores;
- detalhes do indicador;
- último valor disponível;
- último ano disponível;
- série histórica;
- gráfico histórico;
- tabela histórica;
- definição;
- uso do indicador;
- unidade, quando disponível;
- periodicidade, quando disponível;
- fonte;
- metodologia, quando disponível;
- tratamento visual para ausência de dados.

## Executando localmente

### Requisitos

- Python 3
- pip

A versão atual não precisa de PostgreSQL nem de FastAPI para funcionar.

### Inicialização recomendada

Na raiz do projeto:

```bash
python scripts/orquest_init_projeto.py
```

O script cria e utiliza o ambiente virtual `.venv` quando necessário, instala as dependências, executa a preparação dos dados e inicia o servidor local.

Endereço local:

```text
http://localhost:8000
```

**Não abra `index.html` diretamente com `file://`, porque o navegador pode bloquear o carregamento do JSON local.**

## Estrutura do projeto

```text
.
├── .github/
│   └── workflows/
│
├── api/
│   └── main.py
│
├── data/
│   ├── dados_em_csv/
│   ├── dados_processados/
│   └── indicadores.csv
│
├── front/
│   ├── css/
│   ├── data/
│   ├── js/
│   ├── index.html
│   └── indicadores.html
│
├── scripts/
│   ├── validar_dados.py
│   ├── padronizar_dados.py
│   ├── gerar_json.py
│   ├── exibir_front.py
│   ├── orquest_init_projeto.py
│   └── importar_banco_dados.py
│
├── .gitignore
├── README.md
└── requirements.txt
```

## Arquitetura atual

```text
CSV
 |
 v
Python + pandas
 |
 v
JSON
 |
 v
HTML + CSS + JavaScript
 |
 v
GitHub Pages
```

A interface está desacoplada da origem dos dados por meio de:

```text
front/js/data-provider.js
```

Isso permite substituir o JSON local por uma API sem reconstruir toda a interface.

O primeiro estágio da API poderá utilizar os dados já preparados, sem introduzir PostgreSQL imediatamente.


## Fontes

Os indicadores são obtidos de diferentes fontes públicas, de acordo com a natureza de cada informação. Entre as fontes utilizadas estão, conforme o indicador:

- IBGE;
- DATASUS;
- INEP;
- Atlas Brasil;
- ISP-RJ;
- SNIS;
- SEEG;
- outros órgãos e bases públicas responsáveis pelos dados.

A fonte e a metodologia de cada indicador devem ser consultadas em seu respectivo cadastro.

## Contribuições

O projeto está em desenvolvimento. Sugestões, correções de dados, melhorias de interface e contribuições técnicas podem ser registradas por meio das ferramentas do GitHub, como Issues e Pull Requests.

## Autor

**Vinicius**

Projeto desenvolvido para estudo, organização de dados e disponibilização de informações socioeconômicas de São Gonçalo - RJ.