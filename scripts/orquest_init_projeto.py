"""
Inicializador do Projeto de Índices Socioeconômicos de São Gonçalo - RJ.
O que ele deve executar com sucesso para nao cair nas linhsa de erro:

1. Cria .venv se necessário.
2. Usa diretamente o Python do .venv (não depende de ativação do shell).
3. Instala as dependências de requirements.txt quando necessário.
4. Verifica pandas.
5. Valida os dados.
6. Normaliza os dados.
7. Gera o JSON do frontend.
8. Inicia o servidor local.
9. Abre o navegador.

Uso:
    python scripts/orquest_init_projeto.py
"""

from __future__ import annotations

import hashlib
import subprocess
import sys
import time
import urllib.request
import webbrowser
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VENV_DIR = ROOT / ".venv"
REQUIREMENTS = ROOT / "requirements.txt"
STAMP = VENV_DIR / ".requirements.sha256"
SCRIPTS = ROOT / "scripts"

HOST = "127.0.0.1"
PORT = 8000
URL = f"http://{HOST}:{PORT}"



def python_venv() -> Path:
    """Retorna o executável Python do venv."""
    if sys.platform == "win32":
        return VENV_DIR / "Scripts" / "python.exe"
    return VENV_DIR / "bin" / "python"



def executar(comando: list[str], nome: str) -> None:
    """Executa um comando e interrompe o fluxo se houver falha."""
    print("\n" + "=" * 64)
    print(nome)
    print("=" * 64)

    resultado = subprocess.run(comando, cwd=ROOT)

    if resultado.returncode != 0:
        raise SystemExit(
            f"\nERRO: {nome} falhou. "
            f"Código de saída: {resultado.returncode}"
        )



def hash_requirements() -> str:
    """Gera uma assinatura do requirements.txt."""
    return hashlib.sha256(REQUIREMENTS.read_bytes()).hexdigest()



def dependencias_precisam_ser_instaladas() -> bool:
    """Instala novamente somente quando requirements.txt mudar."""
    if not STAMP.exists():
        return True
    return STAMP.read_text(encoding="utf-8").strip() != hash_requirements()



def preparar_ambiente() -> Path:
    """Cria .venv e garante que as dependências estejam instaladas."""
    if not REQUIREMENTS.exists():
        raise SystemExit(
            f"ERRO: requirements.txt não encontrado em {REQUIREMENTS}"
        )

    py = python_venv()

    if not py.exists():
        print("\n" + "=" * 64)
        print("ETAPA 1 — CRIANDO AMBIENTE VIRTUAL")
        print("=" * 64)

        executar(
            [sys.executable, "-m", "venv", str(VENV_DIR)],
            "Criação do .venv",
        )
    else:
        print("[OK] Ambiente virtual já existe.")

    if dependencias_precisam_ser_instaladas():
        print("\n" + "=" * 64)
        print("ETAPA 2/3 — CONFIGURANDO O AMBIENTE E INSTALANDO DEPENDÊNCIAS")
        print("=" * 64)
        print(f"Python usado: {py}")

        executar(
            [py.as_posix(), "-m", "pip", "install", "-r", str(REQUIREMENTS)],
            "Instalação das dependências",
        )

        STAMP.write_text(hash_requirements(), encoding="utf-8")
    else:
        print("[OK] Dependências já estão atualizadas.")
        print(f"[OK] Python do projeto: {py}")

    teste = subprocess.run(
        [
            str(py),
            "-c",
            "import pandas as pd; print(pd.__version__)",
        ],
        cwd=ROOT,
        capture_output=True,
        text=True,
    )

    if teste.returncode != 0:
        print(teste.stdout)
        print(teste.stderr)
        raise SystemExit(
            "ERRO: pandas não está disponível no ambiente virtual."
        )

    print(f"[OK] pandas {teste.stdout.strip()}")
    return py



def servidor_pronto(timeout: float = 8.0) -> bool:
    """Espera até o servidor HTTP responder."""
    limite = time.time() + timeout

    while time.time() < limite:
        try:
            with urllib.request.urlopen(URL, timeout=0.5) as resposta:
                return resposta.status < 500
        except Exception:
            time.sleep(0.2)

    return False



def main() -> None:
    print("=" * 64)
    print("PROJETO DE ÍNDICES SOCIOECONÔMICOS DE SÃO GONÇALO - RJ")
    print("=" * 64)

    py = preparar_ambiente()

    executar(
        [str(py), str(SCRIPTS / "validar_dados.py")],
        "VALIDAÇÃO DOS DADOS",
    )

    executar(
        [str(py), str(SCRIPTS / "padronizar_dados.py")],
        "NORMALIZAÇÃO DOS DADOS",
    )

    executar(
        [str(py), str(SCRIPTS / "gerar_json.py")],
        "GERAÇÃO DO JSON DO FRONTEND",
    )

    print("\n" + "=" * 64)
    print("INICIANDO SITE")
    print("=" * 64)

    servidor = subprocess.Popen(
        [str(py), str(SCRIPTS / "exibir_front.py")],
        cwd=ROOT,
    )

    if not servidor_pronto():
        servidor.terminate()
        raise SystemExit(
            "ERRO: o servidor não respondeu no tempo esperado."
        )

    print(f"Site: {URL}")
    print("Abrindo o navegador...")
    webbrowser.open(URL)
    print("Pressione Ctrl+C para encerrar.")

    try:
        servidor.wait()
    except KeyboardInterrupt:
        print("\nEncerrando o servidor...")
        servidor.terminate()
        try:
            servidor.wait(timeout=3)
        except subprocess.TimeoutExpired:
            servidor.kill()


if __name__ == "__main__":
    main()
