# Análisis Frontend — Challenge Acciones

Documento de diseño técnico del cliente web. Define stack, arquitectura, responsabilidades, casos de uso e intencionalidad.

---

## Objetivo

Ofrecer una interfaz web funcional para login, gestión de acciones preferidas y visualización de cotizaciones (tiempo real e histórico), consumiendo exclusivamente la API propia.

---

## Stack

| Componente | Tecnología | Motivo |
| --- | --- | --- |
| Framework | React ≥ 18 (Vite) | Opción válida del challenge; ecosistema maduro, buen encaje con SPA y gráficos |
| Lenguaje | TypeScript | Contratos claros con el Backend y menos errores en integración |
| Routing | React Router | Navegación Login → Mis Acciones → Detalle |
| Estado / datos | TanStack Query (React Query) | Caché, refetch y polling para tiempo real sin lógica ad hoc |
| HTTP | fetch o axios | Cliente HTTP simple hacia la API |
| Gráficos | Highcharts (o equivalente) | Sugerido por el challenge; series temporales claras |
| UI | Componentes propios / librería mínima | El diseño no se evalúa; prioridad a claridad y estabilidad |

> **Nota:** Angular ≥ 18 también es válido. Se elige React por velocidad de entrega en una SPA con autocomplete, grilla y gráfico con refresco periódico.

---

## Arquitectura

SPA con rutas protegidas y capas delgadas:

```
┌──────────────────────────────────────────┐
│  Pages (Login, Favorites, StockDetail)   │
│           │                              │
│           ▼                              │
│  Features / Components                   │
│  (Autocomplete, StockGrid, ChartForm,    │
│   PriceChart, Header)                    │
│           │                              │
│           ▼                              │
│  Services / API client                   │
│  (auth, favorites, stocks, timeseries)   │
│           │                              │
│           ▼                              │
│  Auth store (token + usuario)            │
└──────────────────────────────────────────┘
                 │
                 ▼
            Backend API
```

| Capa | Responsabilidad |
| --- | --- |
| **Pages** | Orquestan pantallas y casos de uso |
| **Components** | UI reutilizable (autocomplete, grilla, formulario de gráfico, chart) |
| **API client** | Llamadas HTTP, headers con JWT, manejo de errores |
| **Auth** | Guardar token/usuario (memory + `localStorage` o `sessionStorage`), proteger rutas |

### Rutas

| Ruta | Página | Acceso |
| --- | --- | --- |
| `/login` | Login | Público |
| `/acciones` | Mis Acciones | Autenticado |
| `/acciones/:symbol` | Detalle de Acción | Autenticado |

Tras login exitoso → redirect a `/acciones`.  
Sin token válido → redirect a `/login`.

---

## Funciones del Frontend

### Login

| Función | Descripción |
| --- | --- |
| Formulario usuario/password | Envía credenciales al Backend |
| Manejo de error | Si falla, muestra exactamente **"usuario o clave invalida"** |
| Persistencia de sesión | Guarda JWT y nombre de usuario para la cabecera |

### Mis Acciones

| Función | Descripción |
| --- | --- |
| Cabecera | Muestra el nombre del usuario logueado |
| Autocomplete | Busca símbolos mientras el usuario escribe; muestra coincidencias |
| Agregar símbolo | Selección + botón **"Agregar símbolo"** → POST favorito → refresca grilla |
| Grilla de preferidas | Lista símbolo, nombre y moneda |
| Eliminar | Link **"Eliminar"** por fila → DELETE → refresca grilla |
| Navegación a detalle | Click en el símbolo (ej. `TSLA`) → `/acciones/TSLA` |

### Detalle de Acción

| Función | Descripción |
| --- | --- |
| Cabecera de acción | Muestra datos del símbolo seleccionado |
| Selector de modo | **Tiempo real** o **Histórico** |
| Selector de intervalo | `1min` / `5min` / `15min` |
| Rango histórico | Inputs fecha/hora desde – hasta (solo en modo histórico) |
| Gráfico | Renderiza la serie con Highcharts (o similar) |
| Auto-refresh (tiempo real) | Reconsulta la API cada 1 / 5 / 15 minutos según el intervalo elegido |

---

## Casos de uso

| ID | Caso de uso | Flujo Frontend |
| --- | --- | --- |
| UC-01 | Login válido | Enviar credenciales → guardar JWT → ir a Mis Acciones |
| UC-02 | Login inválido | Mostrar mensaje fijo de error; no navegar |
| UC-03 | Ver preferidas | Cargar grilla al montar la página |
| UC-04 | Buscar y agregar | Autocomplete → seleccionar → Agregar → refrescar grilla |
| UC-05 | Eliminar preferida | Click Eliminar → confirmar respuesta → refrescar grilla |
| UC-06 | Abrir detalle | Click en símbolo → cargar metadata + formulario de gráfico |
| UC-07 | Graficar histórico | Elegir histórico + rango + intervalo → pedir timeseries → dibujar |
| UC-08 | Graficar tiempo real | Elegir tiempo real + intervalo → pedir serie del día → programar refetch automático |

---

## Intencionalidad y por qué

| Decisión | Por qué |
| --- | --- |
| **SPA con rutas protegidas** | Encaja con el flujo Login → Mis Acciones → Detalle sin recargas innecesarias |
| **No llamar Twelve Data desde el browser** | Seguridad (API key) y un solo contrato con el Backend |
| **React Query + polling** | Cumple el refresco automático de tiempo real de forma explícita y controlable; fácil de apagar al salir de la página |
| **Highcharts (o similar)** | Cubrir el requisito de gráfico sin invertir tiempo en visualización custom |
| **TypeScript** | Alinea tipos con el API (favoritas, intervals, modes) y reduce regresiones |
| **UI simple** | El challenge evalúa funcionalidad y estabilidad, no diseño |
| **Componentes por feature** | Facilita mantenimiento y extensión (nuevo intervalo, nuevo proveedor, etc.) |

---

## Comportamiento clave: tiempo real vs histórico

| Modo | Comportamiento en UI |
| --- | --- |
| **Tiempo real** | Sin rango manual; usa fecha del día. El gráfico se **actualiza solo** según el intervalo (`1min` / `5min` / `15min`). Al desmontar la página o cambiar a histórico, se cancela el polling. |
| **Histórico** | Requiere desde/hasta. Una sola consulta al graficar (sin auto-refresh). |
| **Intervalo** | Aplica a ambos modos; define la granularidad de la serie y, en tiempo real, también el período de refresco. |

---

## NFR cubiertos desde el Frontend

- **Mantenibilidad**: páginas delgadas, cliente API centralizado  
- **Extensibilidad**: cambiar librería de charts o agregar filtros sin reescribir el dominio  
- **Escalabilidad de UX**: caché/refetch evita llamadas redundantes  
- **Seguridad**: token solo en cliente autorizado; sin secretos de Twelve Data  

---

## Entregables asociados

1. Proyecto Frontend independiente del API.  
2. Configuración de URL base del Backend por entorno.  
3. Instrucciones en el `README` para instalar, configurar y levantar el cliente.
