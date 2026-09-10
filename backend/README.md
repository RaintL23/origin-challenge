# Challenge Acciones — Backend API

API REST en **Python + FastAPI** que autentica usuarios, administra acciones preferidas y entrega series temporales de cotización como intermediario seguro hacia [Twelve Data](https://twelvedata.com/).

## Stack

- FastAPI + Uvicorn
- Persistencia mock: `data/db.json` (repositorios abstractos, listos para Postgres)
- Auth: JWT (Bearer) + bcrypt
- Cliente HTTP async: httpx

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

| Variable | Descripción |
| --- | --- |
| `TWELVE_DATA_API_KEY` | API key de Twelve Data |
| `JWT_SECRET` | Secreto para firmar tokens |
| `JWT_EXPIRE_MINUTES` | Expiración del token (default `60`) |
| `CORS_ORIGINS` | Orígenes permitidos, separados por coma |

## Levantar la API

Desde la **raíz del repositorio**:

```bash
python start.py --backend-only
python start.py --api-port 8000
python start.py --install   # fuerza reinstalación de dependencias
```

O desde `backend/` (con venv activo):

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

- Docs OpenAPI: http://localhost:8000/docs
- Health: http://localhost:8000/health

> En el navegador usá `http://localhost:8000` (o `127.0.0.1`). `0.0.0.0` es solo la interfaz de bind; en Windows suele dar `ERR_ADDRESS_INVALID`.

## Usuarios de prueba (seed)

Datos en `data/db.json`:

| Usuario | Password | Display name | Favoritos |
| --- | --- | --- | --- |
| `demo` | `demo123` | Usuario Demo | NFLX, AAPL, MSFT (+ lo que se agregue en runtime) |
| `ana` | `ana123` | Ana Pérez | AMZN, GOOGL, META |
| `bruno` | `bruno123` | Bruno López | NVDA, AMD, INTC |
| `carla` | `carla123` | Carla Gómez | JPM, BAC, V |
| `diego` | `diego123` | Diego Ruiz | DIS, NKE, KO, PEP |

Passwords solo como hashes bcrypt. Ese JSON es a la vez seed y backup de la BD mock.

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
| `GET` | `/health` | No |

Login inválido responde con el mensaje: `"usuario o clave invalida"`.

Parámetros de timeseries:

- `mode`: `realtime` \| `historical`
- `interval`: `1min` \| `5min` \| `15min`
- `start_date` / `end_date`: requeridos en modo `historical`

---

## Arquitectura

```
HTTP → routers → services → repositories / Twelve Data / auth
                                ↓
                          data/db.json
```

| Capa | Carpeta | Rol |
| --- | --- | --- |
| Entrada HTTP | `app/routers/` | Rutas, status codes, Depends |
| Reglas de negocio | `app/services/` | Validaciones, orquestación |
| Persistencia | `app/repositories/` | ABC + impl. JSON |
| Integración externa | `app/integrations/` | Cliente Twelve Data |
| Seguridad | `app/auth/` | JWT Bearer + bcrypt |
| Contratos | `app/schemas/` | Pydantic request/response |
| Cableado | `app/dependencies.py` | Inyección de repos/services |
| App | `app/main.py` | CORS, routers, `/health` |
| Config | `app/config.py` | Settings desde `.env` |

### Árbol relevante

```
backend/
├── .env.example
├── requirements.txt
├── data/
│   └── db.json                 # persistencia mock + seed + backup
└── app/
    ├── main.py
    ├── config.py
    ├── dependencies.py
    ├── auth/
    │   ├── __init__.py         # get_current_user (Bearer → user)
    │   └── security.py         # hash/verify + encode/decode JWT
    ├── routers/
    │   ├── auth.py
    │   ├── favorites.py
    │   └── stocks.py
    ├── services/
    │   ├── auth_service.py
    │   ├── favorite_service.py
    │   └── stock_service.py
    ├── repositories/
    │   └── __init__.py         # JsonStore + ABCs + repos JSON
    ├── integrations/
    │   └── twelvedata.py
    └── schemas/
        ├── auth.py
        ├── favorites.py
        └── stocks.py
```

---

## Mapa feature → código

| Feature del challenge | Endpoint | Dónde mirar |
| --- | --- | --- |
| Login + mensaje inválido | `POST /auth/login` | `routers/auth.py` → `services/auth_service.py` → `auth/security.py` |
| Usuario autenticado | `GET /auth/me` | `routers/auth.py` + `auth/__init__.py` (`get_current_user`) |
| Listar preferidas | `GET /favorites` | `routers/favorites.py` → `favorite_service.py` → `JsonFavoriteRepository` |
| Agregar (símbolo, nombre, moneda) | `POST /favorites` | idem + `schemas/favorites.py` |
| Eliminar símbolo | `DELETE /favorites/{symbol}` | idem (404 si no existe) |
| Autocomplete / búsqueda | `GET /stocks/search?q=` | `routers/stocks.py` → `stock_service.py` → `integrations/twelvedata.py` |
| Datos de una acción (cabecera detalle) | `GET /stocks/{symbol}` | idem |
| Serie tiempo real / histórico | `GET /stocks/{symbol}/timeseries` | idem (`mode`, `interval`, fechas) |
| Health check | `GET /health` | `main.py` |
| Seed / backup | — | `data/db.json` |

---

## Decisiones de diseño (por qué)

| Decisión | Por qué |
| --- | --- |
| **Capas routers → services → repositories** | Separar HTTP, negocio y persistencia mejora mantenibilidad y permite cambiar la BD sin reescribir endpoints (NFR del challenge). |
| **JSON + ABCs en vez de SQL ya** | Arranque local sin Docker/motor SQL; la interfaz de repos permite migrar a PostgreSQL/SQLAlchemy sin tocar routers/services. El enunciado pide relacional; este mock cubre el flujo funcional. |
| **API propia como proxy a Twelve Data** | La API key queda solo en el servidor; el frontend nunca habla con Twelve Data; errores y contratos unificados. |
| **JWT Bearer + bcrypt** | Auth stateless típica de SPA; passwords nunca en texto plano (seguridad pedida en la evaluación). |
| **httpx async en stocks** | I/O de red no bloqueante, alineado con FastAPI. |
| **CORS configurable** | SPA en otro origen (`localhost:5173`); permite header `Authorization`. |
| **Search filtrado en el servidor (NYSE)** | El endpoint de listado de Twelve Data es amplio; filtrar por `q` en la API reduce payload al FE. **Trade-off:** el autocomplete solo cubre NYSE (símbolos solo NASDAQ no aparecen ahí; el detalle por símbolo sí puede resolverlos). |
| **Realtime = rango del día calendario** | Cumple “cotización del día” sin WebSockets; el auto-refresh lo hace el frontend según el intervalo. |
| **Escritura atómica + lock en `JsonStore`** | Evita corrupción del JSON ante escrituras concurrentes (`tmp` + `replace`). |
| **Mensaje de login hardcodeado al enunciado** | Criterio de aceptación literal: `"usuario o clave invalida"`. |

## Extender / migrar

1. Implementar `UserRepository` / `FavoriteRepository` contra Postgres.
2. Registrar la nueva impl. en `dependencies.py`.
3. Routers y services no deberían cambiar.
