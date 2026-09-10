# Challenge Acciones

Aplicación web para graficar cotizaciones (tiempo real / histórico), con **Frontend** (React) y **API** (FastAPI).

## Arranque rápido (un solo comando)

Desde la raíz del repositorio:

```bash
python start.py
```

Eso prepara (si hace falta) el venv del backend, `npm install` del frontend, copia `.env` desde los examples, y levanta:

| Servicio | URL |
| --- | --- |
| Frontend | http://localhost:5173 |
| API / docs | http://localhost:8000/docs |

Usuario de prueba: `demo` / `demo123` (también `ana`/`ana123`, `bruno`/`bruno123`, `carla`/`carla123`, `diego`/`diego123`)

### Opciones útiles

```bash
python start.py --install          # fuerza reinstalar deps
python start.py --backend-only     # solo API
python start.py --frontend-only    # solo Vite
python start.py --api-port 8000 --web-port 5173
```

> En el navegador usá `localhost` (no `0.0.0.0`). Editá `backend/.env` con tu `TWELVE_DATA_API_KEY`.

## Proyectos

- [`backend/`](backend/README.md) — API FastAPI
- [`frontend/`](frontend/README.md) — SPA React + Vite
