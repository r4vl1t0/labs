# Writeup — Lab 2: XSS Almacenado (Profesor)

**Ruta:** `/profesor/almacenado/`

## Descripción
Un libro de visitas guarda los comentarios en un archivo de texto en el
servidor y los muestra a **todos** los visitantes sin escapar el HTML. A
diferencia del reflejado, aquí el payload persiste: basta con que un
atacante lo publique una vez para que afecte a cualquiera que visite la
página después.

## Código vulnerable
```php
file_put_contents($dataFile, $_POST['comentario'] . "\n@@@\n", FILE_APPEND);
...
foreach ($comentarios as $c) {
    echo $c;  // sin htmlspecialchars
}
```

## Explotación (para la demo)
1. En el formulario, publicar:
   ```html
   <script>alert('XSS Almacenado ejecutado para: ' + document.cookie)</script>
   ```
2. Recargar la página (o abrirla en otra pestaña / navegador en incógnito)
   para demostrar que el JavaScript se ejecuta para **cualquier visitante**,
   no solo para quien lo publicó.
3. Usar el botón "Reiniciar comentarios" para limpiar el estado antes de la
   siguiente demo.

## Impacto
- Mucho más grave que el reflejado: no requiere engañar a la víctima con un
  link, el ataque queda "esperando" en la página.
- Puede afectar a todos los usuarios del sitio, incluyendo administradores.
- Permite gusanos XSS (self-propagating), robo masivo de sesiones, defacement
  persistente.

## Remediación
```php
echo htmlspecialchars($c, ENT_QUOTES, 'UTF-8');
```
Además:
- Si se necesita permitir formato (negritas, links), usar una librería de
  sanitización de HTML como **HTML Purifier**, nunca escapar "a medias" con
  reemplazos manuales.
- Validar longitud y contenido permitido en el servidor.
- CSP como defensa adicional.
