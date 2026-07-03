# Writeup — Lab 1: XSS Reflejado (Profesor)

**Ruta:** `/profesor/reflejado/`

## Descripción
El buscador toma el parámetro `q` de la URL y lo imprime directamente en el
HTML de la respuesta, sin sanitizar. Al ser un XSS **reflejado**, el payload
solo se ejecuta si la víctima abre una URL manipulada por el atacante
(por ejemplo, recibida por correo o chat).

## Código vulnerable
```php
$q = isset($_GET['q']) ? $_GET['q'] : '';
...
echo $q;
```

## Explotación (para la demo)
1. Navegar a:
   ```
   http://localhost:8080/profesor/reflejado/?q=<img src=x onerror=alert(document.cookie)>
   ```
2. El navegador intenta cargar la imagen `x`, falla, y ejecuta el manejador
   `onerror`, que dispara `alert(document.cookie)`.
3. Se puede mostrar cómo la misma URL, enviada a otra persona, ejecutaría el
   mismo código en su navegador con **sus** cookies de sesión.

## Impacto
- Robo de cookies de sesión / secuestro de sesión.
- Phishing dentro del propio sitio confiable (defacement puntual).
- Ejecución de acciones en nombre de la víctima (si hay CSRF combinado).

## Remediación
```php
echo htmlspecialchars($q, ENT_QUOTES, 'UTF-8');
```
Además:
- Definir una **Content-Security-Policy** (`script-src 'self'`) como defensa
  en profundidad.
- Validar el formato esperado del parámetro (whitelist) cuando sea posible.
- Usar cookies con flag `HttpOnly` para que no sean accesibles desde JS.
