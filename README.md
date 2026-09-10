# Challenge Acciones

Aplicación web para graficar cotizaciones (tiempo real / histórico), con **Frontend** (React) y **API** (FastAPI), según el enunciado en [`challenge.md`](challenge.md).

## Arranque rápido

```bash
python start.py
```

Prepara (si hace falta) el venv del backend, `npm install` del frontend, copia `.env` desde los examples y levanta ambos:

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

> En el navegador usá `localhost` (no `0.0.0.0`). Editá `backend/.env` con tu `TWELVE_DATA_API_KEY`.

## Qué se hizo

Se implementó el flujo completo del cliente:

1. **Login** con mensaje exacto `"usuario o clave invalida"`.
2. **Mis Acciones**: autocomplete, alta/baja de preferidas (símbolo, nombre, moneda) y navegación al detalle.
3. **Detalle de acción**: cabecera del símbolo + gráfico tiempo real (auto-refresh 1/5/15 min) o histórico (rango desde–hasta).
4. **API propia** como intermediario hacia Twelve Data (la API key no sale al navegador).
5. **Auth** JWT + passwords con bcrypt; favoritos y stocks protegidos.
6. **Seed** multi-usuario en `backend/data/db.json` (ese archivo es también el “backup” de la BD mock).
7. **Orquestación** con `start.py` y README por proyecto.

Detalle de arquitectura y mapa de código:

- [`backend/README.md`](backend/README.md) — decisiones, capas y dónde vive cada feature de la API
- [`frontend/README.md`](frontend/README.md) — decisiones, rutas y dónde vive cada feature de la UI

## Qué quedó fuera (y por qué)

El objetivo del challenge es una app funcional, estable y con buena estructura. Varias piezas habituales de producción **no hacen falta para demostrar ese objetivo** y se dejaron fuera a propósito:

| Fuera de alcance | Motivo |
| --- | --- |
| **PostgreSQL / SQLAlchemy / Alembic** | El enunciado pide BD relacional; la app usa `db.json` con repositorios abstractos listos para swap. Cumple login, favoritos y seed sin instalar motor SQL. Migrar a Postgres es el siguiente paso natural, no un requisito para ejercitar el flujo. |
| **Backup SQL / dumps** | El seed versionado en `backend/data/db.json` cubre “datos mínimos + backup” en este mock. |
| **Registro de usuarios / admin / roles** | El challenge solo pide login sobre usuarios existentes. |
| **WebSockets / SSE** | “Tiempo real” se resuelve con polling HTTP según el intervalo (1/5/15 min), como pide el enunciado. |
| **Tests automatizados / CI / Docker** | No aportan al demo funcional del flujo; el foco fue estructura, seguridad básica y NFR de mantenibilidad vía capas. |
| **Cache / rate-limit de Twelve Data** | La cuota (800/día) se cuida con debounce en el FE y sin polling en histórico; un cache server-side sería optimización, no requisito. |
| **Refresh tokens, logout server-side, i18n, design system** | Fuera del alcance funcional; UI no se evalúa. |
| **Observabilidad (métricas, tracing)** | Innecesaria para levantar y demostrar el challenge en local. |

En resumen: se priorizó **funcionalidad del enunciado + estructura extensible + seguridad mínima (JWT, bcrypt, key solo en backend)** sobre infraestructura de producción.

## Proyectos

| Carpeta | Rol |
| --- | --- |
| [`backend/`](backend/README.md) | API FastAPI |
| [`frontend/`](frontend/README.md) | SPA React + Vite |
| [`start.py`](start.py) | Levanta ambos desde la raíz |
| [`challenge.md`](challenge.md) | Enunciado original |
