"""
Padroniza o histórico para o formato:

CODIGO | ANO | VALOR

Também gera um JSON pronto para o Painel de Indices Socioeconomicos.

Códigos sem metadados são ignorados no processamento (com aviso);
use validar_dados.py --strict antes da importação oficial.
"""

from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
ARQ_DADOS = ROOT / "data" / "dados_em_csv" / "dados_socioeconomicos.csv"
ARQ_INDICADORES = ROOT / "data" / "indicadores.csv"

SAIDA_DIR = ROOT / "data" / "dados_processados"
SAIDA_FRONT = ROOT / "front" / "data"

SAIDA_DIR.mkdir(parents=True, exist_ok=True)
SAIDA_FRONT.mkdir(parents=True, exist_ok=True)


# Regras explícitas para tratar a entrada do valor
REGRAS_MILHAR_PONTO = {
    "moburb_frota_automoveis",
}


def normalizar_numero(valor: str, codigo: str):
    if valor is None or pd.isna(valor):
        return None

    texto = str(valor).strip()
    if not texto:
        return None

    texto = texto.replace("\u00a0", "").replace(" ", "")

    # Exemplo: "104,89" -> 104.89
    if "," in texto:
        # Formato brasileiro: 1.234,56
        if "." in texto:
            texto = texto.replace(".", "").replace(",", ".")
        else:
            texto = texto.replace(",", ".")
        return float(texto)

    # Exemplo conhecido de frota: "90.884" -> 90884
    if codigo in REGRAS_MILHAR_PONTO and re.fullmatch(r"-?\d{1,3}(?:\.\d{3})+", texto):
        return float(texto.replace(".", ""))

    # Exemplo das emissões: "1.089.970.49" -> 1089970.49
    if texto.count(".") >= 2:
        partes = texto.split(".")
        if len(partes[-1]) in (1, 2, 3, 4, 5, 6):
            parte_inteira = "".join(partes[:-1])
            parte_decimal = partes[-1]
            return float(f"{parte_inteira}.{parte_decimal}")

    # Padrão simples: 73.89
    return float(texto)


def texto_limpo(value):
    if value is None or pd.isna(value):
        return ""
    return str(value).strip()


def main():
    dados = pd.read_csv(
        ARQ_DADOS,
        dtype=str,
        keep_default_na=False,
    )
    indicadores = pd.read_csv(
        ARQ_INDICADORES,
        dtype=str,
        keep_default_na=False,
    )

    dados.columns = [str(c).strip() for c in dados.columns]
    indicadores.columns = [str(c).strip() for c in indicadores.columns]

    indicadores["CODIGO"] = indicadores["CODIGO"].astype(str).str.strip()
    dados["CODIGO"] = dados["CODIGO"].astype(str).str.strip()

    catalogo = (
        indicadores
        .set_index("CODIGO")
        .to_dict(orient="index")
    )

    anos = [c for c in dados.columns if re.fullmatch(r"\d{4}", c)]

    observacoes = []
    avisos = []

    for _, row in dados.iterrows():
        codigo = texto_limpo(row["CODIGO"])

        if not codigo:
            avisos.append("Linha do histórico sem CODIGO: ignorada.")
            continue

        if codigo not in catalogo:
            avisos.append(
                f"{codigo}: presente no histórico, mas ausente no catálogo; "
                "não será publicado no Painel."
            )
            continue

        for ano in anos:
            raw = texto_limpo(row[ano])

            # Vazios são válidos e não geram observação.
            if raw == "":
                continue

            try:
                valor = normalizar_numero(raw, codigo)
            except ValueError:
                avisos.append(
                    f"{codigo}/{ano}: valor '{raw}' não pôde ser convertido."
                )
                continue

            observacoes.append(
                {
                    "CODIGO": codigo,
                    "ANO": int(ano),
                    "VALOR": valor,
                }
            )

    df_obs = pd.DataFrame(
        observacoes,
        columns=["CODIGO", "ANO", "VALOR"],
    )

    # Guarda o histórico.
    arq_obs = SAIDA_DIR / "observacoes_padronizada.csv"
    df_obs.to_csv(
        arq_obs,
        index=False,
        encoding="utf-8-sig",
        float_format="%.6f",
    )


    # Relatório da execução.
    relatorio = SAIDA_DIR / "relatorio_padronizaçai.txt"
    relatorio.write_text(
        "\n".join(
            [
                "RELATORIO DE PADRONIZAÇAO",
                "=" * 40,
                f"Observacoes padronizdas: {len(df_obs)}",
                "",
                "AVISOS:",
                *([f"- {x}" for x in avisos] if avisos else ["- nenhum"]),
            ]
        ),
        encoding="utf-8",
    )

    print("=" * 62)
    print("PADRONIZAÇAO CONCLUÍDA")
    print("=" * 62)
    print(f"Observações            : {len(df_obs)}")
    print(f"CSV padronizado        : {arq_obs}")
    if avisos:
        print("\nAVISOS")
        print("-" * 62)
        for aviso in avisos:
            print(f"[AVISO] {aviso}")


if __name__ == "__main__":
    main()
