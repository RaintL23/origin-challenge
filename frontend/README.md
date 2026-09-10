# Challenge Acciones — Frontend

SPA en **React + TypeScript (Vite)** para login, gestión de acciones preferidas y gráficos de cotización (tiempo real / histórico). Consume exclusivamente la API propia del backend.

## Stack

- React ≥ 18 (Vite)
- TypeScript
- React Router
- TanStack Query
- Highcharts

## Requisitos

- Node.js 20+
- Backend levantado (por defecto en `http://localhost:8000`)

## Setup

```bash
cd frontend
npm install
cp .env.example .env
```

Variable de entorno:

| Variable | Descripción | Default |
| --- | --- | --- |
| `VITE_API_BASE_URL` | URL base del Backend | `http://localhost:8000` |

## Levantar el cliente

Desde la **raíz del repositorio** (API + Frontend juntos):

```bash
python start.py
```

Solo el frontend:

```bash
python start.py --frontend-only
```

O desde esta carpeta:

```bash
npm run dev
```

Abrí http://localhost:5173

Build de producción:

```bash
npm run build
npm run preview
```

## Rutas

| Ruta | Página | Acceso |
| --- | --- | --- |
| `/login` | Login | Público |
| `/acciones` | Mis Acciones | Autenticado |
| `/acciones/:symbol` | Detalle de Acción | Autenticado |

Usuario de prueba (seed del backend): `demo` / `demo123`

## Comportamiento del gráfico

- **Tiempo real:** serie del día; auto-refresh cada `1min` / `5min` / `15min` según el intervalo.
- **Histórico:** requiere desde/hasta; una sola consulta al graficar (sin polling).

## Estructura

```
src/
  api/           # Cliente HTTP (auth, favorites, stocks)
  auth/          # Sesión JWT + rutas protegidas
  components/    # Autocomplete, grilla, formulario, chart, header
  pages/         # Login, Mis Acciones, Detalle
  types/         # Contratos con la API
```
