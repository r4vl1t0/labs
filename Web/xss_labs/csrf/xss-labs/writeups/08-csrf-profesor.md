# Writeup — Lab 8: CSRF en transferencias (Profesor)

**Ruta:** `/profesor/csrf/`

## Descripcion
BancoWeb es una app minima con sesion (login con `victima` / `victima123`)
y un endpoint de transferencia de fondos. La accion de transferir:

1. Se ejecuta mediante **GET** (una accion que cambia estado nunca deberia
   usar un metodo "seguro" como GET).
2. No incluye ningun **token anti-CSRF**.
3. No valida los headers `Origin` ni `Referer`.

Esto permite que cualquier pagina externa fuerce una transferencia
mientras la victima tenga una sesion activa, sin que ella lo note ni lo
autorice.

## Codigo vulnerable
```php
// transferir.php
$monto   = (float)($_GET['monto'] ?? 0);
$destino = $_GET['destino'] ?? '';
if ($monto > 0 && $monto <= $_SESSION['saldo'] && $destino !== '') {
    $_SESSION['saldo'] -= $monto;
}
```
No hay ninguna verificacion de que la peticion provenga realmente del
formulario legitimo de BancoWeb.

## Explotacion (para la demo)
1. Iniciar sesion en `/profesor/csrf/login.php` con `victima` / `victima123`.
2. En otra pestana, abrir `/profesor/csrf/exploit.html`. Esta pagina
   simula un sitio externo malicioso; contiene una etiqueta
   `<img src="transferir.php?monto=1000&destino=ATACANTE-9999">` oculta.
3. Al cargarse la imagen, el navegador envia automaticamente la cookie de
   sesion de BancoWeb junto con la peticion, sin pedir confirmacion.
4. Volver a `banco.php`: el saldo bajo a 0 sin que la victima haya usado
   el formulario de transferencia.

Explicar a la clase que en un ataque real `exploit.html` estaria alojada
en un dominio completamente distinto (por ejemplo, enviada por correo o
insertada en un foro), y el navegador igualmente adjuntaria la cookie de
sesion de BancoWeb porque las cookies se envian segun el dominio de
**destino** de la peticion, no segun el origen de la pagina que la genera.

## Impacto
- Ejecucion de acciones con los privilegios de la victima sin su
  consentimiento (transferencias, cambios de contrasena, cambios de
  email, eliminacion de cuenta, etc., segun la app).
- Combinado con XSS, el impacto puede ser aun mayor (XSS puede leer
  tokens CSRF si el atacante logra ejecutar JS en el mismo origen).

## Remediacion
```php
// 1. Usar POST (o mejor, metodos no "safe") para cambios de estado
// 2. Generar y validar un token CSRF unico por sesion
if (!hash_equals($_SESSION['csrf_token'], $_POST['csrf_token'] ?? '')) {
    http_response_code(403);
    die('Token CSRF invalido');
}
```
Ademas:
- Configurar la cookie de sesion con `SameSite=Strict` o `SameSite=Lax`
  (`session_set_cookie_params(['samesite' => 'Strict'])`), lo que evita
  que el navegador envie la cookie en peticiones de origen cruzado.
- Validar el header `Origin`/`Referer` como capa adicional (no como unica
  defensa).
- Para APIs, considerar exigir un header personalizado que solo JavaScript
  del mismo origen puede establecer (los formularios HTML puros no pueden
  agregar headers personalizados).
