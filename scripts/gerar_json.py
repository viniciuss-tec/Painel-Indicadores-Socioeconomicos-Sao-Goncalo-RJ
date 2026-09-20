"""
Organiza os dados padronizados para consumo do frontend.

Entrada:
    data/indicadores.csv
    data/dados_processados/observacoes_normalizadas.csv

Saída:
    data/dados_processados/indicadores.json
    front/data/indicadores.json

Uso:
    python scripts/gerar_json.py

O JSON é um artefato e não precisa ser gerado a cada acesso ao site.
"""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[1]

ARQ_INDICADORES = ROOT / "data" / "indicadores.csv"
ARQ_OBSERVACOES = ROOT / "data" / "dados_processados" / "observacoes_normalizadas.csv"

SAIDA_PROCESSADO = ROOT / "data" / "dados_processados" / "indicadores.json"
SAIDA_FRONT = ROOT / "front" / "data" / "indicadores.json"


def texto_limpo(value) -> str:
    if value is None or pd.isna(value):
        return ""
    return str(value).strip()


def main():
    if not ARQ_OBSERVACOES.exists():
        raise FileNotFoundError(
            "Arquivo não encontrado. Execute primeiro:\n"
            "python scripts/padronizar_dados.py"
        )

    indicadores = pd.read_csv(
        ARQ_INDICADORES,
        dtype=str,
        keep_default_na=False,
    )

    observacoes = pd.read_csv(
        ARQ_OBSERVACOES,
        dtype={"CODIGO": str},
    )

    indicadores.columns = [str(c).strip() for c in indicadores.columns]
    indicadores["CODIGO"] = indicadores["CODIGO"].astype(str).str.strip()

    observacoes["CODIGO"] = observacoes["CODIGO"].astype(str).str.strip()

    catalogo = indicadores.set_index("CODIGO").to_dict(orient="index")

    resultado = []

    for codigo, meta in catalogo.items():
        serie_df = (
            observacoes[observacoes["CODIGO"] == codigo]
            .sort_values("ANO")
        )

        dados = []
        for _, linha in serie_df.iterrows():
            valor = linha["VALOR"]

            if pd.isna(valor):
                continue

            dados.append(
                {
                    "ano": int(linha["ANO"]),
                    "valor": float(valor),
                }
            )

        ultimo_ano = dados[-1]["ano"] if dados else None
        ultimo_valor = dados[-1]["valor"] if dados else None

        resultado.append(
            {
                "codigo": codigo,
                "tema": texto_limpo(meta.get("TEMA")),
                "nome": texto_limpo(meta.get("INDICADOR")),
                "unidade": texto_limpo(meta.get("UNIDADE")),
                "definicao": texto_limpo(meta.get("DEFINICAO")),
                "uso": texto_limpo(meta.get("USO")),
                "metodologia": texto_limpo(meta.get("METODOLOGIA")),
                "periodicidade": texto_limpo(meta.get("PERIODICIDADE")),
                "fonte": texto_limpo(meta.get("FONTE")),
                "criado_em": texto_limpo(meta.get("CRIADO EM")),
                "atualizado_em": texto_limpo(meta.get("ATUALIZADO EM")),
                "ultimo_ano": ultimo_ano,
                "ultimo_valor": ultimo_valor,
                "dados": dados,
            }
        )

    temas = []
    for indicador in resultado:
        tema = indicador["tema"]
        if tema and tema not in temas:
            temas.append(tema)

    payload = {
        "gerado_em": datetime.now().isoformat(timespec="seconds"),
        "fonte_local": "indicadores.csv + observacoes_normalizadas.csv",
        "temas": temas,
        "indicadores": resultado,
    }

    for destino in (SAIDA_PROCESSADO, SAIDA_FRONT):
        destino.parent.mkdir(parents=True, exist_ok=True)
        destino.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    print("=" * 62)
    print("JSON DO FRONTEND GERADO")
    print("=" * 62)
    print(f"Indicadores: {len(resultado)}")
    print(f"Temas      : {len(temas)}")
    print(f"Saída      : {SAIDA_FRONT}")


if __name__ == "__main__":
    main()
