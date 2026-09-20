"""
INTEGRAR COM POSTGRESQL + FASTAPI.

Este arquivo NÃO grava no banco ainda.

Fluxo previsto para a próxima fase:

1. validar_dados.py --strict
2. padronizar_dados.py
3. importar_banco_dados.py
4. FastAPI consulta PostgreSQL
5. frontend troca o data-provider local pelo endpoint da API

Modelo planejado:

temas
    id
    nome
    ordem

indicadores
    id
    codigo
    tema_id
    nome
    unidade
    definicao
    uso
    metodologia
    periodicidade
    fonte
    criado_em
    atualizado_em

observacoes
    id
    indicador_id
    ano
    valor
"""

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARQ_NORMALIZADO = ROOT / "data" / "dados_processados" / "observacoes_normalizadas.csv"


def carregar_dados_normalizados():
    """
    Ponto onde futuramente será feita a leitura e importação para PostgreSQL.
    """
    if not ARQ_NORMALIZADO.exists():
        raise FileNotFoundError(
            "Execute primeiro: python scripts/padronizar_dados.py"
        )

    return ARQ_NORMALIZADO


if __name__ == "__main__":
    arquivo = carregar_dados_normalizados()
    print("Arquivo normalizado pronto para futura importação:")
    print(arquivo)
    print("\nPostgreSQL ainda não está conectado nesta versão do MVP.")
