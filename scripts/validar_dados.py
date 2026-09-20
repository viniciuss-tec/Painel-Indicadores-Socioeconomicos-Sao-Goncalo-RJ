"""
Valida os arquivos de dados antes da normalização/importação para o pianel.

Uso:
    python scripts/validar_dados.py [--strict]

Regras:
- campos históricos vazios são válidos (significam ausência de dado temporal nas bases consultadas);
- CODIGO deve ser único em ambos os arquivos;
- todos os códigos do histórico devem existir no catálogo em modo strict;
- o script distingue ERRO de AVISO;
- problemas de formatação numérica são sinalizados, não "corrigidos" silenciosamente.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import pandas as pd

#Local dos arquvos
ROOT = Path(__file__).resolve().parents[1]
ARQ_DADOS = ROOT / "data" / "dados_em_csv" / "dados_socioeconomicos.csv"
ARQ_INDICADORES = ROOT / "data" / "indicadores.csv"


COLUNAS_ANOS_ESPERADAS = [
    str(ano) for ano in [2000] + list(range(2006, 2026))
]

COLUNAS_OBRIGATORIAS_INDICADORES = [
    "CODIGO",
    "TEMA",
    "INDICADOR",
    "DEFINICAO",
    "USO",
    "FONTE",
]

# Indicadores em que um ponto isolado representa separador de milhar.
# Ex.: "90.884" -> 90884
REGRAS_MILHAR_PONTO = {
    "moburb_frota_automoveis",
}


def normalizar_codigo(value) -> str:
    if pd.isna(value):
        return ""
    return str(value).strip()


def parece_numero(valor: str) -> bool:
    valor = valor.strip()
    if valor == "":
        return True

    # Formatos aceitos:
    # 123
    # 123.45
    # 123,45
    # 1.234,56
    # 1.234.567.89 (caso específico de fonte)
    padroes = [
        r"^-?\d+(?:[.,]\d+)?$",
        r"^-?\d{1,3}(?:\.\d{3})+(?:,\d+)?$",
        r"^-?\d{1,3}(?:\.\d{3})+\.\d{1,6}$",
    ]
    return any(re.match(p, valor) for p in padroes)


def registrar(lista, severidade, mensagem):
    lista.append((severidade, mensagem))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Transforma inconsistências de relacionamento entre arquivos em erro bloqueante.",
    )
    args = parser.parse_args()

    erros = []
    avisos = []

#verifica se as planilhas estao no lugar certo
    if not ARQ_DADOS.exists():
        registrar(erros, "ERRO", f"Arquivo não encontrado: {ARQ_DADOS}")
    if not ARQ_INDICADORES.exists():
        registrar(erros, "ERRO", f"Arquivo não encontrado: {ARQ_INDICADORES}")

    if erros:
        for _, msg in erros:
            print(f"[ERRO] {msg}")
        return 1

    try:
        dados = pd.read_csv(ARQ_DADOS, dtype=str, keep_default_na=False)
        indicadores = pd.read_csv(
            ARQ_INDICADORES,
            dtype=str,
            keep_default_na=False,
        )
    except Exception as exc:
        print(f"[ERRO] Falha ao ler os CSVs: {exc}")
        return 1

    dados.columns = [str(c).strip() for c in dados.columns]
    indicadores.columns = [str(c).strip() for c in indicadores.columns]

    # Estrutura
    if "CODIGO" not in dados.columns:
        registrar(erros, "ERRO", "dados_socioeconomicos.csv não possui a coluna CODIGO.")
    else:
        colunas_anos = [c for c in dados.columns if re.fullmatch(r"\d{4}", c)]
        faltantes = [c for c in COLUNAS_ANOS_ESPERADAS if c not in colunas_anos]
        extras = [c for c in colunas_anos if c not in COLUNAS_ANOS_ESPERADAS]

        if faltantes:
            registrar(
                erros,
                "ERRO",
                "Colunas de ano ausentes: " + ", ".join(faltantes),
            )
        if extras:
            registrar(
                avisos,
                "AVISO",
                "Colunas de ano adicionais encontradas: " + ", ".join(extras),
            )

    faltantes_ind = [
        c for c in COLUNAS_OBRIGATORIAS_INDICADORES
        if c not in indicadores.columns
    ]
    if faltantes_ind:
        registrar(
            erros,
            "ERRO",
            "indicadores.csv possui colunas obrigatórias ausentes: "
            + ", ".join(faltantes_ind),
        )

    # Códigos
    cod_dados = [normalizar_codigo(x) for x in dados["CODIGO"]]
    cod_ind = [normalizar_codigo(x) for x in indicadores["CODIGO"]]

    vazios_dados = [i + 2 for i, c in enumerate(cod_dados) if c == ""]
    if vazios_dados:
        registrar(
            erros,
            "ERRO",
            "Existem linhas sem CODIGO em dados_socioeconomicos.csv: "
            + ", ".join(map(str, vazios_dados)),
        )
#resolver erro ai entrar nesse if aqui
    vazios_ind = [i + 2 for i, c in enumerate(cod_ind) if c == ""]
    if vazios_ind:
        registrar(
            erros,
            "ERRO",
            "Existem linhas sem CODIGO em indicadores.csv: "
            + ", ".join(map(str, vazios_ind)),
        )

    duplicados_dados = sorted(
        {c for c in cod_dados if c and cod_dados.count(c) > 1}
    )
    duplicados_ind = sorted(
        {c for c in cod_ind if c and cod_ind.count(c) > 1}
    )

    if duplicados_dados:
        registrar(
            erros,
            "ERRO",
            "Códigos duplicados em dados_socioeconomicos.csv: "
            + ", ".join(duplicados_dados),
        )

    if duplicados_ind:
        registrar(
            erros,
            "ERRO",
            "Códigos duplicados em indicadores.csv: "
            + ", ".join(duplicados_ind),
        )

    set_dados = {c for c in cod_dados if c}
    set_ind = {c for c in cod_ind if c}

    somente_dados = sorted(set_dados - set_ind)
    somente_ind = sorted(set_ind - set_dados)

    if somente_dados:
        mensagem = (
            "Códigos presentes no histórico mas ausentes no catálogo: "
            + ", ".join(somente_dados)
        )
        registrar(erros if args.strict else avisos, "ERRO" if args.strict else "AVISO", mensagem)

    if somente_ind:
        registrar(
            avisos,
            "AVISO",
            "Códigos presentes no catálogo mas sem linha no histórico: "
            + ", ".join(somente_ind),
        )

    # Metadados: vazios geram aviso, não erro. O intuito é sinalizar que a fonte nao tem dados para o ano vazio por questoes de metodologia ou interrupçao de coleta e entrega dos dados
    for col in ["TEMA", "INDICADOR", "DEFINICAO", "USO", "FONTE"]:
        if col not in indicadores.columns:
            continue
        vazios = (
            indicadores[col]
            .astype(str)
            .str.strip()
            .eq("")
        )
        if vazios.any():
            qtd = int(vazios.sum())
            registrar(
                avisos,
                "AVISO",
                f"{qtd} indicador(es) com {col} vazio em indicadores.csv.",
            )

    # Verificação dos valores históricos
    colunas_anos = [c for c in dados.columns if re.fullmatch(r"\d{4}", c)]
    for _, row in dados.iterrows():
        codigo = normalizar_codigo(row["CODIGO"])
        for ano in colunas_anos:
            raw = str(row[ano]).strip()
            if raw == "":
                # Ausência de dado é válida.
                continue
            if not parece_numero(raw):
                registrar(
                    erros,
                    "ERRO",
                    f"Valor não reconhecido em {codigo}, ano {ano}: '{raw}'",
                )

    print("=" * 62)
    print("VALIDAÇÃO DO DATASET")
    print("=" * 62)
    print(f"Indicadores no catálogo : {len(indicadores)}")
    print(f"Linhas no histórico     : {len(dados)}")
    print(f"Temas                   : {indicadores['TEMA'].nunique()}")
    print(f"Modo                    : {'STRICT' if args.strict else 'DESENVOLVIMENTO'}")
    print()

    if avisos:
        print("AVISOS")
        print("-" * 62)
        for _, msg in avisos:
            print(f"[AVISO] {msg}")
        print()

    if erros:
        print("ERROS")
        print("-" * 62)
        for _, msg in erros:
            print(f"[ERRO] {msg}")
        print()
        print("Resultado: FALHA")
        return 1

    print("Resultado: OK")
    if avisos:
        print("Observação: existem avisos que merecem revisão.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
