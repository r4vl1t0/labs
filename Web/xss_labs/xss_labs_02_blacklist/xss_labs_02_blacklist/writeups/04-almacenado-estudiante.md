# Writeup (solución) — Lab 5: Reto XSS Almacenado (Estudiante)

**Ruta:** `/estudiante/almacenado/`

> ⚠️ Este documento contiene la solución.

## Objetivo del reto
Publicar un comentario que, al recargar la página, ejecute JS y muestre la
cookie `flag` en un `alert()`.

## Pasos de la solución
1. Escribir en el campo de comentario:
   ```html
   <script>alert(document.cookie)</script>
   ```
2. Enviar el formulario (botón "Publicar").
3. La página redirige y vuelve a cargar la lista de comentarios: al
   renderizar el comentario guardado, el navegador ejecuta el script
   automáticamente y aparece el `alert` con
   `flag=FLAG{stored_xss_demo_2026}`.
4. Punto clave para la discusión: **no hace falta volver a enviar nada**; el
   ataque ya quedó guardado en el servidor y se dispara solo.

## Preguntas para reforzar el aprendizaje
- ¿Qué pasaría si otro estudiante abre esta misma página en su navegador?
- ¿Cómo cambiaría el impacto si el "libro de visitas" fuera visto por un
  administrador con más privilegios?
- ¿Qué diferencia práctica hay con el XSS reflejado del Lab 4?

## Criterio de evaluación sugerido
- ✅ Logra que el payload persista y se ejecute automáticamente.
- ✅ Explica la diferencia entre reflejado y almacenado en cuanto a
  persistencia y alcance del ataque.
- ✅ Propone la corrección (`htmlspecialchars` o sanitización de HTML).
