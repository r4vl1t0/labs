<?php
// ============================================================
// LABORATORIO 2 — XSS ALMACENADO — VERSIÓN PROFESOR
// ------------------------------------------------------------
// VULNERABILIDAD: los comentarios se guardan y se muestran tal
// cual, sin sanitizar. Cualquier visitante que cargue la página
// ejecutará el JS inyectado por un atacante anterior.
// ============================================================

$dataFile = __DIR__ . '/data/comentarios.txt';
if (!file_exists($dataFile)) {
    file_put_contents($dataFile, '');
}

if (isset($_POST['reset'])) {
    file_put_contents($dataFile, '');
    header('Location: index.php');
    exit;
}

if ($_SERVER['REQUEST_METHOD'] === 'POST' && isset($_POST['comentario']) && trim($_POST['comentario']) !== '') {
    // VULNERABLE: se guarda el comentario sin sanitizar
    file_put_contents($dataFile, $_POST['comentario'] . "\n@@@\n", FILE_APPEND);
    header('Location: index.php');
    exit;
}

$raw = file_get_contents($dataFile);
$comentarios = array_filter(explode("\n@@@\n", $raw), fn($c) => trim($c) !== '');
?>
<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<title>Libro de visitas — Modo Profesor</title>
<link rel="stylesheet" href="/assets/style.css">
</head>
<body>
<div class="banner profesor">MODO PROFESOR — XSS Almacenado (Lab 2/6)</div>
<div class="container">
  <p><a href="/">&larr; volver al índice</a></p>
  <h1>📖 Libro de visitas</h1>
  <p class="hint">
    Objetivo de la demo: mostrar que el HTML guardado en el servidor se
    ejecuta para TODOS los visitantes que carguen la página, no solo
    para quien lo envió.
  </p>

  <form method="POST">
    <textarea name="comentario" rows="3" placeholder="Escribe un comentario..."></textarea>
    <button type="submit">Publicar</button>
  </form>
  <form method="POST" style="margin-top:6px;">
    <button type="submit" name="reset" value="1" style="background:#dc2626;color:white;">
      🗑 Reiniciar comentarios
    </button>
  </form>

  <div class="payload-box">
    <h3>▶ Payload de ejemplo para la demo en vivo</h3>
    <code>&lt;script&gt;alert('XSS Almacenado ejecutado para: ' + document.cookie)&lt;/script&gt;</code>
    <p>Publícalo en el campo de arriba y recarga la página con otra pestaña
    (o en modo incógnito) para ver que se ejecuta para cualquier visitante.</p>
  </div>

  <h3 style="margin-top:24px;">💬 Comentarios (<?php echo count($comentarios); ?>)</h3>
  <?php foreach ($comentarios as $c): ?>
    <!-- VULNERABLE: se imprime $c tal cual, sin htmlspecialchars() -->
    <div class="comment"><?php echo $c; ?></div>
  <?php endforeach; ?>

  <div class="fix-box">
    <h3>🔧 Corrección (mostrar al final de la demo)</h3>
    <pre>&lt;?php echo htmlspecialchars($c, ENT_QUOTES, 'UTF-8'); ?&gt;</pre>
    <p>Además: validar/limitar el contenido permitido, usar una librería de
    sanitización de HTML (ej. HTML Purifier) si se necesita permitir
    formato, y aplicar CSP.</p>
  </div>
</div>
</body>
</html>
