<?php
// ============================================================
// LABORATORIO 4 — XSS REFLEJADO — VERSIÓN ESTUDIANTE (RETO)
// ============================================================

if (!isset($_COOKIE['flag'])) {
    setcookie('flag', 'FLAG{reflected_xss_demo_lum_2026}', time() + 3600, '/');
}

$q = isset($_GET['q']) ? $_GET['q'] : '';
?>
<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<title>Buscador — Reto Estudiante</title>
<link rel="stylesheet" href="/assets/style.css">
</head>
<body>
<div class="banner estudiante">RETO ESTUDIANTE — XSS Reflejado (Lab 4/6)</div>
<div class="container">
  <p><a href="/">&larr; volver al índice</a></p>
  <h1>Buscador de productos</h1>

  <div class="challenge-box">
    <h3>Reto</h3>
    <p>Este buscador refleja tu búsqueda en la página. El servidor guardó
    una cookie llamada <code>flag</code>. Consigue que el navegador
    ejecute JavaScript y muestre esa cookie en un <code>alert()</code>.</p>
    <p><strong>Pista:</strong> prueba primero con texto normal y observa
    dónde aparece en el HTML (clic derecho → Ver código fuente / Inspeccionar).</p>
  </div>

  <form method="GET">
    <input type="text" name="q" placeholder="Buscar producto...">
    <button type="submit">Buscar</button>
  </form>

  <?php if ($q !== ''): ?>
    <p class="result">Resultados para: <?php echo $q; ?></p>
  <?php endif; ?>
</div>
</body>
</html>
