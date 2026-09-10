#!/usr/bin/env python3
"""Levanta el backend desde la raíz del repositorio en un solo comando."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
import venv
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BACKEND = ROOT / "backend"
VENV_DIR = BACKEND / ".venv"
REQUIREMENTS = BACKEND / "requirements.txt"
ENV_FILE = BACKEND / ".env"
ENV_EXAMPLE = BACKEND / ".env.example"


def venv_python() -> Path:
    if sys.platform == "win32":
        return VENV_DIR / "Scripts" / "python.exe"
    return VENV_DIR / "bin" / "python"


def ensure_venv() -> tuple[Path, bool]:
    python = venv_python()
    created = False
    if not python.exists():
        print(f"Creando entorno virtual en {VENV_DIR} ...")
        venv.create(VENV_DIR, with_pip=True)
        created = True
    return python, created


def deps_installed(python: Path) -> bool:
    result = subprocess.run(
        [str(python), "-c", "import fastapi, uvicorn, httpx, jose, bcrypt, pydantic_settings"],
        cwd=BACKEND,
        capture_output=True,
    )
    return result.returncode == 0


def ensure_deps(python: Path, *, force: bool) -> None:
    if not force and deps_installed(python):
        return
    print("Instalando / actualizando dependencias ...")
    subprocess.check_call(
        [str(python), "-m", "pip", "install", "-r", str(REQUIREMENTS)],
        cwd=BACKEND,
    )


def ensure_env() -> None:
    if ENV_FILE.exists():
        return
    if not ENV_EXAMPLE.exists():
        raise SystemExit(f"No existe {ENV_EXAMPLE}")
    ENV_FILE.write_text(ENV_EXAMPLE.read_text(encoding="utf-8"), encoding="utf-8")
    print(f"Creado {ENV_FILE} desde .env.example — editá TWELVE_DATA_API_KEY y JWT_SECRET.")


def run_server(python: Path, host: str, port: str) -> None:
    print(f"API en http://localhost:{port}  |  docs: http://localhost:{port}/docs")
    cmd = [
        str(python),
        "-m",
        "uvicorn",
        "app.main:app",
        "--reload",
        "--host",
        host,
        "--port",
        port,
    ]
    subprocess.check_call(cmd, cwd=BACKEND)


def main() -> None:
    parser = argparse.ArgumentParser(description="Levantar la API Challenge Acciones")
    parser.add_argument("--host", default=os.environ.get("HOST", "0.0.0.0"))
    parser.add_argument("--port", default=os.environ.get("PORT", "8000"))
    parser.add_argument(
        "--install",
        action="store_true",
        help="Forzar reinstalación de requirements.txt",
    )
    args = parser.parse_args()

    if not BACKEND.is_dir():
        raise SystemExit(f"No se encontró la carpeta backend en {ROOT}")

    python, created = ensure_venv()
    ensure_deps(python, force=args.install or created)
    ensure_env()
    run_server(python, args.host, args.port)


if __name__ == "__main__":
    main()
