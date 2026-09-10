#!/usr/bin/env python3
"""Levanta backend y frontend desde la raíz del repositorio en un solo comando."""

from __future__ import annotations

import argparse
import os
import shutil
import signal
import subprocess
import sys
import time
import venv
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BACKEND = ROOT / "backend"
FRONTEND = ROOT / "frontend"
VENV_DIR = BACKEND / ".venv"
REQUIREMENTS = BACKEND / "requirements.txt"
BACKEND_ENV = BACKEND / ".env"
BACKEND_ENV_EXAMPLE = BACKEND / ".env.example"
FRONTEND_ENV = FRONTEND / ".env"
FRONTEND_ENV_EXAMPLE = FRONTEND / ".env.example"
FRONTEND_NODE_MODULES = FRONTEND / "node_modules"


def venv_python() -> Path:
    if sys.platform == "win32":
        return VENV_DIR / "Scripts" / "python.exe"
    return VENV_DIR / "bin" / "python"


def ensure_backend_venv() -> tuple[Path, bool]:
    python = venv_python()
    created = False
    if not python.exists():
        print(f"Creando entorno virtual en {VENV_DIR} ...")
        venv.create(VENV_DIR, with_pip=True)
        created = True
    return python, created


def backend_deps_installed(python: Path) -> bool:
    result = subprocess.run(
        [
            str(python),
            "-c",
            "import fastapi, uvicorn, httpx, jose, bcrypt, pydantic_settings, psycopg, psycopg_pool",
        ],
        cwd=BACKEND,
        capture_output=True,
    )
    return result.returncode == 0


def ensure_backend_deps(python: Path, *, force: bool) -> None:
    if not force and backend_deps_installed(python):
        return
    print("Instalando / actualizando dependencias del backend ...")
    subprocess.check_call(
        [
            str(python),
            "-m",
            "pip",
            "install",
            "--trusted-host",
            "pypi.org",
            "--trusted-host",
            "files.pythonhosted.org",
            "-r",
            str(REQUIREMENTS),
        ],
        cwd=BACKEND,
    )


def ensure_env_file(target: Path, example: Path, label: str) -> None:
    if target.exists():
        return
    if not example.exists():
        raise SystemExit(f"No existe {example}")
    target.write_text(example.read_text(encoding="utf-8"), encoding="utf-8")
    print(f"Creado {target} desde {example.name} ({label}).")


def find_npm() -> str:
    npm = shutil.which("npm")
    if not npm:
        raise SystemExit(
            "No se encontró npm en el PATH. Instalá Node.js 20+ para levantar el frontend."
        )
    return npm


def ensure_frontend_deps(*, force: bool) -> str:
    npm = find_npm()
    if force or not FRONTEND_NODE_MODULES.is_dir():
        print("Instalando / actualizando dependencias del frontend ...")
        subprocess.check_call([npm, "install"], cwd=FRONTEND)
    return npm


def start_backend(python: Path, host: str, port: str) -> subprocess.Popen[str]:
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
    return subprocess.Popen(cmd, cwd=BACKEND)


def start_frontend(npm: str, port: str, api_url: str) -> subprocess.Popen[str]:
    env = os.environ.copy()
    env.setdefault("VITE_API_BASE_URL", api_url)
    cmd = [npm, "run", "dev", "--", "--host", "0.0.0.0", "--port", port]
    return subprocess.Popen(cmd, cwd=FRONTEND, env=env)


def terminate_processes(procs: list[subprocess.Popen[str]]) -> None:
    for proc in procs:
        if proc.poll() is not None:
            continue
        proc.terminate()
    deadline = time.time() + 5
    for proc in procs:
        remaining = max(0, deadline - time.time())
        try:
            proc.wait(timeout=remaining)
        except subprocess.TimeoutExpired:
            proc.kill()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Levantar Challenge Acciones (API + Frontend) desde la raíz"
    )
    parser.add_argument("--host", default=os.environ.get("HOST", "0.0.0.0"))
    parser.add_argument("--api-port", default=os.environ.get("API_PORT", "8000"))
    parser.add_argument("--web-port", default=os.environ.get("WEB_PORT", "5173"))
    parser.add_argument(
        "--backend-only",
        action="store_true",
        help="Solo levantar la API",
    )
    parser.add_argument(
        "--frontend-only",
        action="store_true",
        help="Solo levantar el frontend",
    )
    parser.add_argument(
        "--install",
        action="store_true",
        help="Forzar reinstalación de dependencias",
    )
    # Compatibilidad con el flag anterior
    parser.add_argument("--port", dest="api_port", help=argparse.SUPPRESS)
    args = parser.parse_args()

    if args.backend_only and args.frontend_only:
        raise SystemExit("Usá solo una de --backend-only / --frontend-only")

    run_backend = not args.frontend_only
    run_frontend = not args.backend_only

    if run_backend and not BACKEND.is_dir():
        raise SystemExit(f"No se encontró la carpeta backend en {ROOT}")
    if run_frontend and not FRONTEND.is_dir():
        raise SystemExit(f"No se encontró la carpeta frontend en {ROOT}")

    procs: list[subprocess.Popen[str]] = []
    python: Path | None = None
    npm: str | None = None

    if run_backend:
        python, created = ensure_backend_venv()
        ensure_backend_deps(python, force=args.install or created)
        ensure_env_file(
            BACKEND_ENV,
            BACKEND_ENV_EXAMPLE,
            "editá TWELVE_DATA_API_KEY, JWT_SECRET y DATABASE_URL",
        )

    if run_frontend:
        npm = ensure_frontend_deps(force=args.install)
        ensure_env_file(
            FRONTEND_ENV,
            FRONTEND_ENV_EXAMPLE,
            f"API en http://localhost:{args.api_port}",
        )

    api_url = f"http://localhost:{args.api_port}"
    web_url = f"http://localhost:{args.web_port}"

    print()
    if run_backend:
        print(f"API docs:  {api_url}/docs")
    if run_frontend:
        print(f"Frontend:  {web_url}")
    print("Ctrl+C para detener.\n")

    try:
        if run_backend and python is not None:
            procs.append(start_backend(python, args.host, args.api_port))
        if run_frontend and npm is not None:
            procs.append(start_frontend(npm, args.web_port, api_url))

        while True:
            for proc in procs:
                code = proc.poll()
                if code is not None:
                    raise SystemExit(f"Un proceso salió con código {code}")
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("\nDeteniendo procesos ...")
    finally:
        terminate_processes(procs)


if __name__ == "__main__":
    # Evita que Ctrl+C mate solo el padre sin cleanup en algunos entornos
    signal.signal(signal.SIGINT, signal.default_int_handler)
    main()
