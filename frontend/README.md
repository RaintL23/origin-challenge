# Challenge Acciones — Frontend

SPA en **React + TypeScript (Vite)** para login, gestión de acciones preferidas y gráficos de cotización (tiempo real / histórico). Consume **solo** la API propia del backend (nunca Twelve Data directo).

## Stack

- React ≥ 18 (Vite) + TypeScript
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

| Variable | Descripción | Default |
| --- | --- | --- |
| `VITE_API_BASE_URL` | URL base del Backend | `http://localhost:8000` |

## Levantar el cliente

Desde la **raíz del repositorio**:

```bash
python start.py                 # API + Frontend
python start.py --frontend-only
```

O desde esta carpeta:

```bash
npm run dev
```

Abrí http://localhost:5173

```bash
npm run build
npm run preview
```

Usuario de prueba (seed del backend): `demo` / `demo123`

## Rutas

| Ruta | Página | Acceso | Archivo |
| --- | --- | --- | --- |
| `/login` | Login | Público | `pages/LoginPage.tsx` |
| `/acciones` | Mis Acciones | Autenticado | `pages/FavoritesPage.tsx` |
| `/acciones/:symbol` | Detalle de Acción | Autenticado | `pages/StockDetailPage.tsx` |
| `/` y `*` | Redirect a Mis Acciones | — | `App.tsx` |

Las rutas autenticadas pasan por `auth/ProtectedRoute.tsx`.

## Comportamiento del gráfico

- **Tiempo real:** serie del día; `refetchInterval` cada `1min` / `5min` / `15min` según el intervalo elegido.
- **Histórico:** requiere desde/hasta; una sola consulta al graficar (sin polling, para no gastar cuota de Twelve Data).
- Al pasar a histórico se limpia la query activa y se corta el poll.

---

## Arquitectura

```
pages  →  components  →  api/*  →  Backend
   ↑           ↑
 auth/     types/api.ts
```

| Carpeta | Rol |
| --- | --- |
| `src/pages/` | Pantallas (orquestan queries/mutations y layout) |
| `src/components/` | UI reutilizable (header, autocomplete, grilla, form, chart) |
| `src/api/` | Cliente HTTP tipado por dominio |
| `src/auth/` | Sesión JWT, storage y guard de rutas |
| `src/types/` | Contratos TypeScript alineados al backend |

### Árbol de `src/`

```
src/
├── main.tsx                 # QueryClient + Router + AuthProvider
├── App.tsx                  # Definición de rutas
├── index.css                # Estilos globales (sin UI kit)
├── api/
│   ├── client.ts            # fetch + Bearer + ApiError
│   ├── auth.ts
│   ├── favorites.ts
│   └── stocks.ts
├── auth/
│   ├── AuthContext.tsx      # login / logout / user en memoria
│   ├── ProtectedRoute.tsx   # redirect a /login si no hay sesión
│   └── storage.ts           # localStorage (token + user)
├── components/
│   ├── Header.tsx           # nombre usuario + Salir
│   ├── Autocomplete.tsx     # debounce + search
│   ├── StockGrid.tsx        # tabla preferidas + Eliminar
│   ├── ChartForm.tsx        # modo / intervalo / fechas
│   └── PriceChart.tsx       # Highcharts (serie close)
├── pages/
│   ├── LoginPage.tsx
│   ├── FavoritesPage.tsx
│   └── StockDetailPage.tsx
└── types/
    └── api.ts
```

---

## Mapa feature → código

| Feature del challenge | UI | API FE | Notas |
| --- | --- | --- | --- |
| Login + error inválido | `LoginPage.tsx` + `AuthContext.tsx` | `api/auth.ts` → `POST /auth/login` | Mensaje fijo del enunciado |
| Nombre en cabecera | `Header.tsx` | user desde storage / login | — |
| Mis Acciones (lista) | `FavoritesPage.tsx` + `StockGrid.tsx` | `api/favorites.ts` → `GET /favorites` | React Query |
| Autocomplete | `Autocomplete.tsx` | `api/stocks.ts` → `GET /stocks/search` | Debounce 300 ms |
| Agregar símbolo | `FavoritesPage.tsx` | `POST /favorites` | Invalida query de favoritos |
| Eliminar | `StockGrid.tsx` | `DELETE /favorites/{symbol}` | Idem |
| Ir al detalle | link en `StockGrid.tsx` | — | Ruta `/acciones/:symbol` |
| Cabecera del detalle | `StockDetailPage.tsx` | `GET /stocks/{symbol}` | — |
| Parámetros del gráfico | `ChartForm.tsx` | — | modo, intervalo, datetime-local |
| Dibujar serie | `PriceChart.tsx` | `GET .../timeseries` | Highcharts |
| Auto-refresh realtime | `StockDetailPage.tsx` (`POLL_MS` + `refetchInterval`) | mismo endpoint | Histórico sin poll |
| Guard de sesión | `ProtectedRoute.tsx` | — | Sin token → `/login` |
| Persistencia de sesión | `auth/storage.ts` | — | Sobrevive al refresh del browser |

---

## Decisiones de diseño (por qué)

| Decisión | Por qué |
| --- | --- |
| **React + Vite + TypeScript** | Stack permitido por el enunciado (React ≥ 18); Vite da DX rápida para una evaluación. |
| **Solo hablar con la API propia** | Seguridad: la key de Twelve Data no viaja al browser; un solo contrato de errores. |
| **TanStack Query** | Cache, invalidación tras altas/bajas, y `refetchInterval` para tiempo real sin `setInterval` manual. |
| **AuthContext + localStorage** | Sesión simple para el challenge; sobrevive F5; sin refresh tokens (fuera de alcance). |
| **Cliente `fetch` propio** (`api/client.ts`) | Menos dependencias; parsea `detail` de FastAPI y errores HTTP de forma uniforme (`ApiError`). |
| **Highcharts** | Opción sugerida en el enunciado; serie datetime lista con el wrapper React oficial. |
| **Polling solo en realtime** | Cumple el auto-refresh del enunciado; en histórico una sola request evita quemar la cuota diaria. |
| **Debounce 300 ms en autocomplete** | Evita un storm de `/stocks/search` mientras se tipea. |
| **Páginas delgadas + componentes por responsabilidad** | Facilita ubicar UI (form/chart/grid) vs orquestación (pages) vs red (api). |
| **CSS único sin design system** | El challenge no evalúa diseño; se prioriza claridad funcional. |
| **Rutas en español (`/acciones`)** | Alineado al copy del enunciado (“Mis Acciones”). |

## Flujo rápido de lectura

1. Entrada: `main.tsx` → `App.tsx` (rutas).
2. Login: `LoginPage` → `AuthContext.login` → token en `storage`.
3. Preferidas: `FavoritesPage` arma Autocomplete + grilla; mutaciones en `api/favorites.ts`.
4. Detalle: `StockDetailPage` carga meta + `ChartForm`; al graficar activa query de timeseries y, si es realtime, el poll.
