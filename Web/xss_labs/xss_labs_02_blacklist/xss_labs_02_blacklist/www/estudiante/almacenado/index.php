<?php
// ============================================================
// LABORATORIO 5 — XSS ALMACENADO — VERSIÓN ESTUDIANTE (RETO)
// ============================================================

if (!isset($_COOKIE['flag'])) {
    setcookie('flag', 'FLAG{stored_xss_demo_2026}', time() + 3600, '/');
}

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
<title>Libro de visitas — Reto Estudiante</title>
<link rel="stylesheet" href="/assets/style.css">
</head>
<body>
<div class="banner estudiante">RETO ESTUDIANTE — XSS Almacenado (Lab 5/6)</div>
<div class="container">
  <p><a href="/">&larr; volver al índice</a></p>
  <h1>📖 Libro de visitas</h1>

  <div class="challenge-box">
    <h3>🎯 Reto</h3>
    <p>Publica un comentario que haga que, al recargar la página (o al
    abrirla en otra pestaña / navegador), se ejecute JavaScript y muestre
    la cookie <code>flag</code> en un <code>alert()</code>.</p>
    <p><strong>Pista:</strong> el comentario se guarda tal cual en el
    servidor. Piensa qué pasa cuando la página vuelve a cargar ese
    contenido.</p>
  </div>

  <form method="POST">
    <textarea name="comentario" rows="3" placeholder="Escribe un comentario..."></textarea>
    <button type="submit">Publicar</button>
  </form>
  <form method="POST" style="margin-top:6px;">
    <button type="submit" name="reset" value="1" style="background:#dc2626;color:white;">
      🗑 Reiniciar comentarios
    </button>
  </form>

  <h3 style="margin-top:24px;">💬 Comentarios (<?php echo count($comentarios); ?>)</h3>
  <?php foreach ($comentarios as $c): ?>
    <div class="comment"><?php echo $c; ?></div>
  <?php endforeach; ?>
</div>
</body>
</html>
