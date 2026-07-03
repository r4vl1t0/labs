# Writeup (solucion) -- Lab 7: XSS Reflejado con Blacklist (Estudiante)

**Ruta:** `/estudiante/blacklist/`

> Este documento contiene la solucion. Es para el profesor, no compartir
> con los estudiantes antes del reto.

## Objetivo del reto
Robar el valor de la cookie `flag` mostrandolo en un `alert()`, evadiendo
un filtro de blacklist que bloquea ciertas etiquetas y eventos.

## Blacklist implementada
```php
$blacklist = [
    '<script', '<img', '<iframe', '<svg', '<body',
    '<object', '<embed', '<form', '<input', '<video', '<audio',
    'onerror', 'onload', 'onclick',
    'javascript:', 'eval(', 'document.write',
];
```
La comparacion se hace con `strpos()`, que es **sensible a mayusculas y
minusculas**. Esto es intencional: es un error comun en filtros reales.

## Vias de bypass (hay mas de una)

### 1. Etiquetas no cubiertas por la lista
La blacklist no incluye `<details>`, `<marquee>`, `<select>`,
`<table>`, `<math>`, `<template>`, entre otras. Combinando una etiqueta no
bloqueada con un atributo de evento tampoco bloqueado (por ejemplo
`ontoggle`, `onfocus`, `onstart`, `onpointerenter`) se logra ejecucion de
JavaScript.

Payload recomendado:
```
?q=<details open ontoggle=alert(document.cookie)>
```
URL codificada:
```
http://localhost:8080/estudiante/blacklist/?q=%3Cdetails%20open%20ontoggle%3Dalert(document.cookie)%3E
```
El atributo `open` hace que el elemento `<details>` aparezca ya expandido,
lo que dispara el evento `ontoggle` de forma automatica al cargar la
pagina, sin necesidad de interaccion del usuario.

Alternativa con `<marquee>`:
```
?q=<marquee onstart=alert(document.cookie)>x</marquee>
```

### 2. Bypass por mayusculas/minusculas
Como la comparacion es sensible a mayusculas, cambiar el caso de la
etiqueta bloqueada evade el filtro:
```
?q=<ScRiPt>alert(document.cookie)</script>
```
Nota: dependiendo del navegador, el parser HTML normaliza igual la
etiqueta a minusculas al momento de interpretarla, por lo que el script
se ejecuta aunque el texto original tenga mayusculas mezcladas.

## Proceso de fuzzing esperado
1. Probar etiquetas conocidas una por una: `<script`, `<img`, `<svg`,
   `<iframe`, `<body`... el sistema responde "Entrada bloqueada" e indica
   el patron detectado exacto.
2. Ir anotando que patrones estan en la lista negra y cuales no.
3. Probar etiquetas menos comunes: `<details`, `<marquee`, `<select`,
   `<table`, `<math`... estas no generan bloqueo.
4. Confirmar que la etiqueta se refleja sin escapar (ver codigo fuente).
5. Agregar un atributo de evento que dispare la ejecucion sin necesitar
   clic del usuario (`ontoggle` con `open`, o `onstart` en `marquee`).
6. Verificar que el atributo de evento elegido tampoco este en la
   blacklist.
7. Construir el payload final y confirmar la ejecucion del `alert()` con
   la cookie `flag`.

## Impacto
Igual que cualquier XSS reflejado: robo de sesion, phishing dentro del
sitio, ejecucion de acciones en nombre de la victima. La particularidad
de este lab es demostrar que **las blacklists son inherentemente
incompletas**: la superficie de ataque de HTML/JS (etiquetas, atributos de
evento, esquemas de URL, variaciones de mayusculas, encoding) es demasiado
grande para enumerarla por completo.

## Remediacion
- Reemplazar la blacklist por un **whitelist** de caracteres permitidos, o
  mejor aun, escapar la salida con `htmlspecialchars()`.
- Si se necesita permitir HTML limitado, usar una libreria de sanitizacion
  robusta y mantenida (por ejemplo HTML Purifier o DOMPurify del lado del
  cliente), nunca una lista negra hecha a mano.
- Aplicar una Content-Security-Policy estricta como defensa adicional.
