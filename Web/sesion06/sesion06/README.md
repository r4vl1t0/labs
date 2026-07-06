# Laboratorio IDOR y Fallos de Control de Acceso

Aplicacion vulnerable unica para levantar con Docker en Linux.

## Ejecutar con Docker Compose

```bash
docker compose up --build
```

Abrir:

```text
http://localhost:8000
```

Para detener:

```bash
docker compose down
```

## Ejecutar con Docker sin Compose

```bash
docker build -t idor-access-lab .
docker run --rm -p 8000:8000 idor-access-lab
```

## Credenciales

Para los laboratorios que usan login:

```text
root:987654321
```

## Secciones

- Laboratorio 1: IDOR en voucher de compra, version alumno y profesor.
- Laboratorio 2: IDOR con pseudo GUID, version alumno y profesor.
- Laboratorio 3: LFI, version alumno y profesor.
- Laboratorio 4: Mass Assignment, version alumno y profesor.
- Laboratorio final: reto encadenado con directorio oculto, IDOR, JWT y LFI en API antigua.

Las flags de alumno y profesor son distintas.
