# Writeup (solucion) — Lab 9: CSRF en transferencias (Estudiante)

**Ruta:** `/estudiante/csrf/`

> Este documento contiene la solucion. Es para el profesor.

## Objetivo del reto
Drenar el saldo de la cuenta de la victima a cero, forzando una
transferencia sin usar el formulario legitimo de BancoWeb.

## Analisis previo esperado
El estudiante deberia notar, inspeccionando el formulario de
transferencia:
1. El metodo es GET (`<form method="GET" action="transferir.php">`), asi
   que toda la accion se puede reproducir con una simple URL.
2. No hay ningun campo oculto tipo `csrf_token`.
3. La sesion se mantiene solo por cookie (`PHPSESSID`).

## Pasos de la solucion
1. Iniciar sesion en `/estudiante/csrf/login.php` con
   `victima` / `victima123`. Esto dejara la sesion activa en el navegador.
2. Crear en su propia computadora (fuera del contenedor) un archivo HTML,
   por ejemplo `exploit.html`, con contenido similar a:
   ```html
   <!DOCTYPE html>
   <html>
   <body>
     <img src="http://localhost:8080/estudiante/csrf/transferir.php?monto=1000&destino=ATACANTE-9999" style="display:none">
   </body>
   </html>
   ```
3. Guardar el archivo y abrirlo directamente en el mismo navegador donde
   se inicio sesion (doble clic, o arrastrarlo a una pestana nueva).
4. Volver a `http://localhost:8080/estudiante/csrf/banco.php`: el saldo
   deberia estar en 0 y aparecer la flag.

## Por que funciona
- La etiqueta `<img>` genera automaticamente una peticion GET al cargar la
  pagina, sin necesitar clic ni JavaScript.
- El navegador adjunta la cookie de sesion de `localhost:8080` porque la
  peticion va dirigida a ese dominio, sin importar que la pagina que la
  origino sea un archivo local (`file://`) o este en otro dominio.
- Como la peticion es GET y no una navegacion de nivel superior que
  cambie de sitio de forma "no seguro", ni siquiera las protecciones por
  defecto de cookies `SameSite=Lax` de los navegadores modernos la
  bloquean: las peticiones "seguras" (GET) generadas por recursos como
  `<img>`, `<script src>` o enlaces siguen enviando la cookie.
- El servidor nunca valida que la peticion provenga realmente del
  formulario de BancoWeb, asi que la acepta igual.

## Variantes validas de la solucion
- Usar un enlace `<a href="...">Reclama tu premio</a>` en vez de `<img>`
  (requiere que la victima haga clic, pero al ser un GET normal tambien
  evade `SameSite=Lax`).
- Usar un formulario HTML con auto-submit via JavaScript
  (`document.forms[0].submit()`), tanto con GET como con POST, ya que el
  endpoint no valida el metodo ni el token en ningun caso.

## Preguntas para reforzar el aprendizaje
- Que hubiera pasado si `transferir.php` solo aceptara POST, la cookie de
  sesion tuviera `SameSite=Strict`, y ademas exigiera un token CSRF.
- Por que usar GET para una accion que cambia estado es un problema
  incluso sin pensar en CSRF (cacheable, queda en el historial del
  navegador, en logs de proxies, etc.).

## Criterio de evaluacion sugerido
- Identifica que la transferencia se puede reproducir con una URL simple.
- Construye una pagina HTML que dispare la peticion sin interaccion
  directa con el formulario original.
- Logra drenar el saldo a cero y obtiene la flag.
- Explica correctamente el rol de la cookie de sesion y la ausencia de
  token CSRF en el ataque.
