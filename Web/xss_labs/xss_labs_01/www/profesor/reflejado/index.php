<?php
// ============================================================
// LABORATORIO 1 — XSS REFLEJADO — VERSIÓN PROFESOR
// ------------------------------------------------------------
// VULNERABILIDAD: el parámetro GET "q" se refleja directamente
// dentro del HTML de respuesta SIN sanitizar (sin htmlspecialchars).
// Esto permite inyectar HTML/JS que el navegador de la víctima
// ejecutará al visitar una URL manipulada.
// ============================================================

if (!isset($_COOKIE['flag'])) {
    setcookie('flag', 'FLAG{reflected_xss_demo_2026}', time() + 3600, '/');
}

$q = isset($_GET['q']) ? $_GET['q'] : '';
?>
<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<title>Buscador — Modo Profesor</title>
<link rel="stylesheet" href="/assets/style.css">
</head>
<body>
<div class="banner profesor">DEMO - XSS Reflejado (Lab 1)</div>
<div class="container">
  <p><a href="/">&larr; volver al índice</a></p>
  <h1>Buscador de productos</h1>
  <p class="hint">
    Objetivo de la demo: mostrar cómo un parámetro de la URL
    (<code>?q=</code>) se inserta sin escapar dentro del HTML de respuesta.
  </p>

  <form method="GET">
    <input type="text" name="q" placeholder="Buscar producto...">
    <button type="submit">Buscar</button>
  </form>

  <?php if ($q !== ''): ?>
    <!-- VULNERABLE: se imprime $q tal cual, sin htmlspecialchars() -->
    <p class="result">Resultados para: <?php echo $q; ?></p>
  <?php endif; ?>

</div>
</body>
</html>
