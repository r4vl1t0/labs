# Laboratorio final - entorno vulnerable con Docker Compose

Entorno con 8 retos independientes desplegados como subdominios de un mismo
dominio ficticio `lab.local`, pensado para reconocimiento + explotación en
un solo flujo (DNS -> descubrimiento de subdominios -> explotacion de cada app).

## 1. Requisitos

- Docker y Docker Compose instalados en la maquina donde se ejecutara el laboratorio.
- Acceso para editar `/etc/hosts` (o el archivo equivalente) de las maquinas de los alumnos.

## 2. Levantar el entorno

```
cd lab-final
docker compose up -d --build
```

Esto expone:

- Puerto `8080` (HTTP, nginx) -> todas las aplicaciones web, enrutadas por virtualhost.
- Puerto `5353` (UDP/TCP) -> servidor DNS con la zona `lab.local`.

## 3. Configuracion en las maquinas de los alumnos

Como el DNS corre en un puerto no estandar (`5353`) para no pisar el resolver
del host, hay dos formas de trabajar:

**Opcion A (recomendada para el reto de AXFR):** los alumnos consultan el DNS
directamente contra el puerto publicado, sin tocar `/etc/hosts`:

```
dig @<ip_del_host_docker> -p 5353 lab.local AXFR
```

Esto les debe devolver el listado completo de subdominios (varios de ellos
no estan enlazados desde ninguna pagina publica).

**Opcion B (para navegar las apps):** agregar a `/etc/hosts` una entrada por
cada subdominio descubierto, apuntando a la IP del host donde corre Docker,
y acceder con el puerto `8080`, por ejemplo:

```
<ip_del_host_docker>  portal-clientes.lab.local intranet.lab.local gestion.lab.local catalogo.lab.local soporte.lab.local backup-docs.lab.local reportes-xml.lab.local

http://portal-clientes.lab.local:8080/
```

## 4. Mapa de retos (para el docente)

| # | Subdominio | Vulnerabilidad | Flag |
|---|---|---|---|
| 1 | zona `lab.local` (puerto 5353) | Transferencia de zona (AXFR) mal configurada, revela subdominios no publicados | (no aplica flag, es reconocimiento) |
| 2 | portal-clientes.lab.local | SQLi (UNION-based) en buscador de facturas | `LAB{union_based_sqli_en_buscador_facturas}` |
| 3 | soporte.lab.local | XSS almacenado en ticket, un bot administrador lo visita y expone su cookie de sesion | `LAB{stored_xss_roba_cookie_de_admin_bot}` |
| 4 | intranet.lab.local | IDOR en legajo de empleados (`/legajo.php?id=`) | `LAB{idor_legajo_sin_control_de_acceso}` |
| 5 | gestion.lab.local | Credenciales por defecto `admin:admin` | `LAB{admin_admin_credenciales_por_defecto}` |
| 6 | catalogo.lab.local | Scraping, flag oculta en comentario HTML de un producto no enlazado directamente | `LAB{scraping_html_comment_pag_173}` |
| 7 | backup-docs.lab.local | Command injection en la funcion "Duplicar documento" | `LAB{command_injection_en_duplicado_de_documentos}` |
| 8 | reportes-xml.lab.local | XXE en importador de reportes XML | `LAB{xxe_lectura_de_archivos_via_entidad_externa}` |

### Detalle de cada reto

**1. AXFR**
La zona `lab.local` tiene `allow-transfer { any; };` sin restriccion.
`dig axfr lab.local @<ip> -p 5353` entrega todos los registros, incluyendo
subdominios como `intranet`, `backup-docs`, `reportes-xml`, que no aparecen
enlazados en ninguna pagina publica.

**2. SQLi - portal-clientes.lab.local**
Credenciales de prueba: `demo / demo123`.
Tras iniciar sesion, el buscador de facturas (`/facturas.php?buscar=`)
concatena el parametro directamente en la consulta SQL. Es inyectable con
`UNION SELECT` (la consulta original tiene 4 columnas: numero, concepto,
monto, fecha) para leer la tabla `sistema_config`.

**3. XSS almacenado - soporte.lab.local**
El alumno se registra, crea un ticket con un payload en el campo "mensaje"
(por ejemplo un `fetch` que envie `document.cookie` a
`/log.php?c=`). Un bot headless revisa los tickets pendientes cada
25 segundos usando una sesion de administrador autenticada; al renderizar
el ticket en `/admin/ticket.php`, el mensaje se imprime sin escapar y el
payload se ejecuta con la cookie del administrador. El resultado queda
registrado en `/captura.php`. Con esa cookie de sesion (`PHPSESSID`) se
puede acceder a `/admin/panel.php` y ver la flag.

**4. IDOR - intranet.lab.local**
El alumno se registra como empleado nuevo y accede a su propio legajo en
`/legajo.php?id=<su_id>`. Cambiando el parametro `id` (por ejemplo a `1`,
la cuenta de RRHH precargada) se accede a legajos ajenos sin control de
autorizacion, incluida la nota confidencial con la flag.

**5. Credenciales debiles - gestion.lab.local**
Login con `admin / admin`, sin bloqueo de intentos.

**6. Scraping - catalogo.lab.local**
Catalogo de 300 productos paginados de a 10. La flag esta como comentario
HTML (no visible en el render) en el detalle del producto con `id=173`,
al que no se llega por ningun enlace directo salvo recorriendo la
paginacion o iterando directamente `producto.php?id=`.

**7. Command injection - backup-docs.lab.local**
El formulario "Duplicar documento" arma un comando `cp origen destino`
con el campo `destino` sin sanitizar. Es explotable con separadores de
comandos, por ejemplo como nombre de destino:
`a.txt; cat /var/www/flag.txt #`

**8. XXE - reportes-xml.lab.local**
El importador de reportes XML parsea el XML con `DOMDocument` habilitando
resolucion de entidades. Es vulnerable a la tecnica clasica de XXE con
`DOCTYPE` + `ENTITY SYSTEM "file:///var/www/flag.txt"`, referenciando la
entidad en alguno de los campos (`proveedor`, `concepto` o `monto`).

## 5. Notas de mantenimiento

- Todas las apps PHP se conectan al mismo contenedor `mysql` (usuario
  `root`, password `rootpass123`), cada una con su propia base de datos.
- Los datos se inicializan una sola vez al crear el volumen de MySQL. Para
  reiniciar el estado del laboratorio: `docker compose down -v && docker
  compose up -d --build`.
- El bot de administrador (`admin-bot`) revisa tickets pendientes en un
  ciclo continuo; no hace falta interaccion manual del docente durante
  la clase.
- El log de cookies capturadas (`soporte.lab.local/logs/captura.log`) se
  reinicia al reconstruir el contenedor `xss-app`.
