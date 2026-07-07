# Laboratorio de Inyecciones Avanzadas y XXE

Laboratorio unico en Docker para clase. Expone una sola entrada HTTP con Nginx y enruta internamente a Flask, PHP y Java/Pebble.

## Levantar

```bash
docker compose up --build
```

Abrir:

```text
http://localhost:5001
```

En Linux remoto, reemplazar `localhost` por la IP del servidor.

## Rutas

Profesor:

```text
/A/lab1-command-injection-1
/A/lab2-command-njection2
/A/lab3-ssti-pebble
/A/lab4-ssti-jinja2
/A/lab5-xxe
```

Alumno:

```text
/B/lab1-command-injection-1
/B/lab2-command-njection2
/B/lab3-ssti-pebble
/B/lab4-ssti-jinja2
/B/lab5-xxe
```

Reto final:

```text
/zorum
```

## Notas

El archivo `WRITEUPS_PROFESOR.md` contiene las soluciones y payloads. No debe compartirse con estudiantes.
