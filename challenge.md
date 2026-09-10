# Challenge Acciones

**Origin Solutions** · Evaluación  
**Autor:** Daniel Perrone  
**Creado:** 26/05/2021 · **Última revisión:** 08/09/2026

---

## Ejercicio

El cliente necesita que se le desarrolle una interfaz web para graficar la cotización de una acción en tiempo real. El detalle del proyecto se describe a continuación.

---

## Especificaciones

### Login

- El sitio cuenta con una página de login, donde se ingresa el usuario y password.
- En caso de ingresar algún dato inválido, informar: **"usuario o clave invalida"**.

### Mis Acciones

Luego de ingresar al sitio, se redirecciona a la página de **"Mis Acciones"**. Esta página muestra las acciones preferidas que haya seleccionado cada usuario.

- En la cabecera de la página se debe visualizar el nombre del usuario logueado.
- Para agregar una acción:
  1. Escribir en el **Autocomplete** para que muestre las acciones que coinciden con el texto buscado.
  2. Seleccionar una acción.
  3. Hacer click en **"Agregar símbolo"**.
  4. Se agrega la acción a las preferidas y se refresca la grilla con los datos correspondientes.
- De cada acción se debe guardar: **símbolo**, **nombre** y **moneda**.
- Para eliminar un símbolo: hacer click en el link **"Eliminar"** de la fila correspondiente. Esto borra la acción de las preferidas del usuario y refresca la grilla.
- Al hacer click en el símbolo (ejemplo: `TSLA`), se navega a la página de detalle.

### Página de Detalle de Acción

Esta página muestra en la cabecera los datos de la acción seleccionada. Luego se pueden seleccionar los parámetros para graficar la cotización.

| Parámetro | Descripción |
| --- | --- |
| **Tiempo real** | Grafica la cotización en base a la fecha del día. El gráfico debe actualizarse automáticamente según el intervalo seleccionado (cada 1 min / 5 min / 15 min). Por ejemplo, con intervalo de 1 minuto, el gráfico debería actualizarse solo tras ese tiempo. |
| **Histórico** | Grafica la cotización según los parámetros fecha y hora desde – fecha y hora hasta ingresados. |
| **Intervalo** | Define el intervalo de tiempo para graficar. Valores posibles: `1min` / `5min` / `15min`. |

Para el gráfico se puede utilizar [Highcharts](https://www.highcharts.com/) o similar.

---

## API para obtener datos

1. Usar la API de [Twelve Data](https://api.twelvedata.com/) (gratuita, permite **800 requests por día**).

2. Datos de una acción (ejemplo Netflix, `NFLX`):

   ```
   https://api.twelvedata.com/stocks?symbol=NFLX&source=docs
   ```

   Listado de acciones para el Autocomplete:

   ```
   https://api.twelvedata.com/stocks?source=docs&exchange=NYSE
   ```

3. Cotización / time series (ejemplo `TSLA`):

   ```
   https://api.twelvedata.com/time_series?symbol=TSLA&interval=5min&start_date=2021-04-16%2009:48:00&end_date=2021-04-16%2019:48:00&apikey=*******
   ```

   - Los parámetros `start_date` y `end_date` son opcionales.
   - En `apikey` colocar la API key obtenida al crear una cuenta en [api.twelvedata.com](https://api.twelvedata.com/).

---

## Tarea

1. Crear la base de datos y todos los objetos necesarios para que la aplicación funcione.
2. Insertar una cantidad mínima de datos para poder probar la aplicación.
3. Desarrollar una aplicación web en un **repositorio público**, utilizando una herramienta de versionado (GitHub / Bitbucket / etc.), que responda a los requisitos descriptos por el cliente.
4. Incluir un **backup** de la base de datos.
5. Incluir en el repositorio un `README.md` con los pasos para levantar la aplicación.

---

## Notas técnicas

La arquitectura debe contener **dos proyectos**: un Frontend y una API.

### Base de datos

- Relacional: **SQL Server**, **MySQL** o **PostgreSQL**

### Stack tecnológico

| Capa | Tecnología |
| --- | --- |
| Frontend (elegir una) | Angular ≥ 18 **o** React ≥ 18 |
| API | Python + FastAPI |

---

## Criterios de evaluación

No se evaluará el diseño ni el conocimiento sobre UI, sino:

- Funcionalidad y estabilidad de la solución
- Modelo de datos
- Atención a los requerimientos
- Seguridad
- Estructura del código
- Actitud frente a los NFR (*non-functional requirements*): **mantenibilidad**, **extensibilidad** y **escalabilidad**
