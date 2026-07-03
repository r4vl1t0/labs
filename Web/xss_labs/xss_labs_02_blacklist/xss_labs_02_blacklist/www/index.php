<?php
// ============================================================
// PROTECCIÓN DE ACCESO — SOLO PARA EL PROFESOR
// ------------------------------------------------------------
// Este índice lista los 6 laboratorios y por eso no debe ser
// visible para los estudiantes: ellos deben entrar directamente
// a la ruta de cada lab que el profesor les entregue.
//
// Usuario y contraseña se pueden configurar con variables de
// entorno en docker-compose.yml (INDEX_USER / INDEX_PASS).
// Si no se configuran, se usan estos valores por defecto:
// usuario "profesor" / contraseña "cambiame123".
// ============================================================
$usuarioValido    = getenv('INDEX_USER') ?: 'profesor';
$contrasenaValida = getenv('INDEX_PASS') ?: 'cambiame123';

$usuarioRecibido    = $_SERVER['PHP_AUTH_USER'] ?? '';
$contrasenaRecibida = $_SERVER['PHP_AUTH_PW'] ?? '';

if ($usuarioRecibido !== $usuarioValido || $contrasenaRecibida !== $contrasenaValida) {
    header('WWW-Authenticate: Basic realm="Panel del profesor - Laboratorios XSS"');
    header('HTTP/1.0 401 Unauthorized');
    echo "Acceso restringido. Esta página es solo para el profesor.";
    exit;
}
?>
<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<title>Laboratorios de XSS - Clase de Seguridad Web</title>
<link rel="stylesheet" href="/assets/style.css">
</head>
<body>
<div class="container" style="max-width:900px;">
  <h1>🧪 Laboratorios de XSS</h1>
  <div class="warning">
    ⚠️ Estas aplicaciones son <strong>intencionalmente vulnerables</strong>.
    Úsalas solo en este contenedor Docker aislado, con fines educativos.
    No las despliegues en internet ni con datos reales.
  </div>

  <h2>👨‍🏫 Módulo Profesor (demo guiada)</h2>
  <div class="lab-grid">
    <div class="lab-card">
      <h4>1. XSS Reflejado</h4>
      <p>Buscador con payload de ejemplo y botón de demo.</p>
      <a class="btn" href="/profesor/reflejado/">Abrir</a>
    </div>
    <div class="lab-card">
      <h4>2. XSS Almacenado</h4>
      <p>Libro de visitas con payload guardado en el servidor.</p>
      <a class="btn" href="/profesor/almacenado/">Abrir</a>
    </div>
    <div class="lab-card">
      <h4>3. XSS DOM-based</h4>
      <p>Saludo dinámico manipulado 100% en el navegador.</p>
      <a class="btn" href="/profesor/dom/">Abrir</a>
    </div>
  </div>

  <h2 style="margin-top:32px;">🧑‍🎓 Módulo Estudiante (retos)</h2>
  <div class="lab-grid">
    <div class="lab-card">
      <h4>4. Reto XSS Reflejado</h4>
      <p>Roba la cookie <code>flag</code> mediante el buscador.</p>
      <a class="btn" href="/estudiante/reflejado/">Abrir</a>
    </div>
    <div class="lab-card">
      <h4>5. Reto XSS Almacenado</h4>
      <p>Deja un comentario que ejecute JS para cualquier visitante.</p>
      <a class="btn" href="/estudiante/almacenado/">Abrir</a>
    </div>
    <div class="lab-card">
      <h4>6. Reto XSS DOM-based</h4>
      <p>Explota el router basado en <code>location.hash</code>.</p>
      <a class="btn" href="/estudiante/dom/">Abrir</a>
    </div>
  </div>
</div>
</body>
</html>
