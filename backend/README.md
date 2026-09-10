# Challenge Acciones — Backend API

API REST en **Python + FastAPI** que autentica usuarios, administra acciones preferidas y entrega series temporales de cotización como intermediario seguro hacia [Twelve Data](https://twelvedata.com/).

## Stack (fase actual)

- FastAPI + Uvicorn
- Persistencia mock: `data/db.json`
- Auth: JWT (Bearer) + bcrypt
- Cliente HTTP: httpx

> **TODO (entrega final):** migrar a PostgreSQL con SQLAlchemy (async) + Alembic, seed y backup de BD, manteniendo la misma interfaz de repositories.

## Requisitos

- Python 3.10+
- API key de Twelve Data ([api.twelvedata.com](https://api.twelvedata.com/))

## Setup

```bash
cd backend
python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux / macOS
# source .venv/bin/activate

pip install -r requirements.txt
cp .env.example .env
```

Editar `.env` y completar al menos:

| Variable | Descripción |
| --- | --- |
| `TWELVE_DATA_API_KEY` | API key de Twelve Data |
| `JWT_SECRET` | Secreto para firmar tokens |
| `JWT_EXPIRE_MINUTES` | Expiración del token (default `60`) |
| `CORS_ORIGINS` | Orígenes permitidos, separados por coma |

## Levantar la API

Desde la **raíz del repositorio** (crea venv, instala deps y copia `.env` si falta):

```bash
python start.py
```

Opciones útiles:

```bash
python start.py --port 8000
python start.py --install   # fuerza reinstalación de dependencias
```

También desde `backend/` (con venv activo):

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

- Docs OpenAPI: http://localhost:8000/docs
- Health: http://localhost:8000/health

## Usuario de prueba (seed)

| Usuario | Password | Display name |
| --- | --- | --- |
| `demo` | `demo123` | Usuario Demo |

Favoritos iniciales: `TSLA`, `NFLX`.

## Endpoints

| Método | Ruta | Auth |
| --- | --- | --- |
| `POST` | `/auth/login` | No |
| `GET` | `/auth/me` | Sí |
| `GET` | `/favorites` | Sí |
| `POST` | `/favorites` | Sí |
| `DELETE` | `/favorites/{symbol}` | Sí |
| `GET` | `/stocks/search?q=` | Sí |
| `GET` | `/stocks/{symbol}` | Sí |
| `GET` | `/stocks/{symbol}/timeseries` | Sí |

Login inválido responde con el mensaje: `"usuario o clave invalida"`.

Parámetros de timeseries:

- `mode`: `realtime` | `historical`
- `interval`: `1min` | `5min` | `15min`
- `start_date` / `end_date`: requeridos en modo `historical`

## Arquitectura

```
routers → services → repositories / Twelve Data / auth
                         ↓
                   data/db.json
```

Los repositories exponen una interfaz común para poder reemplazar el mock JSON por PostgreSQL sin tocar routers/services.
