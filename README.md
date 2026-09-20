# Projeto Índices Socioeconômicos

Painel estático e sem banco de dados para visualizar, buscar e filtrar indicadores socioeconômicos.

## Arquitetura atual

```text
CSV de entrada
   |
   v
scripts/validar_dados.py
   |
   v
scripts/padronizar_dados.py
   |
   +--> data/dados_processados/observacoes_normalizadas.csv
   |
   +--> front/data/indicadores.json
                     |
                     v
               HTML + CSS + JS
```

## Estrutura

```text
api/
data/
  dados_em_csv/
  dados_processados/
  indicadores.csv
front/
  css/
  js/
  data/
scripts/
```

## Instalação

```bash
python -m venv .venv
```

Linux/macOS:

```bash
source .venv/bin/activate
```

Windows:

```powershell
.venv\Scripts\activate
```

Instale:

```bash
pip install -r requirements.txt
```

## 1. Validar os dados

Modo de desenvolvimento:

```bash
python scripts/validar_dados.py
```

Modo de bloqueio antes de uma futura importação ao banco:

```bash
python scripts/validar_dados.py --strict
```

Campos históricos vazios são aceitos como ausência de dado.

## 2. Normalizar os dados

```bash
python scripts/padronizar_dados.py
```

Saída principal:

```text
data/dados_processados/observacoes_normalizadas.csv
```

## 3. Gerar o JSON para o frontend

```bash
python scripts/gerar_json.py
```

Saídas:

```text
data/dados_processados/indicadores.json
front/data/indicadores.json
```

Esses scripts são executados quando os dados mudarem. O site não executa pandas durante o acesso.

## 4. Abrir o MVP

```bash
python scripts/exibir_front.py
```

Acesse:

```text
http://localhost:8000
```

Não abra `index.html` diretamente com `file://`. O navegador pode bloquear o carregamento do JSON por política de origem.

## Busca e temas

O frontend oferece:

- busca por palavra-chave;
- abas por tema;
- lista de indicadores;
- detalhe do indicador;
- histórico em gráfico SVG;
- tabela histórica;
- definição, uso, fonte, metodologia e demais metadados quando disponíveis;
- mensagem específica para indicadores sem dados.

## Conexão futura com FastAPI

O arquivo:

```text
front/js/data-provider.js
```

concentra a origem dos dados.

Hoje:

```javascript
const DATA_SOURCE = "local";
```

Futuramente:

```javascript
const DATA_SOURCE = "api";
const API_BASE_URL = "http://localhost:8000";
```

A interface não precisará ser reescrita.

## Regras de dados

- vazio significa ausência de dado;
- ausência de dado não é convertida em zero;
- códigos devem ser únicos;
- um código do histórico precisa existir no catálogo para ser publicado;
- inconsistências numéricas são reportadas;
- o processamento não altera os CSVs originais.

## Próxima fase

- revisar e completar metodologia/unidade/periodicidade;
- PostgreSQL;
- FastAPI;
- endpoints públicos;
- exportação CSV pela API;
- comparação histórica mais completa;
- integração frontend -> API;
- GitHub Pages + hospedagem da API;
- autenticação e notificações em versões posteriores.
