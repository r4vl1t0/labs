# Writeup — Lab 3: XSS DOM-based (Profesor)

**Ruta:** `/profesor/dom/`

## Descripción
Esta página es HTML/JS puro: **el servidor no procesa el parámetro** en
ningún momento. Todo el flujo vulnerable ocurre en el navegador (source →
sink), lo que hace este tipo de XSS invisible para muchos escáneres del lado
del servidor y para los logs del backend.

## Código vulnerable
```javascript
const params = new URLSearchParams(location.search);
const nombre = params.get('nombre') || 'invitado';
document.getElementById('saludo').innerHTML = nombre; // sink peligroso
```
- **Source:** `location.search` (controlado por el atacante vía URL).
- **Sink:** `innerHTML` (interpreta el string como HTML).

## Explotación (para la demo)
1. Navegar a:
   ```
   http://localhost:8080/profesor/dom/?nombre=<img src=x onerror=alert('DOM XSS')>
   ```
2. Mostrar en las DevTools (pestaña *Network*) que **no hay ninguna
   petición al servidor con el payload como tal**: todo ocurre en el
   cliente al parsear la URL con JavaScript.

## Impacto
- Igual de peligroso que el reflejado/almacenado (ejecución de JS arbitrario
  en el contexto de la página), pero más difícil de detectar con WAFs o
  logs de servidor tradicionales, ya que el servidor nunca "ve" el payload
  interpretado como código.

## Remediación
```javascript
document.getElementById('saludo').textContent = nombre;
```
Además:
- Evitar sinks peligrosos (`innerHTML`, `document.write`, `eval`,
  `setTimeout(string)`) con datos no confiables.
- Si se necesita insertar HTML, sanitizar con **DOMPurify** antes.
- CSP con `script-src` estricto reduce el impacto aunque no elimina la causa.
