# Análisis Backend — Challenge Acciones

Documento de diseño técnico del API. Define stack, arquitectura, responsabilidades, casos de uso e intencionalidad.

---

## Objetivo

Exponer una API REST que autentique usuarios, administre acciones preferidas y entregue series temporales de cotización, actuando como intermediario seguro entre el Frontend y Twelve Data.

---

## Stack

| Componente | Tecnología | Motivo |
| --- | --- | --- |
| Framework | Python + FastAPI | Requerido por el challenge; tipado, documentación OpenAPI automática y buen rendimiento async |
| Persistencia (fase actual) | **JSON mock** (`data/db.json`) | Acelera el desarrollo y facilita testear el Backend sin levantar PostgreSQL |
| Persistencia (objetivo) | PostgreSQL | Relacional, estable; requerida para la entrega final del challenge |
| Acceso a datos | Repositories con interfaz común | Permite cambiar JSON → PostgreSQL sin tocar routers/services |
| Auth | JWT (Bearer) + hash de passwords (bcrypt/argon2) | Stateless, escalable y alineado a seguridad del challenge |
| Cliente HTTP | httpx | Consumo async de Twelve Data |
| Configuración | Variables de entorno (`.env`) | No hardcodear API keys ni credenciales |

> **TODO:** Crear la base de datos real en **PostgreSQL** (esquema, migraciones, seed y backup) y reemplazar el repositorio JSON por SQLAlchemy + Alembic, manteniendo la misma interfaz de repositories.

---

## Arquitectura

Arquitectura en capas, con separación clara de responsabilidades. En esta fase el repositorio lee/escribe un archivo JSON; la forma de las capas no cambia cuando se migre a PostgreSQL.

```
Frontend
   │  HTTP / JSON
   ▼
┌─────────────────────────────────────┐
│  API (FastAPI)                      │
│  ┌─────────┐  ┌──────────────────┐  │
│  │ Routers │→ │ Services         │  │
│  └─────────┘  └────────┬─────────┘  │
│                        │            │
│           ┌────────────┼──────────┐ │
│           ▼            ▼          ▼ │
│     Repositories   TwelveData   Auth│
│           │                         │
│           ▼                         │
│     data/db.json  (mock)            │
│     TODO → PostgreSQL               │
└─────────────────────────────────────┘
```

| Capa | Responsabilidad |
| --- | --- |
| **Routers** | Endpoints HTTP, validación de entrada (Pydantic), códigos de respuesta |
| **Services** | Reglas de negocio (login, preferidas, modos tiempo real / histórico) |
| **Repositories** | Acceso a datos (CRUD de usuarios y acciones preferidas). Hoy: JSON. Luego: PostgreSQL |
| **Integrations** | Cliente Twelve Data (`stocks`, `time_series`) |
| **Auth** | Login, emisión/validación de JWT, protección de rutas |

### Persistencia mock (fase actual)

Archivo sugerido: `data/db.json`

```json
{
  "users": [
    {
      "id": 1,
      "username": "demo",
      "password_hash": "<hash>",
      "display_name": "Usuario Demo",
      "created_at": "2026-01-01T00:00:00Z"
    }
  ],
  "favorite_stocks": [
    {
      "id": 1,
      "user_id": 1,
      "symbol": "TSLA",
      "name": "Tesla Inc",
      "currency": "USD",
      "created_at": "2026-01-01T00:00:00Z"
    }
  ]
}
```

Reglas del mock:

- Unique lógico `(user_id, symbol)` al agregar preferidas.
- Lectura/escritura atómica del archivo (cargar → mutar → guardar).
- Suficiente para probar login, favoritos y el resto del API de forma aislada.

### Modelo de datos (mínimo) — mismo contrato para JSON y PostgreSQL

- **users**: id, username, password_hash, display_name, created_at  
- **favorite_stocks**: id, user_id, symbol, name, currency, created_at  
  - Unique `(user_id, symbol)` para evitar duplicados  

La API key de Twelve Data **no** se persiste con los usuarios: vive en configuración del servidor.

### TODO — Base de datos PostgreSQL

- [ ] Definir esquema SQL (`users`, `favorite_stocks` + constraints/índices)
- [ ] Incorporar SQLAlchemy (async) + Alembic
- [ ] Implementar repositorio PostgreSQL con la misma interfaz que el mock JSON
- [ ] Seed mínimo de usuarios y preferidas
- [ ] Incluir backup de la BD en el repositorio (requisito del challenge)
- [ ] Retirar o dejar el mock JSON solo para desarrollo local opcional

