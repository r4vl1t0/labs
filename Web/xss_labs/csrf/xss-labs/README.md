# Laboratorios de XSS — Docker

Entorno Docker con **6 laboratorios de XSS** para clase de seguridad web:
3 vulnerabilidades (Reflejado, Almacenado, DOM-based) x 2 versiones
(Profesor / Estudiante).

> ⚠️ **Uso exclusivamente educativo.** Las aplicaciones son intencionalmente
> vulnerables. Ejecuta este entorno solo en tu máquina local / red aislada.
> No lo expongas a internet ni lo uses con datos reales.

## Requisitos
- Docker y Docker Compose instalados.

## Cómo levantar el entorno
```bash
cd xss-labs
docker compose up -d
```
Luego abre en el navegador:
```
http://localhost:8080
```
Ahí encontrarás el índice con enlaces a los 6 labs.

### 🔒 El índice está protegido con contraseña
La página `/` (índice con el listado de los 6 labs) pide usuario y
contraseña mediante HTTP Basic Auth, para que los estudiantes **no puedan
verla ni navegar por ella**. Tú les compartes directamente la ruta de cada
lab que quieras que resuelvan (ver tabla más abajo).

Credenciales por defecto (**cámbialas antes de la clase**):
- Usuario: `profesor`
- Contraseña: `cambiame123`

Para cambiarlas, edita `docker-compose.yml`:
```yaml
environment:
  - INDEX_USER=tu_usuario
  - INDEX_PASS=tu_contraseña_segura
```
y vuelve a levantar el contenedor:
```bash
docker compose up -d
```
> Nota: esta protección aplica **solo al índice** (`/`). Las rutas de cada
> lab (`/profesor/...`, `/estudiante/...`) no piden contraseña, para que
> puedas compartirlas directamente con los estudiantes.

Para detener y limpiar:
```bash
docker compose down
```

## Estructura del proyecto
```
xss-labs/
├── docker-compose.yml
├── www/
│   ├── index.php                  # índice con los 6 labs
│   ├── assets/style.css
│   ├── profesor/
│   │   ├── reflejado/index.php    # Lab 1 (demo guiada)
│   │   ├── almacenado/index.php   # Lab 2 (demo guiada)
│   │   └── dom/index.html         # Lab 3 (demo guiada)
│   └── estudiante/
│       ├── reflejado/index.php    # Lab 4 (reto)
│       ├── almacenado/index.php   # Lab 5 (reto)
│       └── dom/index.html         # Lab 6 (reto)
└── writeups/                      # soluciones y explicación de cada lab
```

## Los 6 laboratorios

| # | Tipo             | Versión    | Ruta                        | Descripción |
|---|------------------|------------|------------------------------|-------------|
| 1 | Reflejado        | Profesor   | `/profesor/reflejado/`       | Buscador con payload de ejemplo y botón de demo lista para clase. |
| 2 | Almacenado       | Profesor   | `/profesor/almacenado/`      | Libro de visitas; el payload persiste para todos los visitantes. |
| 3 | DOM-based        | Profesor   | `/profesor/dom/`              | Saludo dinámico manipulado 100% en el navegador (`innerHTML`). |
| 4 | Reflejado        | Estudiante | `/estudiante/reflejado/`     | Reto: robar la cookie `flag` vía el buscador. |
| 5 | Almacenado       | Estudiante | `/estudiante/almacenado/`    | Reto: dejar un comentario que ejecute JS para cualquier visitante. |
| 6 | DOM-based        | Estudiante | `/estudiante/dom/`            | Reto: explotar el router basado en `location.hash`. |
| 7 | Reflejado + Blacklist | Estudiante | `/estudiante/blacklist/`  | Reto: fuzzear etiquetas HTML para evadir un filtro de blacklist. |
| 8 | CSRF (transferencia)  | Profesor   | `/profesor/csrf/`         | App bancaria con página maliciosa de demo lista para mostrar. |
| 9 | CSRF (transferencia)  | Estudiante | `/estudiante/csrf/`       | Reto: construir un HTML que fuerce la transferencia sin token CSRF. |

Las versiones **Profesor** incluyen: explicación de la vulnerabilidad,
payload de ejemplo con un botón "Ejecutar demo", y la corrección comentada
al final de la página — pensadas para proyectarlas en clase.

Las versiones **Estudiante** solo incluyen el enunciado del reto (sin la
solución), para que el alumno investigue y explote la vulnerabilidad por su
cuenta. Las soluciones están en la carpeta `writeups/`.

## Writeups
En `writeups/` hay un documento por laboratorio:
- `01-reflejado-profesor.md`
- `02-reflejado-estudiante.md` (solución del reto)
- `03-almacenado-profesor.md`
- `04-almacenado-estudiante.md` (solución del reto)
- `05-dom-profesor.md`
- `06-dom-estudiante.md` (solución del reto)
- `07-blacklist-estudiante.md` (solución del reto de fuzzing)
- `08-csrf-profesor.md`
- `09-csrf-estudiante.md` (solución del reto)

Cada uno incluye: descripción de la vulnerabilidad, código vulnerable,
pasos de explotación, impacto y remediación.

## Reiniciar el estado de los labs almacenados
Los labs de XSS Almacenado (2 y 5) guardan los comentarios en archivos de
texto dentro de `www/*/almacenado/data/`. Cada uno tiene un botón
"Reiniciar comentarios" en la propia página, o puedes borrar el contenido
manualmente:
```bash
echo "" > www/profesor/almacenado/data/comentarios.txt
echo "" > www/estudiante/almacenado/data/comentarios.txt
```

## Notas para el profesor
- Todas las cookies `flag` se generan automáticamente en cada lab la primera
  vez que se visita.
- Puedes proyectar directamente las versiones "Profesor" y luego pedir a los
  estudiantes que resuelvan las versiones "Estudiante" por su cuenta.
- El código de cada lab está comentado señalando la línea exacta de la
  vulnerabilidad, útil para lectura de código en clase.
