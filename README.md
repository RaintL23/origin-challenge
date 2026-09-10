# Challenge Acciones

Aplicación web para graficar cotizaciones (tiempo real / histórico), con **Frontend** (React) y **API** (FastAPI), según el enunciado en [`challenge.md`](challenge.md).

## Arranque rápido

1. PostgreSQL con la base `challenge_acciones` y el seed:

```bash
psql -U postgres -c "CREATE DATABASE challenge_acciones;"
psql -U postgres -d challenge_acciones -f backend/data/seed_postgres.sql
```

2. Configurar `backend/.env` (copiá desde `.env.example`) con tu `TWELVE_DATA_API_KEY` y `DATABASE_URL`.

3. Levantar todo:

```bash
python start.py
```

| Servicio | URL |
| --- | --- |
| Frontend | http://localhost:5173 |
| API / docs | http://localhost:8000/docs |

Usuario de prueba: `demo` / `demo123` (también `ana`/`ana123`, `bruno`/`bruno123`, `carla`/`carla123`, `diego`/`diego123`).

```bash
python start.py --install          # fuerza reinstalar deps
python start.py --backend-only     # solo API
python start.py --frontend-only    # solo Vite
python start.py --api-port 8000 --web-port 5173
```

> En el navegador usá `localhost` (no `0.0.0.0`).

## Qué se hizo

1. **Login** con mensaje exacto `"usuario o clave invalida"`.
2. **Mis Acciones**: autocomplete, alta/baja de preferidas (símbolo, nombre, moneda) y navegación al detalle.
3. **Detalle de acción**: cabecera del símbolo + gráfico tiempo real (auto-refresh 1/5/15 min) o histórico (rango desde–hasta).
4. **API propia** como intermediario hacia Twelve Data (la API key no sale al navegador).
5. **Auth** JWT + passwords con bcrypt; favoritos y stocks protegidos.
6. **PostgreSQL** como persistencia real (schema/seed + backup SQL).
7. **Orquestación** con `start.py` y README por proyecto.

Detalle de arquitectura y mapa de código:

- [`backend/README.md`](backend/README.md) — decisiones, capas y dónde vive cada feature de la API
- [`frontend/README.md`](frontend/README.md) — decisiones, rutas y dónde vive cada feature de la UI

## Datos / backup

| Archivo | Rol |
| --- | --- |
| [`backend/data/seed_postgres.sql`](backend/data/seed_postgres.sql) | Crea tablas + inserta usuarios/favoritos de prueba |
| [`backend/data/challenge_acciones_backup.sql`](backend/data/challenge_acciones_backup.sql) | Backup `pg_dump` de la BD |

## Qué quedó fuera (y por qué)

| Fuera de alcance | Motivo |
| --- | --- |
| **SQLAlchemy / Alembic** | El schema está en SQL versionado; `psycopg` alcanza para el alcance del challenge. |
| **Registro de usuarios / admin / roles** | El challenge solo pide login sobre usuarios existentes. |
| **WebSockets / SSE** | “Tiempo real” se resuelve con polling HTTP según el intervalo (1/5/15 min). |
| **Tests automatizados / CI / Docker** | No aportan al demo funcional del flujo. |
| **Cache / rate-limit de Twelve Data** | Debounce en FE y sin polling en histórico cuidan la cuota. |
| **Refresh tokens, logout server-side, i18n, design system** | Fuera del alcance funcional; UI no se evalúa. |

## Proyectos

| Carpeta | Rol |
| --- | --- |
| [`backend/`](backend/README.md) | API FastAPI + PostgreSQL |
| [`frontend/`](frontend/README.md) | SPA React + Vite |
| [`start.py`](start.py) | Levanta ambos desde la raíz |
| [`challenge.md`](challenge.md) | Enunciado original |
