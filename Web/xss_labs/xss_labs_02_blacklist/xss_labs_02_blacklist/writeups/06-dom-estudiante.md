# Writeup (solución) — Lab 6: Reto XSS DOM-based (Estudiante)

**Ruta:** `/estudiante/dom/`

> ⚠️ Este documento contiene la solución.

## Objetivo del reto
Conseguir que se ejecute `alert('FLAG_DOM')` explotando el "router" basado en
`location.hash`.

## Análisis
```javascript
function render() {
  const hash = decodeURIComponent(location.hash.substring(1));
  ...
  } else {
    contenedor.innerHTML = hash; // sink vulnerable
  }
}
```
- **Source:** `location.hash`.
- **Sink:** `innerHTML`, en la rama "else" (cualquier valor que no sea
  `inicio` ni `contacto`).

## Pasos de la solución
1. Modificar el fragmento de la URL a algo distinto de `inicio`/`contacto`,
   por ejemplo:
   ```
   http://localhost:8080/estudiante/dom/#<img src=x onerror=alert('FLAG_DOM')>
   ```
2. Como es un cambio de hash, puede ser necesario forzar el evento
   `hashchange` (recargar la página tras pegar la URL, o escribirla
   directamente en la barra y presionar Enter).
3. El navegador ejecuta el `onerror` del `<img>` y aparece
   `alert('FLAG_DOM')`.

## Punto clave para la discusión
Este patrón ("router" simple basado en hash) es muy común en aplicaciones de
una sola página (SPA) hechas a mano. Aunque el hash **nunca se envía al
servidor**, sigue siendo una fuente de datos no confiable para el DOM.

## Criterio de evaluación sugerido
- ✅ Identifica el source (`location.hash`) y el sink (`innerHTML`).
- ✅ Construye un payload que evita las ramas `inicio`/`contacto`.
- ✅ Explica por qué el servidor nunca ve este ataque en sus logs.
- ✅ Propone la corrección (`textContent` o sanitización con DOMPurify).