---

## Funciones del Backend

### Autenticación

| Función | Descripción |
| --- | --- |
| `POST /auth/login` | Valida usuario/password. Si es inválido, responde con mensaje **"usuario o clave invalida"**. Si es válido, emite JWT y datos del usuario. |
| `GET /auth/me` | Devuelve el usuario autenticado (nombre para la cabecera del Frontend). |

### Acciones preferidas

| Función | Descripción |
| --- | --- |
| `GET /favorites` | Lista las acciones preferidas del usuario logueado (símbolo, nombre, moneda). |
| `POST /favorites` | Agrega un símbolo a preferidas. Persiste símbolo, nombre y moneda. |
| `DELETE /favorites/{symbol}` | Elimina el símbolo de las preferidas del usuario. |

### Catálogo / búsqueda (Autocomplete)

| Función | Descripción |
| --- | --- |
| `GET /stocks/search?q=` | Busca acciones por texto (vía Twelve Data / exchange NYSE) para alimentar el Autocomplete. |

### Cotización / gráfico

| Función | Descripción |
| --- | --- |
| `GET /stocks/{symbol}` | Datos de cabecera de la acción (símbolo, nombre, moneda, etc.). |
| `GET /stocks/{symbol}/timeseries` | Serie temporal para graficar. Parámetros: `mode` (`realtime` \| `historical`), `interval` (`1min` \| `5min` \| `15min`), y opcionalmente `start_date` / `end_date`. |

En modo **tiempo real**, el Backend entrega la serie del día; el Frontend se encarga del refresco automático según el intervalo. El Backend no mantiene WebSockets en la versión base (simplicidad y cupo de 800 req/día).

---

## Casos de uso

| ID | Caso de uso | Flujo Backend |
| --- | --- | --- |
| UC-01 | Login válido | Validar credenciales → emitir JWT → devolver perfil |
| UC-02 | Login inválido | Responder error controlado con mensaje requerido |
| UC-03 | Ver mis acciones | Autenticar → listar `favorite_stocks` del usuario |
| UC-04 | Buscar símbolo | Autenticar → consultar Twelve Data → devolver coincidencias |
| UC-05 | Agregar preferida | Autenticar → validar símbolo → persistir → devolver lista actualizada o entidad creada |
| UC-06 | Eliminar preferida | Autenticar → borrar por `(user_id, symbol)` → confirmar |
| UC-07 | Ver detalle | Autenticar → obtener metadata del símbolo |
| UC-08 | Graficar histórico | Autenticar → `time_series` con `start_date` / `end_date` e intervalo |
| UC-09 | Graficar tiempo real | Autenticar → `time_series` del día sin rango fijo (o con rango del día) |

---

## Intencionalidad y por qué

| Decisión | Por qué |
| --- | --- |
| **API como único punto hacia Twelve Data** | Oculta la API key, centraliza rate limit y evita CORS/credenciales en el cliente |
| **JWT** | Sesión sin estado en el servidor; facilita escalar y desacoplar Frontend/API |
| **Preferidas en almacenamiento propio** | Twelve Data no guarda favoritos por usuario; el dominio del challenge es del sistema |
| **JSON mock en fase actual** | Acelera el desarrollo y permite testear el Backend sin infraestructura de BD |
| **Misma interfaz de repositories** | Migrar a PostgreSQL después sin reescribir routers/services |
| **Capas (router → service → repo)** | Mantenibilidad y testabilidad; cumple NFR de extensibilidad |
| **PostgreSQL (objetivo final)** | Modelo relacional claro, backup y requisito del challenge |
| **Sin WebSocket en v1** | El requisito de refresco se cubre con polling en Frontend; se ahorran requests y complejidad |
| **Pydantic + OpenAPI** | Contratos claros entre Frontend y Backend; menos ambigüedad en integración |

---

## NFR cubiertos desde el Backend

- **Mantenibilidad**: capas separadas, tipado, repositorio intercambiable  
- **Extensibilidad**: nuevo endpoint o proveedor de mercado sin romper el Frontend; swap JSON → PostgreSQL  
- **Escalabilidad**: API stateless (JWT); BD relacional en la fase final  
- **Seguridad**: passwords hasheados, JWT en rutas protegidas, API key solo en servidor  

---

## Entregables asociados

1. Persistencia mock JSON + seed mínimo para desarrollo/pruebas.  
2. **TODO:** esquema PostgreSQL + seed + backup de BD (entrega final).  
3. `README` con variables de entorno y cómo levantar la API.
